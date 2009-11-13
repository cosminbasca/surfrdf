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
    

from surf.plugin.writer import RDFWriter
from allegro import Allegro

from surf.rdf import BNode, Literal, URIRef
from reader import ReaderPlugin

class WriterPlugin(RDFWriter):
    def __init__(self,reader,*args,**kwargs):
        RDFWriter.__init__(self,reader,*args,**kwargs)
        if isinstance(self.reader, ReaderPlugin):
            self.__server           = self.reader.server
            self.__port             = self.reader.port
            self.__root_path        = self.reader.root_path
            self.__repository_path  = self.reader.repository_path
            self.__repository       = self.reader.repository
            self.__allegro          = self.reader.allegro
            
        else:
            self.__server           = kwargs['server'] if 'server' in kwargs else 'localhost'
            self.__port             = kwargs['port'] if 'port' in kwargs else 6789
            self.__root_path        = kwargs['root_path'] if 'root_path' in kwargs else '/sesame'
            self.__repository_path  = kwargs['repository_path'] if 'repository_path' in kwargs else ''
            self.__repository       = kwargs['repository'] if 'repository' in kwargs else None
            
            self.log.info('INIT : '+str(self.server)+','+str(self.port)+','+str(self.root_path)+','+str(self.repository_path))
            self.__allegro          = Allegro(self.server,self.port,self.root_path,self.repository_path)
            if not self.repository:
                raise Exception('No <repository> argument supplyed.')
            opened = self.allegro.open_repository(self.repository)
            self.log.info('ALLEGRO Repo opened : '+str(opened))
        
    server              = property(lambda self: self.__server)
    port                = property(lambda self: self.__port)
    root_path           = property(lambda self: self.__root_path)
    repository_path     = property(lambda self: self.__repository_path)
    repository          = property(lambda self: self.__repository)
    allegro             = property(lambda self: self.__allegro)
        
    def _save(self,resource):
        s = resource.subject
        self.__allegro.remove_statements(self.__repository,s=s.n3())
        graph = resource.graph()
        self.__allegro.add_statements(self.__repository,
                                      graph.serialize(format='nt'),update=True,content_type='nt')
    
    def _update(self,resource):
        graph = resource.graph()
        for s,p,o in graph:
            self.__allegro.remove_statements(self.__repository,s=s.n3(),p=p.n3())
        self.__allegro.add_statements(self.__repository,
                                      graph.serialize(format='nt'),update=True,content_type='nt')
    
    def _remove(self,resource):
        self.__allegro.remove_statements(self.__repository,s=resource.subject.n3())
        self.__allegro.remove_statements(self.__repository,o=resource.subject.n3())
    
    def _size(self):
        return self.__allegro.size(self.__repository)
    
    def _add_triple(self,s=None,p=None,o=None,context = None):
        self.__allegro.add_statements(self.__repository,
                                      self.__tontriples(s,p,o),update=True,content_type='nt')
    
    def _set_triple(self,s=None,p=None,o=None,context = None):
        sn3 = s.n3() if s else None
        pn3 = p.n3() if p else None
        on3 = o.n3() if o else None
        self.__allegro.remove_statements(self.__repository,s=sn3,p=pn3,context=context)
        self.__allegro.add_statements(self.__repository,
                                      self.__tontriples(s,p,o),update=True,content_type='nt')
    
    def _remove_triple(self,s=None,p=None,o=None,context = None):
        sn3 = s.n3() if s else None
        pn3 = p.n3() if p else None
        on3 = o.n3() if o else None
        self.__allegro.remove_statements(self.__repository,s=sn3,p=pn3,o=on3,context=context)
        
    def __tontriples(self,s,p,o):
        return '%s %s %s'%(s.n3(),p.n3(),o.n3())
        
    def _clear(self, context=None):
        self.__allegro.remove_all_statements(self.__repository)
        
    def load_triples(self,**kwargs):
        '''
        loads triples from supported sources if such functionality is present
        returns True if operation successfull
        '''
        location    = kwargs['location'] if 'location' in kwargs else None
        update      = kwargs['update'] if 'update' in kwargs else True
        format      = kwargs['format'] if 'format' in kwargs else 'rdf'
        context     = kwargs['context'] if 'context' in kwargs else None
        baseURI     = kwargs['baseURI'] if 'baseURI' in kwargs else None
        externalFormat = kwargs['externalFormat'] if 'externalFormat' in kwargs else None
        saveStrings = kwargs['saveStrings'] if 'saveStrings' in kwargs else None
        self.__allegro.load_statements(self.__repository,
                                       location,
                                       update=update,
                                       format=format,
                                       context=context,
                                       baseURI = baseURI,
                                       externalFormat = externalFormat,
                                       saveStrings = saveStrings)
        return True
    