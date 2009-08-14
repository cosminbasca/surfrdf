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

def __literal(term):
    #TODO - this is sparql specific, it needs to be pushed to the query, the query object
    # must handle this by supporting a better unified model between the filters and the query
    if type(term) is Literal:
        return '"%s"@%s'%(term,term.language)
    elif type(term) in [list,tuple]:
        return '"%s"@%s'%(term[0],term[1])
    return '"%s"'%term

def query_PO(c,direct,filter='',preds={}):
    '''helper query builder method
    constructs a `surf.query.Query` where the unknowns are `?s ?c`, with the possibility
    to specify **SPARQL** `filters` as strings - follow the SPARQL filter syntax'''
    query = select('?s','?c').distinct()
    i = 0 
    for p, v in preds.items():
        s, v, f = ('?s', v, '') if direct else (v, '?s', '')
        if filter is 'regex':
            s, v, f = ('?s', '?v%d'%i, 'regex(?v%d,%s)'%(i,__literal(v))) if direct else (v, '?s', '')
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
    #protected interface
    def _get(self,subject,attribute,direct):
        query = query_SP(subject, attribute, direct)
        result = self._execute(query)
        return self.__values(result)
    
    def _load(self,subject,direct):
        query = query_S(subject, direct)
        result = self._execute(query)
        return self.__predicate_values(result)
    
    def _is_present(self,subject):
        query = query_Ask(subject)
        result = self._execute(query)
        return self._ask(result)
    
    def _all(self,concept,limit=None,offset=None):
        query = query_All(concept, limit=limit, offset=offset)
        result = self._execute(query)
        return [result for result in self.__values(result,vkey='s')]
    
    def _concept(self,subject):
        query = query_Concept(subject)
        result = self._execute(query)
        cval = self.__values(result,vkey='c',ckey=None)
        return cval.keys()[0] if len(cval) > 0 else None
        
    def _instances_by_attribute(self,concept,attributes,direct):
        query = query_P_S(concept,attributes,direct)
        result = self._execute(query)
        return self.__values(result)
        
    def _instances(self,concept,direct,filter,predicates):
        query = query_PO(concept,direct,filte=filte,preds=predicates)
        result = self._execute(query)
        return self.__values(result)
        
    def _instances_by_value(self,concept,direct,attributes):
        query = query_P_V(concept,direct,p=attributes)
        result = self._execute(query)
        return self.__values(result)
    
    # wrapper for error handling
    def __values(self,result,vkey='v',ckey='c'):
        try:
            return self._values(result,vkey=vkey,ckey=ckey)
        except Exception, e:
            self.log.error('Error on values : '+str(e))
        return {}
    
    def __predicate_values(self,result,pkey='p',vkey='v',ckey='c'):
        try:
            return self._predicate_values(result,pkey=pkey,vkey=vkey,ckey=ckey)
        except Exception, e:
            self.log.error('Error on predicate values : '+str(e))
        return {}
    
    # to implement
    def _values(self,result,vkey='v',ckey='c'):
        '''`result` represents the query returned result,
        returns a dictionary of the form
        
        .. code-block:: python
            
            {value_1 : [concept_uri_1,concept_uri_2,]}
            
        '''
        return {}
    
    def _predicate_values(self,result,pkey='p',vkey='v',ckey='c'):
        '''`result` represents the query returned result
        returns a dictionary with predicates as keys, the values
        are the same as returned by the _values function
        returns a dictionary of the form
        
        .. code-block:: python
        
            {predicate_1: {value_1 : [concept_uri_1,concept_uri_2,]},
             predicate_2: {value_2 : [concept_uri_2,concept_uri_3,]},
            }
        
        '''
        return {}
        
    def _ask(self,result):
        '''returns the boolean `value` of a **ASK** query'''
        return False
    
    # execute
    def _execute(self,query):
        '''to be implemeted by classes the inherit from `RDFQueryReader`, is
        called internally by `execute`'''
        return None

    # public interface    
    def execute(self,query):
        '''execute a `query` of type `surf.query.Query`'''
        q = query if type(query) is Query else None
        if q:
            return self._execute(q)
        return None
