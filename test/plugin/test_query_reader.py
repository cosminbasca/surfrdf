""" Module for SPARQL generation tests. """

from unittest import TestCase

from surf import ns
from surf.plugin.query_reader import RDFQueryReader

class TestQueryReader(TestCase):
    """ Tests for query_reader module. """
    
    def setUp(self):
        """ Prepare store and session. """
        
        pass
        
    def test_all_subjects(self):
        """ Test RDFQueryReader.all() method.  
            
        Mock query_reader._values function, test that _all returns list
        of URIs.
         
        """

        concept = ns.FOAF["PERSON"] 
        expected_result = {"uri1" : [concept], "uri2" : [concept]}

        query_reader = RDFQueryReader()
        def values_func(*args, **kwargs):
            return expected_result
        query_reader._values = values_func
        
        result = query_reader._all(concept)
        self.assertEqual(set(result), set(["uri1", "uri2"]))
        
    def test_all_full(self):
        """ Test RDFQueryReader.all() method with full=True. """

        concept = ns.FOAF["PERSON"] 
        expected_result = [("a", "b", "c")]
        query_reader = RDFQueryReader(use_subqueries = True)
        
        def triples_func(*args, **kwargs):
            return expected_result
        
        query_reader._triples = triples_func

        result = query_reader._all(concept, full = True)
        self.assertEqual(result, expected_result)
        
        
