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
import os
import pkg_resources
from surf.exceptions import PluginNotFoundException
from surf.plugin.reader import RDFReader
from surf.plugin.writer import RDFWriter
from surf.log import info
from .rdflib.reader import ReaderPlugin as RdflibReader
from .rdflib.writer import WriterPlugin as RdflibWriter
from .sparql_protocol.reader import ReaderPlugin as SparqlReader
from .sparql_protocol.writer import WriterPlugin as SparqlWriter

__author__ = 'Cosmin Basca'

_plugins_loaded = False

ENTRY_POINT_READER = 'surf.plugins.reader'
ENTRY_POINT_WRITER = 'surf.plugins.writer'

_readers = {}
_writers = {}


def _init_plugins(plugins, entry_point_name):
    for entry_point in pkg_resources.iter_entry_points(entry_point_name):
        plugin_class = entry_point.load()
        plugins[entry_point.name] = plugin_class
        info('loaded plugin [%s]'%entry_point.name)


def load_plugins(reload=False):
    """
    Call this method to load the plugins into the manager. The method is called
    by default when a :class:`surf.store.Store` is instantiated. To cause a reload, call the method with `reload`
    set to *True*

    :param bool reload: reload plugins if True
    :param logger: the logger
    """
    global _plugins_loaded
    if not _plugins_loaded or reload:
        _init_plugins(_readers, ENTRY_POINT_READER)
        _init_plugins(_writers, ENTRY_POINT_WRITER)
        _plugins_loaded = True


def register(name, reader, writer):
    """
    register reader and writer plugins
    :param str name: the plugin name
    :param reader: the reader plugin
    :param writer: the writer plugin
    """
    assert issubclass(reader, RDFReader) or reader is None
    assert issubclass(writer, RDFWriter) or writer is None
    if reader:
        _readers[name] = reader
    if writer:
        _writers[name] = writer


def _register_surf():
    import surf
    surf_parent = os.path.split(os.path.split(surf.__file__)[0])[0]
    for dist in pkg_resources.find_distributions(surf_parent):
        if dist.key == 'surf':
            pkg_resources.working_set.add(dist)
            break


def add_plugin_path(plugin_path):
    """
    Loads plugins from `path`. Method can be called multiple times, with different locations. (Plugins are loaded only
    once).

    :param str plugin_path: register plugin search path
    """
    _register_surf()
    for dist in pkg_resources.find_distributions(plugin_path):
        # only load SURF plugins!
        if ENTRY_POINT_READER in dist.get_entry_map() or ENTRY_POINT_WRITER in dist.get_entry_map():
            pkg_resources.working_set.add(dist)


def registered_readers():
    """
    gets the registered reader plugins. Plugins are instances of :cls:`surf.plugin.reader.RDFReader`.

    :return: the registered reader plugins
    :rtype: list or set
    """
    return _readers.keys()


def registered_writers():
    """
    gets the registered writer plugins. Plugins are instances of :cls:`surf.plugin.reader.RDFWriter`.

    :return: the registered writer plugins
    :rtype: list or set
    """
    return _writers.keys()


def get_reader(reader_id, *args, **kwargs):
    global _readers
    if reader_id in _readers:
        return _readers[reader_id](*args, **kwargs)
    raise PluginNotFoundException('reader plugin [{0}] was not found'.format(reader_id))


def get_writer(writer_id, reader, *args, **kwargs):
    assert isinstance(reader, RDFReader), 'reader is not an instance of RDFReader!'
    global _writers
    if writer_id in _writers:
        return _writers[writer_id](reader, *args, **kwargs)


# ----------------------------------------------------------------------------------------------------------------------
#
# register builtin plugins
#
# ----------------------------------------------------------------------------------------------------------------------
register("rdflib", RdflibReader, RdflibWriter)
register("sparql_protocol", SparqlReader, SparqlWriter)
# load the rest of the plugins
load_plugins(reload=False)
