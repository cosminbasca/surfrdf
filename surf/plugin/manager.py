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
import pkg_resources
import os

class PluginNotFoundException(Exception):
    """ Raised when the required Plugin is not found

    """
    pass

log = logging.getLogger(__name__)
__plugins_loaded = False

__ENTRYPOINT_READER__ = 'surf.plugins.reader'
__ENTRYPOINT_WRITER__ = 'surf.plugins.writer'

__readers__ = {}
__writers__ = {}

def __init_plugins(plugins, entry_point):
    for entrypoint in pkg_resources.iter_entry_points(entry_point):
        plugin_class = entrypoint.load()
        plugins[entrypoint.name] = plugin_class
        log.info('loaded plugin [%s]'%entrypoint.name)

def load_plugins(reload=False):
    ''' Call this method to load the plugins into the manager. The method is called
    by default when a :class:`surf.store.Store` is instantiated. To cause a reload, call the method with `reload`
    set to *True*

    '''
    global __plugins_loaded
    if not __plugins_loaded or reload:
        __init_plugins(__readers__, __ENTRYPOINT_READER__)
        __init_plugins(__writers__, __ENTRYPOINT_WRITER__)
        __plugins_loaded = True

def __add_plugin(plugin):
    ext = os.path.splitext(plugin)[1]
    if ext == '.egg':
        pkg_resources.working_set.add_entry(os.path.abspath(plugin))

def add_plugin_path(plugin_path):
    ''' Add a `path` to the plugin manager. Can be a folder or a single file. If multiple paths (modules) need
    to be added this method can be called multiple times

    '''
    if os.path.isfile(plugin_path):
        __add_plugin(plugin_path)
    elif os.path.isdir(plugin_path):
        for file in os.listdir(plugin_path):
            __add_plugin(file)

# registered :cls:`surf.plugin.reader.RDFReader` plugins
registered_readers = lambda : __readers__.keys()

# registered :cls:`surf.plugin.writer.RDFWriter` plugins
registered_writers = lambda : __writers__.keys()
