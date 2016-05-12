# Copyright (c) 2009, Digital Enterprise Research Institute (DERI),
# NUI Galway
# All rights reserved.
# author: Cosmin Basca
# email: cosmin.basca@gmail.com
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer
#      in the documentation and/or other materials provided with
#      the distribution.
#    * Neither the name of DERI nor the
#      names of its contributors may be used to endorse or promote
#      products derived from this software without specific prior
#      written permission.

# THIS SOFTWARE IS PROVIDED BY DERI ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DERI BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

# -*- coding: utf-8 -*-
__author__ = 'Cosmin Basca, Adam Gzella'

import six
import sys

from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import EndPointNotFound, QueryBadFormed, SPARQLWrapperException

from .reader import ReaderPlugin
from surf.plugin.writer import RDFWriter
from surf.query import Filter, Group, NamedGroup, Union
from surf.query.update import insert, delete, clear, load
from surf.rdf import BNode, Literal, URIRef
from surf.util import is_uri
from surf.log import *


class SparqlWriterException(Exception):
    pass


def _group_by_context(resources):
    contexts = {}
    for resource in resources:
        context_group = contexts.setdefault(resource.context, [])
        context_group.append(resource)
    return contexts


def _prepare_add_many_query(resources, context=None):
    query = insert()

    if context:
        query.into(context)

    for resource in resources:
        s = resource.subject
        for p, objs in resource.rdf_direct.items():
            for o in objs:
                query.template((s, p, o))

    return query


def _prepare_delete_many_query(resources, context, inverse=False):
    query = delete()
    if context:
        query.from_(context)

    query.template(("?s", "?p", "?o"))

    if context:
        where_clause = NamedGroup(context)
    else:
        where_clause = Group()

    subjects = [resource.subject for resource in resources]
    filter = " OR ".join([u"?s = <{0:s}>".format(subject) for subject in subjects])
    filter = Filter("(%s)" % filter)

    if inverse:
        filter2 = " OR ".join([u"?o = <{0:s}>".format(subject) for subject in subjects])
        filter2 = Filter("(%s)" % filter2)

        where1 = Group([("?s", "?p", "?o"), filter])
        where2 = Group([("?s", "?p", "?o"), filter2])
        where_clause.append(Union([where1, where2]))
    else:
        where_clause.append(("?s", "?p", "?o"))
        where_clause.append(filter)

    query.where(where_clause)

    return query


def _prepare_selective_delete_query(resources, context=None):
    query = delete()
    if context:
        query.from_(context)

    query.template(("?s", "?p", "?o"))

    clauses = []
    for resource in resources:
        for p in resource.rdf_direct:
            filter = Filter("(?s = <{0:s}> AND ?p = <{1:s}>)".format(resource.subject, p))
            clauses.append(Group([("?s", "?p", "?o"), filter]))

    query.union(*clauses)
    return query


