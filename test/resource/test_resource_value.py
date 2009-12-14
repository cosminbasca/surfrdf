""" Module for ResultProxy tests. """

import unittest
from surf.resource.value import ResourceValue

class MockResource(object):
    subject = "mock_subject"
    
    def to_rdf(self, arg):
        assert arg in ["value_as_surf_object", "value_as_uriref"]
        return "value_as_uriref"

class TestResultValue(unittest.TestCase):

    def test_contains(self):
        """ Test ResultValue.__contains__. """
        
        def values_source():
            return ["value_as_surf_object"], ["value_as_uriref"]
        
        instance = ResourceValue(values_source, MockResource(), "some_name")
        # Test basic membership check.
        self.assertTrue("value_as_surf_object" in instance)

        # Test that "to_rdf" is tried.
        self.assertTrue("value_as_uriref" in instance)
