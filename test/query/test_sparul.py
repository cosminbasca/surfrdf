""" Module for SPARQL/Update generation tests. """

import re 
from unittest import TestCase

from rdflib.URIRef import URIRef

from surf.query.update import insert, delete, clear
from surf.query.translator.sparul import SparulTranslator 

def canonical(sparql_string):
    """ Strip extra whitespace, convert to lowercase.
    
    This can be used to compare generated SPARQL queries and ignore whitespace,
    capitalization differences.
    
    """
    
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
        
        
        expected = canonical("INSERT { <http://a> <http://b> <http://c> }")
        statement = URIRef("http://a"), URIRef("http://b"), URIRef("http://c")  
        query = insert().template(statement)
        result = canonical(SparulTranslator(query).translate())
        self.assertEqual(expected, result)
        
    def test_delete_from(self):
        """ Try to produce DELETE DATA FROM ... { ... } query. """
        
        expected = canonical("DELETE DATA FROM <g> { <a>  <b> <c> }")
        statement = URIRef("a"), URIRef("b"), URIRef("c")
        query = delete(data = True).from_(URIRef("g")).template(statement)
        result = canonical(SparulTranslator(query).translate())
        self.assertEqual(expected, result)
        
    def test_insert_data_into(self):
        """ INSERT DATA INTO ... { ... } """
        
        expected = canonical("INSERT DATA INTO <g> { <a>  <b> <c>. <a> <b> <d> }")
        st1 = URIRef("a"), URIRef("b"), URIRef("c")
        st2 = URIRef("a"), URIRef("b"), URIRef("d")
        query = insert(data = True).into(URIRef("g"))
        query.template(st1, st2)
        
        result = canonical(SparulTranslator(query).translate())
        self.assertEqual(expected, result)

    def test_delete_where(self):
        """ DELETE ... WHERE ... """
        
        expected = canonical("""
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
        
        expected = canonical("""
            CLEAR GRAPH <a>
        """)        
        
        query = clear().graph(URIRef("a"))
        result = canonical(SparulTranslator(query).translate())
        self.assertEqual(expected, result)

    def test_unicode(self):
        """ Check that returned query string is unicode.  """
        
        statement = URIRef("http://a"), URIRef("http://b"), URIRef("http://c")  
        query = insert().template(statement)
        result = SparulTranslator(query).translate()
        self.assertTrue(isinstance(result, unicode))
        
        
        
        
        
        
        
        