""" Module for sparql_protocol plugin tests. """

from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from unittest import TestCase

import surf

class TestResource(TestCase):
    """ Tests for Resource class. """
    
        
    def _get_store_session(self, cleanup = True):
        """ Return initialized SuRF store and session objects. """
        
        store = surf.Store(reader = "rdflib", writer = "rdflib")
        session = surf.Session(store)
        return store, session

    def test_empty_attribute_sync(self):
        """ Test synchronization between empty attribute and rdf_direct. """
        
        _, session = self._get_store_session()
        instance = session.get_resource("http://smth", surf.ns.OWL["Thing"])
        self.assertEquals(len(instance.rdf_direct), 1)
        
        # Poke foaf_name so it gets initialized
        list(instance.foaf_name)
        
        # Append value
        instance.foaf_name.append("John")

        self.assertEquals(len(instance.rdf_direct), 2)
        self.assertEquals(len(instance.rdf_direct[surf.ns.FOAF["name"]]), 1)

    def test_loaded_attribute_sync(self):
        """ Test synchronization between loaded attribute and rdf_direct. """
        
        _, session = self._get_store_session()
        instance = session.get_resource("http://smth", surf.ns.OWL["Thing"])
        instance.foaf_name = "John"
        instance.save()
        
        instance = session.get_resource("http://smth", surf.ns.OWL["Thing"])
        # Load foaf_name
        list(instance.foaf_name)
        # rdf_direct should contain two attributes now
        self.assertEquals(len(instance.rdf_direct), 2)
        self.assertEquals(len(instance.rdf_direct[surf.ns.FOAF["name"]]), 1)
