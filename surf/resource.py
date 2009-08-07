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
from rdf.term import URIRef, Literal, BNode, RDF, RDFS, XSD
from rdf.namespace import Namespace, ClosedNamespace
from rdf.graph import Graph, ConjunctiveGraph
from namespace import *
from surf.query import Query
from surf.store import Store
import util
import serializer
from weakref import WeakKeyDictionary
from datetime import datetime, date, time

__all__ = ['Resource', 'ResourceMeta']

a = RDF['type']

'''
the Resource
'''
class ResourceMeta(type):
    def __new__(meta,classname,bases,class_dict):
        ResourceClass = super(ResourceMeta,meta).__new__(meta,classname,bases,class_dict)
        if 'uri' not in class_dict:
            ResourceClass.uri = None
        ResourceClass._instance = meta._instance
        ResourceClass._lazy = meta._lazy
        return ResourceClass
    
    def __init__(self,*args,**kwargs):
        pass
    
    @classmethod
    def _instance(cls,subject,vals):
        if cls.session:
            uri = vals[0] if len(vals) > 0 else None
            classes = map(util.uri_to_class,vals[1:]) if len(vals) > 1 else []
            return cls.session.map_instance(uri,subject,classes=classes,block_outo_load=True) if uri else subject
        else:
            return None
    
    @classmethod
    def _lazy(cls,value):
        '''
        does lazy instantiation of rdf predicates
        value is a dictionary {val:[concept,concept,...]}
        '''        
        attr_value = []
        for r in value:
            inst = r
            if isinstance(value[r], Resource) :
                inst = value[r]
            elif type(r) is URIRef:
                inst = cls._instance(r, value[r])
            attr_value.append(inst)
        
        if len(attr_value) == 0:
            return None
        elif len(attr_value) == 1:
            return attr_value[0]
        return attr_value
    
    def __getattr__(self,attr_name):
        #TODO: add persistence at metaclass level
        value = None
        predicate, direct = util.attr2rdf(attr_name)
        if predicate:
            instances = self.session[self.store_key].instances_by_value(self,direct,[predicate])
            value = self._lazy(instances)
            if value or (type(value) is list and len(value) > 0):
                pass
            else:
                value = None
        return value
    
