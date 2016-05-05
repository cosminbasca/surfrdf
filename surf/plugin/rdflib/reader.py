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

try:
    from json import loads
except ImportError, e:
    from simplejson import loads
from surf.plugin.query_reader import RDFQueryReader
from surf.rdf import ConjunctiveGraph
from surf.log import *

__author__ = 'Cosmin Basca'


class ReaderPlugin(RDFQueryReader):
    def __init__(self, *args, **kwargs):
        RDFQueryReader.__init__(self, *args, **kwargs)

        self.__rdflib_store = kwargs.get("rdflib_store", "IOMemory")
        self.__rdflib_identifier = kwargs.get("rdflib_identifier") 
        self.__commit_pending_transaction_on_close = \
            kwargs.get("commit_pending_transaction_on_close", True)

        self.__graph = ConjunctiveGraph(store = self.__rdflib_store,
                                        identifier = self.__rdflib_identifier)

    rdflib_store = property(lambda self: self.__rdflib_store)
    rdflib_identifier = property(lambda self: self.__rdflib_identifier)
    graph = property(lambda self: self.__graph)
    commit_pending_transaction_on_close = \
        property(lambda self: self.__commit_pending_transaction_on_close)

    def _to_table(self, result):
        # Elements in result.selectionF are instances of rdflib.Variable,
        # rdflib.Variable is subclass of unicode. We convert them to 
        # unicode here anyway to hide rdflib internals from clients. 
        vars = [unicode(var) for var in result.vars]

        # Convert each row to dict: { var->value, ... }
        return [dict(zip(vars, row)) for row in result]

    def _ask(self, result):
        # askAnswer is list with boolean values, we want first value. 
        return result.askAnswer[0]

    # execute
    def _execute(self, query):
        q_string = unicode(query)
        debug(q_string)
        return self.__graph.query(q_string)

    def execute_sparql(self, q_string, format = None):
        debug(q_string)

        result = self.__graph.query(q_string)
        return loads(result.serialize(format='json'))

    def close(self):
        self.__graph.close(commit_pending_transaction = self.__commit_pending_transaction_on_close)

