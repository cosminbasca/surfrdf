""" Module for sparql_protocol plugin tests. """

from unittest import TestCase

import surf
from sparql_protocol.reader import ReaderPlugin

class TestSparqlProtocol(TestCase):
    """ Tests for sparql_protocol plugin. """
    
    def test_to_rdflib(self):
        """ Test _toRdflib with empty bindings.  """
        
        data = {'results' : {'bindings' : [{'c' : {}}]}}
        
        # This should not raise exception.
        store = surf.store.Store(reader = "sparql_protocol")
        store.reader._toRdflib(data)
        