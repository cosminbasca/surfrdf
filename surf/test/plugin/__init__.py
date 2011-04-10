# -*- coding: UTF-8 -*-
""" Standard plugin tests to be mixed in with specific plugin tests. """

import random
import datetime

import surf
from surf.store import NO_CONTEXT
from surf.query import select, a
from surf.rdf import Literal, URIRef
from surf.exc import CardinalityException
from surf.util import value_to_rdf, json_to_rdflib
from surf import ns

class PluginTestMixin(object):
    """ Tests for SuRF plugins. """

    def _get_store_session(self, use_default_context = True):
        """ Return initialized SuRF store and session objects. """
        raise NotImplementedError

    # sparql_protocol test cases

    def _create_persons(self, session):
        Person = session.get_class(surf.ns.FOAF + "Person")
        for name in ["John", "Mary", "Jane"]:
            # Some test data.
            person = session.get_resource("http://%s" % name, Person)
            person.foaf_name = name
            person.save()

    def test_save_remove(self):
        """ Test that saving SuRF resource works.  """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://John", Person)
        self.assertEquals(john.foaf_name.one, "John")

        # Remove and try to read again.
        john.remove()
        john = session.get_resource("http://John", Person)
        self.assertEquals(john.foaf_name.first, None)

    def test_remove_without_context(self):
        """ Test that removing without context works.  """

        # Not specifying default graph here!
        _, session = self._get_store_session(use_default_context = False)
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://Nonexistent-John", Person)
        john.remove()

    def test_save_multiple(self):
        """ Test that saving multiple resources work.  """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")

        rob = session.get_resource("http://Robert", Person)
        rob.foaf_name = "Robert"
        michael = session.get_resource("http://Michael", Person)
        michael.foaf_name = "Michael"

        store = session.default_store
        writer = store.writer

        writer.save(rob, michael)

        self.assertTrue(rob.is_present())
        self.assertTrue(michael.is_present())

    def test_ask(self):
        """ Test ask method. """

        _, session = self._get_store_session()
        self._create_persons(session)

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
        self._create_persons(session)
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

        store, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")
        context = URIRef("http://my_context_1")
        store.clear(context)

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
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")

        jay = session.get_resource("http://jay", Person)
        jay.foaf_name = "Jay"
        jay.save()

        persons = Person.all().get_by(foaf_name = Literal("Jay"))
        persons = list(persons)
        self.assertEquals(persons[0].foaf_name.first, "Jay")

    def test_get_by_alternatives(self):
        """ Test reader.get_by() with several values """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")

        persons = Person.all().get_by(foaf_name = ["John", "Mary"])
        self.assertEquals(len(persons), 2)

    def test_get_by_int(self):
        """ Test reader.get_by() given an int value"""

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")

        jay = session.get_resource("http://jay", Person)
        jay.foaf_age = 40
        jay.save()

        persons = Person.all().get_by(foaf_age=40)
        persons = list(persons)
        self.assertEquals(persons[0].subject, URIRef("http://jay"))

    def test_get_by_int_alternatives(self):
        """ Test reader.get_by() with several int values """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")

        jane = session.get_resource("http://Jane", Person)
        jane.foaf_age = 32
        jane.save()

        mary = session.get_resource("http://Mary", Person)
        mary.foaf_age = 38
        mary.save()

        persons = Person.all().get_by(foaf_age=[32, 38])
        self.assertEquals(len(persons), 2)

    def test_full(self):
        """ Test loading details. """

        _, session = self._get_store_session()
        self._create_persons(session)
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
        self._create_persons(session)
        for i in range(0, 10):
            person = session.get_resource("http://A%d" % i, Person)
            person.foaf_name = "A%d" % i
            person.save()

        persons = Person.all().order().limit(2).offset(5)
        uris = [person.subject for person in persons]
        self.assertEquals(len(uris), 2)
        self.assertTrue(URIRef("http://A5") in uris)
        self.assertTrue(URIRef("http://A6") in uris)

    def test_order_by_attr(self):
        """ Test ordering by attribute other than subject. """

        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        self._create_persons(session)
        for i in range(0, 10):
            person = session.get_resource("http://A%d" % i, Person)
            person.foaf_name = "A%d" % (10 - i)
            person.save()

        sort_uri = URIRef(surf.ns.FOAF["name"])
        persons = list(Person.all().order(sort_uri).limit(1))
        self.assertEquals(len(persons), 1)
        self.assertEquals(persons[0].subject, URIRef("http://A9"))

    def test_desc_order(self):
        """ Test descending order by. """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")
        for i in range(0, 10):
            person = session.get_resource("http://Z%d" % i, Person)
            person.foaf_name = "Z%d" % i
            person.save()

        sort_uri = surf.ns.FOAF["name"]
        persons = list(Person.all().order(sort_uri).desc().limit(10))
        self.assertEquals(len(persons), 10)
        self.assert_(all((person.subject == URIRef("http://Z%d" % (9 - i)))
                         for i, person in enumerate(persons)))

    def test_first(self):
        """ Test ResourceProxy.first(). """

        _, session = self._get_store_session()
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://John", Person)
        john.foaf_name = "John"
        john.save()

        person = Person.all().first()
        self.assertEquals(person.subject, URIRef("http://John"))

    def test_one(self):
        """ Test ResourceProxy.one(). """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")
        # There are two persons and one() should fail
        self.assertRaises(CardinalityException, Person.all().one)

    def test_attribute_limit(self):
        """ Test limit on attributes. """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource(URIRef("http://John"), Person)
        john.foaf_knows = [URIRef("http://Mary"), URIRef("http://Jane")]
        john.save()


        # Get this instance again, test its foaf_knows attribute
        john = session.get_resource(URIRef("http://John"), Person)
        self.assertEquals(len(list(john.foaf_knows)), 2)

        # Get this instance again, test its foaf_knows attribute
        john = session.get_resource(URIRef("http://John"), Person)
        self.assertEquals(len(list(john.foaf_knows.limit(1))), 1)
        assert isinstance(john.foaf_knows.limit(1).first(), surf.Resource)

    def test_instancemaker(self):
        """ Test instancemaker. """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource(URIRef("http://John"), Person)
        john.foaf_knows = [URIRef("http://Joe")]
        john.save()

        # Get this instance again, test its foaf_knows attribute
        john = session.get_resource(URIRef("http://John"), Person)
        assert isinstance(john.foaf_knows.first, URIRef)

    def test_attribute_access(self):
        """ Test limit on attributes. """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource(URIRef("http://John"), Person)
        # Access with query
        self.assertEquals(john.foaf_name.limit(1).first(), "John")
        # Access as attribute
        self.assertEquals(john.foaf_name.first, "John")

    def test_result_proxy_len(self):
        """ Test len(result_proxy). """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")
        self.assertEquals(len(Person.all()), 3)

        john = session.get_resource("http://John", Person)
        self.assertEquals(len(john.all()), 3)

    def test_atrribute_get_by(self):
        """ Test resource.some_attr.get_by(). """

        _, session = self._get_store_session()
        self._create_persons(session)
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
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF["Person"])
        self.assertEquals(len(Person.all().full()), 3)

    def test_class_attrs_order(self):
        """ Test operations on Class.some_attr.

        Class attributes should be ResourceValue instances and behave the
        same as with Resources.

        """

        _, session = self._get_store_session()
        self._create_persons(session)
        person_instance = session.get_resource(surf.ns.FOAF["Person"], surf.ns.OWL["Class"])
        person_instance.rdfs_comment = "Comment"
        person_instance.save()

        Person = session.get_class(surf.ns.FOAF["Person"])
        self.assertEqual(len(Person.rdfs_comment.order()), 1)

    def test_filter(self):
        """ Test filter on ResultProxy. """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF["Person"])

        # Select persons which have names starting with "J"
        js = Person.all().filter(foaf_name = "regex(%s, '^J')")
        self.assertEqual(len(js), 2)

    def test_save_unicode(self):
        """ Test that saving unicode data works.  """

        # Read from different session.
        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://John", Person)
        john.foaf_name = u"Jānis"
        john.save()

    def test_update_multiple(self):
        """ Test that saving multiple resources work.  """

        # Read from different session.
        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")

        jane = session.get_resource("http://Jane", Person)
        jane.foaf_mbox = "jane@example.com"

        mary = session.get_resource("http://Mary", Person)
        mary.foaf_mbox = "mary@example.com"

        store = session.default_store
        store.update(jane, mary)

        # Check that names are still set
        self.assertEquals(jane.foaf_name.first, "Jane")
        self.assertEquals(mary.foaf_name.first, "Mary")

    def test_remove_inverse(self):
        """ Test removing inverse attributes of resource. """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")

        jane = session.get_resource("http://Jane", Person)
        mary = session.get_resource("http://Mary", Person)
        jane.foaf_knows = mary
        jane.update()

        # This should also remove <jane> foaf:knows <mary>.
        mary.remove(inverse = True)

        jane = session.get_resource("http://Jane", Person)
        self.assertEquals(len(jane.foaf_knows), 0)

    def test_update_integrity(self):
        """ Test resource.update().  """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")

        # Update 1
        jane = session.get_resource("http://Jane", Person)
        jane.foaf_mbox = "jane@example.com"
        jane.update()

        # Update 2
        jane = session.get_resource("http://Jane", Person)
        jane.foaf_mbox = "anotherjane@example.com"
        jane.update()

        # Check that Jane has only the second email set.
        jane = session.get_resource("http://Jane", Person)
        self.assertEquals(len(jane.foaf_mbox), 1)

    def test_constructor_default_context(self):
        """ Test that Person(uri) sets default context. """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF.Person)

        p = Person()
        self.assertTrue(p.context, "Default context not set")

    def test_equality(self):
        """ Test __eq__ """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")

        jane = Person.get_by(foaf_name='Jane').one()
        self.assertEquals(jane, session.get_resource("http://Jane", Person))

    def test_contains(self):
        """ Test resource in query """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")

        jane = session.get_resource("http://Jane", Person)
        persons = Person.all()

        self.assertTrue(jane in persons)

    def test_set_contains(self):
        """ Test resource in set() """

        _, session = self._get_store_session()
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")

        jane = session.get_resource("http://Jane", Person)
        humbert = session.get_resource("http://Humbert", Person)
        persons = Person.all()

        self.assertTrue(jane in set(persons))
        self.assertFalse(humbert in set(persons))

    # allegro_franz test cases

    def _create_logic(self, session):
        Logic = session.get_class(surf.ns.SURF.Logic)

        for i in range(0, 10):
            instance = Logic()
            instance.save()

    def test_is_present(self):
        """ Test that is_present returns True / False.  """

        _, session = self._get_store_session(use_default_context=False)
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)
        john.remove()

        self.assertEquals(john.is_present(), False)
        john.save()
        self.assertEquals(john.is_present(), True)

    def test_all(self):
        _, session = self._get_store_session(use_default_context=False)
        self._create_logic(session)
        Logic = session.get_class(surf.ns.SURF.Logic)
        all = Logic.all().limit(10)
        assert len(all) == 10

    def test_resource(self):
        _, session = self._get_store_session(use_default_context=False)
        self._create_logic(session)
        Logic = session.get_class(surf.ns.SURF.Logic)
        res = Logic.all().limit(1).first()

        assert res.uri == surf.ns.SURF.Logic
        assert hasattr(res, 'subject')
        assert type(res.subject) is URIRef
        assert res.is_present()
        assert res.namespace() == surf.ns.SURF

    # TODO this is not a plug-in testcase
    def test_val2rdf(self):
        _, session = self._get_store_session(use_default_context=False)
        self._create_logic(session)
        Logic = session.get_class(surf.ns.SURF.Logic)
        res = Logic.all().limit(1).first()
        method = value_to_rdf
        XSD = surf.ns.XSD

        assert type(method(str('Literal'))) is Literal and method(str('Literal')) == Literal('Literal')
        assert type(method(u'Literal')) is Literal and method(u'Literal') == Literal(u'Literal')
        # list
        assert method(['Literal', 'en', None]) == Literal('Literal', lang = 'en')
        assert method(['Literal', None, XSD['string']]) == Literal('Literal', datatype = XSD['string'])
        # tuple
        assert method(('Literal', 'en', None)) == Literal('Literal', lang = 'en')
        assert method(('Literal', None, XSD['string'])) == Literal('Literal', datatype = XSD['string'])
        # dict
        assert method({'value':'Literal', 'language':'en'}) == Literal('Literal', lang = 'en')
        assert method({'value':'Literal', 'datatype' : XSD['string']}) == Literal('Literal', datatype = XSD['string'])

        # other
        assert method(10) == Literal(10)
        assert method(10.0) == Literal(10.0)
        # unknown
        o = object()
        assert method(o) == o

    def test_load(self):
        _, session = self._get_store_session(use_default_context=False)
        self._create_logic(session)
        Logic = session.get_class(surf.ns.SURF.Logic)
        res = Logic.all().limit(1).first()
        res.load()

    def test_concept(self):
        _, session = self._get_store_session(use_default_context=False)
        self._create_logic(session)
        Logic = session.get_class(surf.ns.SURF.Logic)
        res = Logic.all().limit(1).first()
        con = res.concept(res.subject)[0]
        self.assertEquals(con, Logic.uri)

    def test_remove_inverse2(self):

        _, session = self._get_store_session(use_default_context=False)
        Person = session.get_class(surf.ns.FOAF + "Person")

        jane = session.get_resource("http://Jane", Person)
        mary = session.get_resource("http://Mary", Person)
        jane.foaf_knows = mary
        jane.update()

        # This should also remove <jane> foaf:knows <mary>.
        mary.remove(inverse = True)

        jane = session.get_resource("http://Jane", Person)
        self.assertEquals(len(jane.foaf_knows), 0)

    def test_attr_order_by(self):
        """ Test ordering of attribute value. """

        _, session = self._get_store_session(use_default_context=False)
        Person = session.get_class(surf.ns.FOAF + "Person")

        # First remove any previously created
        for p in Person.all(): p.remove()

        for i in range(0, 10):
            person = session.get_resource("http://A%d" % i, Person)
            person.foaf_name = "A%d" % i
            person.save()

        all_persons = list(Person.all())
        random.shuffle(all_persons)

        person = person = session.get_resource("http://A0", Person)
        person.foaf_knows = all_persons
        person.foaf_name = []
        person.update()

        persons = list(person.foaf_knows.order(surf.ns.FOAF["name"]).limit(1))
        self.assertEquals(len(persons), 1)
        # Unbound results sort earliest
        self.assertEquals(persons[0].subject, URIRef("http://A0"))

    def test_contains2(self):
        _, session = self._get_store_session(use_default_context=False)
        Person = session.get_class(surf.ns.FOAF + "Person")

        john = session.get_resource("http://John", Person)
        john.foaf_name = "John"
        john.update()

        persons = Person.get_by(foaf_name="John")
        self.assert_(any("John" in p.foaf_name for p in persons),
                     '"John" not found in foaf_name')

    def test_save_context2(self):
        """ Test saving resource with specified context. """
        # Copied from surf.sparql_protocol/test/test_sparql_protocol.py

        _, session = self._get_store_session(use_default_context=False)
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

    # sesame2 test cases

    def test_get_session(self):
        """ Test that getting store and session works.  """

        self._get_store_session(use_default_context=False)

    def test_get_persons(self):
        """ Test querying for persons.  """

        _, session = self._get_store_session(use_default_context=False)
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")
        persons = Person.all()
        self.assertEqual(len(persons), 3)

    def test_remove_inverse3(self):

        _, session = self._get_store_session(use_default_context=False)
        self._create_persons(session)
        Person = session.get_class(surf.ns.FOAF + "Person")

        jane = session.get_resource("http://Jane", Person)
        mary = session.get_resource("http://Mary", Person)
        jane.foaf_knows = mary
        jane.update()

        # This should also remove <jane> foaf:knows <mary>.
        mary.remove(inverse = True)

        jane = session.get_resource("http://Jane", Person)
        self.assertEquals(len(jane.foaf_knows), 0)

    # rdflib test cases

    def test_is_present2(self):
        """ Test that is_present returns True / False.  """

        _, session = self._get_store_session(use_default_context=False)
        Person = session.get_class(surf.ns.FOAF + "Person")
        john = session.get_resource("http://john", Person)

        self.assertEquals(john.is_present(), False)
        john.save()
        self.assertEquals(john.is_present(), True)

    def test_get_resource_lazy_attr(self):
        """ Check that attributes are converted into SuRF objects. """

        _, session = self._get_store_session(use_default_context=False)
        Person = session.get_class(surf.ns.FOAF["Person"])

        p1 = session.get_resource("http://p1", Person)
        p2 = session.get_resource("http://p2", Person)
        p1.foaf_knows = p2
        p2.foaf_knows = p1
        p1.save()
        p2.save()

        another_p1 = session.get_resource("http://p1", Person)
        another_p1.load()
        another_p2 = another_p1.foaf_knows.first

        # .foaf_knows.first should be SuRF object not URIRef
        self.assertTrue(isinstance(another_p2, surf.Resource))
        self.assertTrue(isinstance(another_p2.foaf_knows.first, surf.Resource))

    def test_all2(self):
        """ Test that resource.all() works. """

        _, session = self._get_store_session(use_default_context=False)
        Person = session.get_class(surf.ns.FOAF["Person"])
        p1 = session.get_resource("http://p1", Person)

        list(Person.all())
        list(p1.all())

    def test_all_limit_order(self):

        _, session = self._get_store_session(use_default_context=False)

        FoafPerson = session.get_class(surf.ns.FOAF.Person)
        # John
        john = session.get_resource("http://john.com/me", FoafPerson)
        john.foaf_name = "John"
        john.save()
        # Jane
        jane = session.get_resource("http://jane.com/me", FoafPerson)
        jane.foaf_name = "Jane"
        jane.save()

        # This is currently broken in both rdflib 2.4.2 and
        # 3.0.0--ordering in SuRF uses OPTIONAL which doesn't seem to work
        # in rdflib.
        # See http://code.google.com/p/rdflib/issues/detail?id=92
        # and http://code.google.com/p/rdfextras/issues/detail?id=8
        query = FoafPerson.all().limit(10).order(surf.ns.FOAF.name)
        names = [p.foaf_name.first for p in query]
        assert "John" in names
        assert "Jane" in names

    def test_save_multiple2(self):
        """ Test that saving multiple resources work.  """

        # Read from different session.
        _, session = self._get_store_session(use_default_context=False)
        Person = session.get_class(surf.ns.FOAF + "Person")

        rob = session.get_resource("http://Robert", Person)
        rob.foaf_name = "Robert"
        michael = session.get_resource("http://Michael", Person)
        michael.foaf_name = "Michael"

        store = session.default_store
        writer = store.writer

        writer.save(rob, michael)

        self.assertTrue(rob.is_present())
        self.assertTrue(michael.is_present())

    def test_remove_inverse4(self):

        _, session = self._get_store_session(use_default_context=False)
        Person = session.get_class(surf.ns.FOAF + "Person")

        jane = session.get_resource("http://Jane", Person)
        mary = session.get_resource("http://Mary", Person)
        jane.foaf_knows = mary
        jane.update()

        # This should also remove <jane> foaf:knows <mary>.
        mary.remove(inverse = True)

        jane = session.get_resource("http://Jane", Person)
        self.assertEquals(len(jane.foaf_knows), 0)

    # new test cases

    def test_json_datatypes(self):
        """ Test that proper datatypes are returned. """
        # Tests for a bug wrt datatype uri with AllegroGraph

        store, session = self._get_store_session(use_default_context=False)
        Person = session.get_class(surf.ns.FOAF + "Person")

        # Store datatype
        jake = session.get_resource("http://Jake", Person)
        jake.foaf_name = "Jake"
        jake.foaf_age = 62
        jake.save()

        # Get birthday
        query = select('?age').where(('?s', a, Person.uri),
                                   ('?s', ns.FOAF.age, '?age'))
        result = store.execute_sparql(unicode(query))
        assert len(result['results']['bindings']) == 1
        entry = result['results']['bindings'][0]

        # Test that rdflib type is properly constructed
        age = json_to_rdflib(entry['age'])
        self.assertEquals(age.toPython(), 62)

    def test_clear_context(self):
        """ Test clear() with context. """

        store, session = self._get_store_session(use_default_context=False)
        Person = session.get_class(surf.ns.FOAF + "Person")

        context = URIRef("http://my_context_1")
        store.clear(context)

        # First clear given context
        jake = session.get_resource("http://Jake", Person, context = context)
        jake.foaf_name = "Jake"
        jake.save()

        jacob = session.get_resource("http://Jacob", Person)
        jacob.foaf_name = "Jacob"
        jacob.save()

        store.clear(context)

        persons = list(Person.all().context(context))
        self.assertEquals(len(persons), 0)
        persons = list(Person.all().context(NO_CONTEXT))
        self.assertEquals(len(persons), 1)

        # Now clear default context
        jake = session.get_resource("http://Jake", Person, context = context)
        jake.foaf_name = "Jake"
        jake.save()

        store.clear()

        persons = list(Person.all().context(context))
        self.assertEquals(len(persons), 1)
        # Only Jake is left
        persons = list(Person.all().context(NO_CONTEXT))
        self.assertEquals(len(persons), 1)

    def test_namespace_as_context(self):
        """ Test rdflib.Namespace given as context. """

        store, session = self._get_store_session(use_default_context=False)
        Person = session.get_class(surf.ns.FOAF + "Person")

        # Don't pass URIRef, pass Namespace (which inherits URIRef)
        surf.ns.register(mycontext="http://my_context_1#")
        context = surf.ns.MYCONTEXT
        store.clear(context)

        jake = session.get_resource("http://Jake", Person, context = context)
        jake.foaf_name = "Jake"
        jake.save()

        persons = list(Person.all().context(context))
        self.assertEquals(len(persons), 1)

        store.clear(context)

        persons = list(Person.all().context(context))
        self.assertEquals(len(persons), 0)

    def test_execute_json_result(self):
        """ Test execute_sparql() returns proper JSON. """
        store, session = self._get_store_session(use_default_context=False)
        self._create_persons(session)

        Person = session.get_class(surf.ns.FOAF + "Person")
        query = ('SELECT ?s ?n WHERE { ?s a <%(type)s> . ?s <%(name)s> ?n }'
                 % {'type': Person.uri, 'name': surf.ns.FOAF.name})
        result = store.execute_sparql(query, format='JSON')

        self.assertEquals(result['head']['vars'], ['s', 'n'])
        self.assertEquals(set(b['s']['value'] for b in result['results']['bindings']),
                          set(unicode(p.subject) for p in Person.all()))
        self.assertEquals(set(b['s']['type'] for b in result['results']['bindings']),
                          set(['uri']))

    def test_execute_ask_json_result(self):
        """ Test execute_sparql() with ASK returns proper JSON. """
        store, session = self._get_store_session(use_default_context=False)
        self._create_persons(session)

        Person = session.get_class(surf.ns.FOAF + "Person")
        query = 'ASK { ?s a <%(type)s> }' % {'type': Person.uri}
        result = store.execute_sparql(query, format='JSON')

        self.assert_('head' in result)
        self.assertEquals(result['boolean'], True)

    # TODO we currently do not support this feature
    #def test_keep_context_defaultgraphunion(self):
        #""" Test that context does not change during load/save when working
        #with the default graph as union over all named graphs. """
        #store, session = self._get_store_session(use_default_context=False)
        #Person = session.get_class(surf.ns.FOAF + "Person")

        #context = URIRef("http://my_context_1")
        #store.clear(context)

        #jake = session.get_resource("http://Jake", Person, context=context)
        #jake.foaf_name = "Jake"
        #jake.save()

        ## Get all persons, don't use context. Some stores like Virtuoso or
        ## AllegroGraph have designed the default graph (used when NO_CONTEXT
        ## given) to be the union over all named graphs. In this case we will
        ## yield entries from all contexts here.
        #persons = Person.all().context(NO_CONTEXT)
        #self.assert_(len(persons) < 2)

        #if len(persons) == 1:
            #jake = persons.one()
            #jake.load()
            #jake.foaf_name = "Jacob"
            #jake.save()

        ## Check that we only changed the foaf_name attribute
        #self.assertEquals(len(Person.all().context(context)), 1)
        #self.assertEquals(Person.all().context(context).one().foaf_name.first,
                          #'Jacob')

        #persons = Person.all().context(NO_CONTEXT)
        #self.assert_(len(persons) < 2)
