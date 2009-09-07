""" Module for rdflib plugin tests. """

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
