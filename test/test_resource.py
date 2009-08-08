import os, os.path
import sys
from unittest import TestCase

from surf import ns
from surf.resource import Resource
from surf import *

#from rdf.namespace import Namespace, ClosedNamespace
#from rdf.term import URIRef, Literal
from rdflib.Namespace import Namespace
from rdflib.URIRef import URIRef
from rdflib.Literal import Literal

class TestResource(TestCase):
    def setUp(self):
        rdf_store = Store(  reader      =   'allegro_franz',
                            writer      =   'allegro_franz',
                            server      =   'localhost',
                            port        =   6789,
                            catalog     =   'repositories',
                            repository  =   'tagbuilder')
        self.rdf_session = Session(rdf_store, {})
        ns.register(tagbuilder='http://tagbuilder.deri.ie/ns#')
        
        self.Logic = self.rdf_session.get_class(ns.TAGBUILDER['Logic'])
        
    def tearDown(self):
        #self.rdf_session.close()
        pass
    
    def test_01_all(self):
        all = self.Logic.all(0,10)
        assert len(all) == 10
    
    def test_02_resource(self):
        all = self.Logic.all(0,10)
        res = all[0]
        assert res.uri == ns.TAGBUILDER['Logic']
        assert hasattr(res,'subject')
        assert type(res.subject) is URIRef
        assert res.is_present()
        assert res.namespace() == ns.TAGBUILDER

    def test_03_val2rdf(self):
        all = self.Logic.all(0,10)
        res = all[0]
        method = res._Resource__val2rdf
        assert type(method(str('Literal'))) is Literal and method(str('Literal')) == Literal('Literal')
        assert type(method(u'Literal')) is Literal and method(u'Literal') == Literal(u'Literal')
        # list
        assert method(['Literal','en',None]) == Literal('Literal',language = 'en')
        assert method(['Literal',None,ns.XSD['string']]) == Literal('Literal',datatype = ns.XSD['string'])
        # tuple
        assert method(('Literal','en',None)) == Literal('Literal',language = 'en')
        assert method(('Literal',None,ns.XSD['string'])) == Literal('Literal',datatype = ns.XSD['string'])
        # dict
        assert method({'value':'Literal','language':'en'}) == Literal('Literal',language = 'en')
        assert method({'value':'Literal','datatype':ns.XSD['string']}) == Literal('Literal',datatype = ns.XSD['string'])
        # resource
        assert method(res) == res.subject
        # other 
        assert method(10) == Literal(10)
        assert method(10.0) == Literal(10.0)
        # unknown
        o = object()
        assert method(o) == o

    def test_04_load(self):
        all = self.Logic.all(0,10)
        res = all[0]
        res.load()
        
    def test_05_concept(self):
        all = self.Logic.all(0,10)
        res = all[0]
        con = Resource.concept(res.subject)
        assert con == self.Logic.uri
        