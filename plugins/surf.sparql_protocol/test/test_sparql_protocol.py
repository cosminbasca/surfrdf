""" Module for sparql_protocol plugin tests. """

from rdflib.URIRef import URIRef
from rdflib.Literal import Literal
from unittest import TestCase

import surf

class TestSparqlProtocol(TestCase):
    """ Tests for sparql_protocol plugin. """
    
    def test_to_rdflib(self):
        """ Test _toRdflib with empty bindings.  """
        
        data = {'results' : {'bindings' : [{'c' : {}}]}}
        
        # This should not raise exception.
        store = surf.store.Store(reader = "sparql_protocol")
        store.reader._toRdflib(data)
        
    def _get_store_session(self):
        """ Return initialized SuRF store and session objects. """
        
        # FIXME: take endpoint from configuration file,
        # maybe we can mock SPARQL endpoint.
        store = surf.Store(reader = "sparql_protocol",
                           writer = "sparql_protocol",
                           endpoint = "http://localhost:8890/sparql",
                           default_context = "http://surf_test_graph/dummy2")
        session = surf.Session(store)
        return store, session
    
        
    def test_save_remove(self):
        """ Test that saving SuRF resource works.  """
        
        # Save
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)
        john.foaf_name = "John"
        john.foaf_surname = "Smith"
        john.save()
                              
        # Read from different session.
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)
        self.assertEquals(john.foaf_name, "John")
        self.assertEquals(john.foaf_surname, "Smith")
        
        # Remove and try to read again.
        john.remove()
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)
        self.assertEquals(john.foaf_name, None)
        self.assertEquals(john.foaf_surname, None)
        
        
    def test_ask(self):
        """ Test ask method. """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)
        john.remove()
        
        # ASK gets tested indirectly: resource.is_present uses ASK.
        self.assertTrue(not john.is_present())
        john.save()
        self.assertTrue(john.is_present())        
        
    def test_save_context(self):
        """ Test saving resource with specified context. """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        context = URIRef("http://my_context_1")
        
        jane = session.get_resource("http://jane", Person, context = context)
        jane.foaf_name = "Jane"
        jane.save()

        # Same context.
        jane2 = session.get_resource("http://jane", Person, context = context)
        jane2.load()
        self.assertEqual(jane2.foaf_name, "Jane")
        self.assertEqual(jane2.context, context)

        # Different context.
        other_context = URIRef("http://other_context_1")
        jane3 = session.get_resource("http://jane", Person, 
                                     context = other_context)
        
        self.assertEqual(jane3.is_present(), False)
        
    def test_queries_context(self):
        """ Test resource.all() and get_by() with specified context. """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        context = URIRef("http://my_context_1")
        
        jane = session.get_resource("http://jane", Person, context = context)
        jane.foaf_name = "Jane"
        jane.save()

        persons = Person.all(context = context)
        self.assertAlmostEquals(len(persons), 1)

        persons = Person.get_by(foaf_name = Literal("Jane"), context = context)
        self.assertAlmostEquals(len(persons), 1)

        persons = Person.get_by_attribute(["foaf_name"], context = context)
        self.assertAlmostEquals(len(persons), 1)

        