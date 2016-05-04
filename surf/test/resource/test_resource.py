import pytest
import surf
from surf import Resource
from surf.rdf import URIRef
from surf.util import uri_split
from rdflib.term import Literal


@pytest.fixture
def store_session():
    """ Return initialized SuRF store and session objects. """

    store = surf.Store(reader="rdflib", writer="rdflib")
    session = surf.Session(store)
    return store, session


def test_empty_attribute_sync(store_session):
    """
    Test synchronization between empty attribute and rdf_direct.
    """

    _, session = store_session
    instance = session.get_resource("http://smth", surf.ns.OWL["Thing"])
    assert len(instance.rdf_direct) == 1

    # Poke foaf_name so it gets initialized
    list(instance.foaf_name)

    # Append value
    instance.foaf_name.append("John")

    assert len(instance.rdf_direct) == 2
    assert len(instance.rdf_direct[surf.ns.FOAF["name"]]) == 1


def test_loaded_attribute_sync(store_session):
    """
    Test synchronization between loaded attribute and rdf_direct.
    """

    _, session = store_session
    instance = session.get_resource("http://smth", surf.ns.OWL["Thing"])
    instance.foaf_name = "John"
    instance.save()

    instance = session.get_resource("http://smth", surf.ns.OWL["Thing"])
    # Load foaf_name
    list(instance.foaf_name)
    # rdf_direct should contain two attributes now
    assert len(instance.rdf_direct) == 2
    assert len(instance.rdf_direct[surf.ns.FOAF["name"]]) == 1


def test_class_mapping(store_session):
    """
    Test class mapping.
    """

    class MyPerson(object):
        def get_something(self):
            pass

    _, session = store_session
    session.mapping[surf.ns.FOAF.Person] = [MyPerson]

    # Class-level tests.
    cls = session.get_class(surf.ns.FOAF.Person)

    assert issubclass(cls, surf.Resource)
    assert issubclass(cls, MyPerson)
    assert hasattr(cls, "get_something")

    # Instance-level tests.

    instance = session.get_resource("http://someuri", surf.ns.FOAF.Person)

    assert isinstance(instance, surf.Resource)
    assert isinstance(instance, MyPerson)
    assert hasattr(instance, "get_something")


def test_class_instances(store_session):
    """
    Test that dirty class instances are not lost to GC.
    """

    _, session = store_session

    # Class-level tests.
    cls = session.get_class(surf.ns.FOAF.Person)
    for i in range(0, 100):
        c = cls("http://test_instance_%d" % i)
        # Make some changes to instance to trigger its "dirty" state.
        c.rdfs_comment = "Test Instance %d" % i

    assert len(Resource._dirty_instances) == 100
    session.commit()
    assert len(Resource._dirty_instances) == 0


def test_init_namespace(store_session):
    """
    Test resource initialization in specified namespace.
    """

    _, session = store_session

    Person = session.get_class(surf.ns.FOAF.Person)
    surf.ns.register(nstest="http://example.com/ns#")

    # namespace is an instance of Namespace
    p = Person(namespace=surf.ns.NSTEST)
    ns, _ = uri_split(p.subject)
    assert ns == "NSTEST"

    # namespace is an instance of URIRef
    p = Person(namespace=URIRef("http://example.com/ns#"))
    ns, _ = uri_split(p.subject)
    assert ns == "NSTEST"

    # namespace is string
    p = Person(namespace="http://example.com/ns#")
    ns, _ = uri_split(p.subject)
    assert ns == "NSTEST"


def test_default_namespace(store_session):
    """
    Test resource initialization in specified namespace.
    """

    _, session = store_session

    Person = session.get_class(surf.ns.FOAF.Person)
    surf.ns.register_fallback("http://example.com/ns#")
    p = Person()
    assert unicode(p.subject).startswith("http://example.com/ns#")


def test_multiple_sessions(store_session):
    """
    Test that multiple sessions coexist correctly.
    """

    s1 = surf.Session(surf.Store(reader="rdflib"))
    P = s1.get_class(surf.ns.FOAF.Person)

    assert P.session == s1

    _ = surf.Session(surf.Store(reader="rdflib"))

    # Making another session shouldn't change session of already
    # instantiated classes and instances:
    assert P.session == s1


def test_instance(store_session):
    """
    Test Resource._instance().
    """

    try:
        _, session = store_session
        Thing = session.get_class(surf.ns.OWL.Thing)

        subject = surf.ns.SURF.test1
        Thing._instance(subject, [surf.ns.OWL.Thing], store=Thing.store_key)
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


@pytest.mark.skip(reason="type mapping hasn't been implemented yet")
def test_type_mapping(store_session):
    """
    Test that XSD types are mapped to Python types.
    """

    _, session = store_session
    Thing = session.get_class(surf.ns.OWL.Thing)

    t1 = Thing("http://t1")
    t1.surf_string_value = "text"
    t1.surf_bool_value = True
    t1.surf_float_value = 3.14
    t1.surf_int_value = 2010
    t1.save()

    t1 = Thing("http://t1")
    assert type(t1.surf_string_value.first) == unicode
    assert type(t1.surf_bool_value.first) == bool
    assert type(t1.surf_float_value.first) == float
    assert type(t1.surf_int_value.first) == int


def test_dict_access():
    """
    Test that resources support dictionary-style attribute access.
    """

    session = surf.Session(surf.Store(reader="rdflib"))
    Person = session.get_class(surf.ns.FOAF.Person)
    person = Person()
    person.foaf_name = "John"

    # Reading
    assert person["foaf_name"].first == Literal(u"John")
    assert person[surf.ns.FOAF.name].first == Literal(u"John")

    # Writing
    person["foaf_name"] = "Dave"
    assert person.foaf_name.first == Literal(u"Dave")

    # Deleting
    del person["foaf_name"]
    assert person.foaf_name.first is None


def test_auto_load():
    """
    Test that session.auto_load works.
    """

    store = surf.Store(reader="rdflib", writer="rdflib")
    session = surf.Session(store, auto_load=True)
    Person = session.get_class(surf.ns.FOAF.Person)
    person = Person()
    person.foaf_name = "John"
    person.save()

    same_person = Person(person.subject)
    # Check that rdf_direct is filled
    assert surf.ns.FOAF.name in same_person.rdf_direct


def test_query_attribute_unicode(store_session):
    """
    Test that query_attribute calls ResultProxy with string arguments.

    query_attribute sets up and returns ResultProxy instance. Here we test
    that it doesn't pass unicode keywords to it, these don't work
    in Python 2.6.2.
    """

    def mock_get_by(self, **kwargs):
        """ Verify that all passed keywords are strings. """

        for keyword in kwargs.keys():
            assert isinstance(keyword, str), \
                "Passed non-string keyword: %s" % keyword

    _, session = store_session
    resource = session.get_resource("http://p1", surf.ns.FOAF.Person)

    RP = surf.resource.result_proxy.ResultProxy
    try:
        # Patch ResultProxy with mock get_by method
        original_get_by, RP.get_by = RP.get_by, mock_get_by
        resource.query_attribute(u"foaf_knows")
    except Exception, e:
        pytest.fail(e.message, pytrace=True)
    finally:
        # Regardless of results, revert our patch so other tests are not
        # affected.
        RP.get_by = original_get_by
