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
        
        # Hack to make RDFQueryReader available as it was provided by plugin.
        surf.store.__readers__["query_reader"] = query_reader.RDFQueryReader

        self.store = surf.Store(reader = "query_reader", use_subqueries = True)
        self.session = surf.Session(self.store) 

        
    def test_get_by(self):
        """ Test Resource.get_by() method. """
        
        store = surf.Store()
        session = surf.Session(store) 
        Person = session.get_class(ns.FOAF['Person'])

        Person.get_by(foaf_name = u"John")
        # FIXME: should also test returned data.         
        
  
        