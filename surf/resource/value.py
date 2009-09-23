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

class ResourceValue(list):
    def __init__(self,sequence,resource,predicate,direct):
        list.__init__(self,sequence)
        self.resource = resource
        self.predicate = predicate
        self.direct = direct

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
    
    def __setitem__(self, key, value):
        if hasattr(self.resource, 'value_set_item'):
            self.resource.value_set_item(key, value, self.predicate, self.direct)
        list.__setitem__(self, key, value)
        
    def __delitem__(self, key):
        if hasattr(self.resource, 'value_del_item'):
            self.resource.value_del_item(key, self.predicate, self.direct)
        list.__delitem__(self, key)
    
    # implement the other list methods 