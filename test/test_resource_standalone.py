""" Module for Resource tests that don't require running triple store. """
 
from unittest import TestCase


import surf
import surf.store
from surf import ns
from surf.plugin import query_reader

class TestResourceStandalone(TestCase):
    """ Resource tests that don't require running triple store. """
    
    def setUp(self):
        """ Prepare store and session. """
        
        
    def test_get_by(self):
        """ Test Resource.get_by() method. """
        
        store = surf.Store()
        session = surf.Session(store) 
        Person = session.get_class(ns.FOAF['Person'])

        Person.get_by(foaf_name = u"John")
        # FIXME: should also test returned data.         
        
    def test_all_full(self):
        """ Test Resource.all() with full=True option. """
        
        # Hack to make RDFQueryReader available as it was provided by plugin.
        surf.store.__readers__["query_reader"] = query_reader.RDFQueryReader
        
        store = surf.Store(reader = "query_reader", use_subqueries = True)
        session = surf.Session(store) 
        Person = session.get_class(ns.FOAF['Person'])
        

        def triples_func(*args, **kwargs):
            foaf = ns.FOAF
            print "hello"
            return [("person1", foaf['name'], "John")]
        
        # Plug in mocked data source.        
        store.reader._triples = triples_func

        instances = Person.all(full = True)
        
        assert len(instances), "Returned list is empty."
        for instance in instances:
            assert isinstance(instance, Person)
            assert instance.foaf_name == u"John", "Name is not John."
        
        