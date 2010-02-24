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

from surf.query import Query, Group, NamedGroup, Filter, OptionalGroup, validate_statement
from surf.rdf import RDF, URIRef
from surf.util import is_uri

a = RDF['type']

# Update
MODIFY = 'MODIFY'
INSERT = 'INSERT'
INSERT_DATA = 'INSERT_DATA'
DELETE = 'DELETE'
DELETE_DATA = 'DELETE_DATA'
LOAD = 'LOAD'
CLEAR = 'CLEAR'

# Manage
CREATE = 'CREATE'
DROP = 'DROP'

class QueryUpdate(Query):
    """ Update query. """

    STATEMENT_TYPES = list(Query.STATEMENT_TYPES)
    TYPES = list(Query.TYPES)
    TYPES.extend([MODIFY, INSERT, INSERT_DATA, DELETE, DELETE_DATA, LOAD, CLEAR, CREATE, DROP])

    def __init__(self, type, *vars):
        Query.__init__(self, type, *vars)
        self._into_uri = []
        self._from_uri = []
        self._template = []
        self._remote_uri = None
        self._clear_uri = None

    query_into_uri = property(fget = lambda self: self._into_uri)
    ''''''
    query_from_uri = property(fget = lambda self: self._from_uri)
    ''''''
    query_template = property(fget = lambda self: self._template)
    ''''''
    query_remote_uri = property(fget = lambda self: self._remote_uri)
    ''''''
    query_clear_uri = property(fget = lambda self: self._clear_uri)
    ''''''

    def into(self, *uris):
        if self.query_type not in [INSERT_DATA, INSERT]:
            raise ValueError('The specified <%s> query type does not support the INTO clause' % (self.query_type))
        if self.query_type is LOAD and len(uris) != 1:
            raise ValueError('The LOAD query, supports only one uri for the INTO clause')
        self._into_uri.extend([uri for uri in uris if type(uri) is URIRef or is_uri(uri)])
        return self

    def from_(self, *uris):
        if self.query_type not in [DELETE_DATA, DELETE]:
            raise ValueError('The specified <%s> query type does not support the FROM clause' % (self.query_type))
        self._from_uri.extend([uri for uri in uris if type(uri) is URIRef or is_uri(uri)])
        return self

    def template(self, *statements):
        self._template.extend([stmt for stmt in statements if validate_statement(stmt)])
        return self

    def where(self, *statements):
        if self.query_type in [INSERT_DATA, DELETE_DATA]:
            raise ValueError('The specified <%s> query type does not support the WHERE clause' % (self.query_type))
        return Query.where(self, *statements)

    def load(self, remote_uri):
        if self.query_type not in [LOAD]:
            raise ValueError('The specified <%s> query type does not support the LOAD clause' % (self.query_type))
        if type(remote_uri) is not URIRef and not is_uri(remote_uri):
            raise ValueError('The argument is not a uri')
        self._remote_uri = remote_uri
        return self

    def graph(self, uri):
        if self.query_type not in [CLEAR]:
            raise ValueError('The specified <%s> query type does not support the CLEAR GRAPH clause' % (self.query_type))
        if type(uri) is not URIRef and not is_uri(uri):
            raise ValueError('The argument is not a uri')
        self._clear_uri = uri
        return self

    def __unicode__(self):
        # Importing here to avoid circular imports.
        from surf.query.translator.sparul import SparulTranslator
        return SparulTranslator(self).translate()


def insert(data = False):
    q_type = data and INSERT_DATA or INSERT
    return QueryUpdate(q_type)

def delete(data = False):
    q_type = data and DELETE_DATA or DELETE
    return QueryUpdate(q_type)

def load():
    return QueryUpdate(LOAD)

def clear():
    return QueryUpdate(CLEAR)

#TODO: to be supported in the near future
def modify():
    pass
