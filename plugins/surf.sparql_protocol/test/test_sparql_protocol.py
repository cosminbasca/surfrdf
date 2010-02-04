# -*- coding: UTF-8 -*-
""" Module for sparql_protocol plugin tests. """

from unittest import TestCase

from sparql_protocol.reader import SparqlReaderException
from sparql_protocol.writer import SparqlWriterException
import surf
from surf.query import select
from surf.rdf import Literal, URIRef
from surf.resource.result_proxy import CardinalityException

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
                           endpoint = "http://localhost:9980/sparql",
                           default_context = "http://surf_test_graph/dummy2",
                           use_subqueries = True)

        session = surf.Session(store)
        if cleanup: 
            # Fresh start!
            store.clear("http://surf_test_graph/dummy2")
        
        Person = session.get_class(surf.ns.FOAF + "Person")
        for name in ["John", "Mary", "Jane"]:
            # Some test data.
            person = session.get_resource("http://%s" % name, Person)
            person.foaf_name = name
            person.save()
        
        return store, session
    
        
    def test_save_remove(self):
        """ Test that saving SuRF resource works.  """
        
        # Read from different session.
        _, session = self._get_store_session(cleanup = False)
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://John", Person)
        self.assertEquals(john.foaf_name.one, "John")
        
        # Remove and try to read again.
        john.remove()
        john = session.get_resource("http://John", Person)
        self.assertEquals(john.foaf_name.first, None)
        
    def test_ask(self):
        """ Test ask method. """
        
        _, session = self._get_store_session()
        
        # ASK gets tested indirectly: resource.is_present uses ASK.
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://John", Person)
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
        self.assertEquals(len(persons), 1)

        persons = Person.get_by(foaf_name = Literal("Jane")).context(context)
        self.assertEquals(len(list(persons)), 1)

        persons = Person.get_by_attribute(["foaf_name"], context = context)
        self.assertEquals(len(persons), 1)

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
        
        # Create inverse foaf_knows attribute for Mary
        jane = session.get_resource("http://Jane", Person)
        jane.foaf_knows = URIRef("http://Mary")
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
            person = session.get_resource("http://A%d" % i, Person)
            person.foaf_name = "A%d" % i
            person.save()

        persons = Person.all().order().limit(2).offset(5)
        uris = [person.subject for person in persons] 
        print uris
        self.assertEquals(len(uris), 2)
        self.assertTrue(URIRef("http://A5") in uris)
        self.assertTrue(URIRef("http://A6") in uris)

    def test_order_by_attr(self):
        """ Test ordering by attribute other than subject. """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        for i in range(0, 10):
            person = session.get_resource("http://A%d" % i, Person)
            person.foaf_name = "A%d" % (10 - i)
            person.save()

        sort_uri = URIRef(surf.ns.FOAF["name"])
        persons = list(Person.all().order(sort_uri).limit(1))
        self.assertEquals(len(persons), 1)
        self.assertEquals(persons[0].subject, URIRef("http://A9"))
        
    def test_first(self):
        """ Test ResourceProxy.first(). """

        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        person = Person.all().first()
        self.assertEquals(person.subject, URIRef("http://John"))
        
    def test_one(self):
        """ Test ResourceProxy.one(). """

        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        # There are two persons and one() should fail
        self.assertRaises(CardinalityException, Person.all().one)
        
    def test_attribute_limit(self):
        """ Test limit on attributes. """

        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource(URIRef("http://John"), Person)
        john.foaf_knows = [URIRef("http://Mary"), URIRef("http://Joe")]
        john.save()
        
        
        # Get this instance again, test its foaf_knows attribute
        john = session.get_resource(URIRef("http://John"), Person)
        self.assertEquals(len(list(john.foaf_knows)),  2)
        
        # Get this instance again, test its foaf_knows attribute
        john = session.get_resource(URIRef("http://John"), Person)
        self.assertEquals(len(list(john.foaf_knows.limit(1))),  1)
        assert isinstance(john.foaf_knows.limit(1).first(), surf.Resource)
        
    def test_attribute_access(self):
        """ Test limit on attributes. """

        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource(URIRef("http://John"), Person)
        # Access with query
        self.assertEquals(john.foaf_name.limit(1).first(), "John")
        # Access as attribute
        self.assertEquals(john.foaf_name.first, "John")

    def test_result_proxy_len(self):
        """ Test len(result_proxy). """

        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        self.assertEquals(len(Person.all()), 3)

        john = session.get_resource("http://John", Person)
        self.assertEquals(len(john.all()), 3)

    def test_atrribute_get_by(self):
        """ Test resource.some_attr.get_by(). """

        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://John", Person)
        mary = session.get_resource("http://Mary", Person)
        jane = session.get_resource("http://Jane", Person)
        
        john.foaf_knows = mary
        john.save()

        self.assertEquals(len(john.foaf_knows.get_by(foaf_name = "Jane")), 0)

    def test_class_all(self):
        """ Test Class.all().full(). 
        
        all() and get_by() on Classes should behave the same as on Resources.
        
        """

        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF["Person"])
        self.assertEquals(len(Person.all().full()), 3)

    def test_class_attrs_order(self):
        """ Test operations on Class.some_attr. 

        Class attributes should be ResourceValue instances and behave the
        same as with Resources.
        
        """
        
        _, session = self._get_store_session()
        person_instance = session.get_resource(surf.ns.FOAF["Person"], surf.ns.OWL["Class"])
        person_instance.rdfs_comment = "Comment"
        person_instance.save()
        
        Person = session.get_class(surf.ns.FOAF["Person"])
        self.assertEqual(len(Person.rdfs_comment.order()), 1)

    def test_filter(self):
        """ Test filter on ResultProxy. """
        
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF["Person"])
        
        # Select persons which have names starting with "J"
        js = Person.all().filter(foaf_name = "(%s LIKE 'J%%')") 
        self.assertEqual(len(js), 2)
        
    def test_exceptions(self):
        """ Test that exceptions are raised on invalid queries. """

        store = surf.Store(reader = "sparql_protocol",
                           writer = "sparql_protocol",
                           endpoint = "invalid")

        def try_query():
            store.execute(query)
        
        query = select("?a") 
        self.assertRaises(SparqlReaderException, try_query)
        
        def try_add_triple():
            store.add_triple("?s", "?p", "?o") 

        self.assertRaises(SparqlWriterException, try_add_triple)


    def test_save_unicode(self):
        """ Test that saving unicode data works.  """
        
        # Read from different session.
        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://John", Person)
        john.foaf_name = u"Jānis"
        john.save()
