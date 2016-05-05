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
from surf.rdf import BNode, Graph, ConjunctiveGraph, Literal, Namespace
from surf.rdf import RDF, URIRef
import re

__author__ = 'Cosmin Basca'

a = RDF['type']

SELECT = 'select'
ASK = 'ask'
CONSTRUCT = 'construct'
DESCRIBE = 'describe'

DISTINCT = 'distinct'
REDUCED = 'reduced'

UNION = 'union'


class Group(list):
    """
    A **SPARQL** triple pattern group
    """


class NamedGroup(Group):
    """
    A **SPARQL** triple pattern named group
    """
    def __init__(self, name = None):
        super(NamedGroup, self).__init__()
        if isinstance(name, URIRef) or (type(name) in [str, unicode] and name.startswith('?')):
            self.name = name
        else:
            raise ValueError("Invalid specifier for named group"
                             ", should be either a variable (e.g. '?s')"
                             " or a URIRef instance")


class OptionalGroup(Group):
    """
    A **SPARQL** triple pattern optional group
    """


class Union(Group):
    """
    A **SPARQL** union
    """


class Filter(unicode):
    """
    A **SPARQL** triple pattern filter
    """
    @classmethod
    def regex(cls, var, pattern, flag=None):
        if isinstance(var, (str, unicode)) and var.startswith('?'):
            pass
        else:
            raise ValueError('not a filter variable')

        if isinstance(pattern, (str, unicode)):
            pass
        elif isinstance(pattern, Literal):
            pattern = '"{0:s}"@{1:s}'.format(pattern, pattern.language)
        elif isinstance(pattern, (list, tuple)):
            pattern = '"{0:s}"@{1:s}'.format(pattern[0], pattern[1])
        else:
            raise ValueError('regular expression')

        if flag is None:
            flag = ""
        else:
            if not isinstance(flag, (str, unicode)):
                raise ValueError('not a filter flag')

        return Filter('regex({0:s},"{1:s}"{2:s})'.format(var, pattern, u',"{0:s}"'.format(flag)))


