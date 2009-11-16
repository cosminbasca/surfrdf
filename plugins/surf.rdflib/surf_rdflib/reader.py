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
from surf.query.translator.sparql import SparqlTranslator
from surf.rdf import BNode, ConjunctiveGraph, Literal, URIRef 

class ReaderPlugin(RDFQueryReader):
    def __init__(self, *args, **kwargs):
            RDFQueryReader.__init__(self,*args,**kwargs)
            
            self.__rdflib_store         = kwargs['rdflib_store'] if 'rdflib_store' in kwargs else 'IOMemory'
            self.__rdflib_identifier    = kwargs['rdflib_identifier'] if 'rdflib_identifier' in kwargs else None
            self.__commit_pending_transaction_on_close = kwargs['commit_pending_transaction_on_close'] if 'commit_pending_transaction_on_close' in kwargs else True
            
            self.__graph = ConjunctiveGraph(store = self.__rdflib_store, 
                                            identifier = self.__rdflib_identifier)
    
    rdflib_store        = property(lambda self: self.__rdflib_store)
    rdflib_identifier   = property(lambda self: self.__rdflib_identifier)
    graph               = property(lambda self: self.__graph)
    commit_pending_transaction_on_close = property(lambda self: self.__commit_pending_transaction_on_close)
    
    def _to_table(self,result):
        vars = [str(var) for var in result.selectionF]
        def row_to_dict(row):
            return dict([ (vars[i],row[i]) for i in range(len(row)) ])
        return [ row_to_dict(row) for row in result ]
    
    def _ask(self, result):
        # askAnswer is list with boolean values, we want first value. 
        return result.askAnswer[0]
    
    # execute
    def _execute(self, query):
        q_string = SparqlTranslator(query).translate()
        return self.execute_sparql(q_string)
        
    def execute_sparql(self, q_string, format = None):
        self.log.debug(q_string)
        return self.__graph.query(q_string)
    
    def close(self):
        self.__graph.close(commit_pending_transaction = self.__commit_pending_transaction_on_close)
        
