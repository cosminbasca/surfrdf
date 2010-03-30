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

from surf.rdf import BNode, URIRef
from surf.resource import Resource
from surf.store import Store, NO_CONTEXT
from surf.util import DE_CAMEL_CASE_DEFAULT
from surf.util import attr2rdf, de_camel_case, is_uri, uri_to_classname

'''
TODO:
    Come to a resolution regarding the metaclass conflict
    for now classes that extend the Resource must have no metaclasses of 
    their own.
    
    Q: is it a good idea the generate a sublclass of all meta?
    or should the only meta to be used be ResourceMeta ?
    what are the implications ?

    from noconflict import classmaker
'''

__all__ = ['Session']

DEFAULT_RESOURCE_EXPIRE_TIME = 60 * 60
DEFAULT_STORE_KEY = 'default'

class Session(object):
    """ The `Session` will manage the rest of the components in **SuRF**,
    it also acts as the type factory for surf, the resources will walk the
    graph in a lazy manner based on the session that they are bound to
    (the last created session).

    """

    # TODO: add cache

    def __init__(self, default_store = None, mapping = {},
                 auto_persist = False, auto_load = False):
        """ Create a new `session` object that handles the creation of types
        and instances, also the session binds itself to the `Resource` objects
        to allow the Resources to access the data `store` and perform
        `lazy loading` of results.

        .. note:: The `session` object *behaves* like a `dict` when it
                  comes to managing the registered `stores`.

        """

        self.mapping = mapping

        self.__auto_persist = auto_persist
        self.__auto_load = auto_load
        #self.__use_cached = use_cached
        #self.__cache_expire = cache_expire
        self.__stores = {}

        if default_store:
            if type(default_store) is not Store:
                raise Exception('the arguments is not a valid Store instance')
            self.default_store = default_store

    # Emulate a dict for the sessions stores.
    def __len__(self):
        """ Total number of `stores` managed by the session. """
        return len(self.__stores)

    def __getitem__(self, key):
        """ Return the `store` associated with the key. """

        return self.__stores[key]

    def __setitem__(self, key, value):
        """ Set the `store` for the specified key, if value not a `Store`
        instance ignored. """

        if type(value) is Store :
            self.__stores[key] = value

    def __delitem__(self, key):
        """ Remove the specified `store` from the management `session`. """
        del self.__stores[key]

    def __iter__(self):
        """ `iterator` over the managed `stores`. """
        return self.__stores.__iter__()

    def __reversed__(self):
        return self.__stores.__reversed__()

    def __contains__(self, item):
        """ True if the `item` is contained within the managed `stores`. """

        return self.__stores.__contains__(item)

    def keys(self):
        """ The `keys` that are assigned to the managed `stores`. """

        return self.__stores.keys()

    def set_auto_persist(self, val):
        """ Setter function for the `auto_persist` property.

        Do not use this, use the `auto_persist` property instead.

        """

        if not isinstance(val, bool):
            val = False
            
        self.__auto_persist = val

    auto_persist = property(fget = lambda self: self.__auto_persist,
                            fset = set_auto_persist)
    """ Toggle `auto_persistence` (no need to explicitly call `commit`,
    `resources` are persisted to the `store` each time a modification occurs)
    on or off. Accepts boolean values. """

    def set_auto_load(self, val):
        """ Setter function for the `auto_load` property.

        Do not use it, use the `auto_load` property instead

        """

        if not isinstance(val, bool):
            val = False

        self.__auto_load = val

    auto_load = property(fget = lambda self: self.__auto_load,
                         fset = set_auto_load)
    """Toggle `auto_load` (no need to explicitly call `load`, `resources` are
    loaded from the `store` automatically on creation) on or off.
    Accepts boolean values. """

    def get_enable_logging(self):
        """ Getter function for the `enable_logging` property.

        Do not use this, use the `enable_logging` property instead.

        """

        for store in self.__stores:
            if not self.__stores[store].is_enable_logging():
                return False

        return True

    def set_enable_logging(self, enable):
        """ Setter function for the `enable_logging` property.

        Do not use this, use the `enable_logging` property instead.

        """

        for store in self.__stores:
            self.__stores[store].enable_logging(enable)

    enable_logging = property(fget = get_enable_logging,
                              fset = set_enable_logging)
    """ Toggle `logging` on or off. Accepts boolean values. """

    # TODO: add caching ... need strategies
    '''def set_use_cached(self,val):
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
    '''

    def get_default_store_key(self):
        """ Getter function for the `default_store_key` property.

        Do not use this, use the `default_store_key` property instead.

        """

        if DEFAULT_STORE_KEY in self.__stores:
            return DEFAULT_STORE_KEY
        elif len(self.__stores) > 0:
            return self.__stores.keys()[0]
        return None

    default_store_key = property(fget = get_default_store_key)
    """ The `default store key` of the session.

    If it is set explicitly on `session` creation it is returned,
    else the first `store key` is returned. If no `stores` are in the session
    None is returned. """


    def set_default_store(self, store):
        """ Setter function for the `default_store` property.

        Do not use this, use the `default_store` property instead.

        """

        self.__setitem__(DEFAULT_STORE_KEY, store)

    def get_default_store(self):
        """ Getter function for the `default_store` property.

        Do not use this, use the `default_store` property instead.

        """

        ds_key = self.default_store_key
        if ds_key:
            return self.__stores[ds_key]
        return None

    default_store = property(fget = get_default_store,
                              fset = set_default_store)
    """ The `default store` of the session.

    See `default_store_key` to see how the `default store` is selected. """

    def __uri(self, uri):
        """ For **internal** use only, convert the `uri` to a `URIRef`. """

        if not uri:
            return None

        if type(uri) is URIRef:
            return uri
        else:
            if not is_uri(uri):
                attrname = de_camel_case(uri, '_', DE_CAMEL_CASE_DEFAULT)
                uri, _ = attr2rdf(attrname)
            return URIRef(uri)

    def close(self):
        """ Close the `session`.

        .. note:: It is good practice to close the `session` when it's no
                  longer needed.
                  Remember: upon closing session all resources will lose
                  the ability to reference the session thus the store and
                  the mapping.

        """

        for store in self.__stores:
            self.__stores[store].close()
            del self.__stores[store]

        self.mapping = None

    def map_type(self, uri, store = None, *classes):
        """ Create and return a `class` based on the `uri` given.

        Also will add the `classes` to the inheritance list.

        """

        if store is None:
            store = self.default_store_key

        uri = self.__uri(uri)
        if not uri:
            return None
        name = uri_to_classname(uri)

        base_classes = [Resource]
        base_classes.extend(classes)

        # Also take classes from session.mapping
        session_classes = self.mapping.get(uri, [])
        if type(session_classes) not in [list, tuple, set]:
            session_classes = [session_classes]
        base_classes.extend(session_classes)
        return new.classobj(str(name), tuple(base_classes),
                            {'uri' : uri, 
                             'store_key' : store,
                             'session' : self})

    def get_class(self, uri, store = None, context = None, *classes):
        """
        See :func:`surf.session.Session.map_type`.
        The `uri` parameter can be any of the following:

            - a `URIRef`
            - a `Resource`
            - a `string` of the form
                - a URI
                - a Resource class name eg: `SiocPost`
                - a namespace_symbol type string eg: `sioc_post`

        """

        return self.map_type(uri, store, *classes)

    def map_instance(self, concept, subject, store = None, classes = [],
                     block_auto_load = False, context = None):
        """Create a `instance` of the `class` specified by `uri` and `classes`
        to be inherited, see `map_type` for more information. """

        if not type(subject) in [URIRef, BNode]:
            subject = URIRef(str(subject))

        if not store:
            store = self.default_store_key

        if not (isinstance(concept, type) and issubclass(concept, Resource)):
            concept = self.map_type(concept, store, *classes)
            
        return concept(subject, block_auto_load = block_auto_load,
                       context = context)

    def get_resource(self, subject, uri = None, store = None, graph = None,
                     block_auto_load = False, context = None, *classes):
        """ Same as `map_type` but `set` the resource from the `graph`. """

        if not isinstance(subject, URIRef):
            subject = URIRef(str(subject))

        if uri is None:
            uri = Resource.concept(subject)

        resource = self.map_instance(uri, subject, store, classes,
                                     block_auto_load = block_auto_load,
                                     context = context)

        if graph:
            resource.set(graph)

        return resource

    def load_resource(self, uri, subject, store = None, data = None,
                      file = None, location = None, format = None, *classes):
        """ Create a `instance` of the `class` specified by `uri`.

        Also set the internal properties according to the ones by the specified
        source.

        """

        resource = self.map_type(uri, store, *classes)(subject)
        resource.load_from_source(data = data, file = file,
                                  location = location, format = format)
        return resource

    def commit(self):
        """ Commit all the changes, update all the `dirty` `resources`. """

        # Copy set into list because it will shrink as we go through it
        for resource in list(Resource.get_dirty_instances()):
            resource.update()
