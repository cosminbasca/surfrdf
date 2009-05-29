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
from rdf.graph import Graph, ConjunctiveGraph
from namespace import *
from surf.query import Query
from surf.store import Store
import util
import serializer
from weakref import WeakKeyDictionary

__all__ = ['Resource', 'ResourceMeta']

a = RDF['type']

'''
the queries used by Resource
'''

def qSP(s,p,direct):
    s, v = (s, '?v') if direct else ('?v', s)
    return Query.select().distinct('?v','?c').where(s,p,v).where('?v',a,'?c',optional=True)
    
def qS(s,direct):
    s, v = (s, '?v') if direct else ('?v', s)
    return Query.select().distinct('?p','?v','?c').where(s,'?p',v).where('?v',a,'?c',optional=True)

def qP_S(c,p,direct):
    q = Query.select().distinct('?s','?c')
    for i in range(len(p)):
        s, v = ('?s', '?v%d'%i) if direct else ('?v%d'%i, '?s')
        if type(p[i]) is URIRef:
            q.where(s,p[i],v)
    q.where('?s',a,'?c',optional=True)
    return q

def __literal(term):
    #TODO - this is sparql specific, it needs to be pushed to the query, the query object
    # must handle this by supporting a better unified model between the filters and the query
    if type(term) is Literal:
        return '"%s"@%s'%(term,term.language)
    elif type(term) in [list,tuple]:
        return '"%s"@%s'%(term[0],term[1])
    return '"%s"'%term

def qPO(c,direct,filter='',preds={}):
    q = Query.select().distinct('?s','?c')
    i = 0 
    for p, v in preds.items():
        s, v, f = ('?s', v, '') if direct else (v, '?s', '')
        if filter is 'regex':
            s, v, f = ('?s', '?v%d'%i, 'regex(?v%d,%s)'%(i,__literal(v))) if direct else (v, '?s', '')
        q.where(s,p,v,filter=f)
        i += 1    
    q.where('?s',a,'?c',optional=True)
    return q

def qP_V(c,direct,p=[]):
    q = Query.select().distinct('?v','?c')
    for i in range(len(p)):
        s, v= (c, '?v') if direct else ('?v', c)
        q.where(s,p[i],v)
    q.where('?v',a,'?c',optional=True)
    return q

'''
def qO(c,direct,filter='',preds=[]):
    q = Query.select().distinct('?s','?c')
    i = 0 
    for p in preds:
        s, v, f = ('?s', v, '') if direct else (v, '?s', '')
        if filter is 'regex':
            s, v, f = ('?s', '?v%d'%i, 'regex(?v%d,%s)'%(i,__literal(v))) if direct else (v, '?s', '')
        q.where(s,p,v,filter=f)
        i += 1    
    q.where('?s',a,'?c',optional=True)
    return q
'''

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
            classes = map(cls.session.uri_to_class,vals[1:]) if len(vals) > 1 else []
            return cls.session.map_instance(uri,subject,classes=classes,block_outo_load=True) if uri else Resource(subject,block_outo_load=True)
        else:
            return None
    
    @classmethod
    def _lazy(cls,value):
        '''
        does lazy instantiation of rdf predicates
        '''        
        attr_value = []
        for r in value:
            inst = cls._instance(r, value[r]) if type(r) is URIRef else r
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
            q = qP_V(self.uri,direct,[predicate])
            value = self._lazy(self.session.store.predicate_dict(q,'v','c'))
            if value or (type(value) is list and len(value) > 0):
                pass
            else:
                value = None
        return value
    
