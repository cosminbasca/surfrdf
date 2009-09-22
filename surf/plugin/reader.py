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

from surf.plugin import Plugin

class RDFReader(Plugin):
    '''
    super class for all surf Reader Plugins
    '''
    #protected interface
    def _get(self, subject, attribute, direct, context):
        '''to be implemented by classes that inherit `RDFReader`, is called
        directly by `get`'''
        
        return None
    
    def _load(self, subject, context):
        '''to be implemented by classes that inherit `RDFReader`, is called
        directly by `load`'''
        
        return {}
    
    def _is_present(self, subject, context):
        '''to be implemented by classes that inherit `RDFReader`, is called
        directly by `is_present`'''
        
        return False
    
    def _all(self, concept, limit = None, offset = None, 
             full = False, context = None):
        '''to be implemented by classes that inherit `RDFReader`, is called
        directly by `all`'''
        
        return []
        
    def _concept(self,subject):
        '''to be implemented by classes that inherit `RDFReader`, is called
        directly by `concept`'''
        
        return None
    
    def _instances_by_attribute(self, concept, attributes, direct, context):
        '''to be implemented by classes that inherit `RDFReader`, is called
        directly by `instances_by_attribute`'''
        
        return []
        
    def _instances(self, concept, direct, filter, predicates, context):
        '''to be implemented by classes that inherit `RDFReader`, is called
        directly by `instances`'''
        return []
        
    def _instances_by_value(self,concept,direct,attributes):
        '''to be implemented by classes that inherit `RDFReader`, is called
        directly by `instances_by_value`'''
        return []
    
    
    #public interface
    def get(self, resource, attribute, direct):
        '''Return the `value(s)` of the corresponding `attribute`,
        if `direct` is False, than the `subject` of the `resource` is considered
        the `object` of the query'''
        
        subj = resource.subject if hasattr(resource, 'subject') else resource
        return self._get(subj, attribute, direct, resource.context)
        
    def load(self, resource, direct):
        '''Fully load the `resource` from the `store`, returns all statements about
        the `resource`
        if `direct` is False, than the `subject` of the `resource` is considered
        the `object` of the query'''
        
        subj = resource.subject if hasattr(resource, 'subject') else resource
        return self._load(subj, direct, resource.context)
        
    def is_present(self, resource):
        '''True if the `resource` is present in the `store`, False otherwise'''
        
        subj = resource.subject if hasattr(resource, 'subject') else resource
        return self._is_present(subj, resource.context)
        
    def all(self, concept, limit = None, offset = None, 
            full = False, context = None):
        '''returns all `uri's` that are `instances` of `concept` within [`limit`,`limit`+`offset`]'''
        con = concept.uri if hasattr(concept, 'uri') else concept
        return self._all(con, limit = limit, offset = offset, 
                         full = full, context = context)
        
    def concept(self,resource):
        '''returns the `concept` URI of the following `resource`,
        `resource` can be a `string` or a `URIRef`'''
        subj = resource.subject if hasattr(resource, 'subject') else resource
        return self._concept(subj)
        
    def instances_by_attribute(self, resource, attributes, direct, context):
        '''returns all `uri's` that are `instances` of `concept` that have the specified `attributes`
        if `direct` is False, than the `subject` of the `resource` is considered
        the `object` of the query'''
        
        concept = resource.uri if hasattr(resource, 'uri') else resource
        return self._instances_by_attribute(concept, attributes, direct, 
                                            context)
        
    def instances(self, resource, direct, filter, predicates, context):
        '''returns all `uri's` that are `instances` of `concept` that have the
        specified `predicates` - a `dict` where the `key` is the shorthand notation,
        and the `value` is the predicate value
        if `direct` is False, than the `subject` of the `resource` is considered
        the `object` of the query
        
        .. code-block:: python
            
            store.instances(resource,True,None,{'foaf_name':'John Doe'})
            
        '''
        concept = resource.uri if hasattr(resource, 'uri') else resource
        #TODO: make sure uri's are passed further
        return self._instances(concept, direct, filter, predicates, context)
        
    def instances_by_value(self,resource,direct,attributes):
        '''returns all `uri's` that are `instances` of `concept` as values and
        that have the specified `attributes`
        if `direct` is False, than the `subject` of the `resource` is considered
        the `object` of the query'''
        concept = resource.uri if hasattr(resource, 'uri') else resource
        return self._instances_by_value(concept,direct,attributes)
        
