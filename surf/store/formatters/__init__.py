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

import logging

'''
formats the results for the Resource, based on a result type
'''
from surf.store.plugins import AbstractMount

class FormatterPluginMount(AbstractMount):
    pass

class RDFFormatter(object):
    __metaclass__ = FormatterPluginMount
    __type__ = AbstractMount.default
    
    def __init__(self,*args,**kwargs):
        logging.basicConfig()
        self.log = logging.getLogger('Formatter %s '%self.__type__)
        self.log.setLevel(logging.NOTSET)
    
    def enable_logging(self,enable=True):
        if enable:
            self.log.setLevel(logging.DEBUG)
        else :
            self.log.setLevel(logging.NOTSET)
    
    @classmethod
    def get_type(cls):
        return cls.__type__
    
    # to implement
    def _predicate_dict(self,results,value_key,concept_key):
        return results
    
    def _predicates_dict(self,results,predicate_key,value_key,concept_key):
        return results
    
    def _convert_to_rdftypes(self,results):
        return results
    
    # to use
    def predicate_dict(self,results,value_key,concept_key):
        return self._predicate_dict(self._convert_to_rdftypes(results),value_key, concept_key)
    
    def predicates_dict(self,results,predicate_key,value_key,concept_key):
        return self._predicates_dict(self._convert_to_rdftypes(results), predicate_key,value_key, concept_key)

# intialize formatter plugins
import jsonformatter