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

from plugins import RDFReader, RDFWriter
from formatters import RDFFormatter

'''
the store class is comprised of a reader and a writer, getting access to an
underlying tripple store. Also store specific parameters must be handled by
the class, the plugins act based on various settings
'''
class ProtocolNotFoundException(Exception):
    def __init__(self,*args,**kwargs):
        super(ProtocolNotFoundException,self).__init__(self,*args,**kwargs)

class Store(object):
    '''
    handle the query execution, and result parsing
    '''
    def __init__(self,reader='sparql-protocol',writer=None,*args,**kwargs):
        # the reader
        self.reader = RDFReader.get_plugin(reader, use_default=False)(*args,**kwargs)
        if not self.reader:
            raise ProtocolNotFoundException('There is no RDF Reader registered for: %s, please import the module properly.'%reader)
        
        # the writer
        if writer:
            self.writer = RDFWriter.get_plugin(writer, use_default=False)(*args,**kwargs)
            if not self.writer:
                raise ProtocolNotFoundException('There is no RDF Writer registered for: %s, please import the module properly.'%writer)
        else:
            self.writer = RDFWriter(*args,**kwargs)
        
        # the formatter
        self.formatter = RDFFormatter()
        if hasattr(self.reader,'results_format'):
            self.formatter = RDFFormatter.get_plugin(self.reader.results_format, use_default=True)()
    
    def close(self):
        self.reader.close()
        self.writer.close()
    
    def clear(self,context=None):
        self.writer.clear(context=context)
    
    def enable_logging(self,enable):
        self.reader.enable_logging(enable)
        self.writer.enable_logging(enable)
        
    def is_enable_logging(self):
        return self.reader.is_enable_logging() or self.writer.is_enable_logging()
    
    def execute(self,query):
        results = self.reader.execute(query)
        return results
    
    # helper functions for the Resource
    def predicate_dict(self,query,value_key,concept_key):
        results = self.reader.execute(query)
        return self.formatter.predicate_dict(results,value_key,concept_key)
    
    def predicates_dict(self,query,predicate_key,value_key,concept_key):
        results = self.reader.execute(query)
        return self.formatter.predicates_dict(results,predicate_key,value_key,concept_key)
    
    def save(self,resource):
        self.writer.save(resource)
        
    def update(self,resource):
        self.writer.update(resource)
        
    def remove(self,resource):
        self.writer.remove(resource)
        
    def is_present(self,resource):
        return self.reader.is_present(resource)
    
    def concept(self,subject):
        return self.reader.concept(subject)
        
    def all(self,concept,limit=None,offset=None):
        return self.reader.all(concept,limit=limit,offset=offset)
        
    def size(self):
        return self.writer.size()
    
    def add_triple(self,s=None,p=None,o=None,context = None):
        self.writer.add_triple(s,p,o,context)
    
    def set_triple(self,s=None,p=None,o=None,context = None):
        self.writer.set_triple(s,p,o,context)
    
    def remove_triple(self,s=None,p=None,o=None,context = None):
        self.writer.remove_triple(s,p,o,context)
    
    