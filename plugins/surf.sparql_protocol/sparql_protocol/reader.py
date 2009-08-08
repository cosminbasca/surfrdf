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


from surf.plugin.query_reader import RDFQueryReader
from surf.query_to_sparql import translate
from SPARQLWrapper import SPARQLWrapper, JSON, XML, GET, POST
from SPARQLWrapper.SPARQLExceptions import EndPointNotFound, QueryBadFormed, SPARQLWrapperException

# the rdf way
#from rdf.term import URIRef, BNode, Literal
# the rdflib 2.4.x way
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal

class ReaderPlugin(RDFQueryReader):
    def __init__(self,*args,**kwargs):
        RDFQueryReader.__init__(self,*args,**kwargs)
        
        self.__endpoint         = kwargs['endpoint'] if 'endpoint' in kwargs else None
        self.__default_graph    = kwargs['default_graph'] if 'default_graph' in kwargs else None
        #self.__results_format  = kwargs['results_format'] if 'results_format' in kwargs else JSON
        self.__results_format   = JSON
        
        #if self.__results_format not in [JSON, XML]:
        #    raise UnsupportedResultType('Result of type %s is unsupported'%self.__results_format)
        self.__sparql_wrapper   = SPARQLWrapper(self.__endpoint, self.__results_format,defaultGraph=self.__default_graph)
        
    endpoint        = property(lambda self: self.__endpoint)
    default_graph   = property(lambda self: self.__default_graph)
    results_format  = property(lambda self: self.__results_format)
    
    def _values(self,result,vkey='v',ckey='c'):
        '''
        returns a dictionary of the form {value : [concept,concept,...]}
        result represents the query returned result
        '''
        results = result['results']['bindings']
        values = {}
        if not results:
            return values
        for v in results:
            if v[vkey] not in values: values[v[vkey]] = []
            if ckey in v: values[v[vkey]].append(v[ckey])
        return values
    
    def _predicacte_values(self,result,pkey='p',vkey='v',ckey='c'):
        '''
        returns a dictionary with predicates as keys, the values
        are the same as returned by the _values function
        returns a dictionary of the form {value : [concept,concept,...]}
        {predicate: {value : [concept,concept,...]},
         predicate: {value : [concept,concept,...]},}
        result represents the query returned result
        '''
        results = result['results']['bindings']
        pvalues = {}
        if not results:
            return pvalues
        for v in results:
            p = v[pkey]
            if p not in pvalues: pvalues[p] = {}
            if v[vkey] not in pvalues[p]: pvalues[p][v[vkey]] = []
            if ckey in v: pvalues[p][v[vkey]].append(v[ckey])
        return pvalues
        
    def _ask(self,result):
        '''
        returns the boolean value of a ASK query
        '''
        return result
    
    # execute
    def _execute(self,query):
        q_string = translate(query)
        try:
            self.log.debug(q_string)
            self.__sparql_wrapper.setQuery(q_string)
            results = self.__sparql_wrapper.query().convert()
            return self._toRdflib(results)
        except EndPointNotFound, notfound: 
            self.log.error('SPARQL ENDPOINT not found : \n'+str(notfound))
        except QueryBadFormed, badquery:
            self.log.error('SPARQL EXCEPTION ON QUERY (BAD FORMAT): \n '+str(badquery))
        except SPARQLWrapperException, sparqlwrapper:
            self.log.error('SPARQL WRAPPER Exception \n'+str(sparqlwrapper))
        except Exception, e:
            self.log.error('Exception while querying'+str(e))
        return None
    
    def close(self):
        pass
    
    def _toRdflib(self,results):
        """
        converts the result dict to rdfLib types
        """
        if results:
            if results.has_key('results'):
                for i in range(len(results['results']['bindings'])):
                    json_item = results['results']['bindings'][i]
                    rdf_item = {}
                    for key in json_item:
                        type = json_item[key]['type']
                        value = json_item[key]['value']
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
        
    