#TODO: add context to resource --- resources reside in different contexts
class Resource(object):
    '''
    The Resource class, represents the transparent proxy object that exposes sets of
    RDF triples under the form of <s,p,o> and <s',p,s> as an object in python,
    one can create resource directly by instantiating this class, but it is advisable
    to use the session to do so, as the session will create subclasses of Resource based
    on the subjects rdf:type
    '''
    __metaclass__ = ResourceMeta
    _instances = WeakKeyDictionary()
    
    def __init__(self,subject,block_outo_load=False):
        '''
        initializes a Resource, with the subject (a URI - either a string or a URIRef),
        block_autoload will prevent the resource from autoloading all rdf attributes associated
        with the subject of the resource
        '''
        self.__subject = subject if type(subject) is URIRef else URIRef(subject)
        self.__dirty = False
        self._instances[self] = True
        self.__expired = False
        self.rdf_direct = {}
        self.rdf_direct[a] = [self.uri]
        self.rdf_inverse = {}
        self.__namespaces = {}
        if self.session:
            if not self.store_key: self.store_key = self.session.default_store_key
            if self.session.auto_load and not block_outo_load: self.load()
            
    '''the subject of the resource '''
    subject = property(lambda self: self.__subject)
    
    '''the namespaces'''
    namespaces = property(fget = lambda self: self.__namespaces)
    
    def bind_namespaces(self,*namespaces):
        for ns in namespaces:
            if type(ns) in [str,unicode]:
                self.__namespaces[ns] = get_namespace_url(ns)
            elif type(ns) in [Namespace, ClosedNamespace]:
                self.__namespaces[get_prefix(ns)] = ns
                
    def bind_namespaces_to_graph(self,graph):
        if graph:
            for prefix in self.namespaces:
                graph.namespace_manager.bind(prefix, self.namespaces[prefix])
    
    @classmethod
    def instances(cls):
        '''
        returns all the instances of type Resource currently available in memory
        '''
        return cls._instances.keys()
        
    @classmethod
    def instance(cls,subject):
        '''
        returns the Resource instance currently in memory with the specified subject
        '''
        for i in cls._instances:
            if i.subject == subject:
                return i
        return None
        
    def is_dirty(self):
        '''
        True if the resource has been modified during runtime and not persisted, False
        otherwise
        '''
        return self.__dirty
    
    def __val2rdf(self,value):
        '''
        for internal use, converts the value to an RDFLib compatible type if appropriate
        '''
        if type(value) in [str, unicode, basestring, float, int, long, bool, datetime, date, time]:
            return Literal(value)
        elif type(value) in [list, tuple]:
            language = value[1] if len(value) > 1 else None
            datatype = value[2] if len(value) > 2 else None
            return Literal(value[0],language=language,datatype=datatype)
        elif type(value) is dict:
            val = value['value'] if 'value' in value else None
            language = value['language'] if 'language' in value else None
            datatype = value['datatype'] if 'datatype' in value else None
            if val:
                return Literal(val,language=language,datatype=datatype)
            return value
        elif hasattr(value,'subject'):
            return value.subject
        return value
        
    def __setattr__(self,name,value):
        object.__setattr__(self,name,value)
        predicate, direct = util.attr2rdf(name)
        if predicate:
            value = value if type(value) in [list, tuple] else [value]
            value = map(lambda val: Literal(val,datatype=XSD['string']) if type(val) in [str,unicode] else val,value)
            
            rdf_dict = self.rdf_direct if direct else self.rdf_inverse
            rdf_dict[predicate] = []
            rdf_dict[predicate].extend([val.subject if hasattr(val,'subject') else val for val in value])
            self.__dirty = True
            #TODO: add the auto_persist feature...
            
    def __delattr__(self,attr_name):
        predicate, direct = util.attr2rdf(attr_name)
        if predicate:
            value = self.__getattr__(attr_name)
            value = value if type(value) is list else [value]
            
            rdf_dict = self.rdf_direct if direct else self.rdf_inverse
            rdf_dict[predicate] = []
            self.__dirty = True
            #TODO: add the auto_persist feature...
            
        object.__delattr__(self,attr_name)
    
    def __getattr__(self,attr_name):
        value = None
        predicate, direct = util.attr2rdf(attr_name)
        if predicate:
            values = self.session[self.store_key].get(self,predicate,direct)
            # TODO: reuse already existing instances - CACHED
            value =  self._lazy(values)
            if value or (type(value) is list and len(value) > 0):
                self.__setattr__(attr_name,value)
            else:
                value = None
        return value

    def load(self):
        '''
        loads all attributes from the data store, both direct attributes (where the subject
        is the subject of the resource) and indirect attributes (where the object is the subject
        of the resource)
        '''
        def update(results,direct):
            for p,v in results.items():
                attr = util.rdf2attr(p,direct)
                value = self._lazy(v)
                if value or (type(value) is list and len(value) > 0):
                    self.__setattr__(attr,value)
                
        results_d = self.session[self.store_key].load(self,True)
        results_i = self.session[self.store_key].load(self,False)
        update(results_d,True)
        update(results_i,False)
        self.__dirty = False

    @classmethod
    def get_by_attribute(cls,*attributes):
        '''
        retrieves all resources from the data store that have the specified attributes
        and have the type of the class
        '''
        subjects = {}
        subjects.update(cls.session[cls.store_key].instances_by_attribute(self,attributes,True))
        subjects.update(cls.session[cls.store_key].instances_by_attribute(self,attributes,False))
        instances = []
        for s, types in subjects.items():
            if type(s) is URIRef:
                instances.append(cls._instance(s,[cls.uri] if cls.uri else types))
        return instances if len(instances) > 0 else []
        
    @classmethod
    def all(cls,offset=None,limit=None):
        '''
        retrieves all (or just a limited number from the specified offset) resources
        that are of the specified type as the resource class
        '''
        if hasattr(cls,'uri'):
            subjects = [] if cls == Resource else cls.session[cls.store_key].all(cls,limit=limit,offset=offset)
            if subjects:
                return [cls(subject) for subject in subjects]
            return []
        return []
        
    @classmethod
    def __get(cls,filter,*objects,**symbols):
        predicates_d = {}
        predicates_d.update( [(util.attr2rdf(name)[0],symbols[name]) for name in symbols if util.is_attr_direct(name)])
        predicates_i = {}
        predicates_i.update( [(util.attr2rdf(name)[0],symbols[name]) for name in symbols if not util.is_attr_direct(name)])
        
        subjects = {}
        if len(symbols) > 0:
            if len(predicates_d) > 0:
                subjects.update( cls.session[cls.store_key].instances(self,True,filter,predicates_d) )
            if len(predicates_i) > 0:
                subjects.update( cls.session[cls.store_key].instances(self,False,filter,predicates_i) )
        
        #if len(objects) > 0:
        #    subjects.update(cls.store().o(True,cls.uri(),filter,objects))
        #    subjects.update(cls.store().o(False,cls.uri(),filter,objects))
        
        instances = []
        for s, types in subjects.items():
            if type(s) is URIRef:
                instances.append(cls._instance(s,[cls.uri] if cls.uri else types))
        return instances if len(instances) > 0 else []
        
    @classmethod
    def get_by(cls,*objects,**symbols):
        '''
        retrieves all resources that have attribute value pairs as specified
        '''
        return cls.__get(None,*objects,**symbols)
    
    @classmethod
    def get_like(cls,*objects,**symbols):
        '''
        retrieves all resources that have attribute value pairs, with support for regex
        matching on values, currently reges is slow, try to avoid
        '''
        return cls.__get('regex',*objects,**symbols)
    
    def serialize(self,format='xml',direct=False):
        '''
        returns a serialized version of the internal graph represenatation
        of the resource, the format is the same as expected by rdflib's graph
        serialize method
        '''
        graph = self.graph(direct=direct)
        if format == 'json':
            return serializer.to_json(graph)
        return graph.serialize(format=format)
        
    def graph(self,direct=True):
        '''
        returns an RDFLib ConjunctiveGraph represenation of the current resource
        '''
        graph = ConjunctiveGraph()
        self.bind_namespaces_to_graph(graph)
        graph.add((self.subject,RDF['type'],self.uri))
        for predicate in self.rdf_direct:
            for value in self.rdf_direct[predicate]:
                graph.add((self.subject,predicate,value))
        if not direct:
            for predicate in self.rdf_inverse:
                for value in self.rdf_inverse[predicate]:
                    graph.add((value,predicate,self.subject))
        return graph
        
    def __str__(self):
        return '{%s : %s}'%(unicode(self.subject),unicode(self.uri))
    
    def save(self):
        '''
        saves the resource to the data store, replacing the representation with
        the current one
        '''
        self.session[self.store_key].save(self)
        self.__dirty = False
    
    def remove(self):
        '''
        remove the resource from the store
        '''
        self.session[self.store_key].remove(self)
        self.__dirty = False
        
    def update(self):
        '''
        update the resource in the store, does not remove other triples
        related to it
        '''
        self.session[self.store_key].update(self)
        self.__dirty = False
        
    def is_present(self):
        '''
        returns True if the resource is present in the Store or False otherwise
        '''
        return self.session[self.store_key].is_present(self)
    
    formats = {'n3': 'text/rdf+n3',
                 'nt': 'text/plain',
                 'turtle':'application/turtle',
                 'xml':'application/rdf+xml',
    }
    
    def load_from_source(self,data=None,file=None,location=None,format=None):
        '''
        load the resource from a source (uri, file or string rdf data)
        '''
        graph = ConjunctiveGraph()
        if format is None:
            format = 'application/rdf+xml'
        elif format in self.formats:
            format = self.formats[format]
        graph.parse(data=data,file=file,location=location,format=format)
        self.set(graph)
    
    def set(self, graph):
        #TODO: must make this __lazy ... see how
        '''
        sets a resource from the supplied graph
        '''
        # add properties to the resource from the graph
        attrs = {}
        for s,p,o in graph:
            attr_name = None
            value = None
            if str(s) == str(self.subject):
                attr_name = util.rdf2attr(p,True)
                #value = self.__lazy([o])
                value = o
            elif str(o) == str(self.subject):
                attr_name = util.rdf2attr(p,False)
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
        returns the namespace of the Resources type
        '''
        if cls.uri:
            return util.namespace_split(cls.uri)[0]
        return None
        
    @classmethod
    def concept(cls,subject,store=None):
        '''
        returns the Resources Concept uri (type)
        '''
        store_k = store if store else cls.store_key
        store_k = store_k if store_k else cls.session.default_store_key
        return cls.session[store_k].concept(subject)
        
    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        return self.subject == other.subject if isinstance(other, Resource) else False
    