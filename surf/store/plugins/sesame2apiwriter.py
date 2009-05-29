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

from surf.store.plugins import RDFWriter
from surf.store.plugins import RDFReader
try:
    from franz.openrdf.sail.allegrographserver import AllegroGraphServer
    from franz.openrdf.repository.repository import Repository
    from franz.miniclient import repository
    from franz.openrdf.query.query import QueryLanguage
    from franz.openrdf.vocabulary.rdf import RDF
    from franz.openrdf.vocabulary.xmlschema import XMLSchema
    from franz.openrdf.query.dataset import Dataset
    from franz.openrdf.rio.rdfformat import RDFFormat
    from franz.openrdf.rio.rdfwriter import  NTriplesWriter
    from franz.openrdf.rio.rdfxmlwriter import RDFXMLWriter

    import sesame2util as su
    
    class Sesame2ApiWriter(RDFWriter):
        __type__ = 'sesame2-api'
    
        def __init__(self,*args,**kwargs):
            RDFWriter.__init__(self,*args,**kwargs)
            
            self.__server = kwargs['server'] if 'server' in kwargs else 'localhost'
            self.__port = kwargs['port'] if 'port' in kwargs else 6789
            self.__catalog = kwargs['catalog'] if 'catalog' in kwargs else None
            self.__repository = kwargs['repository'] if 'repository' in kwargs else None
            
            if not self.__catalog or not self.__repository:
                raise Exception('Must specify the <catalog> and the <repository> arguments')
            
            self.__allegro_server = AllegroGraphServer(self.__server, port=self.__port)
            self.__allegro_catalog = self.__allegro_server.openCatalog(self.__catalog)
            self.__allegro_repository = self.__allegro_catalog.getRepository(self.__repository, Repository.ACCESS )
            self.__allegro_repository.initialize()
            
            self.__con = self.allegro_repository.getConnection()
            self.__f = self.allegro_repository.getValueFactory()
        
        
        server = property(lambda self: self.__server)
        port = property(lambda self: self.__port)
        catalog = property(lambda self: self.__catalog)
        repository = property(lambda self: self.__repository)
        
        allegro_server = property(lambda self: self.__allegro_server)
        allegro_catalog = property(lambda self: self.__allegro_catalog)
        allegro_repository = property(lambda self: self.__allegro_repository)
        
        def _save(self,subject, graph):
            self.__remove(subject)
            for s,p,o in graph:
                self.__add(s,p,o)
        
        def _update(self,graph):
            for s,p,o in graph:
                self.__remove(s,p)
            for s,p,o in graph:
                self.__add(s,p,o)
            
        def _remove(self,subject):
            self.__remove(s=subject)
            self.__remove(o=subject)
        
        def _size(self):
            return self.__con.size()
        
        def _add_triple(self,s=None,p=None,o=None,context = None):
            self.__add(s,p,o,context)
        
        def _set_triple(self,s=None,p=None,o=None,context = None):
            self.__remove(s,p,context=context)
            self.__add(s,p,o,context)
        
        def _remove_triple(self,s=None,p=None,o=None,context = None):
            self.__remove(s,p,o,context)
        
        # used by the sesame api
        def __add(self,s=None,p=None,o=None,context=None):
            self.__con.addTriple(su.toSesame(s,self.__f), su.toSesame(p,self.__f), su.toSesame(o,self.__f),contexts = su.toSesame(context,self.__f))
            
        def __remove(self,s=None,p=None,o=None,context=None):
            self.__con.removeTriples(su.toSesame(s,self.__f), su.toSesame(p,self.__f), su.toSesame(o,self.__f),contexts = su.toSesame(context,self.__f))
            
        # EXPOSE EXOTIC Functionality for extra use - helper functions
        def index_triples(self,all=True, asynchronous=False):
            self.__allegro_repository.indexTriples(all=all, asynchronous=asynchronous)
            
        def register_fts_predicate(self,namespace, localname):
            self.__allegro_repository.registerFreeTextPredicate(namespace=str(namespace), localname=localname)
            
        def add_file(self,file,base=None,format='nt',context=None,server_side=False):
            format = RDFFormat.NTRIPLES if format is 'nt' else RDFFormat.RDFXML
            self.__con.addFile(file,base=base,format=format,context=su.toSesame(context,self.__f),serverSide=server_side)
        
        def _clear(self,context=None):
            self.__con.clear(contexts = su.toSesame(context,self.__f))
            
        def namespaces(self):
            return self.__con.getNamespaces()
        
        def namespace(self,prefix):
            return self.__con.getNamespace(prefix)
        
        def set_namespace(self,prefix,namespace):
            self.__con.setNamespace(prefix,namespace)
            
        def remove_namespace(self,prefix):
            self.__con.removeNamespace(prefix)
            
        def clear_namespaces(self):
            self.__con.clearNamespaces()
            
        def close(self):
            self.__con.close()
            
except Exception, e:
    pass