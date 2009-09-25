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

import re
import new
from surf.namespace import *
from surf.query import Query
from surf.store import Store
from surf.resource.value import ResourceValue
from surf.util import *
from surf.rest import *
from surf.serializer import to_json
from weakref import WeakKeyDictionary
from datetime import datetime, date, time

# the rdf way
#from rdf.term import URIRef, Literal, BNode, RDF, RDFS, XSD
#from rdf.namespace import Namespace, ClosedNamespace
#from rdf.graph import Graph, ConjunctiveGraph
# the rdflib 2.4.x way
from rdflib.Namespace import Namespace
from rdflib.Graph import Graph, ConjunctiveGraph
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal
from rdflib.RDF import RDFNS as RDF
from rdflib.RDFS import RDFSNS as RRDFS

a = RDF['type']

#--------------------------------------------------------------------------------------------------------

class ResourceMeta(type):
    def __new__(meta, classname, bases, class_dict):
        ResourceClass = super(ResourceMeta,meta).__new__(meta,classname,bases,class_dict)
        if 'uri' not in class_dict:
            ResourceClass.uri = None
        ResourceClass._instance = meta._instance
        ResourceClass._lazy = meta._lazy
        return ResourceClass
    
    def __init__(self,*args,**kwargs):
        pass
    
    @classmethod
    def _instance(cls, subject, vals, context = None):
        '''
        creates an instance from the `subject` and it's associated `concept` (`vals`) uri's
        only the first `concept` uri is considered for inheritance
        '''
        if cls.session:
            uri = vals[0] if len(vals) > 0 else None
            classes = map(uri_to_class,vals[1:]) if len(vals) > 1 else []
            if uri:
                return cls.session.map_instance(uri, subject, classes = classes,
                                                block_outo_load = True,
                                                context = context) 
            else:
                return subject
        else:
            return None
    
    @classmethod
    def _lazy(cls,value):
        '''
        does `lazy` instantiation of rdf predicates
        value is a dictionary {val:[concept,concept,...]},
        returns a instance of `Resource`
        '''        
        attr_value = []
        for r in value:
            inst = r
            if isinstance(value[r], Resource) :
                inst = value[r]
            elif type(r) is URIRef:
                inst = cls._instance(r, value[r])
            attr_value.append(inst)
        return attr_value
    
    def __getattr__(self,attr_name):
        '''
        finds `instances` of the current Class that extends `Resource`,
        the `instances` are selected from the values of the specified predicate (`attr_name`)
        
        for now these are not persisted in the `Resource` class - next time the method
        is called the instances are retrieved from the `store` again.
        '''
        #TODO: add persistence at metaclass level
        value = None
        predicate, direct = attr2rdf(attr_name)
        if predicate:
            
            instances = self.session[self.store_key].instances_by_value(self,direct,[predicate])
            value = self._lazy(instances)
            if value or (type(value) is list and len(value) > 0):
                pass
            else:
                value = None
        return value
    
#--------------------------------------------------------------------------------------------------------

