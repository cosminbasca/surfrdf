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

from surf.rdf import Namespace

# TODO lazy loading ... not implemented when setting the resource from the json_dict ...
class Rest(object):
    ''' The :class:`Rest` class handles the generation of REST like methods to
    perform CRUD operations on a :class:`surf.resource.Resource` class

    note: The REST api exposed is designed in accordance with the REST controller
    used in `pylons` applications, it adheres to the REST specification and offers
    extra features'''
    def __init__(self, resources_namespace, concept_class):
        '''the `resource` is the :class:`surf.resource.Resource` class for which
        the REST interface is exposed,
        the `resources_namespace` represents the URI that instances will be using as
        subjects'''

        self.__concept_class = concept_class

        # Make sure resources_namespace is an instance of Namespace
        if not isinstance(resources_namespace, Namespace):
            resources_namespace = Namespace(resources_namespace)
        
        self.__namespace = resources_namespace

    # the REST methods
    def index(self, offset = None, limit = None):
        '''**REST** : GET /: All items in the collection,
        returns all `instances` for the current `Resource`'''
        return self.__concept_class.all(offset = offset, limit = limit)

    def create(self, json_params):
        '''**REST** : POST /: Create a new item,
        creates a new instance of the current `Resource` type'''
        instance = self.__concept_class()
        for attr_name in json_params:
            setattr(instance, attr_name, json_params[attr_name])
        instance.save()

    def new(self, json_params):
        '''**REST** : GET /new: Form to create a new item.
        creates a new instance of the current `Resource` type'''
        self.create(json_params)

    def update(self, id, json_params):
        '''**REST** : PUT /id: Update an existing item.,
        update an instnaces attributes with the supplied parameters'''
        instance = self.__concept_class(self.__namespace[id])
        for attr_name in json_params:
            setattr(instance, attr_name, json_params[attr_name])
        instance.update()

    def edit(self, id, json_params):
        '''**REST** : GET /id;edit:
        updates an instances attributes with the supplied parameters'''
        self.update(id, json_params)

    def delete(self, id):
        '''**REST** : DELETE /id: Delete an existing item.
        removes the denoted instance from the underlying `store`'''
        instance = self.__concept_class(self.__namespace[id])
        instance.remove()

    def show(self, id):
        '''**REST** : GET /id: Show a specific item.
        show / retrieve the specified resource'''
        instance = self.__concept_class(self.__namespace[id])
        instance.load()
        return instance

    @classmethod
    def resource(cls, session, resources_namespace, concept, id):
        # Make sure resources_namespace is an instance of Namespace
        if not isinstance(resources_namespace, Namespace):
            resources_namespace = Namespace(resources_namespace)

        Concept = session.get_class(concept)
        return Concept(resources_namespace[id])
