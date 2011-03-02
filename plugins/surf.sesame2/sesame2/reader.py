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


from surf.util import json_to_rdflib
from surf.plugin.query_reader import RDFQueryReader
from allegro import Allegro

class ReaderPlugin(RDFQueryReader):
    def __init__(self, *args, **kwargs):
        RDFQueryReader.__init__(self, *args, **kwargs)
        self.__server = kwargs['server'] if 'server' in kwargs else 'localhost'
        self.__port = kwargs['port'] if 'port' in kwargs else 6789
        self.__root_path = kwargs['root_path'] if 'root_path' in kwargs else '/sesame'
        self.__repository_path = kwargs['repository_path'] if 'repository_path' in kwargs else ''
        self.__repository = kwargs['repository'] if 'repository' in kwargs else None
        self.__use_allegro_extensions = kwargs['use_allegro_extensions'] if 'use_allegro_extensions' in kwargs else False

        self.log.info('INIT: %s, %s, %s, %s' % (self.server, 
                                                self.port, 
                                                self.root_path, 
                                                self.repository_path)) 

        if not self.repository:
            raise Exception('No <repository> argument supplied.')

        if self.__use_allegro_extensions:
            opened = self.get_allegro().open_repository(self.repository)
            self.log.info('ALLEGRO repository opened: %s' % opened)

    server = property(lambda self: self.__server)
    port = property(lambda self: self.__port)
    root_path = property(lambda self: self.__root_path)
    repository_path = property(lambda self: self.__repository_path)
    repository = property(lambda self: self.__repository)
    use_allegro_extensions = property(lambda self: self.__use_allegro_extensions)

    def _to_table(self, result):
        return result

    def _ask(self, result):
        '''
        returns the boolean value of a ASK query
        '''
        return result

    def get_allegro(self):
        return Allegro(self.server, self.port, self.root_path, 
                       self.repository_path)

    # execute
    def _execute(self, query):
        q_string = unicode(query)
        result = self.execute_sparql(q_string)

        if 'boolean' in result:
            return result['boolean']

        converted = []
        for binding in result["results"]["bindings"]:
            rdf_item = {}
            for key, obj in binding.items():
                try:
                    rdf_item[key] = json_to_rdflib(obj)
                except ValueError:
                    continue

            converted.append(rdf_item)

        return converted

    def execute_sparql(self, query, format='JSON'):
        try:
            self.log.debug(query)
            result = self.get_allegro().sparql_query(self.repository,
                                                    query, 
                                                    infer = self.inference, 
                                                    format = 'sparql+json')
            if type(result) == bool:
                # Build our own JSON response
                return {'head': {}, 'boolean': result}
            else:
                return result

        except Exception, e:
            self.log.exception("Exception on query")

    def close(self):
        pass

