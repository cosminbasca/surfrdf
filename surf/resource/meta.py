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
from surf.util import *
from surf.rest import *
from surf import serializer
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
    def _instance(cls,subject,vals):
        '''
        creates an instance from the `subject` and it's associated `concept` (`vals`) uri's
        only the first `concept` uri is considered for inheritance
        '''
        if cls.session:
            uri = vals[0] if len(vals) > 0 else None
            classes = map(uri_to_class,vals[1:]) if len(vals) > 1 else []
            return cls.session.map_instance(uri,subject,classes=classes,block_outo_load=True) if uri else subject
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
        
        #if len(attr_value) == 0:
        #    return None
        #elif len(attr_value) == 1:
        #    return attr_value[0]
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