from builtins import str
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

from builtins import zip
try:
    from json import loads
except ImportError as e:
    from simplejson import loads
from surf.plugin.query_reader import RDFQueryReader
from surf.rdf import ConjunctiveGraph
from surf.log import *

__author__ = 'Cosmin Basca'


class ReaderPlugin(RDFQueryReader):
    def __init__(self, *args, **kwargs):
        super(ReaderPlugin, self).__init__(*args, **kwargs)

        self._rdflib_store = kwargs.get("rdflib_store", "IOMemory")
        self._rdflib_identifier = kwargs.get("rdflib_identifier")
        self._commit_pending_transaction_on_close = \
            kwargs.get("commit_pending_transaction_on_close", True)

        self._graph = ConjunctiveGraph(
            store=self._rdflib_store,
            identifier=self._rdflib_identifier
        )

    @property
    def rdflib_store(self):
        return self._rdflib_store

    @property
    def rdflib_identifier(self):
        return self._rdflib_identifier

    @property
    def graph(self):
        return self._graph

    @property
    def commit_pending_transaction_on_close(self):
        return self._commit_pending_transaction_on_close

    def _to_table(self, result):
        # Elements in result.selectionF are instances of rdflib.Variable,
        # rdflib.Variable is subclass of unicode. We convert them to 
        # unicode here anyway to hide rdflib internals from clients. 
        vars = [str(var) for var in result.vars]

        # Convert each row to dict: { var->value, ... }
        return [dict(list(zip(vars, row))) for row in result]

    def _ask(self, result):
        # askAnswer is list with boolean values, we want first value. 
        return result.askAnswer

    def _execute(self, query):
        q_string = str(query)
        debug(q_string)
        return self._graph.query(q_string)

    def execute_sparql(self, q_string, format=None):
        debug(q_string)

        result = self._graph.query(q_string)
        return loads(result.serialize(format='json'))

    def close(self):
        self._graph.close(commit_pending_transaction=self._commit_pending_transaction_on_close)

