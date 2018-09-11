# -*- coding: UTF-8 -*-
from builtins import str
import pytest
import surf
from surf.query import select
from surf.rdf import Literal, URIRef
from surf.exceptions import CardinalityException
from surf.plugin.sparql_protocol.reader import SparqlReaderException
from surf.plugin.sparql_protocol.writer import SparqlWriterException


@pytest.fixture
def get_store_session():
    """
    Return initialized SuRF store and session objects.
    """

    # maybe we can mock SPARQL endpoint.
    kwargs = {"reader": "sparql_protocol",
              "writer": "sparql_protocol",
              "endpoint": "http://localhost:9980/sparql",
              "use_subqueries": True,
              "combine_queries": True}

    if True:  # use_default_context:
        kwargs["default_context"] = "http://surf_test_graph/dummy2"

    store = surf.Store(**kwargs)
    session = surf.Session(store)

    # Fresh start!
    store.clear("http://surf_test_graph/dummy2")
    store.clear(URIRef("http://my_context_1"))
    store.clear(URIRef("http://other_context_1"))

    return store, session


def test_to_table():
    """
    Test _to_table with empty bindings.
    """

    data = {'results': {'bindings': [{'c': {}}]}}

    # This should not raise exception.
    try:
        store = surf.store.Store(reader="sparql_protocol")
        store.reader._to_table(data)
    except Exception as e:
        pytest.fail(e.message, pytrace=True)


def test_exceptions():
    """
    Test that exceptions are raised on invalid queries.
    """

    store = surf.Store(reader="sparql_protocol", writer="sparql_protocol", endpoint="invalid")

    def try_query():
        store.execute(query)

    query = select("?a")
    with pytest.raises(SparqlReaderException):
        try_query()

    def try_add_triple():
        store.add_triple("?s", "?p", "?o")

    with pytest.raises(SparqlWriterException):
        try_add_triple()
