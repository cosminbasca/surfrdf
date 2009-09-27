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

from surf.util import value_to_rdf

class ResourceValue(list):
    def __init__(self,sequence,resource,rdf_values):
        list.__init__(self,sequence)
        self.resource = resource
        self.rdf_values =rdf_values

    def get_one(self):
        if len(self) == 1:
            return self[0]
        else:
            raise Exception('list has more elements than one')
    one = property(fget = get_one)
    
    def get_first(self):
        if len(self) > 0:
            return self[0]
        else:
            return None
    first = property(fget = get_first)
    
    def set_dirty(self, dirty):
        if hasattr(self.resource, 'dirty'):
            self.resource.dirty = dirty
            
    def to_rdf(self, value):
        if hasattr(self.resource, 'to_rdf'):
            return self.resource.to_rdf(value)
        return value_to_rdf(value)
    
    def __setitem__(self, key, value):
        self.rdf_values[key] = self.to_rdf(item_value)
        self.set_dirty(True)
        list.__setitem__(self, key, value)
        
    def __delitem__(self, key):
        del self.rdf_values[key]
        self.set_dirty(True)
        list.__delitem__(self, key)
    
    def append(self, value):
        self.rdf_values.append(self.to_rdf(value))
        self.set_dirty(True)
        list.append(self, value)
        
    def extend(self, L):
        self.rdf_values.extend([self.to_rdf(value) for value in L])
        self.set_dirty(True)
        list.extend(self, L)
        
    def insert(self, i, value):
        self.rdf_values.insert(i, self.to_rdf(value))
        self.set_dirty(True)
        list.insert(self, i, value)
        
    def remove(self, value):
        self.rdf_values.remove(self.to_rdf(value))
        self.set_dirty(True)
        list.remove(self, value)
        
    def pop(self, i = -1):
        self.rdf_values.pop(i)
        self.set_dirty(True)
        list.pop(self, i)
    