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
import logging
from surf.query import Query

# the rdf way
#from rdf.graph import ConjunctiveGraph
#from rdf.term import URIRef, BNode, Literal, RDF
# the rdflib 2.4.x way
from rdflib.Graph import ConjunctiveGraph
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.Literal import Literal
from rdflib.RDF import RDFNS as RDF

class RDFReader(Plugin):
    '''
    super class for all surf Reader Plugins
    '''
    #protected interface
    def _get(self,subject,attribute,direct):
        return None
    
    def _load(self,subject):
        return {}
    
    def _is_present(self,subject):
        return False
    
    def _all(self,concept,limit=None,offset=None):
        return []
        
    def _concept(self,subject):
        return None
    
    def _instances_by_attribute(self,concept,attributes,direct):
        return []
        
    def _instances(self,concept,direct,filter,predicates):
        return []
        
    def _instances_by_value(self,concept,direct,attributes):
        return []
    
    
    #public interface
    def get(self,resource,attribute,direct):
        '''
        returns the value(s) of the corresponding attribute
        '''
        subj = resource.subject if hasattr(resource, 'subject') else resource
        return self._get(subj, attribute, direct)
        
    def load(self,resource,direct):
        '''
        fully loads the resource from the store, returns all statements about the resource
        '''
        subj = resource.subject if hasattr(resource, 'subject') else resource
        return self._load(subj,direct)
        
    def is_present(self,resource):
        '''
        True if the resource is present in the store, False otherwise
        '''
        subj = resource.subject if hasattr(resource, 'subject') else resource
        return self._is_present(subj)
        
    def all(self,concept,limit=None,offset=None):
        '''
        returns all uri's that are instances of concept within [limit,limit+offset]
        '''
        con = concept.uri if hasattr(concept, 'uri') else concept
        return self._all(con,limit=limit,offset=offset)
        
    def concept(self,resource):
        '''
        returns the concept URI of the following resource,
        resource can be a string or a URIRef
        '''
        subj = resource.subject if hasattr(resource, 'subject') else resource
        return self._concept(subj)
        
    def instances_by_attribute(self,resource,attributes,direct):
        '''
        returns all uri's that are instances of concept that have the attributes
        '''
        con = concept.uri if hasattr(concept, 'uri') else concept
        return self._instances_by_attribute(con,attributes,direct)
        
    def instances(self,resource,direct,filter,predicates):
        con = concept.uri if hasattr(concept, 'uri') else concept
        return self._instances(con,direct,filter,predicates)
        
    def instances_by_value(self,resource,direct,attributes):
        con = concept.uri if hasattr(concept, 'uri') else concept
        return self._instances_by_value(con,direct,attributes)
        
