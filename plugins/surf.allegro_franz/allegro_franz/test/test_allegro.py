""" Module for allegro_franz plugin tests. """

from unittest import TestCase

from rdflib import URIRef
import surf
from surf.test.plugin import PluginTestMixin

class AllegroFranzTestMixin(object):

    def _get_store_session(self, use_default_context = True):
        """ Return initialized SuRF store and session objects. """

        # FIXME: take endpoint from configuration file,
        kwargs = {"reader": "allegro_franz",
                  "writer" : "allegro_franz",
                  "server" : "localhost",
                  "port" : 6789,
                  "catalog" : "repositories",
                  "repository" : "test_surf"}

        if use_default_context:
            kwargs["default_context"] = URIRef("http://surf_test_graph/dummy2")

        store = surf.Store(**kwargs)
        session = surf.Session(store)

        # Fresh start!
        store.clear(URIRef("http://surf_test_graph/dummy2"))
        store.clear(URIRef("http://my_context_1"))
        store.clear(URIRef("http://other_context_1"))
        store.clear()

        return store, session

class StandardPluginTest(TestCase, AllegroFranzTestMixin, PluginTestMixin):
    pass
