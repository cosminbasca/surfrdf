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

from surf.plugin.reader import RDFReader
import logging
from surf.query import Query, a, ask, select, Filter

# the rdf way
#from rdf.graph import ConjunctiveGraph
#from rdf.term import URIRef, BNode, Literal, RDF
# the rdflib 2.4.x way
from rdflib.Graph import ConjunctiveGraph
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal


def query_SP(s,p,direct):
    '''helper query builder method
    constructs a `surf.query.Query` where the unknowns are `?v ?c`'''
    s, v = (s, '?v') if direct else ('?v', s)
    return select('?v','?c').distinct().where((s,p,v)).optional_group(('?v',a,'?c'))

def query_S(s,direct):
    '''helper query builder method
    constructs a `surf.query.Query` where the unknowns are `?p ?v ?c`'''
    s, v = (s, '?v') if direct else ('?v', s)
    return select('?p','?v','?c').distinct().where((s,'?p',v)).optional_group(('?v',a,'?c'))
    
def query_Ask(subject):
    '''helper query builder method
    constructs a `surf.query.Query` of type **ASK**, returned value is boolean'''
    return ask().where((subject,'?p','?o'))
    
def query_All(concept,limit=None,offset=None):
    '''helper query builder method
    constructs a `surf.query.Query` where the unknowns are `?s`'''
    return select('?s').distinct().where(('?s',a,concept)).limit(limit).offset(offset)

def query_AllRelated(concept, limit=None, offset=None):
    ''' Return Query that selects subjects and related triples. 
        
    First, in subquery, select resource uris that have type matching concept 
    argument. Then, in main query, select all triples that have previously
    selected uris as subjects.  '''
    inner_query = select('?s').distinct().where(('?s', a, concept))
    inner_query.limit(limit).offset(offset)
    
    query = select('?s', '?p', '?v', '?c').distinct()
    return query.where(('?s', '?p', '?v')).optional_group(('?v',a,'?c')).where(inner_query)
    
#Resource class level
def query_P_S(c,p,direct):
    '''helper query builder method
    constructs a `surf.query.Query` where the unknowns are `?s ?c`'''
    query = select('?s','?c').distinct()
    for i in range(len(p)):
        s, v = ('?s', '?v%d'%i) if direct else ('?v%d'%i, '?s')
        if type(p[i]) is URIRef: query.where((s,p[i],v))
    query.optional_group(('?s',a,'?c'))
    return query

def query_PO(c,direct,filter='',preds={}):
    '''helper query builder method
    constructs a `surf.query.Query` where the unknowns are `?s ?c`, with the possibility
    to specify **SPARQL** `filters` as strings - follow the SPARQL filter syntax'''
    query = select('?s','?c').distinct()
    i = 0 
    for p, v in preds.items():
        f = Filter.regex('?v%d'%(i),v) if filter == 'regex' and direct else None
        s, v = ('?s', v) if direct else (v, '?s')
        query.where((s,p,v)).filter(f)
        i += 1
    query.optional_group(('?s',a,'?c'))
    return query

def query_P_V(c,direct,p=[]):
    '''helper query builder method
    constructs a `surf.query.Query` where the unknowns are `?v ?c`'''
    query = select('?v','?c').distinct()
    for i in range(len(p)):
        s, v= (c, '?v') if direct else ('?v', c)
        query.where((s,p[i],v))
    query.optional_group(('?v',a,'?c'))
    return query
    
def query_Concept(subject):
    '''helper query builder method
    constructs a `surf.query.Query` where the unknowns are `?c`'''
    return select('?c').distinct().where((subject,a,'?c'))

class RDFQueryReader(RDFReader):
    '''super class for all `surf Reader Plugins` that wrap queriable `stores`'''    
    def __init__(self,*args,**kwargs):
        RDFReader.__init__(self,*args,**kwargs)
        self.use_subqueries = kwargs.get('use_subqueries',False)
        if type(self.use_subqueries) in [str, tuple]:
            self.use_subqueries = True if self.use_subqueries.lower() == 'true' else False
        elif type(self.use_subqueries) is not bool:
            raise ValueError('The use_subqueries parameter must be a bool or a string set to "true" or "false"')
    
    #protected interface
    def _get(self,subject,attribute,direct):
        query = query_SP(subject, attribute, direct)
        result = self._execute(query)
        return self.convert(result,'v','c')
    
    def _load(self,subject,direct):
        query = query_S(subject, direct)
        result = self._execute(query)
        return self.convert(result,'p','v','c')
    
    def _is_present(self,subject):
        query = query_Ask(subject)
        result = self._execute(query)
        return self._ask(result)
    
    def _all(self, concept, limit = None, offset = None, full = False):
        if full and self.use_subqueries:
            query = query_AllRelated(concept, limit=limit, offset=offset)            
            result = self._execute(query)
            return self.convert(result,'s','p','v','c')
        else:
            query = query_All(concept, limit=limit, offset=offset)
            result = self._execute(query)
            return self.convert(result,'s')
    
    def _concept(self,subject):
        query = query_Concept(subject)
        result = self._execute(query)
        return self.convert(result,'c')
        
    def _instances_by_attribute(self,concept,attributes,direct):
        query = query_P_S(concept,attributes,direct)
        result = self._execute(query)
        return self.convert(result, 's', 'c')
        
    def _instances(self,concept,direct,filter,predicates):
        query = query_PO(concept,direct,filter=filter,preds=predicates)
        result = self._execute(query)
        return self.convert(result, 's')
        
    def _instances_by_value(self,concept,direct,attributes):
        query = query_P_V(concept,direct,p=attributes)
        result = self._execute(query)
        return self.convert(result, 's', 'c')
    
    # to implement
    def _ask(self,result):
        '''returns the boolean `value` of a **ASK** query'''
        return False
    
    # execute
    def _execute(self,query):
        '''to be implemeted by classes the inherit from `RDFQueryReader`, is
        called internally by `execute`'''
        return None

    def _to_table(self,result):
        return []
    
    def __convert(self,query_result,*keys):
        results_table = self._to_table(query_result)
        
        if len(keys) == 1:
            return [row[keys[0]] for row in results_table]
        
        last = len(keys)-2
        results = {}
        for row in results_table:
            data = results
            for i in range(len(keys)-1):
                v = row[keys[i]]
                if i < last:
                    if v not in data:
                        data[v] = {}
                    data = data[v]
                elif i == last:
                    if v not in data:
                        data[v] = []
                    data[v].append(row[keys[i+1]])
        return results

    # public interface    
    def execute(self,query):
        '''execute a `query` of type `surf.query.Query`'''
        q = query if type(query) is Query else None
        if q:
            return self._execute(q)
        return None
    
    def convert(self, query_result, * keys):
        '''converts the results from the query to a multilevel dictionary, used
        by the :class:`surf.resource.Resource` class'''
        try:
            return self.__convert(query_result, *keys)
        except Exception, e:
            self.log.error('Error on Convert : ' + str(e))
        return []