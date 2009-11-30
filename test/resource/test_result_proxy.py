""" Module for ResultProxy tests. """

import unittest
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

def mock_instancemaker(params, instance_data):
    return "instance"
    

class TestResultProxy(unittest.TestCase):

    def setUp(self):
        self.store = MockStore()
        params = { "store" : self.store, "instancemaker" : mock_instancemaker}
        self.proxy = ResultProxy(params)

    def test_all_empty_list(self):
        """ Test ResultProxy with no filters, no returned data. """
        
        results = list(self.proxy)
        assert len(results) == 0

    def test_limit_offset(self):
        """ Test limit, offset. """
        
        self.store.expect_args({"limit" : 10, "offset" : 5})
        list(self.proxy.limit(10).offset(5))

    def test_full(self):
        """ Test full(). """
        
        self.store.expect_args({"full" : True, "only_direct" : True})
        list(self.proxy.full(only_direct = True))


    def test_order_desc(self):
        """ Test order, desc. """
        
        self.store.expect_args({"order" : "some_attr", "desc" : True})
        list(self.proxy.order("some_attr").desc())

    def test_get_by(self):
        """ Test get_by. """
        
        expected = [(surf.ns.FOAF["name"], "Jane", True)]
        self.store.expect_args({"get_by" : expected})
        list(self.proxy.get_by(foaf_name = "Jane"))

    def test_context(self):
        """ Test context. """
        
        self.store.expect_args({"context" : "my_context"})
        list(self.proxy.context("my_context"))

    def test_filter(self):
        """ Test filter. """
        
        self.store.expect_args({"filter" : [(surf.ns.FOAF["name"], "f", True)]})
        list(self.proxy.filter(foaf_name = "f"))

    def test_get_by_resource(self):
        """ Test that get_by accepts Resources as values. """
        
        resource = MockResource()
        expected = [(surf.ns.FOAF["knows"], resource.subject, True)]
        self.store.expect_args({"get_by" : expected})
        list(self.proxy.get_by(foaf_knows = resource))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()