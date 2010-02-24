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

    def _get_by(self, params):

        return []

    #public interface
    def get(self, resource, attribute, direct):
        """ Return the `value(s)` of the corresponding `attribute`.

        If ``direct`` is `False` then the subject of the ``resource`` is
        considered the object of the query.

        """

        subj = hasattr(resource, 'subject') and resource.subject or resource
        return self._get(subj, attribute, direct, resource.context)

    def load(self, resource, direct):
        """ Fully load the ``resource`` from the `store`.

        This method returns all statements about the `resource`.

        If ``direct`` is `False`, then the subject of the ``resource``
        is considered the object of the query

        """

        subj = hasattr(resource, 'subject') and resource.subject or resource
        return self._load(subj, direct, resource.context)

    def is_present(self, resource):
        """ Return `True` if the ``resource`` is present in the `store`. """

        subj = hasattr(resource, 'subject') and resource.subject or resource
        return self._is_present(subj, resource.context)

    def concept(self, resource):
        """ Return the `concept` URI of the following `resource`.

        `resource` can be a `string` or a `URIRef`.

        """

        subj = hasattr(resource, 'subject') and resource.subject or resource
        return self._concept(subj)

    def instances_by_attribute(self, resource, attributes, direct, context):
        """
        Return all `URIs` that are instances of ``resource`` and
        have the specified `attributes`.

        If ``direct`` is `False`, than the subject of the ``resource``
        is considered the object of the query.

        """

        concept = hasattr(resource, 'uri') and  resource.uri or resource
        return self._instances_by_attribute(concept, attributes, direct,
                                            context)

    def get_by(self, params):
        return self._get_by(params)
