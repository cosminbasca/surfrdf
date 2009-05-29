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
from surf.query import Query
from rdf.graph import ConjunctiveGraph
from rdf.term import URIRef, BNode, Literal, RDF

a = RDF['type']

class UnsupportedResultType(Exception):
    pass


class UnsupportedParameterType(Exception):
    pass


'''
metaclass based plugin architecture :]
to create a plugin all one has to do is sublclass the Plugin Base class
and add the class variable __type__, which will be used as the key to
access the plugin from the repository. The repository is the Base class
itself and is managed by the metaclass
'''
class AbstractMount(type):
    default = 'default'
    
    def __init__(self,*args,**kwargs):
        if not hasattr(self, 'plugins'):
            self.plugins = {}
        else:
            self.plugins[self.__type__] = self
    
    def get_plugin(self,type,use_default=False):
        if use_default:
            dflt = self.plugins[AbstractMount.default] if AbstractMount.default in self.plugins else None
        else:
            dflt = None
        return self.plugins[type] if type in self.plugins else dflt
    
#-------------------------------------------------------------------------------
# the Reader Plugins and Mount Point
#-------------------------------------------------------------------------------
class ReaderPluginMount(AbstractMount):
    pass
    
class RDFReader(object):
    __metaclass__ = ReaderPluginMount
    __type__ = AbstractMount.default
    
    def __init__(self,*args,**kwargs):
        logging.basicConfig()
        self.log = logging.getLogger(self.__type__)
        self.log.setLevel(logging.NOTSET)
    
    def enable_logging(self,enable=True):
        if enable:
            self.log.setLevel(logging.DEBUG)
        else :
            self.log.setLevel(logging.NOTSET)
    
    def is_enable_logging(self):
        return False if self.log.level == logging.NOTSET else True
            
    # to implement
    def _execute(self,q):
        return None
    
    def _is_present(self,q):
        return False
    
    def _concept(self,q):
        return None
    
    def _all(self,q):
        return None
    
    # to use
    def execute(self,q):
        if type(q) != Query:
            raise Exception('parameter must be a Query instance')
        self.log.debug(q)
        return self._execute(q)
    
    def is_present(self,resource):
        if hasattr(resource,'subject'):
            q = Query.ask((resource.subject,'?p','?o'))
            return self._is_present(q)
        return False
        
    def concept(self,subject):
        subject = subject if type(subject) is URIRef else URIRef(str(subject))
        qt = Query.select().distinct('?c').where(subject,a,'?c')
        return self._concept(qt)
        
    def all(self,concept,limit=None,offset=None):
        if concept:
            concept = concept if type(concept) is URIRef else URIRef(str(concept))
            q = Query.select().distinct('?s').where('?s',a,concept)
            if limit:
                q.limit(limit)
            if offset:
                q.offset(offset)
            return self._all(q)
        return None
        
    @classmethod
    def get_type(cls):
        return cls.__type__
    
    def close(self):
        pass
    
#-------------------------------------------------------------------------------
# the Writer Plugins and Mount Point
#-------------------------------------------------------------------------------
class WriterPluginMount(AbstractMount):
    pass
    
class RDFWriter(object):
    __metaclass__ = WriterPluginMount
    __type__ = AbstractMount.default
    
    def __init__(self,*args,**kwargs):
        logging.basicConfig()
        self.log = logging.getLogger(self.__type__)
        self.log.setLevel(logging.NOTSET)
    
    def enable_logging(self,enable=True):
        if enable:
            self.log.setLevel(logging.DEBUG)
        else :
            self.log.setLevel(logging.NOTSET)
            
    def is_enable_logging(self):
        return False if self.log.level == logging.NOTSET else True
            
    @classmethod
    def get_type(cls):
        return cls.__type__
    
    #methods exposed up to the Resource class
    def clear(self,context=None):
        self._clear(context=context)
    
    def save(self,resource):
        if hasattr(resource,'subject') and hasattr(resource,'graph'):
            self._save(resource.subject,resource.graph)
        
    def update(self,resource):
        if hasattr(resource,'graph'):
            self._update(resource.graph)
        
    def remove(self,resource):
        if hasattr(resource,'subject'):
            self._remove(resource.subject)
        
    def size(self):
        return self._size()
    
    def add_triple(self,s=None,p=None,o=None,context = None):
        self._add_triple(s,p,o,context)
    
    def set_triple(self,s=None,p=None,o=None,context = None):
        self._set_triple(s,p,o,context)
    
    def remove_triple(self,s=None,p=None,o=None,context = None):
        self._remove_triple(s,p,o,context)
        
    # to be implemented by plugins
    def _clear(self,context=None):
        pass
    
    def _save(self,subject,graph):
        pass
    
    def _update(self,graph):
        pass
    
    def _remove(self,subject):
        pass
    
    def _add_triple(self,s=None,p=None,o=None,context = None):
        pass
    
    def _set_triple(self,s=None,p=None,o=None,context = None):
        pass
    
    def _remove_triple(self,s=None,p=None,o=None,context = None):
        pass
    
    def _size(self):
        return -1
    
    def close(self):
        pass
    
# register existing plugins
import sesame2apiwriter
import sesame2httpwriter
import sparqlprotocolreader
import sparqlsesame2apireader
import sparqlsesame2httpreader

#perhaps autodiscovery later on from a specific location or something simillar

