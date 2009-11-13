from unittest import TestCase

from surf.util import rdf2attr

class TestUtil(TestCase):
    def test_rdf2attr(self):
        uri = "http://www.w3.org/2000/01/rdf-schema#label"
        self.assertEqual(rdf2attr(uri, True), "rdfs_label")
        
        