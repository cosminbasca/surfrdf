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
from query import Query
from store import Store
from resource import Resource, ResourceMeta
import util
from exceptions import TypeError

# the rdf way
#from rdf.term import URIRef, BNode, Literal
# the rdflib 2.4.x way
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal


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

DEFAULT_RESOURCE_EXPIRE_TIME = 60 * 60
DEFAULT_STORE_KEY = 'default'

class Session(object):
    '''the `Session` will manage the rest of the components in **SuRF**, it also acts as the
    type factory for surf, the resources will walk the graph in a lazy manner based
    on the session that they are bound to (the last created session)'''
    
    def __init__(self,default_store=None,mapping={},auto_persist=False,auto_load=False,use_cached=False,cache_expire=DEFAULT_RESOURCE_EXPIRE_TIME):
        '''creates a new `session` object that handles the creation of types and
        instances, also the session binds itself to the `Resource` objects to allow
        the Resources to access the data `store` and perform `lazy loading` of results
        
        note: the `session` object *behaves* like a `dict` when it comes to managing
        the registered `stores`'''
        self.mapping = mapping
        
        setattr(Resource,'session',self)
        setattr(ResourceMeta,'session',self)
        
        self.__auto_persist = auto_persist
        self.__auto_load = auto_load
        self.__use_cached = use_cached
        self.__cache_expire = cache_expire
        self.__stores = {}
        
        if default_store:
            if type(default_store) is not Store:
                raise Exception('the arguments is not a valid Store instance')
            self.default_store = default_store
        
    #emulate a dict for the sessions stores
    def __len__(self):
        '''total number of `stores` managed by the session'''
        return len(self.__stores)
        
    def __getitem__(self,key):
        '''returns the `store` associated with the key'''
        return self.__stores[key]
    
    def __setitem__(self,key,value):
        '''sets the `store` for the specified key, if value not a `Store` instance ignored'''
        if type(value) is Store :
            self.__stores[key] = value
            
    def __delitem__(self,key):
        '''removes the specified `store` from the management `session`'''
        del self.__stores[key]
        
    def __iter__(self):
        '''`iterator` over the managed `stores`'''
        return self.__stores.__iter__()
        
    def __reversed__(self):
        return self.__stores.__reversed__()
        
    def __contains__(self,item):
        '''True if the `item` is contained within the managed `stores`'''
        return self.__stores.__contains__(item)
        
    def keys(self):
        '''The `keys` that are assigned to the managed `stores`'''
        return self.__stores.keys()
        
    def set_auto_persist(self,val):
        '''setter function for the `auto_persist` property, do not use,
        use the `auto_persist` property instead'''
        self.__auto_persist = val if type(val) is bool else False
    auto_persist = property(fget = lambda self: self.__auto_persist,
                                 fset = set_auto_persist)
    '''toggles `auto_persistence` (no need to explicitly call `commit`, `resources` are
    persited to the `store` each time a modification occurs) on or off'''
    
    def set_auto_load(self,val):
        '''setter function for the `auto_load` property, do not use,
        use the `auto_load` property instead'''
        self.__auto_load = val if type(val) is bool else False
    auto_load = property(fget = lambda self: self.__auto_load,
                                 fset = set_auto_load)
    '''toggles `auto_load` (no need to explicitly call `load`, `resources` are
    loaded from the `store` automatically on creation) on or off'''
    
    def get_enable_logging(self):
        '''getter function for the `enable_logging` property, do not use,
        use the `enable_logging` property instead'''
        for store in self.__stores:
            if not self.__stores[store].is_enable_logging():
                return False
        return True
    def set_enable_logging(self,enable):
        '''setter function for the `enable_logging` property, do not use,
        use the `enable_logging` property instead'''
        for store in self.__stores:
            self.__stores[store].enable_logging(enable)
    enable_logging = property(fget = get_enable_logging,
                              fset = set_enable_logging)
    '''toggles `loggins` on or off'''
    
    
    def set_use_cached(self,val):
        self.__use_cached = val if type(val) is bool else False
    use_cached = property(fget = lambda self: self.__use_cached,
                                 fset = set_use_cached)
    def set_cache_expire(self,val):
        try:
            self.__cache_expire = int(val)
        except TypeError:
            self.__cache_expire = DEFAULT_RESOURCE_EXPIRE_TIME
    cache_expire = property(fget = lambda self: self.__cache_expire,
                                 fset = set_cache_expire)
    
    def get_default_store_key(self):
        '''getter function for the `default_store_key` property, do not use,
        use the `default_store_key` property instead'''
        if DEFAULT_STORE_KEY in self.__stores:
            return DEFAULT_STORE_KEY
        elif len(self.__stores) > 0:
            return self.__stores.keys()[0]
        return None
    default_store_key = property(fget = get_default_store_key)
    '''the `default store key` of the session
    If it is set expcicitly on `session` creation it is returned,
    else the first `store key` is returned. If no `stores` are in the session
    None is returned'''
    
    
    def set_default_store(self,store):
        '''setter function for the `default_store` property, do not use,
        use the `default_store` property instead'''
        self.__setitem__(DEFAULT_STORE_KEY,store)
    def get_default_store(self):
        '''getter function for the `default_store` property, do not use,
        use the `default_store` property instead'''
        ds_key = self.default_store_key
        if ds_key:
            return self.__stores[ds_key]
        return None
    default_store = property(fget = get_default_store,
                              fset = set_default_store)
    '''the `default store` of the session
    see `default_store_key` to see how the `default store` is selected'''
    
    def __uri(self,uri):
        '''for **internal** use only, converts the `uri` to a `URIRef`'''
        if not uri:
            return None
        
        if type(uri) is URIRef:
            return uri
        elif type(uri) is ResourceMeta:
            return uri.uri
        else:
            return URIRef(uri)
        
    def close(self):
        '''closes the `session`
        
        note: good practice to close the `session` when no longer needed, remember, all
        resources will lose the ability to reference the session thus the store
        and the mapping'''
        for store in self.__stores:
            self.__stores[store].close()
            del self.__stores[store]
        self.mapping = None
        setattr(Resource,'session',None)
        setattr(ResourceMeta,'session',None)
        # expire resources (stop timers)
        
    def map_type(self,uri,store=None,*classes):
        '''creates a `class` based on the `uri` given, also will add the `classes`
        to the inheritance list'''
        store = self.default_store_key if not store else store
        
        uri = self.__uri(uri)
        if not uri:
            return None
        name = util.uri_to_classname(uri)
        
        base_classes = [Resource]
        base_classes.extend(list(classes) if classes != None else [])
        return new.classobj(str(name), tuple(base_classes),{'uri':uri,'store_key':store})
        
    def get_class(self,uri,store=None,*classes):
        '''same as `map_type`'''
        return self.map_type(uri,store,*classes)
        
    def map_instance(self,uri,subject,store=None,classes = [],block_outo_load=False):
        '''creates a `instance` of the `class` specified by `uri` and `classes` to be
        inherited, see `map_type` for more information'''
        subject = subject if type(subject) is URIRef else URIRef(str(subject))
        return self.map_type(uri,store,*classes)(subject,block_outo_load=block_outo_load)
        
    def get_resource(self,subject,uri=None,store=None,graph=None,block_outo_load=False,*classes):
        '''same as `map_type` but `sets` the resource from the `graph`'''
        subject = subject if type(subject) is URIRef else URIRef(str(subject))
        uri = uri if uri else Resource.concept(subject)
        resource = self.map_instance(uri,subject,store,block_outo_load=block_outo_load,*classes)
        if graph:
            resource.set(graph)
        return resource
        
    def load_resource(self,uri,subject,store=None,data=None,file=None,location=None,format=None,*classes):
        '''creates a `instance` of the `class` specified by `uri`, and sets the intenal
        properties according to the ones by the specified source'''
        resource = self.map_type(uri,store,*classes)(subject)
        resource.load_from_source(data=data,file=file,location=location,format=format)
        return resource
        
    def commit(self):
        '''commits all the changes, updates all the `dirty` `resources`'''
        resources = Resource.instances()
        print 'SESSION ------------------------------------'
        print resources
        print '--------------------------------------------'
        for resource in resources:
            print resource,'DIRTY > ',resource.dirty
            if resource.dirty:
                resource.update()
        
