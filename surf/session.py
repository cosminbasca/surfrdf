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

import new
from rdf.term import URIRef, BNode, Literal
from query import Query
from store import Store
from resource import Resource, ResourceMeta
import util

'''
TODO:
    come to a resolution regarding the metaclass conflict
    for now classes that extend the Resource must have no metaclasses of their own
    q: is it a good ideea the generate a sublclass of all meta?
    or should the only meta to be used be ResourceMeta ?
    what are the implications ?
    
    from noconflict import classmaker
'''

__all__ = ['Session']

class Session(object):
    '''
    the session will manage the rest of the components in surf, it also acts as the
    type factory for surf, the resources will walk the graph in a lazy manner based
    on the session that they are bound to (the last created session)
    '''
    def __init__(self,store,mapping={},auto_persist=False,auto_load=False):
        '''
        creates a new session object that handles the creation of types and
        instances, also the session binds itself to the Resource objects to allow
        the Resources to perform lazy binding of results
        -- auto_load not working yet problem is deeper
        '''
        if type(store) is not Store:
            raise Exception('the arguments is not a valid Store instance')
        self.store = store
        self.mapping = mapping
        
        setattr(Resource,'session',self)
        setattr(ResourceMeta,'session',self)
        
        self.__auto_persist = auto_persist
        self.__auto_load = auto_load
    
    def set_auto_persist(self,val):
        self.__auto_persist = val if type(val) is bool else False
        
    auto_persist = property(fget = lambda self: self.__auto_persist,
                                 fset = set_auto_persist)
    
    def set_auto_load(self,val):
        self.__auto_load = val if type(val) is bool else False
        
    auto_load = property(fget = lambda self: self.__auto_load,
                                 fset = set_auto_load)
    
        
    def set_enable_logging(self,enable):
        self.store.enable_logging(enable)
        
    enable_logging = property(fget = lambda self: self.store.is_enable_logging(),
                              fset = set_enable_logging)
    
    def __uri(self,uri):
        if not uri:
            return None
        
        if type(uri) is URIRef:
            return uri
        elif type(uri) is ResourceMeta:
            return uri.uri
        else:
            return URIRef(uri)
    
    def close(self):
        '''
        good practice to close the session when no longer needed, remember, all
        resources will lose the ability to reference the session thus the store
        and the mapping
        '''
        self.store.close()
        self.store = None
        self.mapping = None
        setattr(Resource,'session',None)
        setattr(ResourceMeta,'session',None)
    
    def map_type(self,uri,*classes):
        '''
        creates a Python class based on the uri given, also will add the classes
        to the inheritance list
        '''
        uri = self.__uri(uri)
        if not uri:
            return None
        name = util.uri_to_classname(uri)
        
        base_classes = [Resource]
        base_classes.extend(list(classes) if classes != None else [])
        return new.classobj(str(name), tuple(base_classes),{'uri':uri})
        
    def uri_to_class(self,uri):
        return new.classobj(str(util.uri_to_classname(uri)),(),{'uri':uri})
        
    def get_class(self,uri,*classes):
        return self.map_type(uri,*classes)
        
    def get_resource(self,subject,uri=None,graph=None,block_outo_load=False,*classes):
        subject = subject if type(subject) is URIRef else URIRef(str(subject))
        uri = uri if uri else Resource.concept(subject)
        resource = self.map_instance(uri,subject,block_outo_load=block_outo_load,*classes)
        if graph:
            resource.set(graph)
        return resource
        
    def map_instance(self,uri,subject,classes = [],block_outo_load=False):
        '''
        creates a Python instance of the class specified by uri and classes to be
        inherited, see map_type for more information
        '''
        subject = subject if type(subject) is URIRef else URIRef(str(subject))
        return self.map_type(uri,*classes)(subject,block_outo_load=block_outo_load)
    
    def load_resource(self,uri,subject,data=None,file=None,location=None,format=None,*classes):
        '''
        creates a Python instance of the class specified by uri, and sets the intenal
        properties according to the ones by the specified source
        '''
        resource = self.map_type(uri,*classes)(subject)
        resource.load_from_source(data=data,file=file,location=location,format=format)
        return resource
    
    def create_resource(self,uri,subject,graph,*classes):
        '''
        creates a Python instance of the class specified by uri, and sets the intenal
        properties according to the ones in the supplied graph
        '''
        resource = self.map_type(uri,*classes)(subject)
        resource.set(graph)
        return resource
    
    def commit(self):
        resources = Resource.instances()
        for resource in resources:
            if resource.is_dirty():
                resource.update()
        
    
    #load resource from file ...
    #load all resources from file ...
