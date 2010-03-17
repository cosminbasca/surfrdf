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

from allegro_franz.reader import ReaderPlugin
from allegro_franz.util import toSesame

try:
    from franz.openrdf.sail.allegrographserver import AllegroGraphServer
    from franz.openrdf.repository.repository import Repository
    from franz.openrdf.rio.rdfformat import RDFFormat

    print 'surf.plugin allegro_franz writer : franz libraries installed'
    class WriterPlugin(RDFWriter):
        def __init__(self, reader, *args, **kwargs):
            RDFWriter.__init__(self, reader, *args, **kwargs)
            if isinstance(self.reader, ReaderPlugin):
                self.__server = self.reader.server
                self.__port = self.reader.port
                self.__catalog = self.reader.catalog
                self.__repository = self.reader.repository

                self.__allegro_server = self.reader.allegro_server
                self.__allegro_catalog = self.reader.allegro_catalog
                self.__allegro_repository = self.reader.allegro_repository

            else:
                self.__server = kwargs['server'] if 'server' in kwargs else 'localhost'
                self.__port = kwargs['port'] if 'port' in kwargs else 6789
                self.__catalog = kwargs['catalog'] if 'catalog' in kwargs else None
                self.__repository = kwargs['repository'] if 'repository' in kwargs else None

                if not self.__catalog or not self.__repository:
                    raise Exception('Must specify the <catalog> and the <repository> arguments')

                self.__allegro_server = AllegroGraphServer(self.__server, port = self.__port)
                self.__allegro_catalog = self.__allegro_server.openCatalog(self.__catalog)
                self.__allegro_repository = self.__allegro_catalog.getRepository(self.__repository, Repository.ACCESS)
                self.__allegro_repository.initialize()

            self.__con = self.__allegro_repository.getConnection()
            self.__f = self.__allegro_repository.getValueFactory()

        results_format = property(lambda self: 'json')
        server = property(lambda self: self.__server)
        port = property(lambda self: self.__port)
        catalog = property(lambda self: self.__catalog)
        repository = property(lambda self: self.__repository)

        allegro_server = property(lambda self: self.__allegro_server)
        allegro_catalog = property(lambda self: self.__allegro_catalog)
        allegro_repository = property(lambda self: self.__allegro_repository)

        def _save(self, *resources):
            for resource in resources:
                s = resource.subject
                self.__remove(s)
                for p, objs in resource.rdf_direct.items():
                    for o in objs:
                        self.__add(s, p, o)

        def _update(self, *resources):
            for resource in resources:
                s = resource.subject
                for p in resource.rdf_direct:
                    self.__remove(s, p)
                for p, objs in resource.rdf_direct.items():
                    for o in objs:
                        self.__add(s, p, o)

        def _remove(self, *resources, **kwargs):
            inverse = kwargs.get("inverse")
            for resource in resources:
                self.__remove(s = resource.subject)
                if inverse:
                    self.__remove(o = resource.subject)

        def _size(self):
            return self.__con.size()

        def _add_triple(self, s = None, p = None, o = None, context = None):
            self.__add(s, p, o, context)

        def _set_triple(self, s = None, p = None, o = None, context = None):
            self.__remove(s, p, context = context)
            self.__add(s, p, o, context)

        def _remove_triple(self, s = None, p = None, o = None, context = None):
            self.__remove(s, p, o, context)

        # used by the sesame api
        def __add(self, s = None, p = None, o = None, context = None):
            self.log.info('ADD TRIPLE: ' + str(s) + ', ' + str(p) + ', ' + str(o) + ', ' + str(context))
            self.__con.addTriple(toSesame(s, self.__f), toSesame(p, self.__f), toSesame(o, self.__f), contexts = toSesame(context, self.__f))

        def __remove(self, s = None, p = None, o = None, context = None):
            self.log.info('REM TRIPLE: ' + str(s) + ', ' + str(p) + ', ' + str(o) + ', ' + str(context))
            self.__con.removeTriples(toSesame(s, self.__f), toSesame(p, self.__f), toSesame(o, self.__f), contexts = toSesame(context, self.__f))

        def index_triples(self, **kwargs):
            """ Index triples if this functionality is present.  
            
            Return `True` if successful.
            
            """
            all = kwargs['all'] if 'all' in kwargs else False
            asynchronous = kwargs['asynchronous'] if 'asynchronous' in kwargs else False
            self.__allegro_repository.indexTriples(all = all, asynchronous = asynchronous)
            return True

        def load_triples(self, **kwargs):
            '''
            loads triples from supported sources if such functionality is present
            returns True if operation successfull
            '''
            format = kwargs['format'] if 'format' in kwargs else RDFFormat.RDFXML
            format = RDFFormat.NTRIPLES if format is 'nt' else RDFFormat.RDFXML
            source = kwargs['source'] if 'source' in kwargs else None
            base = kwargs['base'] if 'base' in kwargs else None
            context = kwargs['context'] if 'context' in kwargs else None
            server_side = kwargs['server_side'] if 'server_side' in kwargs else True
            if source:
                self.__con.addFile(source, base = base, format = format, context = toSesame(context, self.__f), serverSide = server_side)
                return True
            return False

        def _clear(self, context = None):
            """ Clear the triple-store. """
            
            self.__con.clear(contexts = toSesame(context, self.__f))

        # Extra functionality
        def register_fts_predicate(self, namespace, localname):
            '''
            register free text search predicates
            '''
            self.__allegro_repository.registerFreeTextPredicate(namespace = str(namespace), localname = localname)

        def namespaces(self):
            return self.__con.getNamespaces()

        def namespace(self, prefix):
            return self.__con.getNamespace(prefix)

        def set_namespace(self, prefix, namespace):
            self.__con.setNamespace(prefix, namespace)

        def remove_namespace(self, prefix):
            self.__con.removeNamespace(prefix)

        def clear_namespaces(self):
            self.__con.clearNamespaces()

        def close(self):
            self.__con.close()

except ImportError, e:
    print 'surf.plugin allegro_franz writer : franz libraries not installed ', e
    class WriterPlugin(RDFWriter):
        pass
