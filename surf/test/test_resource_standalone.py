import pytest

import surf
import surf.store
from surf import ns
from surf.plugin import query_reader
from surf.resource import ResultProxy

@pytest.fixture
def default_session():
    """
    Prepare store and session.
    """

    # Hack to make RDFQueryReader available as it was provided by plugin.
    surf.plugin.manager.__readers__["query_reader"] = query_reader.RDFQueryReader

    store = surf.Store(reader="query_reader", use_subqueries=True)
    return surf.Session(store)


def test_get_by():
    """
    Test Resource.get_by() method.
    """

    store = surf.Store()
    session = surf.Session(store)
    Person = session.get_class(ns.FOAF['Person'])

    persons = Person.get_by(foaf_name=u"John")
    assert isinstance(persons, (list, ResultProxy))
