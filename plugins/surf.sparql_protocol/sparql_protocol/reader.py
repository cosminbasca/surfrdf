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

import sys
from SPARQLWrapper import SPARQLWrapper, jsonlayer, JSON
from SPARQLWrapper.SPARQLExceptions import EndPointNotFound, QueryBadFormed, SPARQLWrapperException

from surf.plugin.query_reader import RDFQueryReader
from surf.query.translator.sparql import SparqlTranslator
from surf.rdf import BNode, ConjunctiveGraph, Literal, URIRef

class SparqlReaderException(Exception): pass

class ReaderPlugin(RDFQueryReader):
    def __init__(self, *args, **kwargs):
        RDFQueryReader.__init__(self,*args,**kwargs)
        
        self.__endpoint         = kwargs['endpoint'] if 'endpoint' in kwargs else None
        #self.__results_format  = kwargs['results_format'] if 'results_format' in kwargs else JSON
        self.__results_format   = JSON
        
        #if self.__results_format not in [JSON, XML]:
        #    raise UnsupportedResultType('Result of type %s is unsupported'%self.__results_format)
        self.__sparql_wrapper   = SPARQLWrapper(self.__endpoint, self.__results_format)

        # Try to use cjson
        try: 
            import cjson
            jsonlayer.use("cjson")
            self.log.info("using cjson")
        except:
            self.log.warning("cjson not available, falling back on slower simplejson")
        
    endpoint        = property(lambda self: self.__endpoint)
    results_format  = property(lambda self: self.__results_format)
    
    def _to_table(self, result):
        return result['results']['bindings']
        
    def _ask(self, result):
        '''
        returns the boolean value of a ASK query
        '''

        return result.get("boolean")
    
    def execute_sparql(self, q_string, format = 'JSON'):
        try:
            self.log.debug(q_string)
            if isinstance(q_string, unicode):
                # SPARQLWrapper doesn't like unicode
                q_string = q_string.encode("utf-8")
            self.__sparql_wrapper.setQuery(q_string)
            results = self.__sparql_wrapper.query().convert()
            return self._toRdflib(results)
        except EndPointNotFound, notfound: 
            raise SparqlReaderException("Endpoint not found"), None, sys.exc_info()[2]
        except QueryBadFormed, badquery:
            raise SparqlReaderException("Bad query: %s" % q_string), None, sys.exc_info()[2]
        except Exception, e:
            raise SparqlReaderException(), None, sys.exc_info()[2]
    
    # execute
    def _execute(self, query):
        q_string = SparqlTranslator(query).translate()
        return self.execute_sparql(q_string)
    
    def close(self):
        pass
    
    def _toRdflib(self,results):
        """Convert the result dict to rdfLib types."""
        
        if isinstance(results, ConjunctiveGraph):
            return results        

        if results:
            if results.has_key('results'):
                for i in range(len(results['results']['bindings'])):
                    json_item = results['results']['bindings'][i]
                    rdf_item = {}
                    for key in json_item:
                        type = json_item[key].get('type')
                        value = json_item[key].get('value')
                        rdfType = None
                        if type == 'uri': rdfType = URIRef(value)
                        elif type == 'literal':
                            rdfType = Literal(value,lang=json_item[key]['xml:lang']) if 'xml:lang' in json_item[key] else Literal(value)  
                        elif type == 'typed-literal':
                            rdfType = Literal(value,datatype=URIRef(json_item[key]['datatype']))
                        elif type == 'bnode': rdfType = BNode(value)
                        rdf_item[key] = rdfType 
                    results['results']['bindings'][i] = rdf_item
        return results
        
    
