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

from surf.plugin import Plugin
import logging
from surf.query import Query
from rdf.graph import ConjunctiveGraph
from rdf.term import URIRef, BNode, Literal, RDF

class InvalidResourceException(Exception):
    def __init__(self,*args,**kwargs):
        super(InvalidResourceException,self).__init__(self,*args,**kwargs)

class RDFWriter(Plugin):
    '''
    super class for all surf Writer Plugins
    '''
    #protected interface
    def _clear(self,context=None):
        pass
    
    def _save(self,resource):
        pass
    
    def _update(self,resource):
        pass
    
    def _remove(self,resource):
        pass
    
    def _size(self):
        return -1
    
    def _add_triple(self,s=None,p=None,o=None,context = None):
        pass
    
    def _set_triple(self,s=None,p=None,o=None,context = None):
        pass
    
    def _remove_triple(self,s=None,p=None,o=None,context = None):
        pass
    
    
    #public interface
    def clear(self,context=None):
        '''
        empty the store
        '''
        self._clear(context=context)
        
    def save(self,resource):
        '''
        replace the resource with it's current state
        '''
        if hasattr(resource,'subject'): self._save(resource)
        else: raise InvalidResourceException('argument must be of type surf.resource.Resource')

    def update(self,resource):
        '''
        update the current resource
        '''
        if hasattr(resource,'subject'): self._update(resource)
        else: raise InvalidResourceException('argument must be of type surf.resource.Resource')
        
    def remove(self,resource):
        '''
        completly remove the resource from the store
        only direct triples are removed
        '''
        #TODO: decide wether triples that are indirect (belong to other resource should be rremoved as well)
        if hasattr(resource,'subject'): self._remove(resource)
        else: raise InvalidResourceException('argument must be of type surf.resource.Resource')
        
    def size(self):
        '''
        returns the size in triples, that are contained in the current store
        '''
        return self._size()
        
    # triple level access methods
    def add_triple(self,s=None,p=None,o=None, context=None):
        '''
        add a triple to the store, with the specified context,
        None can be used as a wildcard
        '''
        self._add_triple(s,p,o,context)
    
    def set_triple(self,s=None,p=None,o=None, context=None):
        '''
        replace a triple in the store, with the specified context
        None can be used as a wildcard
        '''
        self._set_triple(s,p,o,context)
    
    def remove_triple(self,s=None,p=None,o=None, context=None):
        '''
        remove a triple from the store, with the specified context
        None can be used as a wildcard
        '''
        self._remove_triple(s,p,o,context)
        
    # management
    def close(self):
        '''
        close the plugin
        '''
        pass
    
    def index_triples(self,**kwargs):
        '''
        performs index of the triples if such functionality is present,
        returns True if operation successfull
        '''
        return False
    
    def load_triples(self,**kwargs):
        '''
        loads triples from supported sources if such functionality is present
        returns True if operation successfull
        '''
        return False