def _validate_variable(variable):
    if isinstance(variable, (str, unicode)):
        if variable.startswith('?'):
            return True
        elif re.match('\s*\(\s*.+\s+AS\s+\?.+\)\s*$', variable):
            # SPARQL 1.1 expressions http://www.w3.org/TR/sparql11-query/#rSelectClause
            return True
        else:
            for aggregate in Query.AGGREGATE_FUNCTIONS:
                if variable.lower().startswith(aggregate):
                    return True
        raise ValueError('''Not a variable : <%s>, check correct syntax ("?",
                            expression, or supported aggregate %s)'''
                         % (variable, str(Query.AGGREGATE_FUNCTIONS)))
    else:
        raise ValueError('''Unknown variable type, all variables must either
                         start with a "?" or be among the recognized aggregates :
                         %s''' % Query.AGGREGATE_FUNCTIONS)


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

    STATEMENT_TYPES = [list, tuple, Group, NamedGroup, OptionalGroup, Union, Filter]  # + Query, (cannot reference here)

    AGGREGATE_FUNCTIONS = ["count", "min", "max", "avg"]

    TYPES = [SELECT, ASK, CONSTRUCT, DESCRIBE]

    def __init__(self, type, *vars):
        if type not in self.TYPES:
            raise ValueError('''The query is not of a supported type [{0:s}], supported
                             types are {1:s}'''.format(type, str(Query.TYPES)))
        self._type = type
        self._modifier = None
        self._vars = [var for var in vars if _validate_variable(var)]
        self._from = []
        self._from_named = []
        self._data = []
        self._limit = None
        self._offset = None
        self._order_by = []

    @property
    def query_type(self):
        """
        the query `type` can be: *SELECT*, *ASK*, *DESCRIBE*or *CONSTRUCT*
        """
        return self._type

    @property
    def query_modifier(self):
        """
        the query `modifier` can be: *DISTINCT*, *REDUCED*, or `None`
        """
        return self._modifier

    @property
    def query_vars(self):
        """
        the query `variables` to return as the resultset
        """
        return self._vars

    @property
    def query_from(self):
        """
        list of URIs that will go into query FROM clauses
        """
        return self._from

    @property
    def query_from_named(self):
        """
        list of URIs that will go into query FROM NAMED clauses
        """
        return self._from_named

    @property
    def query_data(self):
        """
        the query `data`, internal structure representing the contents of the *WHERE* clause
        """
        return self._data

    @property
    def query_limit(self):
        """
        the query `limit`, can be a number or None
        """
        return self._limit

    @property
    def query_offset(self):
        """
        the query `offset`, can be a number or None
        """
        return self._offset

    @property
    def query_order_by(self):
        """
        the query `order by` variables
        """
        return self._order_by

    def distinct(self):
        """
        Add *DISTINCT* modifier.
        """
        self._modifier = DISTINCT
        return self

    def reduced(self):
        """
        Add *REDUCED* modifier.
        """
        self._modifier = REDUCED
        return self

    def from_(self, *uris):
        """
        Add graph URI(s) that will go in separate *FROM* clause.

        Each argument can be either `string` or :class:`surf.rdf.URIRef`.
        """
        for uri in uris:
            if uri is None:
                raise ValueError("Invalid graph URI")

        self._from += uris
        return self

    def from_named(self, *uris):
        """
        Add graph URI(s) that will go in separate *FROM NAMED* clause.

        Each argument can be either `string` or :class:`surf.rdf.URIRef`.
        """
        for uri in uris:
            if uri is None:
                raise ValueError("Invalid graph URI")

        self._from_named += uris
        return self

    def where(self, *statements):
        """
        Add graph pattern(s) to *WHERE* clause.

        `where()` accepts multiple arguments. Each argument represents a
        a graph pattern and will be added to default group graph pattern.
        Each argument can be `tuple`, `list`, :class:`surf.query.Query`,
        :class:`surf.query.NamedGroup`, :class:`surf.query.OptionalGroup`.

        Example:

        .. code-block:: python

            >>> from surf.namespace import FOAF
            >>> query = select("?s").where(("?s", a, FOAF["person"]))

        """
        self._data.extend([stmt for stmt in statements if validate_statement(stmt)])
        return self

    def optional_group(self, *statements):
        """
        Add optional group graph pattern to *WHERE* clause.

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
        """
        Add ``GROUP ?name { ... }`` construct to *WHERE* clause.

        ``name`` is the variable name that will be bound to graph IRI.

        ``*statements`` is one or more graph patterns.

        Example:

        .. code-block:: python

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
        """
        Add *FILTER* construct to query *WHERE* clause.

        ``filter`` must be either `string`/`unicode` or
        :class:`surf.query.Filter` object, if it is `None` then no filter
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
        """
        Add *LIMIT* modifier to query.
        """
        if limit:
            self._limit = limit
        return self

    def offset(self, offset):
        """
        Add *OFFSET* modifier to query.
        """
        if offset:
            self._offset = offset
        return self

    def order_by(self, *variables):
        """
        Add *ORDER_BY* modifier to query.
        """
        pattern = re.compile("(asc|desc)\(\?\w+\)|\?\w+", re.I)
        for var in variables:
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
    if isinstance(statement, tuple(Query.STATEMENT_TYPES + [Query])):
        if isinstance(statement, (list, tuple)):
            try:
                s, p, o = statement
            except:
                raise ValueError('''Statement of type [list, tuple] does not
                                 have all the (s,p,o) members (the length of the
                                 supplied arguemnt must be at least 3)''')
            if isinstance(s, (URIRef, BNode)) or (isinstance(s, (str, unicode)) and s.startswith('?')):
                pass
            else:
                raise ValueError('The subject is not a valid variable type')

            if isinstance(p, URIRef) or (isinstance(p, (str, unicode)) and p.startswith('?')):
                pass
            else:
                raise ValueError('The predicate is not a valid variable type')

            if isinstance(o, (URIRef, BNode, Literal)) or (isinstance(o, (str, unicode)) and o.startswith('?')):
                pass
            else:
                raise ValueError(u'The object is not a valid variable type: {0:s}'.format(o))

        return True
    else:
        raise ValueError('Statement type not in {0:s}'.format)


def optional_group(*statements):
    """
    Return optional group graph pattern.

    Returned object can be used as argument in :meth:`Query.where` method.

    `optional_group()` accepts multiple arguments, similarly
    to :meth:`Query.where()`.
    """
    g = OptionalGroup()
    g.extend([stmt for stmt in statements if validate_statement(stmt)])
    return g


def group(*statements):
    """
    Return group graph pattern.

    Returned object can be used as argument in :meth:`Query.where` method.

    group()` accepts multiple arguments, similarly
    to :meth:`Query.where()`.
    """
    g = Group()
    g.extend([stmt for stmt in statements if validate_statement(stmt)])
    return g


def union(*statements):
    """
    Return union graph pattern.

    Returned object can be used as argument in :meth:`Query.where` method.

    union()` accepts multiple arguments, similarly
    to :meth:`Query.where()`.
    """
    g = Union()
    g.extend([stmt for stmt in statements if validate_statement(stmt)])
    return g


def named_group(name, *statements):
    """
    Return named group graph pattern.

    Returned object can be used as argument in :meth:`Query.where` method.

    ``*statements`` is one or more graph patterns.

    Example:

    .. code-block:: python

        >>> import surf
        >>> from surf.query import a, select, named_group
        >>> query = select("?s", "?src").where(named_group("?src", ("?s", a, surf.ns.FOAF['Person'])))
        >>> print unicode(query)
        SELECT  ?s ?src  WHERE {  GRAPH ?src {  ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person>  }  }

    """
    g = NamedGroup(name)
    g.extend([stmt for stmt in statements if validate_statement(stmt)])
    return g


def select(*variables):
    """
    Construct and return :class:`surf.query.Query` object of type **SELECT**

    ``*vars`` are variables to be selected.

    Example:

    .. code-block:: python

        >>> query = select("?s", "?p", "?o")

    """
    return Query(SELECT, *variables)


def ask():
    """
    Construct and return :class:`surf.query.Query` object of type **ASK**
    """
    return Query(ASK)


def construct(*variables):
    """
    Construct and return :class:`surf.query.Query` object of type **CONSTRUCT**
    """
    return Query(CONSTRUCT, *variables)


def describe(*variables):
    """
    Construct and return :class:`surf.query.Query` object of type **DESCRIBE**
    """
    return Query(DESCRIBE, *variables)
