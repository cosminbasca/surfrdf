""" Module for rdflib plugin tests. """

from rdflib.URIRef import URIRef
from unittest import TestCase

import surf
from sparql_protocol.reader import ReaderPlugin

class TestRdfLib(TestCase):
    """ Tests for sparql_protocol plugin. """
    
    def _get_store_session(self):
        """ Return initialized SuRF store and session objects. """
        
        # FIXME: take endpoint from configuration file,
        # maybe we can mock SPARQL endpoint.
        store = surf.Store(reader = "rdflib", writer = "rdflib")
        session = surf.Session(store)
        return store, session
    
        
    def test_is_present(self):
        """ Test that is_present returns True / False.  """
        
        store, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)

        self.assertEquals(john.is_present(), False)
        john.save()
        self.assertEquals(john.is_present(), True)
    
    def test_get_resource_lazy_attr(self):
        """ Check that attributes are converted into SuRF objects. """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF["Person"])
        
        p1 = session.get_resource("http://p1", Person)
        p2 = session.get_resource("http://p2", Person)
        p1.foaf_knows = p2
        p2.foaf_knows = p1
        p1.save()
        p2.save()

        another_p1 = session.get_resource("http://p1", Person)
        another_p1.load()
        another_p2 = another_p1.foaf_knows.first

        # .foaf_knows.first should be SuRF object not URIRef
        self.assertTrue(isinstance(another_p2, surf.Resource))
        self.assertTrue(isinstance(another_p2.foaf_knows.first, surf.Resource))
        
    def test_all(self):
        """ Test that resource.all() works. """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF["Person"])
        p1 = session.get_resource("http://p1", Person)

        list(Person.all())
        list(p1.all())

        
        
        
        
