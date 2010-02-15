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
from surf.plugin.reader import RDFReader
from surf.rdf import BNode, ConjunctiveGraph, Literal, RDF, URIRef

class InvalidResourceException(Exception):
    def __init__(self,*args,**kwargs):
        super(InvalidResourceException,self).__init__(self,*args,**kwargs)

class RDFWriter(Plugin):
    """ Super class for all surf Writer plugins. """

    def __init__(self,reader, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        if isinstance(reader,RDFReader):
            self.__reader = reader
        else:
            raise ValueError('The reader plugin must be of type RDFReader not %s'%(str(type(reader))))

    reader = property(fget = lambda self: self.__reader)

    #protected interface
    def _clear(self,context = None):
        pass

    def _save(self, *resources):
        pass

    def _update(self, *resources):
        pass

    def _remove(self, *resources, **kwargs):
        pass

    def _size(self):
        return -1

    def _add_triple(self, s = None, p = None, o = None, context = None):
        pass

    def _set_triple(self, s = None, p = None, o = None, context = None):
        pass

    def _remove_triple(self, s = None, p = None, o = None, context = None):
        pass


    #public interface
    def clear(self, context = None):
        """ Remove all triples from the `store`.

        If ``context`` is specified, only the specified context will
        be cleared.

        """

        self._clear(context = context)

    def save(self, *resources):
        """ Replace the ``*resources`` in store with their current state. """

        for resource in resources:
            if not hasattr(resource, "subject"):
                raise InvalidResourceException("Arguments must be of type surf.resource.Resource")

        self._save(*resources)

    def update(self, *resources):
        """ Update the ``*resources`` to the `store` - persist. """

        for resource in resources:
            if not hasattr(resource, "subject"):
                raise InvalidResourceException("Arguments must be of type surf.resource.Resource")

        self._update(resource)

    def remove(self, *resources, **kwargs):
        """ Completely remove the ``*resources`` from the `store`. """

        #TODO: decide whether triples that are indirect (belong to other 
        # resource should be removed as well)
        for resource in resources:
            if not hasattr(resource, "subject"):
                raise InvalidResourceException("Arguments must be of type surf.resource.Resource")

        self._remove(*resources, **kwargs)

    def size(self):
        """ Return the number of `triples` in the current `store`. """

        return self._size()

    # triple level access methods
    def add_triple(self, s = None, p = None, o = None, context = None):
        """ Add a triple to the `store`, in the specified ``context``.

        `None` can be used as a wildcard.

        """

        self._add_triple(s, p, o, context)

    def set_triple(self, s = None, p = None, o = None, context = None):
        """ Replace a triple in the `store` and specified ``context``.

        `None` can be used as a wildcard.

        """

        self._set_triple(s,p,o,context)

    def remove_triple(self,s=None,p=None,o=None, context=None):
        """ Remove a triple from the `store`, from the specified ``context``.

        `None` can be used as a wildcard.

        """

        self._remove_triple(s,p,o,context)

    # management
    def close(self):
        """ Close the `plugin`. """

        pass

    def index_triples(self,**kwargs):
        """ Perform `index` of the `triples` if such functionality is present.

        Return `True` if operation successful.

        """

        return False

    def load_triples(self,**kwargs):
        """ Load `triples` from supported `sources` if such functionality is
        present.

        Return `True` if operation successful.

        """

        return False