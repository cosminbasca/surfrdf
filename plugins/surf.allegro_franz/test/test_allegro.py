""" Module for rdflib plugin tests. """

from unittest import TestCase
import random

import surf
from surf.rdf import Literal, URIRef
from surf.util import value_to_rdf

class TestAllegro(TestCase):
    """ Tests for sparql_protocol plugin. """

    def setUp(self):
        rdf_store = surf.Store(reader = "allegro_franz",
                               writer = "allegro_franz",
                               server = "localhost",
                               port = 6789,
                               catalog = "repositories",
                               repository = "test_surf")

        self.rdf_session = surf.Session(rdf_store)
        self.Logic = self.rdf_session.get_class(surf.ns.SURF.Logic)

        for i in range(0, 10):
            instance = self.Logic()
            instance.save()

    def test_is_present(self):
        """ Test that is_present returns True / False.  """

        Person = self.rdf_session.get_class(surf.ns.FOAF + "Person")
        john = self.rdf_session.get_resource("http://john", Person)
        john.remove()

        self.assertEquals(john.is_present(), False)
        john.save()
        self.assertEquals(john.is_present(), True)

    def test_all(self):
        all = self.Logic.all().limit(10)
        assert len(all) == 10

    def test_resource(self):
        res = self.Logic.all().limit(1).first()

        assert res.uri == surf.ns.SURF.Logic
        assert hasattr(res, 'subject')
        assert type(res.subject) is URIRef
        assert res.is_present()
        assert res.namespace() == surf.ns.SURF

    def test_val2rdf(self):
        res = self.Logic.all().limit(1).first()
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
        res = self.Logic.all().limit(1).first()
        res.load()

    def test_concept(self):
        res = self.Logic.all().limit(1).first()
        con = res.concept(res.subject)[0]
        self.assertEquals(con, self.Logic.uri)
        
    def test_remove_inverse(self):
        
        session = self.rdf_session
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

        session = self.rdf_session
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

    def test_contains(self):
        session = self.rdf_session
        Person = session.get_class(surf.ns.FOAF + "Person")

        john = session.get_resource("http://John", Person)
        john.foaf_name = "John"
        john.update()

        persons = Person.get_by(foaf_name="John")
        self.assert_(any("John" in p.foaf_name for p in persons),
                     '"John" not found in foaf_name')
