# coding=UTF-8
""" Module for SPARQL generation tests. """

from unittest import TestCase

from surf import ns
from surf.plugin.query_reader import RDFQueryReader

class TestQueryReader(TestCase):
    """ Tests for query_reader module. """
    
    def test_convert_unicode_exception(self):
        """ Test RDFQueryReader.convert() handles exceptions with unicode. """

        class MyQueryReader(RDFQueryReader):
            # We want convert() to catch an exception.
            # Cannot override __convert and throw from there,
            # but we know __convert calls _to_table... 
            def _to_table(self, _):
                raise Exception(u"This is unicode: ā")
            
            
        MyQueryReader().convert(None)
