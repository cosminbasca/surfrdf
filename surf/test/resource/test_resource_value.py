import pytest
import surf
from rdflib.term import Literal
from surf.resource.lazy import LazyResourceLoader
from surf.resource.result_proxy import ResultProxy


class MockStore(object):
    def __init__(self):
        self.__expect_args = {}
        self.__data = []
        
    def expect_args(self, args):
        self.__expect_args.update(args)
    
    def set_data(self, data):
        self.__data = data
    
    def get_by(self, params):
        if params != self.__expect_args:
            raise AssertionError("%s != %s" % (params, self.__expect_args))

        return self.__data


def mock_instance_factory(params, instance_data):
    return "instance"


class MockResource(object):
    subject = "mock_subject"

    def __init__(self, store=None):
        self.store = store

    def to_rdf(self, arg):
        assert arg in ["value_as_surf_object", "value_as_uriref"]
        return "value_as_uriref"

    def query_attribute(self, attribute_name):
        return ResultProxy(store=self.store, instance_factory=mock_instance_factory)


# ----------------------------------------------------------------------------------------------------------------------
#
# the tests
#
# ----------------------------------------------------------------------------------------------------------------------
def test_contains():
    """
    Test LazyResourceLoader.__contains__.
    """

    def values_source():
        return ["value_as_surf_object"], ["value_as_uriref"]

    instance = LazyResourceLoader(values_source, MockResource(), "some_name")
    # Test basic membership check.
    assert "value_as_surf_object" in instance

    # Test that "to_rdf" is tried.
    assert "value_as_uriref" in instance


def test_get_one_exceptions():
    """
    Test RessourceValue.one.
    """

    def values_source():
        return ["1st_obj", "2nd_obj"], ["1st_uriref", "2nd_uriref"]

    instance = LazyResourceLoader(values_source, MockResource(), "some_name")
    with pytest.raises(surf.exceptions.CardinalityException):
        instance.get_one()


@pytest.fixture
def store_value():
    def values_source():
        return ["1st_obj", "2nd_obj"], ["1st_uriref", "2nd_uriref"]

    store = MockStore()
    value = LazyResourceLoader(values_source, MockResource(store), "some_name")
    return store, value


def test_limit_offset(store_value):
    """
    Test limit, offset.
    """
    store, value = store_value
    try:
        store.expect_args({"limit": 10, "offset": 5})
        list(value.limit(10).offset(5))
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_full(store_value):
    """
    Test full().
    """
    store, value = store_value
    try:
        store.expect_args({'full': True, 'direct_only': True})
        list(value.full(direct_only=True))
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_order_desc(store_value):
    """
    Test order, desc.
    """
    store, value = store_value
    try:
        store.expect_args({"order": "some_attr", "desc": True})
        list(value.order("some_attr").desc())
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_get_by(store_value):
    """
    Test get_by.
    """
    store, value = store_value
    try:
        expected = [(surf.ns.FOAF["name"], Literal(u"Jane"), True)]
        store.expect_args({"get_by": expected})
        list(value.get_by(foaf_name="Jane"))
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_context(store_value):
    """
    Test context.
    """
    store, value = store_value
    try:
        store.expect_args({"context": "my_context"})
        list(value.context("my_context"))
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_filter(store_value):
    """
    Test filter.
    """
    store, value = store_value
    try:
        store.expect_args({"filter": [(surf.ns.FOAF["name"], Literal(u"f"), True)]})
        list(value.filter(foaf_name="f"))
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_get_by_resource(store_value):
    """
    Test that get_by accepts Resources as values.
    """
    store, value = store_value
    resource = MockResource()
    try:
        expected = [(surf.ns.FOAF["knows"], resource.subject, True)]
        store.expect_args({"get_by": expected})
        list(value.get_by(foaf_knows=resource))
    except Exception, e:
        pytest.fail(e.message, pytrace=True)
