""" Module for sparql_protocol plugin tests. """

from unittest import TestCase

import surf
from surf import Resource

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

    def test_class_mapping(self):
        """ Test class mapping. """
        
        class MyPerson(object):
            def get_something(self):
                pass
        
        _, session = self._get_store_session()
        session.mapping[surf.ns.FOAF.Person] = [MyPerson]

        # Class-level tests.
        cls = session.get_class(surf.ns.FOAF.Person)
        
        assert issubclass(cls, surf.Resource)
        assert issubclass(cls, MyPerson)
        assert hasattr(cls, "get_something")
        
        # Instance-level tests.
        
        instance = session.get_resource("http://someuri", surf.ns.FOAF.Person)
        
        assert isinstance(instance, surf.Resource)
        assert isinstance(instance, MyPerson)
        assert hasattr(instance, "get_something")

    def test_class_instances(self):
        """ Test that dirty class instances are not lost to GC. """
        
        _, session = self._get_store_session()

        # Class-level tests.
        cls = session.get_class(surf.ns.FOAF.Person)
        for i in range(0, 100):
            c = cls("http://test_instance_%d" % i)
            # Make some changes to instance to trigger its "dirty" state.
            c.rdfs_comment = "Test Instance %d" % i

        self.assertEquals(len(Resource._dirty_instances), 100)
        session.commit()
        self.assertEquals(len(Resource._dirty_instances), 0)
