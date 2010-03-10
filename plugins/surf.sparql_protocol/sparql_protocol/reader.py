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
from SPARQLWrapper.SPARQLExceptions import EndPointNotFound, QueryBadFormed

from surf.plugin.query_reader import RDFQueryReader
from surf.rdf import BNode, ConjunctiveGraph, Literal, URIRef

class SparqlReaderException(Exception): pass

class ReaderPlugin(RDFQueryReader):
    def __init__(self, *args, **kwargs):
        RDFQueryReader.__init__(self, *args, **kwargs)

        self.__endpoint = kwargs['endpoint'] if 'endpoint' in kwargs else None
        self.__results_format = JSON

        self.__sparql_wrapper = SPARQLWrapper(self.__endpoint, self.__results_format)
        if kwargs.get("use_keepalive", "").lower().strip() == "true":
            if hasattr(SPARQLWrapper, "setUseKeepAlive"):
                self.__sparql_wrapper.setUseKeepAlive()

        # Try to use cjson
        try:
            import cjson
            jsonlayer.use("cjson")
            self.log.info("using cjson")
        except:
            self.log.warning("cjson not available, falling back on slower simplejson")

    endpoint = property(lambda self: self.__endpoint)
    results_format = property(lambda self: self.__results_format)

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
            self.__sparql_wrapper.setQuery(q_string)
            results = self.__sparql_wrapper.query().convert()
            return self._toRdflib(results)
        except EndPointNotFound, _:
            raise SparqlReaderException("Endpoint not found"), None, sys.exc_info()[2]
        except QueryBadFormed, _:
            raise SparqlReaderException("Bad query: %s" % q_string), None, sys.exc_info()[2]
        except Exception, e:
            raise SparqlReaderException("Exception: %s" % e), None, sys.exc_info()[2]

    # execute
    def _execute(self, query):
        return self.execute_sparql(unicode(query))

    def close(self):
        pass

    def _toRdflib(self, json_data):
        """Convert the result dict to rdfLib types."""

        if not isinstance(json_data, dict):
            return json_data

        if not "results" in json_data:
            return json_data
        
        converted = []
        for binding in json_data["results"]["bindings"]:
            rdf_item = {}
            for key, obj in binding.items():
                if not "type" in obj:
                    continue
                
                type = obj["type"]

                rdfType = None
                if type == 'uri': 
                    rdfType = URIRef(obj["value"])
                elif type == 'literal':
                    if "xml:lang" in obj:
                        rdfType = Literal(obj["value"], lang = obj['xml:lang'])
                    else:
                        rdfType = Literal(obj["value"])
                elif type == 'typed-literal':
                    rdfType = Literal(obj["value"], datatype = URIRef(obj['datatype']))
                elif type == 'bnode': 
                    rdfType = BNode(obj["value"])
                
                rdf_item[key] = rdfType
            
            converted.append(rdf_item)

        return {"results" : {"bindings" : converted} } 


