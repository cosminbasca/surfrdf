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
import inspect
from surf.rdf import Namespace
from surf.resource import Resource

__author__ = 'Cosmin Basca'


# TODO lazy loading ... not implemented when setting the resource from the json_dict ...
class Rest(object):
    """
    The :class:`Rest` class handles the generation of REST like methods to
    perform CRUD operations on a :class:`surf.resource.Resource` instance

    note: The REST api exposed is designed in accordance with the REST controller
    used in `pylons` applications, it adheres to the REST specification and offers
    extra features

    :param resources_namespace: the `uri` used by instances
    :type resources_namespace: :class:`rdflib.namespace.Namespace` or str
    :param concept_class: the class for which the REST interface is exposed
    :type concept_class: :class:`surf.resource.Resource`
    """

    def __init__(self, resources_namespace, concept_class):
        assert issubclass(concept_class, Resource) and inspect.isclass(concept_class)
        self._Resource = concept_class

        # Make sure resources_namespace is an instance of Namespace
        if not isinstance(resources_namespace, Namespace):
            resources_namespace = Namespace(resources_namespace)

        self._namespace = resources_namespace

    def index(self):
        """
        **REST** : GET /: All items in the collection,

        :return: all instances for the current :class:`surf.resources.Resource`
        :rtype: list or :class:`surf.resources.ResultProxy`
        """
        return self._Resource.all()

    def create(self, json_params):
        """
        **REST** : POST /: Create a new item,
        creates a new :class:`surf.resource.Resource` instance

        :param dict json_params: extra *JSON* parameters to set as instance attributes
        """
        instance = self._Resource()
        for attr_name in json_params:
            setattr(instance, attr_name, json_params[attr_name])
        instance.save()

    def new(self, json_params):
        """
        **REST** : GET /new: Form to create a new item.
        alias for :meth:`surf.rest.Rest.create` method

        :param dict json_params: extra *JSON* parameters to set as instance attributes
        """
        self.create(json_params)

    def update(self, id, json_params):
        """
        **REST** : PUT /id: Update an existing item.,
        update an instances attributes with the supplied parameters

        :param str id: the resources id
        :param dict json_params: extra *JSON* parameters to set as instance attributes
        """
        instance = self._Resource(self._namespace[id])
        for attr_name in json_params:
            setattr(instance, attr_name, json_params[attr_name])
        instance.update()

    def edit(self, id, json_params):
        """
        **REST** : GET /id;edit:
        alias for :meth:`surf.rest.Rest.update` method

        :param str id: the resources id
        :param dict json_params: extra *JSON* parameters to set as instance attributes
        """
        self.update(id, json_params)

    def delete(self, id):
        """
        **REST** : DELETE /id: Delete an existing item.
        removes an instance from the underlying :class:`surf.store.Store` store

        :param str id: the resources id
        """
        instance = self._Resource(self._namespace[id])
        instance.remove()

    def show(self, id):
        """
        **REST** : GET /id: Show a specific item.
        show / retrieve the specified resource

        :param str id: the resources id
        :return: the resource
        :rtype: :class:`surf.resources.Resource`
        """
        instance = self._Resource(self._namespace[id])
        instance.load()
        return instance

    @classmethod
    def resource(cls, session, resources_namespace, concept_class, id):
        """
        convenience method to get a resource given the arguments

        :param session: the *SuRF* session
        :type session: :class:`surf.session.Session`
        :param resources_namespace: the `uri` used by instances
        :type resources_namespace: :class:`rdflib.namespace.Namespace` or str
        :param concept_class: the class for which the REST interface is exposed
        :type concept_class: :class:`surf.resource.Resource`
        :param str id: the resources id
        :return: the resource
        :rtype: :class:`surf.resources.Resource`
        """
        # Make sure resources_namespace is an instance of Namespace
        if not isinstance(resources_namespace, Namespace):
            resources_namespace = Namespace(resources_namespace)

        _Resource = session.get_class(concept_class)
        return _Resource(resources_namespace[id])
