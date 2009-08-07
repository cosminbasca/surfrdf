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

import sesame2
from urllib import urlencode
import httplib
import os, os.path, shutil

class AllegroException(Exception):
    def __init__(self,msg):
        self.msg = msg
    
    def __str__(sel):
        return 'Allegro Exception : %s'%self.msg

class Allegro(sesame2.Sesame2):
    
    def __init__(self,host,port=80,root_path='/sesame',directory='',strict=False):
        sesame2.Sesame2.__init__(self,host,port,root_path,strict)
        sesame2.Sesame2.url['load'] = '/repositories/%(id)s/load'
        sesame2.Sesame2.url['index'] = '/repositories/%(id)s/index'
        sesame2.Sesame2.url['map'] = '/repositories/%(id)s/map'
        
        self.directory = directory.strip()
        if self.directory:
            if not os.path.exists(self.directory):
                try:
                    os.makedirs(self.directory)
                except:
                    raise AllegroException('could not create repository folder [%s]'%self.directory)
    
    def open_repository(self,id,name=None):
        return self.create_repository(id,'',name=name,if_exists='open')
    
    def create_repository(self,id,title,name=None,if_exists='open',readable=True,writable=True):
        params = {'id':id,
            'readable': 'true' if readable else 'false',
            'writable': 'true' if writable else 'false',
            'if-exists': if_exists,
            'title': title}
        if self.directory:
            params['directory'] = self.directory
        if name:
            params['name'] = name
        try:
            self.sesame2_request('POST','repositories',params=params)
        except sesame2.Sesame2Exception:
            return False
        return True
    
    def remove_repository(self,name):
        '''
        warning: works only locally!, do not use otherwise
        '''
        if self.directory:
            try:
                shutil.rmtree(os.path.join(self.directory,name))
            except:
                return False
            return True
        return False
    
    def load_statements(self,id,location,update=True,format='rdf',context=None, baseURI = None, externalFormat = None, saveStrings = False):
        method = 'PUT'
        if update:
            method = 'POST'
        params = {format:location}
        if context:
            params['context'] = context
        if format == 'rdf':
            if baseURI:
                params['baseURI'] = baseURI
        elif format == 'ntriple':
            params['saveStrings'] = saveStrings
            if externalFormat:
                params['externalFormat'] = externalFormat
        try:
            self.sesame2_request(method,'load',{'id':str(id)},params=params)
        except sesame2.Sesame2Exception:
            return False
        return True

    def index_info(self,id):
        return self.sesame2_request('GET','index',{'id':id})

    def mappings(self,id):
        return self.sesame2_request('GET','map',{'id':id})
        
if __name__ == '__main__':
    allegro = Allegro('localhost',5678,'/sesame',r'd:\repositories')
    print 'Protocol : ',allegro.protocol()
    print 'Open :',allegro.open_repository('corona')
    print 'Repositories : ',allegro.repositories()
    