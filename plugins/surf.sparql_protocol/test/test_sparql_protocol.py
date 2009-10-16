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
        
    def _get_store_session(self, cleanup = True):
        """ Return initialized SuRF store and session objects. """
        
        # FIXME: take endpoint from configuration file,
        # maybe we can mock SPARQL endpoint.
        store = surf.Store(reader = "sparql_protocol",
                           writer = "sparql_protocol",
                           endpoint = "http://localhost:8890/sparql",
                           default_context = "http://surf_test_graph/dummy2")

        session = surf.Session(store)
        if cleanup: 
            # Fresh start!
            store.clear("http://surf_test_graph/dummy2")
        
        # Some test data.
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)
        john.foaf_name = "John"
        john.foaf_surname = "Smith"
        john.save()
        
        return store, session
    
        
    def test_save_remove(self):
        """ Test that saving SuRF resource works.  """
        
        _, session = self._get_store_session()
                              
        # Read from different session.
        _, session = self._get_store_session(cleanup = False)
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)
        self.assertEquals(john.foaf_name.one, "John")
        self.assertEquals(john.foaf_surname.one, "Smith")
        
        # Remove and try to read again.
        john.remove()
        john = session.get_resource("http://john", Person)
        self.assertEquals(john.foaf_name.first, None)
        self.assertEquals(john.foaf_surname.first, None)
        
    def test_ask(self):
        """ Test ask method. """
        
        _, session = self._get_store_session()
        
        # ASK gets tested indirectly: resource.is_present uses ASK.
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)
        john.remove()
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
        self.assertEqual(jane2.foaf_name.one, "Jane")
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

        persons = list(Person.all().context(context))
        self.assertAlmostEquals(len(persons), 1)

        persons = Person.get_by(foaf_name = Literal("Jane"), context = context)
        self.assertAlmostEquals(len(persons), 1)

        persons = Person.get_by_attribute(["foaf_name"], context = context)
        self.assertAlmostEquals(len(persons), 1)

    def test_get_by(self):
        """ Test reader.get_by() """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        
        jay = session.get_resource("http://jay", Person)
        jay.foaf_name = "Jay"
        jay.save()

        persons = Person.all().get_by(foaf_name = Literal("Jay"))
        persons = list(persons) 
        self.assertTrue(persons[0].foaf_name.first, "Jay")

    def test_full(self):
        """ Test loading details. """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        
        mary = session.get_resource("http://mary", Person)
        mary.foaf_name = "Mary"
        mary.is_foaf_knows_of = URIRef("http://someguy")
        mary.save()

        jane = session.get_resource("http://jane", Person)
        jane.foaf_knows = mary
        jane.save()

        persons = Person.all().get_by(foaf_name = Literal("Mary")).full()
        persons = list(persons) 
        self.assertTrue(len(persons[0].rdf_direct) > 1)
        self.assertTrue(len(persons[0].rdf_inverse) > 0)

        # Now, only direct
        persons = Person.all().get_by(foaf_name = Literal("Mary")).full(only_direct = True)
        persons = list(persons) 
        self.assertTrue(len(persons[0].rdf_direct) > 1)
        self.assertTrue(len(persons[0].rdf_inverse) == 0)

    def test_order_limit_offset(self):
        """ Test ordering by subject, limit, offset. """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        for i in range(0, 10):
            person = session.get_resource("http://a%d" % i, Person)
            person.foaf_name = "A%d" % i
            person.save()

        persons = Person.all().order().limit(2).offset(5)
        uris = [person.subject for person in persons] 
        self.assertEquals(len(uris), 2)
        self.assertTrue(URIRef("http://a5") in uris)
        self.assertTrue(URIRef("http://a6") in uris)

    def test_order_by_attr(self):
        """ Test ordering by attribute other than subject. """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        for i in range(0, 10):
            person = session.get_resource("http://a%d" % i, Person)
            person.foaf_name = "A%d" % (10 - i)
            person.save()

        sort_uri = URIRef(surf.ns.FOAF["name"])
        persons = list(Person.all().order(sort_uri).limit(1))
        self.assertEquals(len(persons), 1)
        self.assertEquals(persons[0].subject, URIRef("http://a9"))
        
    def test_first(self):
        """ Test ResourceProxy.first(). """

        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        person = Person.all().first()
        self.assertEquals(person.subject, URIRef("http://john"))
        
        
