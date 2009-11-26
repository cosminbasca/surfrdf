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
    
import warnings

from surf.plugin.writer import RDFWriter
from surf.rdf import BNode, ConjunctiveGraph, Literal, URIRef
from reader import ReaderPlugin

class WriterPlugin(RDFWriter):
    def __init__(self,reader,*args,**kwargs):
            RDFWriter.__init__(self,reader,*args,**kwargs)
            if isinstance(self.reader, ReaderPlugin):
                self.__rdflib_store         = self.reader.rdflib_store
                self.__rdflib_identifier    = self.reader.rdflib_identifier
                self.__commit_pending_transaction_on_close = self.reader.commit_pending_transaction_on_close
                
                self.__graph = self.reader.graph
            else:
                self.__rdflib_store         = kwargs['rdflib_store'] if 'rdflib_store' in kwargs else 'IOMemory'
                self.__rdflib_identifier    = kwargs['rdflib_identifier'] if 'rdflib_identifier' in kwargs else None
                self.__commit_pending_transaction_on_close = kwargs['commit_pending_transaction_on_close'] if 'commit_pending_transaction_on_close' in kwargs else True
                
                self.__graph = ConjunctiveGraph(store=self.__rdflib_store, identifier = self.__rdflib_identifier)
                warnings.warn("the graph is not readable through the reader plugin", UserWarning)
                
    rdflib_store        = property(lambda self: self.__rdflib_store)
    rdflib_identifier   = property(lambda self: self.__rdflib_identifier)
    graph               = property(lambda self: self.__graph)
    commit_pending_transaction_on_close = property(lambda self: self.__commit_pending_transaction_on_close)
    
            
    def _save(self,resource):
        s = resource.subject
        self.__remove(s)
        for p, objs in resource.rdf_direct.items():
            for o in objs:
               self.__add(s,p,o)
        
        self.__graph.commit()
    
    def _update(self,resource):
        s = resource.subject
        for p in resource.rdf_direct:
            self.__remove(s,p)
        for p, objs in resource.rdf_direct.items():
            for o in objs:
               self.__add(s,p,o)

        self.__graph.commit()
    
    def _remove(self,resource,inverse=False):
        self.__remove(s=resource.subject)
        if inverse: self.__remove(o=resource.subject)
    
    def _size(self):
        return len(self.__graph)
    
    def _add_triple(self,s=None,p=None,o=None,context = None):
        self.__add(s,p,o,context)
    
    def _set_triple(self,s=None,p=None,o=None,context = None):
        self.__remove(s,p,context=context)
        self.__add(s,p,o,context)
    
    def _remove_triple(self,s=None,p=None,o=None,context = None):
        self.__remove(s,p,o,context)
    
    def __add(self,s=None,p=None,o=None,context=None):
        self.log.info('ADD : '+str(s)+', '+str(p)+', '+str(o)+', '+str(context))
        self.__graph.add((s,p,o))
        
    def __remove(self,s=None,p=None,o=None,context=None):
        self.log.info('REM : '+str(s)+', '+str(p)+', '+str(o)+', '+str(context))
        self.__graph.remove((s,p,o))
        
    def index_triples(self,**kwargs):
        '''
        performs index of the triples if such functionality is present,
        returns True if operation successfull
        '''
        # TODO: can indexing be forced ?
        return True
    
    def load_triples(self,source=None,publicID=None, format="xml", **args):
        '''
        load files (or resources on the web) into the triple-store
        this method is kept for backward compatibility only
        '''
        if source:
            self.__graph.parse(source,publicID=publicID,format=format,**args)
            return True
        return False
    
    def _clear(self,context=None):
        '''
        clears the triple-store
        '''
        self.__graph.remove((None,None,None))
        
    def close(self):
        self.__graph.close(commit_pending_transaction = self.__commit_pending_transaction_on_close)
        
