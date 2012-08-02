""" Module for ResultProxy tests. """

import unittest

import surf
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
        return ResultProxy(store=self.store,
                           instance_factory=mock_instance_factory)


class TestResultValue(unittest.TestCase):

    def test_contains(self):
        """ Test LazyResourceLoader.__contains__. """
        
        def values_source():
            return ["value_as_surf_object"], ["value_as_uriref"]
        
        instance = LazyResourceLoader(values_source, MockResource(), "some_name")
        # Test basic membership check.
        self.assertTrue("value_as_surf_object" in instance)

        # Test that "to_rdf" is tried.
        self.assertTrue("value_as_uriref" in instance)

    def test_get_one_exceptions(self):
        """ Test RessourceValue.one. """
        
        def values_source():
            return ["1st_obj", "2nd_obj"], ["1st_uriref", "2nd_uriref"]
        
        instance = LazyResourceLoader(values_source, MockResource(), "some_name")
        self.assertRaises(surf.exceptions.CardinalityException, instance.get_one)
        

class TestResultValueQuery(unittest.TestCase):

    def setUp(self):
        def values_source():
            return ["1st_obj", "2nd_obj"], ["1st_uriref", "2nd_uriref"]
        
        self.store = MockStore()
        self.value = LazyResourceLoader(values_source, MockResource(self.store),
                                   "some_name")

    def test_limit_offset(self):
        """ Test limit, offset. """
        
        self.store.expect_args({"limit" : 10, "offset" : 5})
        list(self.value.limit(10).offset(5))

    def test_full(self):
        """ Test full(). """
        
        self.store.expect_args({'full' : True, 'direct_only' : True})
        list(self.value.full(direct_only = True))


    def test_order_desc(self):
        """ Test order, desc. """
        
        self.store.expect_args({"order" : "some_attr", "desc" : True})
        list(self.value.order("some_attr").desc())

    def test_get_by(self):
        """ Test get_by. """
        
        expected = [(surf.ns.FOAF["name"], "Jane", True)]
        self.store.expect_args({"get_by" : expected})
        list(self.value.get_by(foaf_name = "Jane"))

    def test_context(self):
        """ Test context. """
        
        self.store.expect_args({"context" : "my_context"})
        list(self.value.context("my_context"))

    def test_filter(self):
        """ Test filter. """
        
        self.store.expect_args({"filter" : [(surf.ns.FOAF["name"], "f", True)]})
        list(self.value.filter(foaf_name = "f"))

    def test_get_by_resource(self):
        """ Test that get_by accepts Resources as values. """
        
        resource = MockResource()
        expected = [(surf.ns.FOAF["knows"], resource.subject, True)]
        self.store.expect_args({"get_by" : expected})
        list(self.value.get_by(foaf_knows = resource))
