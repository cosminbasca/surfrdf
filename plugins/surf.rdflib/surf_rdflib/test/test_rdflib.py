""" Module for rdflib plugin tests. """

from unittest import TestCase

import surf
from surf.test.plugin import PluginTestMixin

class RdflibTestMixin(object):

    def _get_store_session(self, use_default_context = True):
        """ Return initialized SuRF store and session objects. """

        # FIXME: take endpoint from configuration file,
        # maybe we can mock SPARQL endpoint.
        kwargs = {"reader": "rdflib",
                  "writer" : "rdflib"}

        if False: #use_default_context:
            kwargs["default_context"] = "http://surf_test_graph/dummy2"

        store = surf.Store(**kwargs)
        session = surf.Session(store)

        # Fresh start!
        #store.clear("http://surf_test_graph/dummy2")
        #store.clear(URIRef("http://my_context_1"))
        #store.clear(URIRef("http://other_context_1"))
        store.clear()

        return store, session

class StandardPluginTest(TestCase, RdflibTestMixin, PluginTestMixin):
    pass
