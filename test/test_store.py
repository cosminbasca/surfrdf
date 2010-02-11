""" Module for surf.store.Store tests. """

from unittest import TestCase

import surf
from surf import Session, Store

class TestStore(TestCase):
    """ Tests for Store class. """
    
    def test_multiples(self):
        """ Test synchronization between empty attribute and rdf_direct. """

        store = Store()
        session = Session(store)
        
        Person = session.get_class(surf.ns.FOAF.Person)
        
        rob = session.get_resource("http://Robert", Person)
        rob.foaf_name = "Robert"
        michael = session.get_resource("http://Michael", Person)
        michael.foaf_name = "Michael"
        
        # Should not fail.
        store.save(rob, michael)
        store.update(rob, michael)
        store.remove(rob, michael)
