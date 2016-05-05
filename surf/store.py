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
from surf.log import *
from surf.plugin.manager import load_plugins, get_reader, get_writer
from surf.plugin.reader import RDFReader, NoneReader
from surf.plugin.writer import RDFWriter, NoneWriter
from surf.query import Query
from surf.rdf import URIRef

__author__ = 'Cosmin Basca'

# A constant to use as context argument when we want to avoid default context.
# Example: sess.get_resource(uri, Concept, context = surf.NO_CONTEXT),
# this explicitly says that no context should be used.
NO_CONTEXT = "no-context"


class Store(object):
    """ The `Store` class is comprised of a reader and a writer, getting
    access to an underlying triple store. Also store specific parameters must
    be handled by the class, the plugins act based on various settings.

    The `Store` is also the `plugin` manager and provides convenience methods
    for working with plugins.

    """

    """ True if the `reader` plugin is using sub queries, False otherwise. """
    use_subqueries = False

    default_context = property(lambda self: self.__default_context)

    def __init__(self, reader = None, writer = None, *args, **kwargs):
        super(Store, self).__init__()

        info('initializing the store')

        self.__default_context = None
        if "default_context" in kwargs:
            self.__default_context = URIRef(kwargs["default_context"])

        if reader:
            self.reader = reader if isinstance(reader, RDFReader) else get_reader(reader, *args, **kwargs)
        else:
            self.reader = NoneReader(*args, **kwargs)

        if writer:
            self.writer = writer if isinstance(writer, RDFWriter) else get_writer(writer, self.reader, *args, **kwargs)
        else:
            self.writer = NoneWriter(self.reader, *args, **kwargs)

        if hasattr(self.reader, 'use_subqueries'):
            self.use_subqueries = property(fget=lambda self: self.reader.use_subqueries)

        info('store initialized')

    def __add_default_context(self, context):
        """ Return default context if context is None. """

        if context == NO_CONTEXT:
            context = None
        elif not context:
            context = self.__default_context

        return context

    def close(self):
        """ Close the `store`.

        Both the `reader` and the `writer` plugins are closed.
        See :func:`surf.plugin.writer.RDFWriter.close`
        and :func:`surf.plugin.reader.RDFReader.close` methods.

        """
        try:
            self.reader.close()
            debug('reader closed successfully')
        except Exception, e:
            error("Error on closing the reader: %s", e.message)

        try:
            self.writer.close()
            debug('writer closed successfully')
        except Exception, e:
            error("Error on closing the writer: %s", e.message)

    def get(self, resource, attribute, direct):
        """ :func:`surf.plugin.reader.RDFReader.get` method. """

        return self.reader.get(resource, attribute, direct)

    # cRud
    def load(self, resource, direct):
        """ :func:`surf.plugin.reader.RDFReader.load` method. """

        return self.reader.load(resource, direct)

    def is_present(self, resource):
        """ :func:`surf.plugin.reader.RDFReader.is_present` method. """

        return self.reader.is_present(resource)

    def concept(self, resource):
        """ :func:`surf.plugin.reader.RDFReader.concept` method. """

        return self.reader.concept(resource)

    def instances_by_attribute(self, resource, attributes, direct, context):
        """ :func:`surf.plugin.reader.RDFReader.instances_by_attribute` method. """

        context = self.__add_default_context(context)
        return self.reader.instances_by_attribute(resource, attributes,
                                                  direct, context)

    def get_by(self, params):
        params["context"] = self.__add_default_context(params.get("context"))
        return self.reader.get_by(params)

    def execute(self, query):
        """see :meth:`surf.plugin.query_reader.RDFQueryReader.execute` method. """

        if hasattr(self.reader, 'execute') and isinstance(query, Query):
            return self.reader.execute(query)

        return None

    def execute_sparql(self, sparql_query, format = 'JSON'):
        """see :meth:`surf.plugin.query_reader.RDFQueryReader.execute_sparql` method. """

        if hasattr(self.reader, 'execute_sparql') and type(sparql_query) in [str, unicode]:
            return self.reader.execute_sparql(sparql_query, format = format)
        return None

    def clear(self, context = None):
        """ See :func:`surf.plugin.writer.RDFWriter.clear` method. """

        context = self.__add_default_context(context)
        self.writer.clear(context = context)

    # Crud
    def save(self, *resources):
        """ See :func:`surf.plugin.writer.RDFWriter.save` method. """

        self.writer.save(*resources)

        for resource in resources:
            resource.dirty = False

    # crUd
    def update(self, *resources):
        """ See :func:`surf.plugin.writer.RDFWriter.update` method. """

        self.writer.update(*resources)

        for resource in resources:
            resource.dirty = False

    # cruD
    def remove(self, *resources, **kwargs):
        """ See :func:`surf.plugin.writer.RDFWriter.remove` method. """

        self.writer.remove(*resources, **kwargs)

        for resource in resources:
            resource.dirty = False

    def size(self):
        """ See :func:`surf.plugin.writer.RDFWriter.size` method. """

        return self.writer.size()

    # triple level access methods
    def add_triple(self, s = None, p = None, o = None, context = None):
        """ See :func:`surf.plugin.writer.RDFWriter.add_triple` method. """

        context = self.__add_default_context(context)
        self.writer.add_triple(s = s, p = p, o = o, context = context)

    def set_triple(self, s = None, p = None, o = None, context = None):
        """ See :func:`surf.plugin.writer.RDFWriter.set_triple` method. """

        context = self.__add_default_context(context)
        self.writer.set_triple(s = s, p = p, o = o, context = context)

    def remove_triple(self, s = None, p = None, o = None, context = None):
        """ See :func:`surf.plugin.writer.RDFWriter.remove_triple` method. """

        context = self.__add_default_context(context)
        self.writer.remove_triple(s = s, p = p, o = o, context = context)

    def index_triples(self, **kwargs):
        """ See :func:`surf.plugin.writer.RDFWriter.index_triples` method. """

        return self.writer.index_triples(**kwargs)

    def load_triples(self, context=None, **kwargs):
        """ See :func:`surf.plugin.writer.RDFWriter.load_triples` method. """

        context = self.__add_default_context(context)
        return self.writer.load_triples(context=context, **kwargs)

    def __len__(self):
        return self.size()
