import os, os.path
import sys
from unittest import TestCase

from surf import ns
#from rdf.namespace import Namespace, ClosedNamespace
from rdflib.Namespace import Namespace

class TestNamespace(TestCase):
    def test_01_register(self):
        ns.register(test='http://sometest.ns/ns#')
        assert ns.TEST == Namespace('http://sometest.ns/ns#')
        
    def test_02_get_namespce(self):
        key, namespace = ns.get_namespace('http://sometest.ns/ns#')
        assert key == 'TEST'
        assert namespace == Namespace('http://sometest.ns/ns#')
        
        key1, namespace1 = ns.get_namespace('http://sometest1.ns/ns#')
        assert key1 == 'NS1'
        assert namespace1 == Namespace('http://sometest1.ns/ns#')
        
    def test_03_get_namespace_url(self):
        url = ns.get_namespace_url('TEST')
        assert url == Namespace('http://sometest.ns/ns#')
        
        url1 = ns.get_namespace_url('NS1')
        assert url1 == Namespace('http://sometest1.ns/ns#')
        
    def test_04_get_prefix(self):
        name = ns.get_prefix(Namespace('http://sometest.ns/ns#'))
        assert name == 'TEST'
        
        name1 = ns.get_prefix('http://sometest1.ns/ns#')
        assert name1 == 'NS1'
        