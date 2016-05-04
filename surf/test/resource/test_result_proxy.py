import pytest
from rdflib.term import Literal
import surf
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


class MockResource(object):
    subject = "mock_subject"


def mock_instance_factory(params, instance_data):
    return "instance"
    

@pytest.fixture
def store_proxy():
    store = MockStore()
    params = {"store": store, "instance_factory": mock_instance_factory}
    proxy = ResultProxy(params)
    return store, proxy


def test_all_empty_list(store_proxy):
    """
    Test ResultProxy with no filters, no returned data.
    """
    _, proxy = store_proxy
    results = list(proxy)
    assert len(results) == 0


def test_limit_offset(store_proxy):
    """
    Test limit, offset.
    """
    store, proxy = store_proxy
    try:
        store.expect_args({"limit": 10, "offset": 5})
        list(proxy.limit(10).offset(5))
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_full(store_proxy):
    """
    Test full().
    """
    store, proxy = store_proxy
    try:
        store.expect_args({'full': True, 'direct_only': True})
        list(proxy.full(direct_only=True))
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_order_desc(store_proxy):
    """
    Test order, desc.
    """
    store, proxy = store_proxy
    try:
        store.expect_args({"order": "some_attr", "desc": True})
        list(proxy.order("some_attr").desc())
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_get_by(store_proxy):
    """
    Test get_by.
    """
    store, proxy = store_proxy
    try:
        expected = [(surf.ns.FOAF["name"], Literal(u"Jane"), True)]
        store.expect_args({"get_by": expected})
        list(proxy.get_by(foaf_name="Jane"))
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_context(store_proxy):
    """
    Test context.
    """
    store, proxy = store_proxy
    try:
        store.expect_args({"context": "my_context"})
        list(proxy.context("my_context"))
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_filter(store_proxy):
    """
    Test filter.
    """
    store, proxy = store_proxy
    try:
        store.expect_args({"filter": [(surf.ns.FOAF["name"], Literal(u"f"), True)]})
        list(proxy.filter(foaf_name="f"))
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_get_by_resource(store_proxy):
    """
    Test that get_by accepts Resources as values.
    """
    store, proxy = store_proxy
    try:
        resource = MockResource()
        expected = [(surf.ns.FOAF["knows"], resource.subject, True)]
        store.expect_args({"get_by" : expected})
        list(proxy.get_by(foaf_knows = resource))
    except Exception, e:
        pytest.fail(e.message, pytrace=True)
