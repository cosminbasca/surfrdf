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
from rdflib.Namespace import Namespace
from rdflib.Graph import Graph, ConjunctiveGraph
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal
from rdflib.RDF import RDFNS as RDF
from rdflib.RDFS import RDFSNS as RRDFS


from surf.query.translator.sparql import SparqlTranslator
from surf.query import Group, NamedGroup, OptionalGroup, Filter
from surf.query.update import QueryUpdate, LOAD, CLEAR, INSERT, INSERT_DATA, DELETE, DELETE_DATA
from surf.util import is_uri

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
            
    def _translate_load(self,query):
        rep = 'LOAD %(remote_uri)s %(into_exp)s'
        if query.query_remote_uri:
            remote_uri = query.query_remote_uri
        else:
            raise ValueError('No Remote URI specified for a LOAD query')
        into_exp = 'INTO %s'%(query.query_into_uri[0]) if len(query.query_into_uri) == 1 else ''
        return rep%({'remote_uri':remote_uri,
                     'into_exp':into_exp})
    
    def _translate_clear(self,query):
        rep = 'CLEAR %(graph)s'
        graph = 'GRAPH %s'%(query.query_clear_uri) if query.query_clear_uri else ''
        return rep%({'graph':graph})
    
    def _translate_insert(self,query):
        rep = 'INSERT %(data)s %(into)s %(template)s %(where)s'
        data            = 'DATA' if query.query_type == INSERT_DATA else ''
        into            = 'INTO %s'%(','.join(query.query_into_uri)) if len(query.query_into_uri) > 0 else ''
        template        = '{ %s }'%('. '.join([self._statement(stmt) for stmt in self.query.query_template]))
        where_pattern   = '. '.join([self._statement(stmt) for stmt in self.query.query_data])
        where           = 'WHERE { %s }'%(where_pattern) if query.query_type == INSERT else ''
        return rep%({'data'     :data,
                     'into'     :into,
                     'template' :template,
                     'where'    :where})
    
    def _translate_delete(self,query):
        rep = 'DELETE %(data)s %(from_)s %(template)s %(where)s'
        data            = 'DATA' if query.query_type == DELETE_DATA else ''
        from_           = 'FROM %s'%(','.join(query.query_into_uri)) if len(query.query_into_uri) > 0 else ''
        template        = '{ %s }'%('. '.join([self._statement(stmt) for stmt in self.query.query_template]))
        where_pattern   = '. '.join([self._statement(stmt) for stmt in self.query.query_data])
        where           = 'WHERE { %s }'%(where_pattern) if query.query_type == DELETE else ''
        return rep%({'data'     :data,
                     'from_'    :from_,
                     'template' :template,
                     'where'    :where})
    