 # coding=UTF-8
""" Module for surf.session.Session tests. """

from unittest import TestCase

from surf import Session, Store

class TestSession(TestCase):
    """ Tests for Session class. """
    
    def test_close_multiples_stores(self):
        """ Test that closing a session with multiple stores work. """

        store1 = Store()
        session = Session(store1)

        store2 = Store()
        session["store2"] = store2
        
        # Should not fail.
        session.close()
