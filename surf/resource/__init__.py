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
from surf.resource.result_proxy import ResultProxy
from surf.util import *
from surf.rest import *
from surf.serializer import to_json
from weakref import WeakKeyDictionary

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
        """
        Create an instance from the `subject` and it's associated `concept` (`vals`) uri's
        only the first `concept` uri is considered for inheritance
        
        """
        
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
        """
        Do `lazy` instantiation of rdf predicates
        value is a dictionary {val:[concept,concept,...]},
        returns a instance of `Resource`.
        
        """
                
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
        """
        Find `instances` of the current Class that extends `Resource`,
        the `instances` are selected from the values of the specified 
        predicate (`attr_name`).
        
        For now these are not persisted in the `Resource` class - next time 
        the method is called the instances are retrieved from the `store` again.
        
        """
        
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
    """
    The Resource class, represents the transparent proxy object that exposes 
    sets of RDF triples under the form of <s,p,o> and <s',p,s> as an object 
    in python.
    
    One can create resource directly by instantiating this class, but it is 
    advisable to use the session to do so, as the session will create 
    subclasses of Resource based on the <s,rdf:type,`concept`> pattern.
    
    Triples that constitute a resource can be accessed via Resource instance
    attributes. SuRF uses the following naming convention for attribute names:
    *nsprefix_predicate*. Attribute name examples: "rdfs_label", "foaf_name",
    "owl_Class".
    
    Resource instance attributes can be set and get. If get, they will 
    be structures of type :class:`ResourceValue`. This class is subclass of 
    `list` (to handle situations when there are several triples with the
    same subject and predicate but different objects) and have some some 
    special features. Since `ResourceValue` is subtype of list, it can be
    iterated, sliced etc.
    
    :meth:`ResourceValue.first` will return first element of list or `None`
    if list is empty::
    
        >>> resource.foaf_knows = [URIRef("http://p1"), URIRef("http://p2")]
        >>> resource.foaf_knows.first
        rdflib.URIRef('http://p1')

    :meth:`ResourceValue.one` will return first element of list or will
    raise if list is empty or has more than one element::
    
    
        >>> resource.foaf_knows = [URIRef("http://p1"), URIRef("http://p2")]
        >>>resource.foaf_knows.one
        Traceback (most recent call last):
            ....
        Exception: list has more elements than one
    
    When setting resource attribute, it will accept about anything and 
    translate it to `ResourceValue`. Attribute can be set to instance 
    of `URIRef`::
    
        >>> resource.foaf_knows = URIRef("http://p1")
        >>> resource.foaf_knows
        [rdflib.URIRef('http://p1')]
        
    Attribute can be set to list or tuple::
    
        >>> resource.foaf_knows = (URIRef("http://p1"), URIRef("http://p2")) 
        >>> resource.foaf_knows
        [rdflib.Literal(u'http://p1', lang=rdflib.URIRef('http://p2'))]
        
    Attribute can be set to string, integer, these will be converted into
    instances of `Literal`::
    
        >>> resource.foaf_name = "John"
        >>> resource.foaf_name
        [rdflib.Literal(u'John')]
        
    Attribute can be set to another SuRF resource. Values of different types
    can be mixed::
    
        >>> resource.foaf_knows = (URIRef("http://p1"), another_resource) 
        >>> resource.foaf_knows
        [rdflib.URIRef('http://p1'), <surf.session.FoafPerson object at 0xad049cc>]
    
    """
    
    __metaclass__ = ResourceMeta
    _instances = WeakKeyDictionary()
    
    def __init__(self, subject = None, block_outo_load = False, context = None):
        """ Initialize a Resource, with the `subject` (a URI - either a string or a URIRef),
        if the `subject` is None than a unique subject will be generated using the
        :func:`surf.util.uuid_subject` method
        `block_autoload` will prevent the resource from autoloading all rdf attributes associated
        with the subject of the resource.
        
        """
        
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
    """ The subject of the resource. """
    
    namespaces = property(fget = lambda self: self.__namespaces)
    """ The namespaces. """
    
    def set_dirty(self, dirty):
        if type(dirty) is bool:
            self.__dirty = dirty
        else:
            raise ValueError('Value must be of type bool not <%s>'%type(dirty))
    dirty = property(fget = lambda self: self.__dirty, fset = set_dirty)
    """ Reflects the `dirty` state of the resource. """
    
    rdf_direct = property(fget = lambda self: self.__rdf_direct)
    """ Direct predicates (`outgoing` predicates). """
    
    rdf_inverse = property(fget = lambda self: self.__rdf_inverse)
    """ Inverse predicates (`incoming` predicates). """

    def __set_context(self, value):
        if not isinstance(value, URIRef):
            value = URIRef(value)
        
        self.__context = value
    
    context = property(fget = lambda self: self.__context,
                       fset = __set_context)
    """ Context (graph) where triples constituting this resource reside in. 
    
    In case of SPARQL and SPARUL, "context" is the same thing as "graph".  
    
    Effects of having context set:
     - When resource as whole or its individual attributes are loaded, 
       triples will be only loaded from this context.
     - When resource is saved, triples will be saved to this context.
     - When existence of resource is checked (:meth:`is_present`), only
       triples in this context will be considered. 
    
    `context` attribute would be usually set by `store` or `session` when
    instantiating resource, but it can also be set or changed on
    already instantiated resource. Here is an inefficient but workable example
    of how to move resource from one context to another::
    
        Person = surf.ns.FOAF["Person"]
        john_uri = "http://example/john"
        
        old_graph_uri = URIRef("http://example/old_graph")
        new_graph_uri = URIRef("http://example/new_graph")
        
        instance = session.get_resource(john_uri, Person, old_graph_uri) 
        instance.context = new_graph_uri
        instance.save()

        # Now john is saved in the new graph but we still have to delete it
        # from the old graph.
        
        instance = session.get_resource(john_uri, Person, old_graph_uri) 
        instance.remove()
         
    """ 
    
    def bind_namespaces(self, *namespaces):
        """ Bind the `namespace` to the `resource`.
        
        Useful for pretty serialization of the resource.
        
        """
        
        for ns in namespaces:
            if type(ns) in [str,unicode]:
                self.__namespaces[ns] = get_namespace_url(ns)
            elif type(ns) in [Namespace, ClosedNamespace]:
                self.__namespaces[get_prefix(ns)] = ns
                
    def bind_namespaces_to_graph(self, graph):
        """ Bind the 'resources' registered namespaces to the supplied `graph`.
        
        """

        if graph:
            for prefix in self.namespaces:
                graph.namespace_manager.bind(prefix, self.namespaces[prefix])
    
    @classmethod
    def instances(cls):
        """
        Return all the `instances` of type `Resource` currently available in memory
        """
        
        return cls._instances.keys()
        
    @classmethod
    def instance(cls, subject):
        """
        Return the `Resource` `instance` currently in memory with the specified subject
        """
        
        for i in cls._instances:
            if i.subject == subject:
                return i
        return None
    
    @classmethod
    def to_rdf(cls, value):
        """ Convert any value to it's appropriate `rdflib` construct. """
        
        if type(value) is ResourceMeta:
            return value.uri
        elif hasattr(value, 'subject'):
            return value.subject
        return value_to_rdf(value)
    
    #TODO: add the auto_persist feature...
    def __setattr__(self, name, value):
        """
        The `set` method - responsible for *caching* the `value` to the 
        corresponding object attribute given by `name`.
        
        .. note: This method sets the state of the resource to *dirty* 
        (the `resource` will be persisted if the `commit` `session` method 
        is called).
        
        """
        
        predicate, direct = attr2rdf(name)
        if predicate:
            rdf_dict = self.__rdf_direct if direct else self.__rdf_inverse
            if not isinstance(value, list):
                value = [value]
            rdf_dict[predicate] = []
            rdf_dict[predicate].extend([self.to_rdf(val) for val in value])
            self.__dirty = True
            
            if type(value) is ResourceValue:
                pass
            else:
                if type(value) not in [list, tuple]: value = [value]
                value = map(value_to_rdf,value)
                value = ResourceValue(value, self, rdf_dict[predicate])
                
        object.__setattr__(self,name,value)
            
    #TODO: add the auto_persist feature...
    def __delattr__(self, attr_name):
        """
        The `del` method - responsible for deleting the attribute of the object given
        by `attr_name`
        
        .. note:: This method sets the state of the resource to *dirty* 
                  (the `resource` will be persisted if the `commit` `session` 
                  method is called)
        
        """
        
        predicate, direct = attr2rdf(attr_name)
        if predicate:
            #value = self.__getattr__(attr_name)
            rdf_dict = self.__rdf_direct if direct else self.__rdf_inverse
            rdf_dict[predicate] = []
            self.__dirty = True
        object.__delattr__(self,attr_name)
    
    # TODO: reuse already existing instances - CACHED
    # TODO: shoud we raise an error when predicate not foud ? or just return an empty list ? hmmm --- error :]
    def __getattr__(self, attr_name):
        """
        The `get` method - responsible for retrieving and caching using 
        `__setattr__` the value(s) of the specified `attr_name` 
        (object attribute).
        
        This method has no impact on the *dirty* state of the object.
        
        """
        
        attr_value = None
        predicate, direct = attr2rdf(attr_name)
        if predicate:
            values = self.session[self.store_key].get(self, predicate, direct)
            surf_values = self._lazy(values)
            rdf_dict = self.__rdf_direct if direct else self.__rdf_inverse
            
            attr_value = ResourceValue(surf_values, self, 
                                       rdf_dict.get(predicate, {}))
            
            self.__setattr__(attr_name,attr_value)
            self.__dirty = False
        else:
            raise ValueError('not a predicate: %s'%(attr_name))
        return attr_value

    def load(self):
        """
        Load all attributes from the data store:
            - direct attributes (where the subject is the subject of the resource)
            - indirect attributes (where the object is the subject of the resource)
            
        .. note:: This method resets the *dirty* state of the object.
        
        """
        
        results_d = self.session[self.store_key].load(self, True)
        results_i = self.session[self.store_key].load(self, False)
        self.__set_predicate_values(results_d,True)
        self.__set_predicate_values(results_i,False)
        self.__dirty = False
        
    def __set_predicate_values(self, results, direct):
        """ set the prediate - value(s) to the resource using lazy loading,
        `results` is a dict under the form:
        {'predicate':{'value':[concept,concept],...},...}.
        
        """
        
        for p,v in results.items():
            attr = rdf2attr(p,direct)
            value = self._lazy(v)
            if value or (type(value) is list and len(value) > 0):
                self.__setattr__(attr,value)
    
        
    @classmethod
    def get_by_attribute(cls, attributes, context = None):
        """
        Retrieve all `instances` from the data store that have the specified `attributes`
        and are of `rdf:type` of the resource class
        
        """
        
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
        `instances` that are of the `rdf:type` as the resource class. Instances
        are returned in no particular order.
        
        If parameter ``full`` is present, returned instances will have
        direct attributes already loaded.
        
        """

        if not hasattr(cls, 'uri') or cls == Resource:
            return []
        
        store = cls.session[cls.store_key]
        
        def instancemaker(params, instance_data):
            subject, data = instance_data
            instance = cls(subject)    
            if "context" in params:
                instance.context = params["context"]

            instance.__set_predicate_values(data.get("direct", {}), True)
            instance.__set_predicate_values(data.get("inverse", {}), False)

            return instance
        
        proxy = ResultProxy(store = store, instancemaker = instancemaker)
        return proxy.get_by(rdf_type = cls.uri)
        
    @classmethod
    def __get(cls, filter, context, *objects, **symbols):
        """
        
        For *internal* use only! Retrieve `instances` of the `rdf:type` as 
        the resource class, that have triples that match the `attr_name:value` 
        pair specified using `**symbols`, the method also supports `filters`.
        
        """
        
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
        """ Retrieve all instances that match specified filters and class.
        
        Filters are specified as keyword arguments, argument names follow SuRF
        naming convention (they take form `namespace_name`).
        
        Example::
        
            >>> Person = session.get_class(surf.ns.FOAF['Person'])
            >>> johns = Person.get_by(foaf_name = u"John") 
        
        """
        
        return cls.__get(None, context, *objects, **symbols)
    
    @classmethod
    def get_like(cls, context = None, *objects, **symbols):
        """ Retrieve all `instances` that match specified regex. 
        
        .. note:: Currently regex is slow, try to avoid the use of this method.
        
        """
        
        return cls.__get('regex', context, *objects, **symbols)
    
    def serialize(self, format = 'xml', direct = False):
        """
        Return a serialized version of the internal graph represenatation
        of the resource, the format is the same as expected by rdflib's graph
        serialize method
        
        supported formats:
            - **n3**
            - **xml**
            - **json** (internal serializer)
            - **nt**
            - **turtle**
        
        """
        
        graph = self.graph(direct=direct)
        if format == 'json':
            return to_json(graph)
        return graph.serialize(format=format)
        
    def graph(self, direct=True):
        """
        Return an `rdflib` `ConjunctiveGraph` represenation of the current `resource`
        
        """
        
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
        """ Return `string` representation of the resource. """

        return '{%s : %s}'%(unicode(self.subject),unicode(self.uri))
    
    def save(self):
        """ Save the `resource` to the data `store`. """
        
        self.session[self.store_key].save(self)
        self.__dirty = False
        
    def remove(self):
        """ Remove the `resource` from the data `store`. """

        self.session[self.store_key].remove(self)
        self.__dirty = False
        
    def update(self):
        """ Update the resource in the data `store`.
        
        This method does not remove other triples
        related to it (the inverse triples of type <s',p,s>, where s is the
        `subject` of the `resource`)
        
        """
        
        self.session[self.store_key].update(self)
        self.__dirty = False
        
    def is_present(self):
        """ Return True if the `resource` is present in data `store`. 
        
        Resource is assumed to be present if there is at least one triple
        having ``subject`` of this resource as subject. 
        
        """  

        return self.session[self.store_key].is_present(self)
    
    formats = {'n3': 'text/rdf+n3',
                 'nt': 'text/plain',
                 'turtle':'application/turtle',
                 'xml':'application/rdf+xml',
    }
    
    def load_from_source(self, data = None, file = None, location = None,
                         format = None):
        """
        Load the `resource` from a source (uri, file or string rdf data).
        
        """
        
        graph = ConjunctiveGraph()
        if format is None:
            format = 'application/rdf+xml'
        elif format in self.formats:
            format = self.formats[format]
        graph.parse(data=data,file=file,location=location,format=format)
        self.set(graph)
    
    def set(self, graph):
        """        
        Load the `resource` from a `graph`. The `graph` must be a `rdflib`
        `ConjunctiveGraph` or `Graph`
        
        .. note: Currently the method does not support *lazy loading* 
                 as `load` does.
                 
        """
        
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
        """
        Return the `namespace` of the currenlt Resources class type.
        """
        
        if cls.uri:
            return namespace_split(cls.uri)[0]
        return None
        
    @classmethod
    def concept(cls, subject, store = None):
        """ Return the Resources `concept` uri (type).         
        
        If parameter ``store`` is specified, concept will be retrieved from
        there. If resource was retrieved via session, it contains reference
        to store it was retrieved from and this reference will be used.
        Otherwise, `sessions` `default_store` will be used to retrieve 
        the `concept`.
        
        """
        
        store_k = store if store else cls.store_key
        store_k = store_k if store_k else cls.session.default_store_key
        return cls.session[store_k].concept(subject)
        
    @classmethod
    def rest_api(cls, resources_namespace):
        """ Return a :class:`surf.rest.Rest` class responsible for exposing 
        **REST** api functions for integration into REST aware web frameworks.
        
        .. note:: The REST API was modeled according to the `pylons` model 
                  but it is generic enough to eb used in other frameworks.
        
        """
        
        if cls.session:
            return Rest(resources_namespace, cls)
        raise Exception("not a known resource (no concept uri), cannot expose REST api")
        
    def __ne__(self, other):
        """ The inverse of :meth:`__eq__`. """
        return not self.__eq__(other)

    def __eq__(self, other):
        """ Return True if the two `resources` have the same `subject` and
        are both of type `Resource`, False otherwise. 
        
        """
        
        return self.subject == other.subject if isinstance(other, Resource) else False
    