class Resource(object):
    '''
    The Resource class, represents the transparent proxy object that exposes sets of
    RDF triples under the form of <s,p,o> and <s',p,s> as an object in python,
    one can create resource directly by instantiating this class, but it is advisable
    to use the session to do so, as the session will create subclasses of Resource based
    on the <s,rdf:type,`concept`> pattern
    '''
    __metaclass__ = ResourceMeta
    _instances = WeakKeyDictionary()
    
    def __init__(self, subject = None, block_outo_load = False, context = None):
        '''initializes a Resource, with the `subject` (a URI - either a string or a URIRef),
        if the `subject` is None than a unique subject will be generated using the
        :func:`surf.util.uuid_subject` method
        `block_autoload` will prevent the resource from autoloading all rdf attributes associated
        with the subject of the resource'''
        self.__subject = subject if subject else uuid_subject()
        self.__subject = self.__subject if type(self.__subject) is URIRef else URIRef(self.__subject)
        self.__context = context
        self.__dirty = False
        self._instances[self] = True
        self.__expired = False
        self.__rdf_direct = {}
        self.__rdf_direct[a] = [self.uri]
        self.__rdf_inverse = {}
        self.__namespaces = {}
        if self.session:
            if not self.store_key: self.store_key = self.session.default_store_key
            if self.session.auto_load and not block_outo_load: self.load()
            
    subject = property(lambda self: self.__subject)
    '''the subject of the resource '''
    
    namespaces = property(fget = lambda self: self.__namespaces)
    '''the namespaces'''
    
    dirty = property(fget = lambda self: self.__dirty)
    '''reflects the `dirty` state of the resource'''
    
    rdf_direct = property(fget = lambda self: self.__rdf_direct)
    '''direct predicates (`outgoing` predicates)'''
    
    rdf_inverse = property(fget = lambda self: self.__rdf_inverse)
    '''inverse predicates (`incoming` predicates)'''

    def __set_context(self, value):
        if not isinstance(value, URIRef):
            value = URIRef(value)
        
        self.__context = value
    
    context = property(fget = lambda self: self.__context,
                       fset = __set_context)
    
    def bind_namespaces(self,*namespaces):
        """ Bind the `namespace` to the `resource`.
        
        Useful for pretty serialization of the resource.
        
        """
        
        for ns in namespaces:
            if type(ns) in [str,unicode]:
                self.__namespaces[ns] = get_namespace_url(ns)
            elif type(ns) in [Namespace, ClosedNamespace]:
                self.__namespaces[get_prefix(ns)] = ns
                
    def bind_namespaces_to_graph(self,graph):
        '''
        binds the 'resources' registered namespaces to the supplied `graph`
        '''
        if graph:
            for prefix in self.namespaces:
                graph.namespace_manager.bind(prefix, self.namespaces[prefix])
    
    @classmethod
    def instances(cls):
        '''
        returns all the `instances` of type `Resource` currently available in memory
        '''
        return cls._instances.keys()
        
    @classmethod
    def instance(cls,subject):
        '''
        returns the `Resource` `instance` currently in memory with the specified subject
        '''
        for i in cls._instances:
            if i.subject == subject:
                return i
        return None
    
    def value_to_rdf(self,value):
        '''
        for **internal** use, converts the value to an RDFLib compatible type if appropriate
        '''
        if type(value) in [str, unicode, basestring, float, int, long, bool, datetime, date, time]:
            return Literal(value)
        elif type(value) in [list, tuple]:
            language = value[1] if len(value) > 1 else None
            datatype = value[2] if len(value) > 2 else None
            return Literal(value[0],lang=language,datatype=datatype)
        elif type(value) is dict:
            val = value['value'] if 'value' in value else None
            language = value['language'] if 'language' in value else None
            datatype = value['datatype'] if 'datatype' in value else None
            if val:
                return Literal(val,lang=language,datatype=datatype)
            return value
        return value
    
    def to_rdf_internal(self, value):
        if type(value) is ResourceMeta:
            return value.uri
        elif hasattr(value,'subject'):
            return value.subject
        elif type(value) not in [URIRef, BNode, Literal]:
            return self.value_to_rdf(value)
        return value
    
    #TODO: add the auto_persist feature...
    def __setattr__(self,name,value):
        '''
        the `set` method - responsible for *caching* the `value` to the coresponding
        object attribute given by `name`
        
        note: this method sets the state of the resource to *dirty* (the `resource`
        will be persisted if the `commit` `session` method is called)
        '''
        predicate, direct = attr2rdf(name)
        if predicate:
            if type(value) is ResourceValue:
                pass
            else:
                if type(value) not in [list, tuple]: value = [value]
                value = map(self.value_to_rdf,value)
                value = ResourceValue(value, self, predicate, direct)
            
            rdf_dict = self.__rdf_direct if direct else self.__rdf_inverse
            rdf_dict[predicate] = []
            rdf_dict[predicate].extend([self.to_rdf_internal(val) for val in value])
            self.__dirty = True
        object.__setattr__(self,name,value)
        
    def value_set_item(self,key, value, predicate, direct):
        item_value = self.value_to_rdf(value)
        rdf_dict = self.__rdf_direct if direct else self.__rdf_inverse
        rdf_dict[predicate][key] = item_value.subject if hasattr(item_value,'subject') else item_value
        self.__dirty = True
            
    #TODO: add the auto_persist feature...
    def __delattr__(self,attr_name):
        '''
        the `del` method - responsible for deleting the attribute of the object given
        by `attr_name`
        
        note: this method sets the state of the resource to *dirty* (the `resource`
        will be persisted if the `commit` `session` method is called)
        '''
        predicate, direct = attr2rdf(attr_name)
        if predicate:
            #value = self.__getattr__(attr_name)
            rdf_dict = self.__rdf_direct if direct else self.__rdf_inverse
            rdf_dict[predicate] = []
            self.__dirty = True
        object.__delattr__(self,attr_name)
    
    def value_del_item(key, predicate, direct):
        rdf_dict = self.__rdf_direct if direct else self.__rdf_inverse
        del rdf_dict[predicate][key]
        self.__dirty = True
    
    # TODO: reuse already existing instances - CACHED
    # TODO: shoud we raise an error when predicate not foud ? or just return an empty list ? hmmm --- error :]
    def __getattr__(self,attr_name):
        '''
        the `get` method - responsible for retrieving and caching using `__setattr__`
        the value(s) of the specified `attr_name` (object attribute)
        
        this method has no impact on the *dirty* state of the object
        '''
        attr_value = None
        predicate, direct = attr2rdf(attr_name)
        if predicate:
            values = self.session[self.store_key].get(self, predicate, direct)
            surf_values = self._lazy(values)
            if len(surf_values) == 0:
                #raise ValueError('the specified attribute <%s> does not exist for the current resource <%s>'%(attr_name,self.subject))
                #attr_value = None
                attr_value = ResourceValue([], self, predicate, direct)
            else:
                attr_value = ResourceValue(surf_values, self, predicate, direct)
            self.__setattr__(attr_name,attr_value)
            self.__dirty = False
        else:
            raise ValueError('not a predicate: %s'%(attr_name))
        return attr_value

    def load(self):
        '''
        Load all attributes from the data store:
            - direct attributes (where the subject is the subject of the resource)
            - indirect attributes (where the object is the subject of the resource)
            
        note: this method resets the *dirty* state of the object
        
        '''
        
        results_d = self.session[self.store_key].load(self, True)
        results_i = self.session[self.store_key].load(self, False)
        self.__set_predicate_values(results_d,True)
        self.__set_predicate_values(results_i,False)
        self.__dirty = False
        
    def __set_predicate_values(self,results,direct):
        ''' set the prediate - value(s) to the resource using lazy loading,
        `results` is a dict under the form:
        {'predicate':{'value':[concept,concept],...},...}'''
        for p,v in results.items():
            attr = rdf2attr(p,direct)
            value = self._lazy(v)
            if value or (type(value) is list and len(value) > 0):
                self.__setattr__(attr,value)
    
        
    @classmethod
    def get_by_attribute(cls, attributes, context = None):
        '''
        Retrieve all `instances` from the data store that have the specified `attributes`
        and are of `rdf:type` of the resource class
        '''
        
        subjects = {}
        subjects.update(cls.session[cls.store_key].instances_by_attribute(cls, attributes, True, context))
        subjects.update(cls.session[cls.store_key].instances_by_attribute(cls, attributes, False, context))
        
        instances = []
        for s, types in subjects.items():
            if type(s) is URIRef:
                instances.append(cls._instance(s,[cls.uri] if cls.uri else types))
        return instances if len(instances) > 0 else []
        
    @classmethod
    def all(cls, offset = None, limit = None, full = False, context = None):
        """Retrieve all or limited number of `instances`.
        
        Retrieve all (or just a limited number from the specified offset) 
        `instances` that are of the `rdf:type` as the resource class.
        
        """
        
        if not hasattr(cls,'uri') or cls == Resource:
            return []
        
        store = cls.session[cls.store_key]
        store_response = store.all(cls, limit = limit, offset = offset, 
                                   full = full, context = context)

        if store.use_subqueries and full:
            direct = True # TODO: must implement for indirect as well
            results = []
            for subject, attrs_values in store_response.items():
                obj = cls(subject, context = context)
                obj.__set_predicate_values(attrs_values,direct)
                results.append(obj) 
        else:
            results = []
            for subject in store_response:
                instance = cls(subject, context = context)
                if full: instance.load()
                results.append(instance)
        
        return results
        
    @classmethod
    def __get(cls, filter, context, *objects, **symbols):
        '''
        
        For *internal* use only! Retrieve `instances` of the `rdf:type` as 
        the resource class, that have triples that match the `attr_name:value` 
        pair specified using `**symbols`, the method also supports `filters`.
        
        '''

        predicates_d = {}
        predicates_d.update( [(attr2rdf(name)[0],symbols[name]) for name in symbols if is_attr_direct(name)])
        predicates_i = {}
        predicates_i.update( [(attr2rdf(name)[0],symbols[name]) for name in symbols if not is_attr_direct(name)])
        
        
        subjects = {}
        if len(symbols) > 0:
            if len(predicates_d) > 0:
                subjects.update(cls.session[cls.store_key].instances(cls, True, filter, predicates_d, context))
            if len(predicates_i) > 0:
                subjects.update(cls.session[cls.store_key].instances(cls, False, filter, predicates_i, context))
        
        #if len(objects) > 0:
        #    subjects.update(cls.store().o(True,cls.uri(),filter,objects))
        #    subjects.update(cls.store().o(False,cls.uri(),filter,objects))
        
        instances = []
        for s, types in subjects.items():
            if type(s) is not URIRef:
                continue
                
            instance = cls._instance(s, [cls.uri] if cls.uri else types,
                                     context = context)
            instances.append(instance)
            
        return instances if len(instances) > 0 else []
        
    @classmethod
    def get_by(cls, context = None, *objects, **symbols):
        ''' Retrieve all instances that match specified filters and class.
        
        Filters are specified as keyword arguments, argument names follow SuRF
        naming convention (they take form `namespace_name`).
        
        Example::
        
            Person = session.get_class(surf.ns.FOAF['Person'])
            johns = Person.get_by(foaf_name = u"John") 
        
        '''
        
        return cls.__get(None, context, *objects, **symbols)
    
    @classmethod
    def get_like(cls, context = None, *objects, **symbols):
        '''
        retrieves all `instances` that have attribute value pairs, with support for regex
        matching on values and have `rdf:type` as the resource class
        
        note: currently regex is slow, try to avoid the use of this method
        '''
        return cls.__get('regex', context, *objects, **symbols)
    
    def serialize(self, format = 'xml', direct = False):
        '''
        returns a serialized version of the internal graph represenatation
        of the resource, the format is the same as expected by rdflib's graph
        serialize method
        
        supported formats:
            - **n3**
            - **xml**
            - **json** (internal serializer)
            - **nt**
            - **turtle**
        '''
        graph = self.graph(direct=direct)
        if format == 'json':
            return to_json(graph)
        return graph.serialize(format=format)
        
    def graph(self,direct=True):
        '''
        returns an `rdflib` `ConjunctiveGraph` represenation of the current `resource`
        '''
        graph = ConjunctiveGraph()
        self.bind_namespaces_to_graph(graph)
        graph.add((self.subject,RDF['type'],self.uri))
        for predicate in self.__rdf_direct:
            for value in self.__rdf_direct[predicate]:
                if type(value) in [URIRef, Literal, BNode]:
                    graph.add((self.subject,predicate,value))
        if not direct:
            for predicate in self.__rdf_inverse:
                for value in self.__rdf_inverse[predicate]:
                    if type(value) in [URIRef, Literal, BNode]:
                        graph.add((value,predicate,self.subject))
        return graph
        
    def __str__(self):
        '''
        the `string` representation of the resource
        '''
        return '{%s : %s}'%(unicode(self.subject),unicode(self.uri))
    
    def save(self):
        '''
        saves the `resource` to the data `store`, replacing the representation with
        the current one
        '''
        self.session[self.store_key].save(self)
        self.__dirty = False
        
    def remove(self):
        '''
        remove the `resource` from the data `store`
        '''
        self.session[self.store_key].remove(self)
        self.__dirty = False
        
    def update(self):
        '''
        update the resource in the data `store`, does not remove other triples
        related to it (the inverse triples of type <s',p,s>, where s is the
        `subject` of the `resource`)
        '''
        self.session[self.store_key].update(self)
        self.__dirty = False
        
    def is_present(self):
        '''
        returns True if the `resource` is present in the data `store`
        or False otherwise
        '''
        return self.session[self.store_key].is_present(self)
    
    formats = {'n3': 'text/rdf+n3',
                 'nt': 'text/plain',
                 'turtle':'application/turtle',
                 'xml':'application/rdf+xml',
    }
    
    def load_from_source(self,data=None,file=None,location=None,format=None):
        '''
        load the `resource` from a source (uri, file or string rdf data)
        '''
        graph = ConjunctiveGraph()
        if format is None:
            format = 'application/rdf+xml'
        elif format in self.formats:
            format = self.formats[format]
        graph.parse(data=data,file=file,location=location,format=format)
        self.set(graph)
    
    def set(self, graph):
        '''
        load the `resource` from a `graph`. The `graph` must be a `rdflib`
        `ConjunctiveGraph` or `Graph`
        
        note: currently the method does not support *lazy loading* as `load` does
        '''
        #TODO: must make this __lazy ... see how
        attrs = {}
        for s,p,o in graph:
            attr_name = None
            value = None
            if str(s) == str(self.subject):
                attr_name = rdf2attr(p,True)
                #value = self.__lazy([o])
                value = o
            elif str(o) == str(self.subject):
                attr_name = rdf2attr(p,False)
                #value = self.__lazy([s])
                value = s
                
            if attr_name:
                if attr_name not in attrs:
                    attrs[attr_name] = value
                elif attr_name in attrs and type(attrs[attr_name]) is not list:
                    attrs[attr_name] = [attrs[attr_name]]
                    attrs[attr_name].append(value)
                else:
                    attrs[attr_name].append(value)
            
        for attr_name in attrs:
            setattr(self,attr_name,attrs[attr_name])
        
    @classmethod
    def namespace(cls):
        '''
        returns the `namespace` of the currenlt Resources class type
        '''
        if cls.uri:
            return namespace_split(cls.uri)[0]
        return None
        
    @classmethod
    def concept(cls,subject,store=None):
        '''
        returns the Resources `concept` uri (type)
        
        the `concept` is retrieved from the specified `store`, or
        from the internal `store` (if the resource was retrieved throug the `session`)
        else the `sessions` `default_store` is used to retrieve the `concept`
        '''
        store_k = store if store else cls.store_key
        store_k = store_k if store_k else cls.session.default_store_key
        return cls.session[store_k].concept(subject)
        
    @classmethod
    def rest_api(cls, resources_namespace):
        '''return a :class:`surf.rest.Rest` class responsible for exposing **REST** api
        functions for integration into REST aware web frameworks
        
        note: the REST api was modeled according to the `pylons` model but it is generic
        enough to eb used in other frameworks'''
        if cls.session:
            return Rest(resources_namespace, cls)
        raise Exeption('not a knwon resource (no concept uri), cannot expose REST api')
        
    def __ne__(self, other):
        '''the inverse of `__eq__` (see documentation)'''
        return not self.__eq__(other)

    def __eq__(self, other):
        '''returns True if the two `resources` have the same `subject` and are both
        of type `Resource`, False otherwise'''
        return self.subject == other.subject if isinstance(other, Resource) else False
    

    