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
__author__ = 'Cosmin Basca'

#TODO: move the translators in the future in a pluggable architecture

# the rdf way
#from rdf.graph import Graph, ConjunctiveGraph
#from rdf.term import URIRef, Literal, BNode, RDF, RDFS
#from rdf.namespace import Namespace
# the rdflib 2.4.x way

from surf.query.translator.sparql import SparqlTranslator
from surf.query.update import LOAD, CLEAR, INSERT, INSERT_DATA, DELETE, DELETE_DATA


class SparulTranslator(SparqlTranslator):
    '''translates a query to SPARQL Update,
    based on the description of the SPARQL UPDATE protocol found here

    http://jena.hpl.hp.com/~afs/SPARQL-Update.html'''

    def translate(self):
        if self.query.query_type == LOAD:
            return self._translate_load(self.query)
        elif self.query.query_type == CLEAR:
            return self._translate_clear(self.query)
        elif self.query.query_type in [INSERT, INSERT_DATA]:
            return self._translate_insert(self.query)
        elif self.query.query_type in [DELETE, DELETE_DATA]:
            return self._translate_delete(self.query)

    def _translate_load(self, query):
        rep = 'LOAD %(remote_uri)s %(into_exp)s'
        if query.query_remote_uri:
            remote_uri = query.query_remote_uri
        else:
            raise ValueError('No Remote URI specified for a LOAD query')
        
        into_exp = ""
        if len(query.query_into_uri) == 1:
            into_exp = "INTO %s" % query.query_into_uri[0]

        return rep % ({'remote_uri':remote_uri,
                       'into_exp':into_exp})

    def _translate_clear(self, query):
        
        graph = ""
        if query.query_clear_uri:
            graph = "GRAPH <%s>" % query.query_clear_uri

        return "CLEAR %s" % graph

    def _translate_insert(self, query):
        rep = 'INSERT %(data)s %(into)s %(template)s %(where)s'
        data = query.query_type == INSERT_DATA and "DATA" or ""
        into = ' '.join([ "INTO <%s>" % uri for uri in query.query_into_uri])
        template = '{ %s }' % ('. '.join([self._statement(stmt) for stmt in self.query.query_template]))
        where_pattern = '. '.join([self._statement(stmt) for stmt in self.query.query_data])

        where = ""
        if query.query_type == INSERT and where_pattern:
            where = "WHERE { %s }" % (where_pattern)

        return rep % ({'data'     :data,
                     'into'     :into,
                     'template' :template,
                     'where'    :where})

    def _translate_delete(self, query):
        rep = 'DELETE %(data)s %(from_)s %(template)s %(where)s'
        data = query.query_type == DELETE_DATA and "DATA" or ""

        from_ = ' '.join([ "FROM <%s>" % uri for uri in query.query_from_uri])
        template = '{ %s }' % ('. '.join([self._statement(stmt) for stmt in self.query.query_template]))
        
        where = ""
        if query.query_type == DELETE:
            where_pattern = '. '.join([self._statement(stmt) for stmt in self.query.query_data])
            where = 'WHERE { %s }' % where_pattern

        return rep % ({'data'     :data,
                     'from_'    :from_,
                     'template' :template,
                     'where'    :where})
