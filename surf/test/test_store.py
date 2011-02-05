 # coding=UTF-8
""" Module for surf.store.Store tests. """

from unittest import TestCase

import surf
from surf import Session, Store
from surf.plugin.reader import RDFReader
from surf.plugin.writer import RDFWriter

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

    def test_close_unicode_exception(self):
        """ Test that closing a store handles exceptions. """
        
        class MockReader(RDFReader):
            def close(self):
                raise Exception(u"Some unicode: ā")

        class MockWriter(RDFWriter):
            def close(self):
                raise Exception(u"Some unicode: ā")
        
        reader = MockReader()
        store = Store(reader, MockWriter(reader))
        store.close()

    def test_successful_close(self):
        """ Test that store handles successful reader and writer closes. """
        
        class MockReader(RDFReader):
            def close(self):
                pass

        class MockWriter(RDFWriter):
            def close(self):
                pass
        
        reader = MockReader()
        store = Store(reader, MockWriter(reader))
        store.close()
