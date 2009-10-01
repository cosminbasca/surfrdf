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
    """ Super class for all surf Reader plugins. """

    #protected interface
    def _get(self, subject, attribute, direct, context):
        """ To be implemented by classes that inherit `RDFReader`.
        
        This method is called directly by :meth:`get`. 
        
        """
        
        return None
    
    def _load(self, subject, context):
        """ To be implemented by classes that inherit `RDFReader`.        
        
        This method is called directly by :meth:`load`.
        
        """
        
        return {}
    
    def _is_present(self, subject, context):
        """ To be implemented by classes that inherit `RDFReader`.
        
        This method is called directly by :meth:`is_present`.
        
        """
        
        return False
    
    def _all(self, concept, limit = None, offset = None, 
             full = False, context = None):
        """ To be implemented by classes that inherit `RDFReader`.
        
        This method is called directly by :meth:`all`.
        
        """
        
        return []
        
    def _concept(self,subject):
        """ To be implemented by classes that inherit `RDFReader`.
        
        This method is called directly by :meth:`concept`. 
        
        """
        
        return None
    
    def _instances_by_attribute(self, concept, attributes, direct, context):
        """ To be implemented by classes that inherit `RDFReader`.
        
        This method is called directly by :meth:`instances_by_attribute`.
        
        """
        
        return []
        
    def _instances(self, concept, direct, filter, predicates, context):
        """ To be implemented by classes that inherit `RDFReader`.
        
        This method is called directly by :meth:`instances`.
        
        """
        
        return []
        
    def _instances_by_value(self,concept,direct,attributes):
        """ To be implemented by classes that inherit `RDFReader`.
        
        This method is called directly by `instances_by_value`. 
        
        """
        
        return []
    
    
    #public interface
    def get(self, resource, attribute, direct):
        """ Return the `value(s)` of the corresponding `attribute`.
        
        If ``direct`` is `False` then the subject of the ``resource`` is 
        considered the object of the query. 
        
        """
        
        subj = resource.subject if hasattr(resource, 'subject') else resource
        return self._get(subj, attribute, direct, resource.context)
        
    def load(self, resource, direct):
        """ Fully load the ``resource`` from the `store`.
        
        This method returns all statements about the `resource`.
        
        If ``direct`` is `False`, then the subject of the ``resource`` 
        is considered the object of the query
        
        """
        
        subj = resource.subject if hasattr(resource, 'subject') else resource
        return self._load(subj, direct, resource.context)
        
    def is_present(self, resource):
        """ Return `True` if the ``resource`` is present in the `store`. """
        
        subj = resource.subject if hasattr(resource, 'subject') else resource
        return self._is_present(subj, resource.context)
        
    def all(self, concept, limit = None, offset = None, 
            full = False, context = None):
        """ Return information about instances of `concept`. 
        
        This method would normally return list of URIs. For example::
        
            >>> Person = surf.ns.FOAF["Person"]
            >>> reader = session.default_store.reader
            >>> reader.all(Person)
            [rdflib.URIRef('http://p1'), rdflib.URIRef('http://p2')]
        
        If parameter ``full`` is set to `True` and reader plugin is instructed
        to use sub queries (:attr:`surf.store.Store.use_subqueries` is 
        set to `True`), then this method will return 
        {subject : attrs_values, ... } dictionary::
        
            >>> Person = surf.ns.FOAF["Person"]
            >>> reader = session.default_store.reader
            >>> reader.all(Person, full = True)
            {rdflib.URIRef('http://p1'): { pred  : { value  : class, value2 : class2 },
                                           pred2 : { value3 : class3 }},
             ...
            }   
                                        
        """
        
        con = concept.uri if hasattr(concept, 'uri') else concept
        return self._all(con, limit = limit, offset = offset, 
                         full = full, context = context)
        
    def concept(self, resource):
        """ Return the `concept` URI of the following `resource`.
        
        `resource` can be a `string` or a `URIRef`.
        
        """
        
        subj = resource.subject if hasattr(resource, 'subject') else resource
        return self._concept(subj)
        
    def instances_by_attribute(self, resource, attributes, direct, context):
        """
        Return all `URIs` that are instances of ``resource`` and 
        have the specified `attributes`.
        
        If ``direct`` is `False`, than the subject of the ``resource`` 
        is considered the object of the query. 
        
        """
        
        concept = resource.uri if hasattr(resource, 'uri') else resource
        return self._instances_by_attribute(concept, attributes, direct, 
                                            context)
        
    def instances(self, resource, direct, filter, predicates, context):
        """ 
        Return all `URIs` that are instances of ``resource`` and have the
        specified `predicates` - a `dict` where the key is the shorthand 
        notation, and the value is the predicate value.
        
        If ``direct`` is `False`, than the subject of the ``resource`` is 
        considered the object of the query.
        
        .. code-block:: python
            
            store.instances(resource, True, None, {'foaf_name' : 'John Doe'})
            
        """
        
        concept = resource.uri if hasattr(resource, 'uri') else resource
        #TODO: make sure uri's are passed further
        return self._instances(concept, direct, filter, predicates, context)
        
    def instances_by_value(self, resource, direct, attributes):
        """
        Return all `URIs` that are instances of ``resource`` as values and
        that have the specified ``attributes``.
        
        If ``direct`` is `False`, than the subject of the ``resource`` is 
        considered the object of the query.
        
        """
        
        concept = resource.uri if hasattr(resource, 'uri') else resource
        return self._instances_by_value(concept,direct,attributes)
        
