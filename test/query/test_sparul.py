""" Module for SPARQL/Update generation tests. """

import re 
from unittest import TestCase

from surf.query.update import insert, load, delete, clear
from surf.query.translator.sparul import SparulTranslator 
from surf.rdf import URIRef

def canonical(sparql_string):
    """ Strip extra whitespace, convert to lowercase.
    
    This can be used to compare generated SPARQL queries and ignore whitespace,
    capitalization differences.
    
    """
    
    assert(isinstance(sparql_string, unicode))
    
    result = sparql_string.strip().lower()
    result = re.sub("\s\s+", " ", result)
    replacements = [ (" distinct where", " where"), # empty DISTINCT clause
                     ("{ ", "{"),                   # whitespace after {
                     (" }", "}"),                   # whitespace before }
                     (" .", "."),                   # whitespace before dot
                    ]
    
    for str1, str2 in replacements:
        result = result.replace(str1, str2)

    return result
    

class TestSparulTranslator(TestCase):
    """ Test SparulTranslator class. """
    
    def test_insert(self):
        """ Try to produce INSERT ..." query.  """
        
        
        expected = canonical(u"INSERT { <http://a> <http://b> <http://c> }")
        statement = URIRef("http://a"), URIRef("http://b"), URIRef("http://c")  
        query = insert().template(statement)
        result = canonical(SparulTranslator(query).translate())
        self.assertEqual(expected, result)
        
    def test_delete_from(self):
        """ Try to produce DELETE DATA FROM ... { ... } query. """
        
        expected = canonical(u"DELETE DATA FROM <g> { <a>  <b> <c> }")
        statement = URIRef("a"), URIRef("b"), URIRef("c")
        query = delete(data = True).from_(URIRef("g")).template(statement)
        result = canonical(SparulTranslator(query).translate())
        self.assertEqual(expected, result)
        
    def test_insert_data_into(self):
        """ INSERT DATA INTO ... { ... } """
        
        expected = canonical(u"INSERT DATA INTO <g> { <a>  <b> <c>. <a> <b> <d> }")
        st1 = URIRef("a"), URIRef("b"), URIRef("c")
        st2 = URIRef("a"), URIRef("b"), URIRef("d")
        query = insert(data = True).into(URIRef("g"))
        query.template(st1, st2)
        
        result = canonical(SparulTranslator(query).translate())
        self.assertEqual(expected, result)

    def test_delete_where(self):
        """ DELETE ... WHERE ... """
        
        expected = canonical(u"""
            DELETE { ?book ?p ?v }
            WHERE
              { ?book ?p ?v .
                FILTER ( ?date < "2000-01-01T00:00:00"^^xsd:dateTime )
              }
        """)        
        
        query = delete().template(("?book", "?p", "?v"))
        query.where(("?book", "?p", "?v"))
        query.filter('( ?date < "2000-01-01T00:00:00"^^xsd:dateTime )')
        
        result = canonical(SparulTranslator(query).translate())
        self.assertEqual(expected, result)
        
    def test_clear(self):
        """ CLEAR GRAPH """
        
        expected = canonical(u"""
            CLEAR GRAPH <a>
        """)        
        
        query = clear().graph(URIRef("a"))
        result = canonical(SparulTranslator(query).translate())
        self.assertEqual(expected, result)

    def test_load(self):
        """ LOAD ... """

        expected = canonical(u"""
            LOAD <http://example.com>
        """)

        query = load().load(URIRef("http://example.com"))
        result = canonical(SparulTranslator(query).translate())
        self.assertEqual(expected, result)

    def test_load_into(self):
        """ LOAD ... INTO ... """

        expected = canonical(u"""
            LOAD <http://example.com> INTO <http://example.com/graph>
        """)

        query = load().load(URIRef("http://example.com"))\
                      .into(URIRef("http://example.com/graph"))
        result = canonical(SparulTranslator(query).translate())
        self.assertEqual(expected, result)

    def test_unicode(self):
        """ Check that returned query string is unicode.  """
        
        statement = URIRef("http://a"), URIRef("http://b"), URIRef("http://c")  
        query = insert().template(statement)
        result = SparulTranslator(query).translate()
        self.assertTrue(isinstance(result, unicode))
        
    def test_str(self):
        """ Test that __str__ translates query to string. """
        
        expected = canonical(u"INSERT { <http://a> <http://b> <http://c> }")
        statement = URIRef("http://a"), URIRef("http://b"), URIRef("http://c")  
        query = insert().template(statement)
        
        # test str()
        self.assertEqual(expected, canonical(unicode(str(query))))        
        # test unicode()
        self.assertEqual(expected, canonical(unicode(query)))        
        
        
        