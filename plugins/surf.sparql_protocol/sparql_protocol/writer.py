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

import sys

from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import EndPointNotFound, QueryBadFormed, SPARQLWrapperException

from reader import ReaderPlugin
from surf.plugin.writer import RDFWriter
from surf.query import Filter, Group, NamedGroup, Union
from surf.query.update import insert, delete, clear
from surf.rdf import BNode, Literal, URIRef

class SparqlWriterException(Exception): pass

class WriterPlugin(RDFWriter):
    def __init__(self, reader, *args, **kwargs):
        RDFWriter.__init__(self, reader, *args, **kwargs)
        
        if isinstance(self.reader, ReaderPlugin):
            self.__endpoint = self.reader.endpoint
        else:
            self.__endpoint = kwargs.get("endpoint")

        self.__combine_queries = kwargs.get("combine_queries")
        self.__results_format = JSON

        print "endpoint: %s" % self.__endpoint
        self.__sparql_wrapper = SPARQLWrapper(self.__endpoint, self.__results_format)
        self.__sparql_wrapper.setMethod("POST")

    endpoint = property(lambda self: self.__endpoint)

    def __group_by_context(self, resources):
        contexts = {}
        for resource in resources:
            context_group = contexts.setdefault(resource.context, [])
            context_group.append(resource)
        
        return contexts
    
    def _save(self, *resources):
        for context, items in self.__group_by_context(resources).items():
            # Deletes all triples with matching subjects.
            remove_query = self.__prepare_delete_many_query(items, context)
            insert_query = self.__prepare_add_many_query(items, context)
            self.__execute(remove_query, insert_query)

    def _update(self, *resources):
        for context, items in self.__group_by_context(resources).items():
            # Explicitly enumerates triples for deletion.
            remove_query = self.__prepare_selective_delete_query(items, context)
            insert_query = self.__prepare_add_many_query(items, context)
            self.__execute(remove_query, insert_query)

    def _remove(self, *resources, **kwargs):
        for context, items in self.__group_by_context(resources).items():
            # Deletes all triples with matching subjects.
            inverse = kwargs.get("inverse")
            query = self.__prepare_delete_many_query(items, context, inverse)
            self.__execute(query)

    def _size(self):
        """ Return total count of triples, not implemented. """

        raise NotImplementedError

    def _add_triple(self, s = None, p = None, o = None, context = None):
        self.__add(s, p, o, context)

    def _set_triple(self, s = None, p = None, o = None, context = None):
        self.__remove(s, p, context = context)
        self.__add(s, p, o, context)

    def _remove_triple(self, s = None, p = None, o = None, context = None):
        self.__remove(s, p, o, context)

    def __prepare_add_many_query(self, resources, context = None):
        query = insert()

        if context:
            query.into(context)

        for resource in resources:
            s = resource.subject
            for p, objs in resource.rdf_direct.items():
                for o in objs:
                    query.template((s, p, o))    

        return query
    
    def __prepare_delete_many_query(self, resources, context, inverse = False):
        query = delete()
        if context:
            query.from_(context)

        query.template(("?s", "?p", "?o"))

        if context:
            where_clause = NamedGroup(context)
        else:
            where_clause = Group()

        subjects = [resource.subject for resource in resources]
        filter = " OR ".join(["?s = <%s>" % subject for subject in subjects])
        filter = Filter("(%s)" % filter)

        if inverse:
            filter2 = " OR ".join(["?o = <%s>" % subject for subject in subjects])
            filter2 = Filter("(%s)" % filter2)

            where1 = Group([("?s", "?p", "?o"), filter])
            where2 = Group([("?s", "?p", "?o"), filter2])
            where_clause.append(Union([where1, where2]))
        else:
            where_clause.append(("?s", "?p", "?o"))
            where_clause.append(filter)

        query.where(where_clause)
        
        return query        
    
    def __prepare_selective_delete_query(self, resources, context = None):
        query = delete()
        if context:
            query.from_(context)

        query.template(("?s", "?p", "?o"))
        
        clauses = []
        for resource in resources:
            for p in resource.rdf_direct:
                filter = Filter("(?s = <%s> AND ?p = <%s>)" % (resource.subject, p))
                clauses.append(Group([("?s", "?p", "?o"), filter]))
                 
        query.union(*clauses)
        return query        
    
    def __execute(self, *queries):
        """ Execute several queries. """
        
        translated = [unicode(query) for query in queries]  
        if self.__combine_queries:
            translated = ["\n".join(translated)]

        try:
            for query_str in translated:
                self.log.debug(query_str)
                
                    
                self.__sparql_wrapper.setQuery(query_str)
                self.__sparql_wrapper.query()

            return True

        except EndPointNotFound, _:
            raise SparqlWriterException("Endpoint not found"), None, sys.exc_info()[2]
        except QueryBadFormed, _:
            raise SparqlWriterException("Bad query: %s" % query_str), None, sys.exc_info()[2]
        except Exception, e:
            raise SparqlWriterException("Exception: %s" % e), None, sys.exc_info()[2]

    def __add_many(self, triples, context = None):
        self.log.debug("ADD several triples")

        query = insert()

        if context:
            query.into(context)

        for s, p, o in triples:
            query.template((s, p, o))

        try:
            query_str = unicode(query)
            self.log.debug(query_str)
            self.__sparql_wrapper.setQuery(query_str)
            self.__sparql_wrapper.query().convert()
            return True

        except EndPointNotFound, notfound:
            raise SparqlWriterException("Endpoint not found"), None, sys.exc_info()[2]
        except QueryBadFormed, badquery:
            raise SparqlWriterException("Bad query: %s" % query_str), None, sys.exc_info()[2]
        except Exception, e:
            raise SparqlWriterException("Exception: %s" % e), None, sys.exc_info()[2]

    def __add(self, s, p, o, context = None):
        return self.__add_many([(s, p, o)], context)

    def __remove(self, s = None, p = None, o = None, context = None):
        self.log.debug('REM : %s, %s, %s, %s' % (s, p, o, context))

        query = delete()
        try:
            #clear
            if s == None and p == None and o == None and context:
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
                filter = Filter("(" + self.__build_filter(s, p, o) + ")")
                where_group.append(filter)

                query.where(where_group)

            query_str = unicode(query)
            self.log.debug(query_str)
            self.__sparql_wrapper.setQuery(query_str)
            self.__sparql_wrapper.query().convert()
            return True
        except EndPointNotFound, notfound:
            self.log.error('SPARQL ENDPOINT not found : \n' + str(notfound))
        except QueryBadFormed, badquery:
            self.log.error('SPARQL EXCEPTION ON QUERY (BAD FORMAT): \n ' + str(badquery))
        except SPARQLWrapperException, sparqlwrapper:
            self.log.error('SPARQL WRAPPER Exception \n' + str(sparqlwrapper))

        return None

    def __build_filter(self, s, p, o):
        vars = [(s, '?s'), (p, '?p'), (o, '?o')]
        parts = []
        for var in vars:
            if var[0] != None:
                parts.append("%s = %s" % (var[1], self._term(var[0])))

        return " and ".join(parts)

    def index_triples(self, **kwargs):
        '''
        performs index of the triples if such functionality is present,
        returns True if operation successfull
        '''

        # SPARQL/Update doesn't have standard way to force reindex. 
        return False

    def _clear(self, context = None):
        """ Clear the triple-store. """

        self.__remove(None, None, None, context = context)

    def _term(self, term):
        if type(term) in [URIRef, BNode]:
            return '%s' % (term.n3())
        elif type(term) in [str, unicode]:
            if term.startswith('?'):
                return '%s' % term
            elif is_uri(term):
                return '<%s>' % term
            else:
                return '"%s"' % term
        elif type(term) is Literal:
            return term.n3()
        elif type(term) in [list, tuple]:
            return '"%s"@%s' % (term[0], term[1])
        elif type(term) is type and hasattr(term, 'uri'):
            return '%s' % term.uri().n3()
        elif hasattr(term, 'subject'):
            return '%s' % term.subject().n3()
        return term.__str__()
