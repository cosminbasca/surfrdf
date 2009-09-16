""" Module for sparql_protocol plugin tests. """

from unittest import TestCase

import surf

class TestSparqlProtocol(TestCase):
    """ Tests for sparql_protocol plugin. """
    
    def test_to_rdflib(self):
        """ Test _toRdflib with empty bindings.  """
        
        data = {'results' : {'bindings' : [{'c' : {}}]}}
        
        # This should not raise exception.
        store = surf.store.Store(reader = "sparql_protocol")
        store.reader._toRdflib(data)
        
    def _get_store_session(self):
        """ Return initialized SuRF store and session objects. """
        
        # FIXME: take endpoint from configuration file,
        # maybe we can mock SPARQL endpoint.
        store = surf.Store(reader = "sparql_protocol",
                           writer = "sparql_protocol",
                           endpoint = "http://localhost:8890/sparql",
                           default_graph = "http://surf_test_graph/dummy")
        session = surf.Session(store)
        return store, session
    
        
    def test_save_remove(self):
        """ Test that saving SuRF resource works.  """
        
        # Save
        store, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)
        john.foaf_name = "John"
        john.save()
                              
        # Read from different session.
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)
        self.assertEquals(john.foaf_name, "John")
        
        # Remove and try to read again.
        john.remove()
        store, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)
        self.assertEquals(john.foaf_name, None)
        
        
    def test_ask(self):
        """ Test ask method. """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)
        john.remove()
        
        # ASK gets tested indirectly: resource.is_present uses ASK.
        self.assertTrue(not john.is_present())
        john.save()
        self.assertTrue(john.is_present())        
        