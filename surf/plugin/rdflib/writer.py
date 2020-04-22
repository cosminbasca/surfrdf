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

import warnings

from surf.plugin.writer import RDFWriter
from surf.rdf import ConjunctiveGraph
from surf.log import *
from .reader import ReaderPlugin


class WriterPlugin(RDFWriter):
    def __init__(self, reader, *args, **kwargs):
        super(WriterPlugin, self).__init__(reader, *args, **kwargs)

        if isinstance(self.reader, ReaderPlugin):
            self._rdflib_store = self.reader.rdflib_store
            self._rdflib_identifier = self.reader.rdflib_identifier
            self._commit_pending_transaction_on_close = \
                self.reader.commit_pending_transaction_on_close

            self._graph = self.reader.graph
        else:
            self._rdflib_store = kwargs.get("rdflib_store", "IOMemory")
            self._rdflib_identifier = kwargs.get("rdflib_identifier")
            self._commit_pending_transaction_on_close = \
                kwargs.get("commit_pending_transaction_on_close", True)

            self._graph = ConjunctiveGraph(store=self._rdflib_store, identifier=self._rdflib_identifier)

            warnings.warn("Graph is not readable through the reader plugin", UserWarning)

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

    def _save(self, *resources):
        for resource in resources:
            s = resource.subject
            self._remove_from_graph(s)
            for p, objs in list(resource.rdf_direct.items()):
                for o in objs:
                    self.__add(s, p, o)

        self._graph.commit()

    def _update(self, *resources):
        for resource in resources:
            s = resource.subject
            for p in resource.rdf_direct:
                self._remove_from_graph(s, p)
            for p, objs in list(resource.rdf_direct.items()):
                for o in objs:
                    self.__add(s, p, o)

        self._graph.commit()

    def _remove(self, *resources, **kwargs):
        inverse = kwargs.get("inverse")
        for resource in resources:
            self._remove_from_graph(s=resource.subject)
            if inverse:
                self._remove_from_graph(o=resource.subject)

        self._graph.commit()

    def _size(self):
        return len(self._graph)

    def _add_triple(self, s=None, p=None, o=None, context=None):
        self.__add(s, p, o, context)

    def _set_triple(self, s=None, p=None, o=None, context=None):
        self._remove_from_graph(s, p, context=context)
        self.__add(s, p, o, context)

    def _remove_triple(self, s=None, p=None, o=None, context=None):
        self._remove_from_graph(s, p, o, context)

    def __add(self, s=None, p=None, o=None, context=None):
        info('ADD: %s, %s, %s, %s' % (s, p, o, context))
        self._graph.add((s, p, o))

    def _remove_from_graph(self, s=None, p=None, o=None, context=None):
        info('REM: %s, %s, %s, %s' % (s, p, o, context))
        self._graph.remove((s, p, o))

    def index_triples(self, **kwargs):
        """
        Index triples if this functionality is present.
        
        :return: True if successful
        :rtype: bool
        """
        # TODO: can indexing be forced ?
        return False

    def load_triples(self, source=None, public_id=None, format="xml", **args):
        """
        Load files (or resources on the web) into the triple-store.

        :param str source: the source file to load RDF triples from
        :param public_id: the :mod:`rdflib` publicID
        :param str format: the source file format
        :param dict args: extra args passed to :meth:`rdflib.graph.Graph.parse`
        :return: True if successful
        :rtype: bool
        """
        if source is not None:
            debug("have %s triples, loading ...", len(self._graph))
            self._graph.parse(source, publicID=public_id, format=format, **args)
            debug("load complete; have %s triples", len(self._graph))
            return True

        return False

    def _clear(self, context=None):
        """
        Clear the triple-store.
        """
        self._graph.remove((None, None, None))

    def close(self):
        self._graph.close(commit_pending_transaction=self._commit_pending_transaction_on_close)
