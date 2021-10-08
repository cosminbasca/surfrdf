from builtins import str
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
from future.utils import raise_
__author__ = 'Cosmin Basca'

import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import EndPointNotFound, QueryBadFormed

from surf.util import json_to_rdflib
from surf.plugin.query_reader import RDFQueryReader
from surf.log import *


class SparqlReaderException(Exception):
    pass


class ReaderPlugin(RDFQueryReader):
    def __init__(self, *args, **kwargs):
        super(ReaderPlugin, self).__init__(*args, **kwargs)

        self._endpoint = kwargs['endpoint'] if 'endpoint' in kwargs else None
        self._results_format = JSON

        self._sparql_wrapper = SPARQLWrapper(self._endpoint, returnFormat=self._results_format)
        user = kwargs.get('user', None)
        password = kwargs.get('password', None)
        if user is not None and password is not None:
            self._sparql_wrapper.setCredentials(user, password)

        if kwargs.get("use_keepalive", "").lower().strip() == "true":
            if hasattr(SPARQLWrapper, "setUseKeepAlive"):
                self._sparql_wrapper.setUseKeepAlive()

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def results_format(self):
        return self._results_format

    def _to_table(self, result):
        if not isinstance(result, dict):
            return result

        if "results" not in result:
            return result

        converted = []
        for binding in result["results"]["bindings"]:
            rdf_item = {}
            for key, obj in list(binding.items()):
                try:
                    rdf_item[key] = json_to_rdflib(obj)
                except ValueError:
                    continue
            converted.append(rdf_item)

        return converted

    def _ask(self, result):
        """
        returns the boolean value of a ASK query
        """
        return result.get("boolean")

    def execute_sparql(self, q_string, format='JSON'):
        try:
            debug(q_string)
            self._sparql_wrapper.setQuery(q_string)
            return self._sparql_wrapper.query().convert()
        except EndPointNotFound as _:
            raise_(SparqlReaderException, "Endpoint not found", sys.exc_info()[2])
        except QueryBadFormed as _:
            raise_(SparqlReaderException, "Bad query: %s" % q_string, sys.exc_info()[2])
        except Exception as e:
            raise_(SparqlReaderException, "Exception: %s" % e, sys.exc_info()[2])

    def _execute(self, query):
        return self.execute_sparql(str(query))

    def close(self):
        pass
