""" Module for rdflib plugin tests. """

from unittest import TestCase

import surf

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
        
        _, session = self._get_store_session()
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

    def test_all_limit_order(self):
        
        _, session = self._get_store_session()

        FoafPerson = session.get_class(surf.ns.FOAF.Person)
        # John
        john = session.get_resource("http://john.com/me", FoafPerson)
        john.foaf_name = "John"
        john.save()
        # Jane
        jane = session.get_resource("http://jane.com/me", FoafPerson)
        jane.foaf_name = "Jane"
        jane.save()
        
        names = map(str, FoafPerson.all().limit(10).order(surf.ns.FOAF.name))
        assert "John" in names
        assert "Jane" in names
        
    def test_save_multiple(self):
        """ Test that saving multiple resources work.  """
        
        # Read from different session.
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        
        rob = session.get_resource("http://Robert", Person)
        rob.foaf_name = "Robert"
        michael = session.get_resource("http://Michael", Person)
        michael.foaf_name = "Michael"
        
        store = session.default_store
        writer = store.writer
        
        writer.save(rob, michael)
        
        self.assertTrue(rob.is_present())
        self.assertTrue(michael.is_present())    
        
    def test_remove_inverse(self):
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        
        jane = session.get_resource("http://Jane", Person)
        mary = session.get_resource("http://Mary", Person)
        jane.foaf_knows = mary
        jane.update()
        
        # This should also remove <jane> foaf:knows <mary>.
        mary.remove(inverse = True)

        jane = session.get_resource("http://Jane", Person)
        self.assertEquals(len(jane.foaf_knows), 0)
             
