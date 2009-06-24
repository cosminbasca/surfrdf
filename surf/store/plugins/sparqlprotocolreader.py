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

from surf.store.plugins import RDFReader, UnsupportedResultType
from sparqlquery import translate
from SPARQLWrapper import SPARQLWrapper, JSON, XML, GET, POST
from SPARQLWrapper.SPARQLExceptions import EndPointNotFound, QueryBadFormed, SPARQLWrapperException

class SPARQLProtocolReader(RDFReader):
    __type__ = 'sparql-protocol'
    
    def __init__(self,*args,**kwargs):
        RDFReader.__init__(self,*args,**kwargs)
        
        self.__endpoint = kwargs['endpoint'] if 'endpoint' in kwargs else None
        self.__default_graph = kwargs['default_graph'] if 'default_graph' in kwargs else None
        #self.__results_format = kwargs['results_format'] if 'results_format' in kwargs else JSON
        self.__results_format = JSON
        
        #if self.__results_format not in [JSON, XML]:
        #    raise UnsupportedResultType('Result of type %s is unsupported'%self.__results_format)
        self.__sparql_wrapper = SPARQLWrapper(self.__endpoint, self.__results_format,defaultGraph=self.__default_graph)
        
    endpoint = property(lambda self: self.__endpoint)
    default_graph = property(lambda self: self.__default_graph)
    results_format = property(lambda self: self.__results_format)
    
    def _all(self,q):
        try:
            res = self._execute(q)['results']['bindings']
            if len(res) > 0:
                return [r['s']['value'] for r in res]
            else:
                return None
        except Exception, e:
            pass
        
    def _concept(self,q):
        try:
            res = self._execute(q)['results']['bindings']
            if len(res) > 0:
                return res[0]['c']['value']
            else:
                return None
        except Exception, e:
            pass
        
    def _is_present(self,q):
        return self._execute(q)['boolean']
        
    def _execute(self,q):
        try:
            q_rep = translate(q)
            self.log.debug(q_rep)
            self.__sparql_wrapper.setQuery(q_rep)
            results = self.__sparql_wrapper.query().convert()
            self.log.info('GET BACK <%d> RESULTS'%(len(results)))
            return results
        except EndPointNotFound, notfound: 
            print 'SPARQL ENDPOINT not found : \n',e
        except QueryBadFormed, badquery:
            print 'SPARQL EXCEPTION ON QUERY (BAD FORMAT): \n ',q
        except SPARQLWrapperException, sparqlwrapper:
            print 'SPARQL WRAPPER Exception \n',e
        except Exception, e:
            print 'Exception while querying', e
        return None