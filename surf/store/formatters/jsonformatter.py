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

from surf.store.formatters import RDFFormatter
from rdf.term import URIRef, BNode, Literal
from copy import copy, deepcopy

class JSONRDFFormatter(RDFFormatter):
    __type__ = 'json'
    
    def __init__(self,*args,**kwargs):
        RDFFormatter.__init__(self,*args,**kwargs)
        
    def _predicate_dict(self,results,value_key,concept_key):
        pdict = {}
        if not results:
            return pdict
        for r in results:
            if r[value_key] not in pdict:
                pdict[r[value_key]] = []
            if concept_key in r:
                pdict[r[value_key]].append(r[concept_key])
        return pdict
    
    def _predicates_dict(self,results,predicate_key,value_key,concept_key):
        pdict = {}
        if not results:
            return pdict
        for r in results:
            pred = r[predicate_key]
            if pred not in pdict:
                pdict[pred] = {}
            if r[value_key] not in pdict[pred]:
                pdict[pred][r[value_key]] = []
            if concept_key in r:
                pdict[pred][r[value_key]].append(r[concept_key])
        return pdict
    
    def _convert_to_rdftypes(self,results):
        """
        @summary: the method converts a JSON response dictionary to a dictionary containing 
        rdf types such as named literals 
        BNodes, Literals URIRefs and so on, defined in RDFLib
        @param results: the input JSON dictionary according to w3c recommendations
        @return : a copy of the dictionary but with results converted to RDFLib types  
        """
        if results:
            rdf_dict = deepcopy(results)
            if results.has_key('results'):
                rdf_dict = []
                for json_item in results['results']['bindings']:
                    rdf_item = {}
                    for key in json_item:
                        type = json_item[key]['type']
                        value = json_item[key]['value']
                        rdfType = None
                        if type == 'uri':
                            rdfType = URIRef(value)
                        elif type == 'literal':
                            rdfType = Literal(value,language=json_item[key]['xml:lang']) if 'xml:lang' in json_item[key] else Literal(value)  
                        elif type == 'typed-literal':
                            rdfType = Literal(value,datatype=URIRef(json_item[key]['datatype']))
                        elif type == 'bnode':
                            rdfType = BNode(value)
                        rdf_item[key] = rdfType 
                    rdf_dict.append(rdf_item)
            return rdf_dict
        return None

