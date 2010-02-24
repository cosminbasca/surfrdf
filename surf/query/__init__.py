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

import logging
import re

from surf.rdf import BNode, Graph, ConjunctiveGraph, Literal, Namespace
from surf.rdf import RDF, URIRef

a = RDF['type']

SELECT = 'select'
ASK = 'ask'
CONSTRUCT = 'construct'
DESCRIBE = 'describe'

DISTINCT = 'distinct'
REDUCED = 'reduced'

UNION = 'union'

#the classes
class Group(list):
    pass

class NamedGroup(Group):

    def __init__(self, name = None):
        Group.__init__(self)
        if isinstance(name, URIRef) or (type(name) in [str, unicode] and name.startswith('?')):
            self.name = name
        else:
            raise ValueError('The names')

class OptionalGroup(Group):
    pass

class Union(Group):
    pass

class Filter(unicode):
    @classmethod
    def regex(cls, var, pattern, flag = None):
        if type(var) in [str, unicode] and var.startswith('?'): pass
        else: raise ValueError('not a filter variable')

        if type(pattern) in [str, unicode]:     pass
        elif type(pattern) is Literal:          pattern = '"%s"@%s' % (pattern, pattern.language)
        elif type(pattern) in [list, tuple]:    pattern = '"%s"@%s' % (pattern[0], pattern[1])
        else:                                   raise ValueError('regular expression')

        if flag is None:
            flag = ""
        else:
            if not type(flag) in [str, unicode]:
                raise ValueError('not a filter flag')

        return Filter('regex(%s,"%s"%s)' % (var, pattern, ',"%s"' % flag))

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

    STATEMENT_TYPES = [list, tuple, Group, NamedGroup, OptionalGroup,
                           Union, Filter] # + Query, but cannot reference it here.
    AGGREGATE_FUCTIONS = ["count", "min", "max", "avg"]
    TYPES = [SELECT, ASK, CONSTRUCT, DESCRIBE]

    def __init__(self, type, *vars):
        if type not in self.TYPES:
            raise ValueError('''The query is not of a supported type [%s], supported
                             types are %s''' % (type, str(Query.TYPES)))
        self._type = type
        self._modifier = None
        self._vars = [var for var in vars if self._validate_variable(var)]
        self._from = []
        self._data = []
        self._limit = None
        self._offset = None
        self._order_by = []

    query_type = property(fget = lambda self: self._type)
    '''the query `type` can be: *SELECT*, *ASK*, *DESCRIBE*or *CONSTRUCT*'''
    query_modifier = property(fget = lambda self: self._modifier)
    '''the query `modifier` can be: *DISTINCT*, *REDUCED*, or `None`'''
    query_vars = property(fget = lambda self: self._vars)
    '''the query `variables` to return as the resultset'''
    query_from = property(fget = lambda self: self._from)
    '''list of URIs that will go into query FROM clauses'''
    query_data = property(fget = lambda self: self._data)
    '''the query `data`, internal structure representing the contents of the *WHERE* clause'''
    query_limit = property(fget = lambda self: self._limit)
    '''the query `limit`, can be a number or None'''
    query_offset = property(fget = lambda self: self._offset)
    '''the query `offset`, can be a number or None'''
    query_order_by = property(fget = lambda self: self._order_by)
    '''the query `order by` variables'''

    def _validate_variable(self, var):
        if type(var) in [str, unicode]:
            if not var.startswith('?'):
                for aggregate in Query.AGGREGATE_FUCTIONS:
                    if var.lower().startswith(aggregate):
                        return True
                raise ValueError('''Not a variable : <%s>, check correct syntax ("?" or
                                 supported aggregate %s)''' % (var, str(Query.AGGREGATE_FUCTIONS)))
            return True
        else:
            raise ValueError('''Unknown variable type, all variables must either
                             start with a "?" or be among the recognized aggregates :
                             %s''' % Query.AGGREGATE_FUCTIONS)

    def distinct(self):
        """ Add *DISTINCT* modifier. """

        self._modifier = DISTINCT
        return self

    def reduced(self):
        """ Add *REDUCED* modifier. """

        self._modifier = REDUCED
        return self

    def from_(self, *uris):
        """ Add graph URI(s) that will go in separate *FROM* clause.

        Each argument can be either `string` or :class:`URIRef`.

        """

        for uri in uris:
            if uri is None:
                raise ValueError("Invalid graph URI")

        self._from += uris
        return self

    def where(self, *statements):
        """ Add graph pattern(s) to *WHERE* clause.

        `where()` accepts multiple arguments. Each argument represents a
        a graph pattern and will be added to default group graph pattern.
        Each argument can be `tuple`, `list`, :class:`Query`,
        :class:`NamedGroup`, :class:`OptionalGroup`.

        Example:

        >>> query = select("?s").where(("?s", a, surf.ns.FOAF["person"]))

        """

        self._data.extend([stmt for stmt in statements if validate_statement(stmt)])
        return self

    def optional_group(self, *statements):
        """ Add optional group graph pattern to *WHERE* clause.

        `optional_group()` accepts multiple arguments, similarly
        to :meth:`where()`.

        """

        g = OptionalGroup()
        g.extend([stmt for stmt in statements if validate_statement(stmt)])
        self._data.append(g)
        return self

    def group(self, *statements):
        g = Group()
        g.extend([stmt for stmt in statements if validate_statement(stmt)])
        self._data.append(g)
        return self

    def union(self, *statements):
        g = Union()
        g.extend([stmt for stmt in statements if validate_statement(stmt)])
        self._data.append(g)
        return self

    def named_group(self, name, *statements):
        """ Add ``GROUP ?name { ... }`` construct to *WHERE* clause.

        ``name`` is the variable name that will be bound to graph IRI.

        ``*statements`` is one or more graph patterns.

        Example:

        >>> import surf
        >>> from surf.query import a, select
        >>> query = select("?s", "?src").named_group("?src", ("?s", a, surf.ns.FOAF['Person']))
        >>> print unicode(query)
        SELECT  ?s ?src  WHERE {  GRAPH ?src {  ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person>  }  }    

        """

        g = NamedGroup(name)
        g.extend([stmt for stmt in statements if validate_statement(stmt)])
        self._data.append(g)
        return self

    def filter(self, filter):
        """ Add *FILTER* construct to query *WHERE* clause.

        ``filter`` must be either `string`/`unicode` or
        :class:`Filter` object, if it is `None` then no filter
        is appended.

        """

        if not filter:
            return self
        elif type(filter) in [str, unicode]:
            filter = Filter(filter)
        elif type(filter) is not Filter:
            raise ValueError('the filter must be of type Filter, str or unicode following the syntax of the query language')
        self._data.append(filter)
        return self

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

        pattern = re.compile("(asc|desc)\(\?\w+\)|\?\w+", re.I)
        for var in vars:
            if re.match(pattern, var):
                self._order_by.append(var)

        return self

    def __unicode__(self):
        # Importing here to avoid circular imports.
        from surf.query.translator.sparql import SparqlTranslator
        return SparqlTranslator(self).translate()

    def __str__(self):
        return unicode(self).encode("utf-8")

