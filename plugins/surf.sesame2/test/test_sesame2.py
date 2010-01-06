""" Module for sparql_protocol plugin tests. """

from unittest import TestCase

import surf
from surf.query import select
from surf.rdf import Literal, URIRef

class TestSesame2(TestCase):
    """ Tests for sesame2 plugin. """
    
        
    def _get_store_session(self):
        """ Return initialized SuRF store and session objects. """
        
        # FIXME: take endpoint from configuration file,
        # maybe we can mock SPARQL endpoint.
        store = surf.Store(reader = "sesame2",
                           writer = "sesame2",
                           port = "8080",
                           root_path = "/openrdf-sesame", 
                           repository = "test")

        session = surf.Session(store)
        
        Person = session.get_class(surf.ns.FOAF + "Person")
        for name in ["John", "Mary", "Jane"]:
            # Some test data.
            person = session.get_resource("http://%s" % name, Person)
            person.foaf_name = name
            person.save()

        return store, session
    
        
    def test_get_session(self):
        """ Test that getting store and session works.  """
        
        self._get_store_session()
        
    def test_get_persons(self):
        """ Test querying for persons.  """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        persons = Person.all()
        self.assertEqual(len(persons), 3)        
        
        
