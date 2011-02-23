""" Module for SPARQL generation tests. """

import re 
from unittest import TestCase

from surf.query import select, describe, ask
from surf.query.translator.sparql import SparqlTranslator 
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
    

class TestSparqlTranslator(TestCase):
    """ Test SparqlTranslator class. """
    
    def test_simple(self):
        """ Try to produce a simple "SELECT ... WHERE ..." query.  """
        
        expected = canonical(u"SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
        query = select("?s", "?p", "?o").where(("?s", "?p", "?o"))
        result = SparqlTranslator(query).translate()

        # Translated query should be unicode object.
        self.assertTrue(isinstance(result, unicode))
        
        result = canonical(result)
        self.assertEqual(expected, result)
        
        
    def test_subquery(self):
        """ Try to produce query that contains subquery in WHERE clause. """
        
        expected = canonical(u"""
            SELECT ?s ?p ?o 
            WHERE { 
                ?s ?p ?o. 
                { SELECT ?s WHERE { ?s ?a ?b } LIMIT 3 }
            }
        """)
        
        subquery = select("?s").where(("?s", "?a", "?b")).limit(3)
        
        query = select("?s", "?p", "?o").where(("?s", "?p", "?o"), subquery)
        result = canonical(SparqlTranslator(query).translate())
        
        self.assertEqual(expected, result)
        
        
    def test_from(self):
        """ Try to produce query that contains FROM clauses. """
        
        expected = canonical(u"""
            SELECT ?s ?p ?o
            FROM <http://uri1>
            FROM <http://uri2> 
            WHERE { 
                ?s ?p ?o 
            }
        """)
        
        query = select("?s", "?p", "?o").where(("?s", "?p", "?o"))
        query.from_("http://uri1", URIRef("http://uri2"))
        result = canonical(SparqlTranslator(query).translate())
        
        self.assertEqual(expected, result)

    def test_from_named(self):
        """ Try to produce query that contains FROM & FROM NAMED clauses. """

        expected = canonical(u"""
            SELECT ?s ?p ?o
            FROM <http://uri1>
            FROM NAMED <http://uri1>
            FROM NAMED <http://uri2>
            WHERE {
                ?s ?p ?o
            }
        """)

        query = select("?s", "?p", "?o").where(("?s", "?p", "?o"))
        query.from_("http://uri1")
        query.from_named("http://uri1", URIRef("http://uri2"))
        result = canonical(SparqlTranslator(query).translate())

        self.assertEqual(expected, result)

    def test_describe(self):
        """ Try to produce DESCRIBE query. """
        
        expected = canonical(u"""
            DESCRIBE ?s
            FROM <http://uri1>
            WHERE { 
                ?s ?p ?o 
            } LIMIT 10
        """)

        query = describe("?s").where(("?s", "?p", "?o"))
        query.from_("http://uri1").limit(10)
        result = canonical(SparqlTranslator(query).translate())
        
        self.assertEqual(expected, result)
        
    def test_from_none(self):
        """ Check that .from_(None) raises. """
        
        query = select("?s")
        self.assertRaises(ValueError, lambda: query.from_(None))

    def test_union(self):
        """ Try to produce query containing union. """
        
        expected = canonical(u"""
            SELECT ?s
            WHERE {
                { ?s ?v1 ?v2} UNION { ?s ?v3  ?v4 }
            }
        """)

        query = select("?s").union(("?s", "?v1", "?v2"), ("?s", "?v3", "?v4"))
        result = canonical(SparqlTranslator(query).translate())
        
        self.assertEqual(expected, result)

    def test_str(self):
        """ Try str(query). """
        
        expected = canonical(u"""
            SELECT ?s ?p ?o
            WHERE { 
                ?s ?p ?o 
            }
        """)
        
        query = select("?s", "?p", "?o").where(("?s", "?p", "?o"))
        # test str()
        self.assertEqual(expected, canonical(unicode(str(query))))
        # test unicode()
        self.assertEqual(expected, canonical(unicode(query)))

    def test_ask(self):
        """ Try ASK. """

        expected = canonical(u"""
            ASK FROM <http://uri1>
            {
                ?s ?p ?o
            }
        """)

        query = ask().from_(URIRef("http://uri1")).where(("?s", "?p", "?o"))

        result = canonical(SparqlTranslator(query).translate())
        self.assertEqual(expected, result)
