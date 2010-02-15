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

from surf.plugin.query_reader import RDFQueryReader
from allegro_franz.util import toRdfLib
from surf.rdf import URIRef

try:
    from franz.openrdf.sail.allegrographserver import AllegroGraphServer
    from franz.openrdf.repository.repository import Repository
    from franz.openrdf.query.query import QueryLanguage
    from franz.openrdf.model import value as sv
    from franz.openrdf.model import literal as sl

    print 'surf.plugin allegro_franz reader : franz libraries installed'
    class ReaderPlugin(RDFQueryReader):
        def __init__(self, *args, **kwargs):
            RDFQueryReader.__init__(self, *args, **kwargs)

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

            self.__con = self.allegro_repository.getConnection()

        results_format = property(lambda self: 'json')
        server = property(lambda self: self.__server)
        port = property(lambda self: self.__port)
        catalog = property(lambda self: self.__catalog)
        repository = property(lambda self: self.__repository)

        allegro_server = property(lambda self: self.__allegro_server)
        allegro_catalog = property(lambda self: self.__allegro_catalog)
        allegro_repository = property(lambda self: self.__allegro_repository)

        def _to_table(self, result):
            table = []
            bindings = result.getBindingNames()
            for bindingSet in result:
                row = {}
                for key in bindings:
                    try:    v = toRdfLib(bindingSet[key])
                    except: v = None
                    row[key] = v
                table.append(row)
            return table

        def _ask(self, result):
            '''
            returns the boolean value of a ASK query
            '''
            return result

        # execute
        def _execute(self, query):
            if query.query_type == 'select':
                return self.__execute_sparql(unicode(query))
            elif query.query_type == 'ask':
                return self.__execute_ask(unicode(query))

        def __execute_ask(self, q_string):
            boolQuery = self.__con.prepareBooleanQuery(QueryLanguage.SPARQL, q_string)
            return boolQuery.evaluate()

        def __execute_sparql(self, q_string):
            self.log.debug(q_string)
            tupleQuery = self.__con.prepareTupleQuery(QueryLanguage.SPARQL, q_string)
            tupleQuery.setIncludeInferred(self.inference)
            return tupleQuery.evaluate()

        def execute_sparql(self, q_string, format = 'JSON'):
            results = self.__execute_sparql(q_string)
            return self._results_to_json(results) if format == 'JSON' else results

        def close(self):
            self.__con.close()

        def _results_to_json(self, results):
            bindings = results.getBindingNames()
            r_dict = {}
            r_dict['head'] = {'vars': bindings}
            r_dict['results'] = {'bindings':[]}
            for bindingSet in results:
                json_binding = {}
                for b in bindings:
                    value = bindingSet.getValue(b)
                    if type(value) is sv.URI:
                        json_binding[b] = {'type':'uri', 'value': value.getURI()}
                    elif type(value) is sv.BNode:
                        json_binding[b] = {'type':'bnode', 'value': value.getID()}
                    elif type(value) is sl.Literal:
                        dtype = value.getDatatype() if value.getDatatype() else None
                        lang = value.getLanguage() if value.getLanguage() else None
                        lit_type = 'typed-literal' if dtype else 'literal'
                        json_binding[b] = {'type':lit_type, 'value': value.getLabel()}
                        if dtype:
                            if type(dtype) in [str, unicode] and dtype.startswith('<') and dtype.endswith('>'):
                                dtype = dtype.strip('<>')
                            json_binding[b]['datatype'] = URIRef(dtype)
                        if lang:
                            json_binding[b]['xml:lang'] = lang
                r_dict['results']['bindings'].append(json_binding)
            return r_dict

except ImportError, e:
    print 'surf.plugin allegro_franz reader : franz libraries not installed', e
    class ReaderPlugin(RDFQueryReader):
        pass
