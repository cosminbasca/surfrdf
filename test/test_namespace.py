from unittest import TestCase

from surf import ns
from surf.rdf import Namespace
from surf.util import get_namespace as util_get_namespace

class TestNamespace(TestCase):
    def test_01_register(self):
        ns.register(test='http://sometest.ns/ns#')
        self.assertEqual(ns.TEST, Namespace('http://sometest.ns/ns#'))
        
    def test_02_get_namespce(self):
        key, namespace = ns.get_namespace('http://sometest.ns/ns#')
        self.assertEqual(key, 'TEST')
        self.assertEqual(namespace, Namespace('http://sometest.ns/ns#'))
        
        key1, namespace1 = ns.get_namespace('http://sometest1.ns/ns#')
        self.assertEqual(key1, 'NS1')
        self.assertEqual(namespace1, Namespace('http://sometest1.ns/ns#'))
        
    def test_03_get_namespace_url(self):
        url = ns.get_namespace_url('TEST')
        self.assertEqual(url, Namespace('http://sometest.ns/ns#'))
        
        url1 = ns.get_namespace_url('NS1')
        self.assertEqual(url1, Namespace('http://sometest1.ns/ns#'))
        
    def test_04_get_prefix(self):
        name = ns.get_prefix(Namespace('http://sometest.ns/ns#'))
        self.assertEqual(name, 'TEST')
        
        name1 = ns.get_prefix('http://sometest1.ns/ns#')
        self.assertEqual(name1, 'NS1')
        
    def test_get_prefix_predefined(self):
        """ Test get_prefix with predefined namespaces. """
        
        prefix, _ = util_get_namespace(ns.RDFS)
        self.assertEquals(prefix, "RDFS")

        prefix, _ = util_get_namespace(ns.GEO)
        self.assertEquals(prefix, "GEO")
        