class Resource(object):
    '''
    the Resource class holds an internal GRAPH, the graph is not synchronized completly
    with the class, as it can be manipulated from outside, if so, the logic will break
    ... not nice, will have to implement this mechanism, but if used properly than
    the resource will behave :], ....
    '''
    __metaclass__ = ResourceMeta
    _instances = WeakKeyDictionary()
    
    def __init__(self,subject,block_outo_load=False):
        self.__subject = subject if type(subject) is URIRef else URIRef(subject)
        self.__graph = ConjunctiveGraph()
        self.__graph.add((self.subject,a,self.uri))
        self.__dirty = False
        self.__to_delete = []
        self._instances[self] = True
        if self.session and self.session.auto_load and not block_outo_load:
            self.load()
        
    subject = property(lambda self: self.__subject)
    graph = property(lambda self: self.__graph)
    
    @classmethod
    def instances(cls):
        return cls._instances.keys()
        
    def is_dirty(self):
        return self.__dirty
    
    def __val2rdf(self,value):
        if type(value) in [str, unicode]:
            return Literal(value)
        elif type(value) in [list, tuple]:
            language = value[1] if len(value) > 1 else None
            datatype = value[2] if len(value) > 2 else None
            return Literal(value[0],language=language,datatype=datatype)
        elif type(value) is dict:
            val = value['value'] if 'value' in value else None
            lang = value['language'] if 'language' in value else None
            datatype = value['datatype'] if 'datatype' in value else None
            if val:
                return Literal(val,language=language,datatype=datatype)
        #elif isinstance(value,Resource):
        elif hasattr(value,'subject'):
            return value.subject
        else:
            return value
    #========================
    #===   SET ATTR
    #========================
    def __setattr__(self,name,value):
        object.__setattr__(self,name,value)
        predicate, direct = util.attr2rdf(name)
        if predicate:
            value = value if type(value) in [list, tuple] else [value]
            value = map(lambda val: Literal(val,datatype=XSD['string']) if type(val) in [str,unicode] else val,value)
            
            self.__clear(predicate,direct)
            for v in value:
                s,p,o = (self.subject, predicate, self.__val2rdf(v))
                if not direct:
                    s,p,o = (self.__val2rdf(v), predicate, self.subject)
                
                self.__graph.add((s,p,o))
                if self.session.auto_persist:
                    self.session.store.add_triple(s,p,o)
                else:
                    self.__dirty = True
    
    def __clear(self,predicate,direct):
        S,P,O = (self.subject, predicate, None) if direct else (None, predicate, self.subject)
        self.__graph.remove((S,P,O))
        if self.session.auto_persist:
            self.session.store.remove_triple(s=S,p=P,o=O)
            
    #========================
    #===   DEL ATTR
    #========================
    def __delattr__(self,attr_name):
        predicate, direct = util.attr2rdf(attr_name)
        if predicate:
            value = self.__getattr__(attr_name)
            value = value if type(value) is list else [value]
            for v in value:
                s,p,o = (self.subject, predicate, self.__val2rdf(v))
                if not direct:
                    s,p,o = (self.__val2rdf(v), predicate, self.subject)
                
                self.graph.remove((s,p,o))
                if self.session.auto_persist:
                    self.session.store.remove_triple(s,p,o)
                else:
                    self.__to_delete.append((s,p,o))
                    self.__dirty = True
        
        object.__delattr__(self,attr_name)
    
    #========================
    #===   GET ATTR
    #========================
    def __getattr__(self,attr_name):
        value = None
        predicate, direct = util.attr2rdf(attr_name)
        if predicate:
            #print 'GET ',attr_name
            q = qSP(self.subject,predicate,direct)
            value = self._lazy(self.session.store.predicate_dict(q,'v','c'))
            if value or (type(value) is list and len(value) > 0):
                self.__setattr__(attr_name,value)
            else:
                value = None
        return value
        
    def load(self):
        def update(results,direct):
            for p,v in results.items():
                attr = util.rdf2attr(p,direct)
                value = self._lazy(v)
                #print 'FILL ',p,type(value)
                if value or (type(value) is list and len(value) > 0):
                    self.__setattr__(attr,value)
                
        direct_r = self.session.store.predicates_dict(qS(self.subject,True),'p','v','c')
        inverse_r = self.session.store.predicates_dict(qS(self.subject,False),'p','v','c')
        update(direct_r,True)
        update(inverse_r,False)
        self.__dirty = False

    @classmethod
    def get_by_attribute(cls,*attributes):
        subjects = {}
        subjects.update(cls.session.store.predicate_dict(qP_S(cls.uri,attributes,True),'s','c'))
        subjects.update(cls.session.store.predicate_dict(qP_S(cls.uri,attributes,False),'s','c'))
        instances = []
        for s, types in subjects.items():
            if type(s) is URIRef:
                instances.append(cls._instance(s,[cls.uri] if cls.uri else types))
        return instances if len(instances) > 0 else []
        
    @classmethod
    def all(cls,offset=None,limit=None):
        if hasattr(cls,'uri'):
            subjects = [] if cls == Resource else cls.session.store.all(cls.uri,limit=limit,offset=offset)
            if subjects:
                return [cls(subject) for subject in subjects]
            return []
        return []
        
    @classmethod
    def __get(cls,filter,*objects,**symbols):
        direct_p = {}
        inverse_p = {}
        direct_p.update(  [(util.attr2rdf(name)[0],symbols[name]) for name in symbols if util.is_attr_direct(name)])
        inverse_p.update( [(util.attr2rdf(name)[0],symbols[name]) for name in symbols if not util.is_attr_direct(name)])
        
        subjects = {}
        if len(symbols) > 0:
            if len(direct_p) > 0:
                subjects.update( cls.session.store.predicate_dict(qPO(cls.uri,True,filter,direct_p),'s','c') )
            if len(inverse_p) > 0:
                subjects.update( cls.session.store.predicate_dict(qPO(cls.uri,False,filter,inverse_p),'s','c') )
        
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
        return cls.__get(None,*objects,**symbols)
    
    @classmethod
    def get_like(cls,*objects,**symbols):
        return cls.__get('regex',*objects,**symbols)
    
    def serialize(self,format='xml'):
        '''
        returns a serialized version of the internal graph represenatation
        of the resource, the format is the same as expected by rdflib's graph
        serialize method
        '''
        if format == 'json':
            return serializer.to_json(self.__graph)
        return self.__graph.serialize(format=format)
    
    def __str__(self):
        return self.serialize('n3')
    
    def save(self):
        '''
        performs persistence of the internal graph representation
        '''
        self.session.store.save(self)
        self.__dirty = False
    
    def remove(self):
        '''
        remove the resource from the store
        '''
        self.session.store.remove(self)
        self.__dirty = False
        
    def update(self):
        '''
        update the resource in the store, does not remove other triples
        related to it
        '''
        self.session.store.update(self)
        #del_graph = ConjunctiveGraph()
        for s,p,o in self.__to_delete:
            self.session.store.remove_triple(s,p,o)
        #    del_graph.add(triple)
        #self.session.store.remove()
        # better to remove all statements to be removed at once...
        self.__dirty = False
        
    def is_present(self):
        '''
        returns True if the resource is present in the Store or False otherwise
        '''
        return self.session.store.is_present(self)
    
    formats = {'n3': 'text/rdf+n3',
                 'nt': 'text/plain',
                 'turtle':'application/turtle',
                 'xml':'application/rdf+xml',
    }
    
    def load_from_source(self,data=None,file=None,location=None,format=None):
        graph = ConjunctiveGraph()
        if format is None:
            format = 'application/rdf+xml'
        elif format in self.formats:
            format = self.formats[format]
        graph.parse(data=data,file=file,location=location,format=format)
        self.set(graph)
    
    #TODO: must make this __lazy ... see how
    def set(self, graph):
        '''
        sets a resource from the supplied graph
        '''
        self.__graph = graph
        # add properties to the resource from the graph
        attrs = {}
        for s,p,o in self.__graph:
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
        if cls.uri:
            return util.namespace_split(cls.uri)[0]
        return None
        
    @classmethod
    def concept(cls,subject):
        return cls.session.store.concept(subject)
        
    def bind_namespaces(self,namespaces):
        '''
        the namespaces param must be a dict of the form:
        {prefix1: namespace1, prefix2 : namespace2, ..... }
        '''
        for prefix in namespaces:
            self.__graph.namespace_manager.bind(prefix, namespaces[prefix])
            
    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        return self.subject == other.subject if isinstance(other, ResourceMeta) else False