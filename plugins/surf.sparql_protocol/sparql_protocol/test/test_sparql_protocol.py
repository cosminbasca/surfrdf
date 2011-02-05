# -*- coding: UTF-8 -*-
""" Module for sparql_protocol plugin tests. """

from unittest import TestCase

from sparql_protocol.reader import SparqlReaderException
from sparql_protocol.writer import SparqlWriterException

import surf
from surf.query import select
from surf.rdf import Literal, URIRef
from surf.exc import CardinalityException
from surf.test.plugin import PluginTestMixin

class SparqlProtocolTestMixin(object):

    def _get_store_session(self, use_default_context = True):
        """ Return initialized SuRF store and session objects. """

        # FIXME: take endpoint from configuration file,
        # maybe we can mock SPARQL endpoint.
        kwargs = {"reader": "sparql_protocol",
                  "writer" : "sparql_protocol",
                  "endpoint" : "http://localhost:9980/sparql",
                  "use_subqueries" : True,
                  "combine_queries" : True}

        if True: #use_default_context:
            kwargs["default_context"] = "http://surf_test_graph/dummy2"

        store = surf.Store(**kwargs)
        session = surf.Session(store)

        # Fresh start!
        store.clear("http://surf_test_graph/dummy2")

        return store, session

class StandardPluginTest(TestCase, SparqlProtocolTestMixin, PluginTestMixin):
    pass

class TestSparqlProtocol(TestCase, SparqlProtocolTestMixin):
    """ Tests for sparql_protocol plugin. """

    def test_to_rdflib(self):
        """ Test _toRdflib with empty bindings.  """

        data = {'results' : {'bindings' : [{'c' : {}}]}}

        # This should not raise exception.
        store = surf.store.Store(reader = "sparql_protocol")
        store.reader._toRdflib(data)

    def test_exceptions(self):
        """ Test that exceptions are raised on invalid queries. """

        store = surf.Store(reader = "sparql_protocol",
                           writer = "sparql_protocol",
                           endpoint = "invalid")

        def try_query():
            store.execute(query)

        query = select("?a")
        self.assertRaises(SparqlReaderException, try_query)

        def try_add_triple():
            store.add_triple("?s", "?p", "?o")

        self.assertRaises(SparqlWriterException, try_add_triple)
