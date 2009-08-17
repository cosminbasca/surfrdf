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

# the rsf way
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
import logging

a = RDF['type']

SELECT      = 'select'
ASK         = 'ask'
CONSTRUCT   = 'construct'
DESCRIBE    = 'describe'

DISTINCT    = 'distinct'
REDUCED     = 'reduced'

UNION       = 'union'

#the classes
class Group(list):
    pass

class NamedGroup(Group):
    
    def __init__(self,name = None):
        Group.__init__(self)
        if type(name) is [URIRef] or (type(name) in [str, unicode] and name.startswith('?')):
            self.name = name
        else:
            raise ValueError('The names')

class OptionalGroup(Group):
    pass

class Filter(unicode):        
    @classmethod
    def regex(cls,var,pattern,flag=None):
        if type(var) in [str, unicode] and var.startswith('?'): pass
        else: raise ValueError('not a filter variable')
        if type(pattern) in [str, unicode]: pass
        else: raise ValueError('regular expression')
        if flag and type(flag) in [str, unicode] or not flag: pass
        else: raise ValueError('not a filter flag')
        
        return Filter('regex(%s,"%s"%s)'%(var, pattern, ',"%s"'%flag if flag else ''))

class Query(object):
    """
    The `Query` object is used by SuRF to construct queries in a programatic 
    manner. The class supports the major SPARQL query types: *select*, *ask*, 
    *describe*, *construct*. Although it follows the SPARQL format the query 
    can be translated to other Query formats such as PROLOG, for now 
    though only SPARQL is supported.
    
    Query objects should not be instatiated directly, instead use module-level
    :func:`ask`, :func:`construct`, :func:`describe`, :func:`select` functions.  
    
    Query methods can be chained.
   
    """
    
    STATEMENT_TYPES     = [list, tuple, Group, NamedGroup, OptionalGroup, 
                           Filter] # + Query, but cannot reference it here.
    AGGREGATE_FUCTIONS  = ['count']
    TYPES               = [SELECT, ASK, CONSTRUCT, DESCRIBE]
    
    def __init__(self, type, *vars):
        if type not in Query.TYPES: 
            raise ValueError('''The query is not of a supported type [%s], supported
                             types are %s'''%(type, str(Query.TYPES)))
        self._type      = type
        self._modifier  = None
        self._vars      = [var for var in vars if self._validate_variable(var)]
        self._data      = []
        self._limit     = None
        self._offset    = None
        self._order_by  = []
        
    query_type        = property(fget = lambda self: self._type)
    query_modifier    = property(fget = lambda self: self._modifier)
    query_vars        = property(fget = lambda self: self._vars)
    query_data        = property(fget = lambda self: self._data)
    query_limit       = property(fget = lambda self: self._limit)
    query_offset      = property(fget = lambda self: self._offset)
    query_order_by    = property(fget = lambda self: self._order_by)
        
    def _validate_variable(self, var):
        if type(var) in [str, unicode]:
            if not var.startswith('?'):
                for aggregate in Query.AGGREGATE_FUCTIONS:
                    if var.lower().startswith(aggregate):
                        return True
                raise ValueError('''Not a variable : <%s>, check correct syntax ("?" or
                                 supported aggregate %s)'''%(var,str(Query.AGGREGATE_FUCTIONS)))
            return True
        else:
            raise ValueError('''Unknown variable type, all variables must either
                             start with a "?" or be among the recognized aggregates :
                             %s'''%Query.AGGREGATE_FUCTIONS)
    
    def _validate_statement(self, statement):
        if type(statement) in Query.STATEMENT_TYPES or isinstance(statement, Query):
            if type(statement) in [list, tuple]:
                try:
                    s,p,o = statement
                except:
                    raise ValueError('''Statement of type [list, tuple] does not
                                     have all the (s,p,o) members (the length of the
                                     supplied arguemnt must be at least 3)''')
                if type(s) in [URIRef, BNode] or \
                    (type(s) in [str, unicode] and s.startswith('?')): pass
                else: raise ValueError('The subject is not a valid variable type')
                
                if type(p) in [URIRef] or \
                    (type(p) in [str, unicode] and p.startswith('?')): pass
                else: raise ValueError('The predicate is not a valid variable type')
                
                if type(o) in [URIRef, BNode, Literal] or \
                    (type(o) in [str, unicode] and o.startswith('?')): pass
                else: raise ValueError('The object is not a valid variable type')
                
            return True
        else:
            raise ValueError('Statement type not in %s'%str(Query.STATEMENT_TYPES))
        
    def distinct(self):
        """ Add *DISTINCT* modifier. """
        
        self._modifier = DISTINCT
        return self
    
    def reduced(self):
        """ Add *REDUCED* modifier. """

        self._modifier = REDUCED
        return self
        
    def where(self,*statements):
        """ Add graph pattern(s) to *WHERE* clause.
                
        `where()` accepts multiple arguments. Each argument represents a
        a graph pattern and will be added to default group graph pattern.
        Each argument can be `tuple`, `list`, :class:`Query`, 
        :class:`NamedGroup`, :class:`OptionalGroup`. 
         
        Example: 
        
        >>> query = select("?s").where(("?s", a, surf.ns.FOAF["person"]))
        
        """ 
        
        self._data.extend([stmt for stmt in statements if self._validate_statement(stmt)])
        return self
    
    def optional_group(self,*statements):
        """ Add optional group graph pattern to *WHERE* clause. 
        
        `optional_group()` accepts multiple arguments, similarly 
        to :meth:`where()`.
        
        """
         
        g = OptionalGroup()
        g.extend([stmt for stmt in statements if self._validate_statement(stmt)])
        self._data.append(g)
        return self
    
    def group(self,*statements):
        g = Group()
        g.extend([stmt for stmt in statements if self._validate_statement(stmt)])
        self._data.append(g)
        return self
    
    def named_group(self,name,*statements):
        """ Add ``GROUP ?name { ... }`` construct to *WHERE* clause. 
        
        ``name`` is the variable name that will be bound to graph IRI.
        
        ``*statements`` is one or more graph patterns. 
        
        Example:
        
        >>> import surf
        >>> from surf.query import a, select
        >>> from surf.query_to_sparql import SparqlTranslator
        >>> query = select("?s", "?src").named_group("?src", ("?s", a, surf.ns.FOAF['Person']))
        >>> SparqlTranslator(query).translate()
        SELECT  ?s ?src WHERE {  GRAPH ?src {  ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person>  }  }   
        
        """

        g = NamedGroup(name)
        g.extend([stmt for stmt in statements if self._validate_statement(stmt)])
        self._data.append(g)
        return self
    
    def filter(self, filter):
        """ Add FILTER construct to query WHERE clause. 
        
        Arguments:
        
        filter -- either `string`/`unicode` or `Filter` object.
        
        """
        
        if not filter:
            raise ValueError('the filter must be of type Filter, str or unicode following the syntax of the query language')
        elif type(filter) in [str, unicode]:
            filter = Filter(filter)
        elif type(filter) is not Filter:
            raise ValueError('the filter must be of type Filter, str or unicode following the syntax of the query language')
        self._data.append(filter)
    
    def limit(self, limit):
        """ Add *LIMIT* modifier to query. """
        
        if limit:
            self._limit = limit
        return self
     
    def offset(self, offset):
        """ Add *OFFSET* modifier to query. """

        if offset:
            self._offset = offset
        return self
    
    def order_by(self, *vars):
        """ Add *ORDER_BY* modifier to query. """

        self._order_by.extend([var for var in vars if type(var) in [str, unicode] and var.startswith('?')])
        return self
    
