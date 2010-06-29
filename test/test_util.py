""" Module for surf.util tests. """

from unittest import TestCase

import surf
from surf.util import attr2rdf, rdf2attr, single

class TestUtil(TestCase):
    """ Tests for surf.util module. """
    
    def test_rdf2attr(self):
        uri = "http://www.w3.org/2000/01/rdf-schema#label"
        self.assertEqual(rdf2attr(uri, True), "rdfs_label")

    def test_attr2rdf_period(self):
        """ Check that attr2rdf handles minus symbol in predicate names. """
        
        uriref, _ = attr2rdf("surf_predicate-with-minus")
        self.assertEquals(uriref, surf.ns.SURF["predicate-with-minus"])
        
    def test_single(self):
        class ResourceValueMock(object):
            value = "v1"
            first = "v1"
        
        class MyClass(object):
            foaf_name = ResourceValueMock()
            name = single("foaf_name")

        class MyClass2(object):
            foaf_name = ResourceValueMock()
            name = single(surf.ns.FOAF.name)
    
        for kls in [MyClass, MyClass2]:
        
            # Test getting "name" property.
            instance = kls()
            self.assertEquals(instance.name, "v1")
            
            # Test setting "name" property.
            instance.name = "v2"
            self.assertEquals(instance.foaf_name, "v2")

            # Test deleting "name"
            del instance.name
            self.assertEquals(instance.foaf_name, [])
