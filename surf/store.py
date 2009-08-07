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
import os
import pkg_resources
from plugin.reader import RDFReader
from plugin.writer import RDFWriter
'''
the store class is comprised of a reader and a writer, getting access to an
underlying tripple store. Also store specific parameters must be handled by
the class, the plugins act based on various settings
'''

__ENTRYPOINT_READER__ = 'surf.plugins.reader'
__ENTRYPOINT_WRITER__ = 'surf.plugins.writer'

__readers__ = {}
__writers__ = {}

def __init_plugins(plugins,entry_point):
    for entrypoint in pkg_resources.iter_entry_points(entry_point):
        plugin_class = entrypoint.load()
        plugins[entrypoint.name] = plugin_class

def load_plugins():
    __init_plugins(__readers__,__ENTRYPOINT_READER__)
    __init_plugins(__writers__,__ENTRYPOINT_WRITER__)

load_plugins()

registered_readers = lambda : __readers__.keys()
registered_writers = lambda : __writers__.keys()

class PluginNotFoundException(Exception):
    def __init__(self,*args,**kwargs):
        super(PluginNotFoundException,self).__init__(self,*args,**kwargs)

class Store(object):
    '''
    The plugin manager, also provides convenience methods for working with plugins
    '''
    def __init__(self,reader=None,writer=None,*args,**kwargs):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.info('initializing the store')
        self.log.info('registered readers : '+str(registered_readers()))
        self.log.info('registered writer : '+str(registered_writers()))
        if reader:
            if reader in __readers__:
                self.reader = __readers__[reader](*args,**kwargs)
            else:
                raise PluginNotFoundException('The <%s> READER plugin was not found'%(reader))
        else:
            self.reader = RDFReader(*args,**kwargs)
            
        if writer:
            if writer in __writers__:
                self.writer = __writers__[writer](*args,**kwargs)
            else:
                raise PluginNotFoundException('The <%s> WRITER plugin was not found'%(reader))
        else:
            self.writer = RDFWriter(*args,**kwargs)
        self.log.info('store initialized')
     
    def enable_logging(self,enable):
        level = logging.DEBUG if enable else logging.NOTSET
        self.log.setLevel(level)
        self.reader.enable_logging(enable)
        self.writer.enable_logging(enable)
    
    def is_enable_logging(self):
        return False if self.log.level == logging.NOTSET else True
    
    def close(self):
        try:
            self.reader.close()
            self.log('reader closed successfully')
        except Exception, e:
            self.log('error on closing the reader '+str(e))
        try:
            self.writer.close()
            self.log('writer closed successfully')
        except Exception, e:
            self.log('error on closing the writer '+str(e))
            
    def index_triples(self,**kwargs):
        '''
        performs index of the triples if such functionality is present
        returns True if operation successfull
        '''
        return self.writer.index_triples(**kwargs)
        
    def load_triples(self,**kwargs):
        '''
        loads triples from supported sources if such functionality is present
        returns True if operation successfull
        '''
        return self.writer.load_triples(**kwargs)
    #---------------------------------------------------------------------------
    # the reader interface
    #---------------------------------------------------------------------------
    
    def get(self,resource,attribute,direct):
        '''
        returns the value(s) of the corresponding attribute
        '''
        return self.reader.get(resource,attribute,direct)
    
    # cRud    
    def load(self,resource,direct):
        '''
        fully loads the resource from the store, returns all statements about the resource
        '''
        return self.reader.load(resource,direct)
        
    def is_present(self,resource):
        '''
        True if the resource is present in the store, False otherwise
        '''
        return self.reader.is_present(resource)
        
    def all(self,concept,limit=None,offset=None):
        '''
        returns all uri's that are instances of concept within [limit,limit+offset]
        '''
        return self.reader.all(concept,limit=limit,offset=offset)
        
    def concept(self,resource):
        '''
        returns the concept URI of the following resource,
        resource can be a string or a URIRef
        '''
        return self.reader.concept(resource)
        
    def instances_by_attribute(self,resource,attributes,direct):
        '''
        returns all uri's that are instances of concept that have the attributes
        '''
        return self.reader.instances_by_attribute(resource,attributes,direct)
        
    def instances(self,resource,direct,filter,predicates):
        '''
        '''
        return self.reader.instances(resource,direct,filter,predicates)
        
    def instances_by_value(self,resource,direct,attributes):
        '''
        '''
        return self.reader.instances_by_value(resource,direct,attributes)
    
    #---------------------------------------------------------------------------
    # the query reader interface
    #---------------------------------------------------------------------------
    
    def execute(self,query):
        '''
        execute a query of type surf.query.Query
        '''
        if hasattr(self.reader,'execute') and type(query) is Query:
            return self.reader.execute(query)
        return None
    
    def execute_sparql(self,sparql_query):
        '''
        execute a SPARQL query as a string
        '''
        if hasattr(self.reader,'execute_sparql') and type(query) in [str,unicode]:
            return self.reader.execute_sparql(query)
        return None
    
    #---------------------------------------------------------------------------
    # the writer interface
    #---------------------------------------------------------------------------
    
    def clear(self,context=None):
        '''
        empty the store
        '''
        self.writer.clear(context=context)
    
    # Crud    
    def save(self,resource):
        '''
        replace the resource with it's current state
        '''
        self.writer.save(resource)
    
    # crUd
    def update(self,resource):
        '''
        update the current resource
        '''
        self.writer.update(resource)
        
    # cruD
    def remove(self,resource):
        '''
        completly remove the resource from the store
        '''
        self.writer.remove(resource)
        
    def size(self):
        '''
        returns the size in triples, that are contained in the current store
        '''
        return self.writer.size()
        
    # triple level access methods
    def add_triple(self,s=None,p=None,o=None, context=None):
        '''
        add a triple to the store, with the specified context,
        None can be used as a wildcard
        '''
        self.writer.add_triple(s=s,p=p,o=o,context=context)
    
    def set_triple(self,s=None,p=None,o=None, context=None):
        '''
        replace a triple in the store, with the specified context
        None can be used as a wildcard
        '''
        self.writer.set_triple(s=s,p=p,o=o,context=context)
    
    def remove_triple(self,s=None,p=None,o=None, context=None):
        '''
        remove a triple from the store, with the specified context
        None can be used as a wildcard
        '''
        self.writer.remove_triple(s=s,p=p,o=o,context=context)
    