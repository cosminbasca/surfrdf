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

from surf.query import Query
from surf.rdf import BNode, ConjunctiveGraph, Graph, Literal, Namespace
from surf.rdf import RDF, URIRef


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

