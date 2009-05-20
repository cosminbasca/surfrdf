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

from rdf.graph import Graph, ConjunctiveGraph
from rdf.term import URIRef, Literal, BNode, RDF, RDFS
from rdf.namespace import Namespace

'''
abstract representation of a query, based on rdflib concepts, and basic python
types
'''
class InvalidTypeQueryException(Exception):
    def __init__(self,message):
        self.message = message
        
    def __str__(self):
        return self.message

# SPARQL vriables are represented as strings that follow the sparql
# variable definition: "?name" represents the SPARQL variable name
class Query(object):
    __query_types__ = ['select','ask','describe','construct']
    
    @classmethod
    def select(cls,*vars):
        q = cls('select')
        q.select_clauses.extend(vars)
        return q
    
    @classmethod
    def ask(cls,*patterns):
        askq = cls('ask')
        for pattern in patterns:
            if type(pattern) in [list, tuple]:
                if len(pattern) == 4:
                    s,p,o,c = pattern
                elif len(pattern) == 3:
                    s,p,o = pattern
                    c = None
                else:
                    continue
                
                if not c:
                    c = '' # default graph
                if c not in askq.ask_clauses:
                    askq.ask_clauses[c] = []
                askq.ask_clauses[c].append((s,p,o))
        return askq
    
    @classmethod
    def describe(cls):
        return cls('describe')
    
    @classmethod
    def construct(cls,*vars):
        q = cls('construct')
        q.select_clauses.extend(vars)
        return q
    
    def __init__(self,q_type='select',template=r'c:\work\.Eclipse\pySurf\src\surf\store\sparql.mako'):
        if q_type.lower() not in Query.__query_types__:
            raise InvalidTypeQueryException('Unsupported Query type [%s]'%q_type)
        
        self.query_type = q_type.lower()
        
        self.select_clauses = []
        self.where_clauses = {'':[]} # '' = default graph
        self.filter_clauses = {'':[]} # '' = default graph
        self.offset_value = None
        self.limit_value = None
        self.order_by_clauses = []
        self.distinct_clauses = []
        self.ask_clauses = {'':[]}
    
    def where(self,s,p,o,c=None,optional=False,filter=''):
        '''
        filter syntax must follow SPARQL syntax
        '''
        if not c:
            c = '' # default graph
        if c not in self.where_clauses:
            self.where_clauses[c] = []
        self.where_clauses[c].append((s,p,o,optional,filter))
        return self
    
    def order_by(self,*vars):
        self.order_by_clauses.extend(vars)
        return self
    
    def offset(self,value):
        self.offset_value = value
        return self
    
    def limit(self,value):
        self.limit_value = value
        return self
    
    def distinct(self,*vars):
        self.distinct_clauses.extend(vars)
        return self
    
    def filter(self,filter_expression,c=None):
        '''
        takes valid SPARQL filter expressions passed in as strings, no checks are
        performed for malformed expressions, the sparql processor against which the
        query is exectued will signall the error.
        '''
        if not c:
            c = '' # default graph
        if c not in self.filter_clauses:
            self.filter_clauses[c] = []
        self.filter_clauses[c].append(filter_expression)
        return self
    
    def __str__(self):
        return ''