class WriterPlugin(RDFWriter):
    def __init__(self, reader, *args, **kwargs):
        super(WriterPlugin, self).__init__(reader, *args, **kwargs)

        if isinstance(self.reader, ReaderPlugin):
            self._endpoint = self.reader.endpoint
        else:
            self._endpoint = kwargs.get("endpoint")

        self._combine_queries = kwargs.get("combine_queries")
        self._results_format = JSON

        self._sparql_wrapper = SPARQLWrapper(self._endpoint, returnFormat=self._results_format)
        user = kwargs.get('user', None)
        password = kwargs.get('password', None)
        if user is not None and password is not None:
            self._sparql_wrapper.setCredentials(user, password)

        self._sparql_wrapper.setMethod("POST")

    @property
    def endpoint(self):
        return self._endpoint

    def _save(self, *resources):
        for context, items in _group_by_context(resources).iteritems():
            # Deletes all triples with matching subjects.
            remove_query = _prepare_delete_many_query(items, context)
            insert_query = _prepare_add_many_query(items, context)
            self._execute(remove_query, insert_query)

    def _update(self, *resources):
        for context, items in _group_by_context(resources).iteritems():
            # Explicitly enumerates triples for deletion.
            remove_query = _prepare_selective_delete_query(items, context)
            insert_query = _prepare_add_many_query(items, context)
            self._execute(remove_query, insert_query)

    def _remove(self, *resources, **kwargs):
        for context, items in _group_by_context(resources).iteritems():
            # Deletes all triples with matching subjects.
            inverse = kwargs.get("inverse")
            query = _prepare_delete_many_query(items, context, inverse)
            self._execute(query)

    def _size(self):
        """ Return total count of triples, not implemented. """
        raise NotImplementedError

    def _add_triple(self, s=None, p=None, o=None, context=None):
        self._add(s, p, o, context)

    def _set_triple(self, s=None, p=None, o=None, context=None):
        self._remove_from_endpoint(s, p, context=context)
        self._add(s, p, o, context)

    def _remove_triple(self, s=None, p=None, o=None, context=None):
        self._remove_from_endpoint(s, p, o, context)

    def _execute(self, *queries):
        """ Execute several queries. """

        translated = [six.text_type(query) for query in queries]
        if self._combine_queries:
            translated = ["\n".join(translated)]

        try:
            for query_str in translated:
                debug(query_str)

                self._sparql_wrapper.setQuery(query_str)
                self._sparql_wrapper.query()

            return True

        except EndPointNotFound:
            e = SparqlWriterException("Endpoint not found")
            six.reraise(type(e), e, sys.exc_info()[2])
        except QueryBadFormed:
            e = SparqlWriterException("Bad query: %s" % query_str)
            six.reraise(type(e), e, sys.exc_info()[2])
        except Exception as e:
            e = SparqlWriterException("Exception: %s (query: %s)" % (e, query_str))
            six.reraise(type(e), e, sys.exc_info()[2])

    def _add_many(self, triples, context=None):
        debug("ADD several triples")
        query = insert()

        if context:
            query.into(context)

        for s, p, o in triples:
            query.template((s, p, o))

        query_str = six.text_type(query)
        try:
            debug(query_str)
            self._sparql_wrapper.setQuery(query_str)
            self._sparql_wrapper.query().convert()
            return True

        except EndPointNotFound:
            e = SparqlWriterException("Endpoint not found")
            six.reraise(type(e), e, sys.exc_info()[2])
        except QueryBadFormed:
            e = SparqlWriterException("Bad query: %s" % query_str)
            six.reraise(type(e), e, sys.exc_info()[2])
        except Exception as e:
            e = SparqlWriterException("Exception: %s" % str(e))
            six.reraise(type(e), e, sys.exc_info()[2])

    def _add(self, s, p, o, context=None):
        return self._add_many([(s, p, o)], context)

    def _remove_from_endpoint(self, s=None, p=None, o=None, context=None):
        debug('REM : %s, %s, %s, %s' % (s, p, o, context))

        query = delete()
        try:
            if s is None and p is None and o is None and context:
                query = clear().graph(context)
            else:
                if context:
                    query = delete().from_(context)

                query.template(("?s", "?p", "?o"))

                if context:
                    where_group = NamedGroup(context)
                else:
                    where_group = Group()

                where_group.append(("?s", "?p", "?o"))
                filter = Filter("({0})".format(self.__build_filter(s, p, o)))
                where_group.append(filter)
                query.where(where_group)

            query_str = six.text_type(query)
            debug(query_str)
            self._sparql_wrapper.setQuery(query_str)
            self._sparql_wrapper.query().convert()
            return True
        except EndPointNotFound:
            error("SPARQL endpoint not found")
        except QueryBadFormed:
            error("Bad-formed SPARQL query")
        except SPARQLWrapperException:
            error("SPARQLWrapper exception")

        return None

    def __build_filter(self, s, p, o):
        vars = [(s, '?s'), (p, '?p'), (o, '?o')]
        parts = []
        for var in vars:
            if var[0] is not None:
                parts.append("%s = %s" % (var[1], self._term(var[0])))

        return " and ".join(parts)

    def index_triples(self, **kwargs):
        """
        performs index of the triples if such functionality is present,
        returns True if operation successful
        """
        # SPARQL/Update does not support indexing operation
        return False

    def load_triples(self, source=None, context=None):
        """
        Load resources on the web into the triple-store.

        :param str source: path to the sources of triples to load
        :param context: the given context
        :return: True if successful
        :rtype: bool
        """
        if source:
            query = load()
            query.load(remote_uri=source)

            if context:
                query.into(context)

            query_str = six.text_type(query)
            debug(query_str)
            self._sparql_wrapper.setQuery(query_str)
            self._sparql_wrapper.query().convert()
            return True

        return False

    def _clear(self, context=None):
        """
        Clear the triple-store.
        """
        self._remove_from_endpoint(None, None, None, context=context)

    def _term(self, term):
        if isinstance(term, (URIRef, BNode)):
            return six.u('{0:s}'.format(term))
        elif isinstance(term, six.string_types):
            if term.startswith('?'):
                return six.u('{0:s}'.format(term))
            elif is_uri(term):
                return six.u('<{0:s}>'.format(term))
            else:
                return six.u('"{0:s}"'.format(term))
        elif isinstance(term, Literal):
            return term.n3()
        elif isinstance(term, (list, tuple)):
            return '"{0:s}"@{1:s}'.format(term[0], term[1])
        elif type(term) is type and hasattr(term, 'uri'):
            return six.u('{0:s}'.format(term))
        elif hasattr(term, 'subject'):
            return six.u('{0:s}'.format(term))

        return term.__str__()
