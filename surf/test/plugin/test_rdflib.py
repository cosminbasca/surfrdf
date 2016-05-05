import pytest
import surf
import os
from rdflib.term import Literal

_card_file = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'card.rdf')


def test_rdflib_store():
    """
    Create a SuRF rdflib based store
    """

    kwargs = {"reader": "rdflib", "writer": "rdflib"}

    if False:  # use_default_context:
        kwargs["default_context"] = "http://surf_test_graph/dummy2"

    try:
        store = surf.Store(**kwargs)
        session = surf.Session(store)

        # clean store
        store.clear()
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_rdflib_load():
    store = surf.Store(reader="rdflib",
                       writer="rdflib",
                       rdflib_store="IOMemory")

    print "Load RDF data"
    store.load_triples(source=_card_file)
    assert len(store) == 76


def test_rdflib_query():
    store = surf.Store(reader="rdflib",
                       writer="rdflib",
                       rdflib_store="IOMemory")
    session = surf.Session(store)
    store.load_triples(source=_card_file)

    Person = session.get_class(surf.ns.FOAF["Person"])
    all_persons = Person.all()

    assert len(all_persons) == 1
    assert all_persons.one().foaf_name.first == Literal(u'Timothy Berners-Lee')