def validate_statement(statement):
    if type(statement) in Query.STATEMENT_TYPES or isinstance(statement, Query):
        if type(statement) in [list, tuple]:
            try:
                s, p, o = statement
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
            else:
                raise ValueError('The object is not a valid variable type: %s' % o)

        return True
    else:
        raise ValueError('Statement type not in %s' % str(Query.STATEMENT_TYPES))

def optional_group(*statements):
    """ Return optional group graph pattern.

    Returned object can be used as argument in :meth:`Query.where` method.

    `optional_group()` accepts multiple arguments, similarly
    to :meth:`Query.where()`.

    """

    g = OptionalGroup()
    g.extend([stmt for stmt in statements if validate_statement(stmt)])
    return g

def group(*statements):
    g = Group()
    g.extend([stmt for stmt in statements if validate_statement(stmt)])
    return g

def named_group(name, *statements):
    """ Return named group graph pattern.

    Returned object can be used as argument in :meth:`Query.where` method.

    ``*statements`` is one or more graph patterns.

    Example:

    >>> import surf
    >>> from surf.query import a, select, named_group
    >>> query = select("?s", "?src").where(named_group("?src", ("?s", a, surf.ns.FOAF['Person'])))
    >>> print unicode(query)
    SELECT  ?s ?src  WHERE {  GRAPH ?src {  ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person>  }  }    

    """

    g = NamedGroup(name)
    g.extend([stmt for stmt in statements if validate_statement(stmt)])
    return g

# the query creators
def select(*vars):
    """ Construct and return :class:`Query` object of type **SELECT**

    ``*vars`` are variables to be selected.

    Example:

    >>> query = select("?s", "?p", "?o")

    """

    return Query(SELECT, *vars)

def ask():
    """ Construct and return :class:`Query` object of type **ASK** """

    return Query(ASK)

def construct(*vars):
    """ Construct and return :class:`Query` object of type **CONSTRUCT** """

    return Query(CONSTRUCT, *vars)

def describe(*vars):
    """ Construct and return :class:`Query` object of type **DESCRIBE** """

    return Query(DESCRIBE, *vars)
