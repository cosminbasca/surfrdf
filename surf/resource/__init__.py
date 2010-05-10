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

from surf.namespace import get_namespace_url, get_prefix, OWL, all
from surf.query import Query
from surf.rdf import BNode, ClosedNamespace, ConjunctiveGraph, Graph, Literal
from surf.rdf import Namespace, RDF, RDFS, URIRef
from surf.resource.value import ResourceValue
from surf.resource.result_proxy import ResultProxy
from surf.rest import Rest
from surf.serializer import to_json
from surf.store import NO_CONTEXT, Store
from surf.util import attr2rdf, namespace_split, rdf2attr
from surf.util import uri_to_class, uuid_subject, value_to_rdf

a = RDF.type
class ResourceMeta(type):
    def __new__(mcs, classname, bases, class_dict):
        ResourceClass = super(ResourceMeta, mcs).__new__(mcs, classname, bases, 
                                                         class_dict)
        
        if "uri" not in class_dict:
            ResourceClass.uri = None
            
        return ResourceClass

    def __getattr__(self, attr_name):
        """
        Find `instances` of the current Class that extends `Resource`,
        the `instances` are selected from the values of the specified
        predicate (`attr_name`).

        For now these are not persisted in the `Resource` class - next time
        the method is called the instances are retrieved from the `store` again.

        """

        if attr_name == "session":
            return None

        # Don't want to reimplement Resource.__getattr__.
        # Instantiate this class as instance of owl:Class and
        # proxy to its __getattr__.

        # If this method gets used often, we'll need to add caching
        # for self_as_instance.

        self_as_instance = self._instance(self.uri, [OWL.Class])
        return getattr(self_as_instance, attr_name)


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
        >>> resource.foaf_knows.one
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
    _dirty_instances = set()

    def __init__(self, subject = None, block_auto_load = False, context = None,
                 namespace = None):
        """ Initialize a Resource, with the `subject` (a URI - either a string 
        or a URIRef). 
        
        If ``subject`` is None than a unique subject will be 
        generated using the :func:`surf.util.uuid_subject` function. If 
        ``namespace`` is specified, generated subject will be in that 
        namespace.
                
        ``block_autoload`` will prevent the resource from autoloading all rdf 
        attributes associated with the subject of the resource.

        """
        
        if subject is None:
            subject = uuid_subject(namespace)
        elif not type(subject) in [URIRef, BNode]:
            subject = URIRef(subject)

        self.__subject = subject
        
        if context == NO_CONTEXT:
            self.__context = None
        elif context:
            self.__context = URIRef(str(context))
        elif self.session and self.store_key:
            self.__context = self.session[self.store_key].default_context
        
        self.__expired = False
        self.__rdf_direct = {}
        self.__rdf_direct[a] = [self.uri]
        self.__rdf_inverse = {}
        self.__namespaces = all()
        # __full is set to true after doing full load. This is used by
        # __getattr__ to decide if it's worth to query triplestore.
        self.__full = False

        if self.session:
            if not self.store_key:
                self.store_key = self.session.default_store_key

            if self.session.auto_load and not block_auto_load:
                self.load()

    subject = property(lambda self: self.__subject)
    """ The subject of the resource. """

    namespaces = property(fget = lambda self: self.__namespaces)
    """ The namespaces. """

    def set_dirty(self, dirty):
        if not isinstance(dirty, bool):
            raise ValueError('Value must be of type bool not <%s>' % type(dirty))

        # Setting dirty to "True" means: 
        # adding this instance to "dirty_instances" set
        if dirty and not self in self._dirty_instances:
            self._dirty_instances.add(self)
            
        # Setting dirty to "False" means: 
        # removing this instance from "dirty_instances" set
        if not dirty and self in self._dirty_instances:
            self._dirty_instances.remove(self)

    def get_dirty(self):
        return self in self._dirty_instances

    dirty = property(fget = get_dirty, fset = set_dirty)
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
    
    @classmethod
    def _instance(cls, subject, vals, context = None, store = None):
        """
        Create an instance from the `subject` and it's associated
        `concept` (`vals`) URIs.

        Only the first `concept` URI is considered for inheritance.

        """

        # vals is list of rdf:type URIs for this instance.
        # If there are none, don't instantiate Resource, return URIRef. 
        if not vals:
            return subject
            
        # Don't have reference to session, cannot instantiate Resource
        if not cls.session:
            return None
            
        uri = vals[0]
        classes = map(uri_to_class, vals[1:])

        return cls.session.map_instance(uri, subject, classes = classes,
                                        block_auto_load = True,
                                        context = context,
                                        store = store)    

    @classmethod
    def _lazy(cls, value):
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
            elif type(r) in [URIRef, BNode]:
                inst = cls._instance(r, value[r])
            attr_value.append(inst)
        return attr_value

    def bind_namespaces(self, *namespaces):
        """ Bind the `namespace` to the `resource`.

        Useful for pretty serialization of the resource.

        """

        for ns in namespaces:
            if type(ns) in [str, unicode]:
                self.__namespaces[ns] = get_namespace_url(ns)
            elif type(ns) in [Namespace, ClosedNamespace]:
                self.__namespaces[get_prefix(ns)] = ns

    def bind_namespaces_to_graph(self, graph):
        """ Bind the 'resources' registered namespaces to the supplied `graph`.

        """
        
        if graph is not None:
            for prefix in self.namespaces:
                graph.namespace_manager.bind(prefix, self.namespaces[prefix])

    @classmethod
    def get_dirty_instances(cls):
        """
        Return all the unsaved (dirty) `instances` of type `Resource`.
        """

        return cls._dirty_instances

    @classmethod
    def to_rdf(cls, value):
        """ Convert any value to it's appropriate `rdflib` construct. """

        if hasattr(value, 'subject'):
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

        def make_values_source(values, rdf_values):
            """ Return callable that returns stored values for this attr. """
            
            def setattr_values_source():
                """ Return stored values for this attribute. """

                return values, rdf_values

            return setattr_values_source

        predicate, direct = attr2rdf(name)
        if predicate:
            rdf_dict = direct and self.__rdf_direct or self.__rdf_inverse
            if not isinstance(value, list):
                value = [value]
            rdf_dict[predicate] = []
            rdf_dict[predicate].extend([self.to_rdf(val) for val in value])
            self.dirty = True

            if type(value) is ResourceValue:
                pass
            else:
                if type(value) not in [list, tuple]: 
                    value = [value]
                    
                value = map(value_to_rdf, value)
                values_source = make_values_source(value, rdf_dict[predicate])
                value = ResourceValue(values_source, self, name)

        object.__setattr__(self, name, value)

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
            rdf_dict = direct and self.__rdf_direct or self.__rdf_inverse
            rdf_dict[predicate] = []
            self.dirty = True
        object.__delattr__(self, attr_name)

    # TODO: reuse already existing instances - CACHED
    # TODO: shoud we raise an error when predicate not foud ? or just return 
    # an empty list ? hmmm --- error :]
    def __getattr__(self, attr_name):
        """ Retrieve and cache attribute values.

        If attribute name is not in the "ns_predicate" form, an
        `AttributeError` will be raised.


        This method has no impact on the *dirty* state of the object.

        """

        predicate, direct = attr2rdf(attr_name)
        if not predicate:
            raise AttributeError('Not a predicate: %s' % attr_name)

        # Closure for lazy execution.
        def make_values_source(resource, predicate, direct, do_query):
            """ Return callable that loads and returns values. """

            def getattr_values_source():
                """ Load and return values for this attribute. """
                
                if do_query:
                    store = resource.session[resource.store_key]
                    # Request to triple store
                    values = store.get(resource, predicate, direct)
                    # Instantiate SuRF objects
                    surf_values = resource._lazy(values)
                else:
                    surf_values = []


                # Select triple dictionary for synchronization
                if direct:
                    rdf_dict = resource.__rdf_direct
                else:
                    rdf_dict = resource.__rdf_inverse

                # Initial synchronization
                rdf_dict[predicate] = [resource.to_rdf(value) for value in surf_values]

                return surf_values, rdf_dict[predicate]

            return getattr_values_source

        # If resource is fully loaded and still we're here
        # at __getattr__, this must be an empty attribute, so
        # no point querying triple store.
        do_query = not self.__full
        values_source = make_values_source(self, predicate, direct, do_query)

        attr_value = ResourceValue(values_source, self, attr_name)

        # Not using self.__setattr__, that would trigger loading of attributes
        object.__setattr__(self, attr_name, attr_value)
        self.dirty = False

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
        self.__set_predicate_values(results_d, True)
        self.__set_predicate_values(results_i, False)
        self.dirty = False
        self.__full = True

    def __set_predicate_values(self, results, direct):
        """ set the prediate - value(s) to the resource using lazy loading,
        `results` is a dict under the form:
        {'predicate':{'value':[concept,concept],...},...}.

        """

        for p, v in results.items():
            attr = rdf2attr(p, direct)
            value = self._lazy(v)
            if value:
                self.__setattr__(attr, value)


    @classmethod
    def get_by_attribute(cls, attributes, context = None):
        """
        Retrieve all `instances` from the data store that have the specified `attributes`
        and are of `rdf:type` of the resource class

        """

        direct_attributes = []
        inverse_attributes = []
        attribute_uris = [inverse_attributes, direct_attributes]
        for attribute_name in attributes:
            attribute_uri, direct = attr2rdf(attribute_name)
            # Using boolean as array index.
            attribute_uris[direct].append(attribute_uri)

        subjects = {}
        subjects.update(cls.session[cls.store_key].instances_by_attribute(cls, direct_attributes, True, context))
        subjects.update(cls.session[cls.store_key].instances_by_attribute(cls, inverse_attributes, False, context))
        
        instances = []
        for s, types in subjects.items():
            if not isinstance(s, URIRef):
                continue

            if cls.uri:
                concepts = [cls.uri]
            else:
                concepts = types

            instances.append(cls._instance(s, concepts))
        
        return instances

    @classmethod
    def __instancemaker(cls, params, instance_data):
        """ Construct resource from `instance_data`, return it. """

        subject, data = instance_data
        # subject is either URIRef/BNode or Literal and we don't try to turn
        # literals into SuRF Resources
        if not (isinstance(subject, URIRef) or isinstance(subject, BNode)):
            return subject

        rdf_type = None
        # Let's see if rdf:type was specified in query parameters
        for predicate, value, _ in params.get("get_by", []):
            if predicate == a:
                rdf_type = value
                break

        # In results?
        if not rdf_type and "direct" in data and a in data["direct"]:
            rdf_type = data["direct"][a].keys()[0]

        if rdf_type is None:
            # We don't know rdf:type, so cannot instantiate Resource,
            # return URIRef instead
            return subject

        context = params.get("context", None)
        instance = cls._instance(subject,
                                 [rdf_type],
                                 context = context,
                                 store = cls.store_key)

        instance.__set_predicate_values(data.get("direct", {}), True)
        instance.__set_predicate_values(data.get("inverse", {}), False)
        instance.__full = bool(params.get("full"))
        # __setattr__ marked it as dirty but it's freshly loaded!
        instance.dirty = False 

        return instance

    @classmethod
    def all(cls):
        """ Retrieve all or limited number of `instances`. """

        if not hasattr(cls, 'uri') or cls == Resource:
            return []

        store = cls.session[cls.store_key]
        proxy = ResultProxy(store = store,
                            instancemaker = cls.__instancemaker)

        return proxy.get_by(rdf_type = cls.uri)

    @classmethod
    def get_by(cls, **filters):
        """ Retrieve all instances that match specified filters and class.

        Filters are specified as keyword arguments, argument names follow SuRF
        naming convention (they take form `namespace_name`).

        Example::

            >>> Person = session.get_class(surf.ns.FOAF['Person'])
            >>> johns = Person.get_by(foaf_name = u"John")

        """

        if not hasattr(cls, "uri") or cls == Resource:
            return []

        store = cls.session[cls.store_key]
        filters = filters.copy()
        filters["rdf_type"] = cls.uri
        proxy = ResultProxy(store = store,
                            instancemaker = cls.__instancemaker)

        return proxy.get_by(**filters)

    def query_attribute(self, attribute_name):
        """ Return ResultProxy for querying attribute values. """

        # If we want to get john.foaf_knows values, we have to formulate
        # query like friends = get_by(is_foaf_knows_of = john), thus the
        # attribute name inversion
        uri, direct = attr2rdf(attribute_name)
        inverse_attribute_name = str(rdf2attr(uri, not direct))

        store = self.session[self.store_key]
        proxy = ResultProxy(store = store,
                            instancemaker = self.__instancemaker)

        kwargs = {inverse_attribute_name : self.subject}
        return proxy.get_by(**kwargs)

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

        graph = self.graph(direct = direct)
        if format == 'json':
            return to_json(graph)
        return graph.serialize(format = format)

    def graph(self, direct = True):
        """
        Return an `rdflib` `ConjunctiveGraph` represenation of the current `resource`

        """

        graph = ConjunctiveGraph()
        self.bind_namespaces_to_graph(graph)
        graph.add((self.subject, RDF['type'], self.uri))
        for predicate in self.__rdf_direct:
            for value in self.__rdf_direct[predicate]:
                if type(value) in [URIRef, Literal, BNode]:
                    graph.add((self.subject, predicate, value))
        if not direct:
            for predicate in self.__rdf_inverse:
                for value in self.__rdf_inverse[predicate]:
                    if type(value) in [URIRef, Literal, BNode]:
                        graph.add((value, predicate, self.subject))
        return graph

    def __str__(self):
        """ Return `string` representation of the resource. """

        return '{%s : %s}' % (unicode(self.subject), unicode(self.uri))

    def save(self):
        """ Save the `resource` to the data `store`. """

        self.session[self.store_key].save(self)

    def remove(self, inverse = False):
        """ Remove the `resource` from the data `store`. """

        self.session[self.store_key].remove(self, inverse = inverse)

    def update(self):
        """ Update the resource in the data `store`.

        This method does not remove other triples
        related to it (the inverse triples of type <s',p,s>, where s is the
        `subject` of the `resource`)

        """

        self.session[self.store_key].update(self)

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
        graph.parse(data = data, file = file, location = location, format = format)
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
        for s, p, o in graph:
            attr_name = None
            value = None
            if str(s) == str(self.subject):
                attr_name = rdf2attr(p, True)
                #value = self.__lazy([o])
                value = o
            elif str(o) == str(self.subject):
                attr_name = rdf2attr(p, False)
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
            setattr(self, attr_name, attrs[attr_name])

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

        if store is None:
            if cls.store_key is None:
                store = cls.session.default_store_key
            else:
                store = cls.store_key

        return cls.session[store].concept(subject)

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
        
        if isinstance(other, Resource):
            return self.subject == other.subject

        return False
