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
    def __init__(self, values_source, resource, attribute_name):
        list.__init__(self)

        self.resource = resource

        # So we know which attribute this ResourceValue object represents
        self.__attribute_name = attribute_name

        # For lazy loading list contents
        self.__values_source = values_source
        self.__data_loaded = False

    def __prepare_values(self):
        if not self.__data_loaded:
            self[:], self.__rdf_values = self.__values_source()
            self.__data_loaded = True

    def get_one(self):
        self.__prepare_values()

        if len(self) == 1:
            return self[0]
        elif len(self) == 0:
            raise Exception('list is empty')
        else:
            raise Exception('list has more elements than one')

    one = property(fget = get_one)

    def get_first(self):
        self.__prepare_values()

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

        raise Exception("to_rdf has no reference to resource")

    def __len__(self):
        self.__prepare_values()
        return list.__len__(self)

    def __contains__(self, key):
        # For now, load all values. In future, if the data is not yet loaded,
        # we can optimize and do ASK query here. 
        self.__prepare_values()
        return self.to_rdf(key) in self.__rdf_values 

    def __getitem__(self, key):
        self.__prepare_values()
        return list.__getitem__(self, key)

    def __setitem__(self, key, value):
        self.__prepare_values()

        self.set_dirty(True)
        self.__rdf_values[key] = self.to_rdf(value)
        return list.__setitem__(self, key, value)

    def __delitem__(self, key):
        self.__prepare_values()

        self.set_dirty(True)
        del self.__rdf_values[key]
        return list.__delitem__(self, key)

    def append(self, value):
        self.__prepare_values()

        self.set_dirty(True)
        self.__rdf_values.append(self.to_rdf(value))
        return list.append(self, value)

    def extend(self, L):
        self.__prepare_values()

        self.set_dirty(True)
        self.__rdf_values.extend([self.to_rdf(value) for value in L])
        return list.extend(self, L)

    def insert(self, i, value):
        self.__prepare_values()

        self.set_dirty(True)
        self.__rdf_values.insert(i, self.to_rdf(value))
        return list.insert(self, i, value)

    def remove(self, value):
        self.__prepare_values()

        self.set_dirty(True)
        self.__rdf_values.remove(self.to_rdf(value))
        return list.remove(self, value)

    def pop(self, i = -1):
        self.__prepare_values()

        self.set_dirty(True)
        self.__rdf_values.pop(i)
        return list.pop(self, i)

    def __iter__(self):
        self.__prepare_values()
        return list.__iter__(self)

    def __str__(self):
        self.__prepare_values()
        return list.__str__(self)

    def __repr__(self):
        self.__prepare_values()
        return list.__repr__(self)

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