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

from surf.store.plugins import RDFReader
from sparqlquery import translate
from allegroprotocol.allegro import Allegro, AllegroException

class SPARQLSesame2HttpReader(RDFReader):
    __type__ = 'sparql-sesame2-http'
    
    def __init__(self,*args,**kwargs):
        RDFReader.__init__(self,*args,**kwargs)
        self.__host = kwargs['host'] if 'host' in kwargs else 'localhost'
        self.__port = kwargs['port'] if 'port' in kwargs else 5678
        self.__root_path = kwargs['root_path'] if 'root_path' in kwargs else '/sesame'
        self.__repository_path = kwargs['repository_path'] if 'repository_path' in kwargs else ''
        self.__repository = kwargs['repository'] if 'repository' in kwargs else None
        
        self.__allegro = Allegro(self.host,self.port,self.root_path,self.repository_path)
        if not self.repository:
            raise Exception('No <repository> argument supplyed.')
        self.allegro.open_repository(self.repository)
        
    host = property(lambda self: self.__host)
    port = property(lambda self: self.__port)
    root_path = property(lambda self: self.__root_path)
    repository_path = property(lambda self: self.__repository_path)
    repository = property(lambda self: self.__repository)
    
    allegro = property(lambda self: self.__allegro)
    
    def _execute(self,q):
        try:
            q_rep = translate(q)
            self.log.debug(q_rep)
            results = self.allegro.sparql_query(self.repository,q_rep,infer=False,format='sparql')
            return results
        except Exception, e:
            print 'Exception while querying', e
        return None