""" Module for Resource tests that don't require running triple store. """
 
import os, os.path
import sys
from unittest import TestCase

from rdflib.Namespace import Namespace
from rdflib.URIRef import URIRef
from rdflib.Literal import Literal

import surf
from surf import ns
from surf.resource import Resource

class TestResourceStandalone(TestCase):
    """ Resource tests that don't require running triple store. """
    
    def setUp(self):
        """ Prepare store and session. """
        
        self.store = surf.Store()
        self.session = surf.Session(self.store) 
        
    def tearDown(self):
        pass
    
    def testGetBy(self):
        """ Test Resource.get_by() method. """
        
        Person = self.session.get_class(ns.FOAF['Person'])
        Person.get_by(foaf_name = u"John")
        # FIXME: should also test returned data.
        