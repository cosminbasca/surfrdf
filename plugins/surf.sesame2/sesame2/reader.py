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
from allegro import Allegro
from surf.query_to_sparql import translate

# the rdf way
#from rdf.term import URIRef, BNode, Literal
# the rdflib 2.4.x way
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal

class ReaderPlugin(RDFQueryReader):
    def __init__(self,*args,**kwargs):
        RDFQueryReader.__init__(self,*args,**kwargs)
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
        print 'SIZE ',self.__allegro.size(self.repository)
        
    server              = property(lambda self: self.__server)
    port                = property(lambda self: self.__port)
    root_path           = property(lambda self: self.__root_path)
    repository_path     = property(lambda self: self.__repository_path)
    repository          = property(lambda self: self.__repository)
    
    allegro             = property(lambda self: self.__allegro)
    
    def _values(self,result,vkey='v',ckey='c'):
        '''
        returns a dictionary of the form {value : [concept,concept,...]}
        result represents the query returned result
        '''
        results = result
        values = {}
        if not results:
            return values
        for v in results:
            if v[vkey] not in values: values[v[vkey]] = []
            if ckey in v: values[v[vkey]].append(v[ckey])
        return values
    
    def _predicacte_values(self,result,pkey='p',vkey='v',ckey='c'):
        '''
        returns a dictionary with predicates as keys, the values
        are the same as returned by the _values function
        returns a dictionary of the form {value : [concept,concept,...]}
        {predicate: {value : [concept,concept,...]},
         predicate: {value : [concept,concept,...]},}
        result represents the query returned result
        '''
        results = result
        pvalues = {}
        if not results:
            return pvalues
        for v in results:
            p = v[pkey]
            if p not in pvalues: pvalues[p] = {}
            if v[vkey] not in pvalues[p]: pvalues[p][v[vkey]] = []
            if ckey in v: pvalues[p][v[vkey]].append(v[ckey])
        return pvalues
        
    def _ask(self,result):
        '''
        returns the boolean value of a ASK query
        '''
        return result
    
    # execute
    def _execute(self,query):
        q_string = translate(query)
        try:
            self.log.debug(q_string)
            results = self.allegro.sparql_query(self.repository,q_string,infer=self.inference,format='sparql')
            return results
            #return self._toRdflib(results)
        except Exception, e: 
            self.log.error('Exception on query : \n'+str(e))
        return None
    
    def close(self):
        pass
    
