# coding=UTF-8
import pytest
import logging
import warnings
from surf.plugin.query_reader import RDFQueryReader


def test_convert_unicode_exception():
    """
    Test RDFQueryReader.convert() handles exceptions with unicode.
    """

    class MyQueryReader(RDFQueryReader):
        def _ask(self, result):
            pass

        def _execute(self, query):
            pass

        # We want convert() to catch an exception.
        # Cannot override __convert and throw from there,
        # but we know __convert calls _to_table...
        def _to_table(self, _):
            warnings.simplefilter("ignore")
            raise Exception(u"This is unicode: ā")

    try:
        logging.disable(logging.ERROR)
        MyQueryReader().convert(None)
        logging.disable(logging.NOTSET)
    except Exception, e:
        pytest.fail(e.message, pytrace=True)
