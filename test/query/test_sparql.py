""" Module for SPARQL generation tests. """

import re 
from unittest import TestCase

from rdflib.URIRef import URIRef

from surf.query import select
from surf.query.translator.sparql import SparqlTranslator 

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
    

class TestSparqlTranslator(TestCase):
    """ Test SparqlTranslator class. """
    
    def test_simple(self):
        """ Try to produce a simple "SELECT ... WHERE ..." query.  """
        
        expected = canonical("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
        query = select("?s", "?p", "?o").where(("?s", "?p", "?o"))
        result = canonical(SparqlTranslator(query).translate())
        
        self.assertEqual(expected, result)
        
        
    def test_subquery(self):
        """ Try to produce query that contains subquery in WHERE clause. """
        
        expected = canonical("""
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
        
        expected = canonical("""
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
        
        
        
        
        
         
        
        