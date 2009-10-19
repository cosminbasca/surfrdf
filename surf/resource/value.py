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

class ResourceValue(object):
    def __init__(self, values_source, resource, attribute_name):
        self.resource = resource
        
        # So we know which attribute this ResourceValue object represents
        self.__attribute_name = attribute_name

        # For lazy loading list contents
        self.__values_source = values_source
        self.__data_loaded = False

    def __get_values(self):
        if not self.__data_loaded:
            self.__values, self.__rdf_values = self.__values_source()
            self.__data_loaded = True

        return self.__values, self.__rdf_values
    

    def get_one(self):
        values, _ = self.__get_values()
        
        if len(values) == 1:
            return values[0]
        elif len(values) == 0:
            raise Exception('list is empty')
        else: 
            raise Exception('list has more elements than one')
            
    one = property(fget = get_one)
    
    def get_first(self):
        values, _ = self.__get_values()

        if len(values) > 0:
            return values[0]
        else:
            return None
    first = property(fget = get_first)
    
    def set_dirty(self, dirty):
        if hasattr(self.resource, 'dirty'):
            self.resource.dirty = dirty
            
    def to_rdf(self, value):
        if hasattr(self.resource, 'to_rdf'):
            return self.resource.to_rdf(value)
        
        raise Exception("to_rdf has no reference to resource")
    
    def __setitem__(self, key, value):
        values, rdf_values = self.__get_values()

        self.set_dirty(True)
        values[key] = value
        rdf_values[key] = self.to_rdf(value)
        
    def __delitem__(self, key):
        values, rdf_values = self.__get_values()

        self.set_dirty(True)
        del values[key]
        del rdf_values[key]
    
    def append(self, value):
        values, rdf_values = self.__get_values()

        self.set_dirty(True)
        values.append(value)
        rdf_values.append(self.to_rdf(value))
        
    def extend(self, L):
        values, rdf_values = self.__get_values()

        self.set_dirty(True)
        values.extend(L)
        rdf_values.extend([self.to_rdf(value) for value in L])
        
    def insert(self, i, value):
        values, rdf_values = self.__get_values()

        self.set_dirty(True)
        values.insert(i, value)
        rdf_values.insert(i, self.to_rdf(value))
        
    def remove(self, value):
        values, rdf_values = self.__get_values()

        self.set_dirty(True)
        values.remove(value)
        rdf_values.remove(self.to_rdf(value))
        
    def pop(self, i = -1):
        values, rdf_values = self.__get_values()

        self.set_dirty(True)
        rdf_values.pop(i)
        return values.pop(i)
    
    def __iter__(self):
        values, _ = self.__get_values()
        return iter(values)
    
    # Shortcuts for querying attributes.
    # It's syntactic sugar around resource.query_attribute(), so instead of 
    #     >>> resource.query_attribute("foaf_knows").limit(3)
    # we can use
    #     >>> resource.foaf_knows.limit(3)  
    
    def __query_attribute(self):
        return self.resource.query_attribute(self.__attribute_name)
    
    def limit(self, value):
        return self.__query_attribute().limit(value)

    def offset(self, value):
        return self.__query_attribute().offset(value)
    
    def full(self, only_direct = False):
        return self.__query_attribute().full(only_direct)
    
    def order(self, value = True):
        return self.__query_attribute().order(value)
    
    def desc(self):
        return self.__query_attribute().desc()
    
    def get_by(self, **kwargs):
        return self.__query_attribute().get_by(**kwargs)

    def context(self, context):
        return self.__query_attribute().context(context)

        
        
        
        
    
    