# the query creators
def select(*vars):
    '''constructs a **SELECT** :class:`surf.query.Query`'''
    return Query(SELECT, *vars)
    
def ask():
    '''constructs a **ASK** :class:`surf.query.Query`'''
    return Query(ASK)

def construct(*vars):
    '''constructs a **CONSTRUCT** :class:`surf.query.Query`'''
    return Query(CONSTRUCT, *vars)

def describe(*vars):
    '''constructs a **DESCRIBE** :class:`surf.query.Query`'''
    return Query(DESCRIBE, *vars)
    
class QueryTranslator(object):
    '''The `QueryTranslator` class is responsible with the translation of the query
    to the appropriate query language in use. One must extend the class and override the
    :meth:`surf.query.QueryTranslator.translate` method'''
    def __init__(self, query):
        self.__query = query
        if not self.__query.query_type:
            raise ValueError('No query type specified')
    
    def set_query(self,query):
        if type(query) is Query:
            self.__query = query
        else:
            raise ValueError('query object must be of Query type')
    query = property(fget = lambda self: self.__query,
                     fset = set_query)
    '''the `query`, a :class:`surf.query.Query` instance'''
    
    def translate(self):
        '''translates the `query` to the appropriate query language
        
        note: **must** be overriden by subclasses'''
        return ''