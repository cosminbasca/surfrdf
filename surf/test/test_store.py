# coding=UTF-8
import pytest

import logging
import surf
from surf import Session, Store
from surf.plugin.reader import RDFReader
from surf.plugin.writer import RDFWriter


def test_multiples():
    """
    Test synchronization between empty attribute and rdf_direct.
    """

    store = Store(log_level=logging.NOTSET)
    session = Session(store)

    Person = session.get_class(surf.ns.FOAF.Person)

    rob = session.get_resource("http://Robert", Person)
    rob.foaf_name = "Robert"
    michael = session.get_resource("http://Michael", Person)
    michael.foaf_name = "Michael"

    try:
        store.save(rob, michael)
        store.update(rob, michael)
        store.remove(rob, michael)
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_close_unicode_exception():
    """
    Test that closing a store handles exceptions.
    """

    class MockReader(RDFReader):
        def _load(self, subject, direct, context):
            pass

        def _instances_by_attribute(self, concept, attributes, direct, context):
            pass

        def _is_present(self, subject, context):
            pass

        def _get(self, subject, attribute, direct, context):
            pass

        def _concept(self, subject):
            pass

        def close(self):
            raise Exception(u"Some unicode: ā")

    class MockWriter(RDFWriter):
        def _set_triple(self, s=None, p=None, o=None, context=None):
            pass

        def _update(self, *resources):
            pass

        def _save(self, *resources):
            pass

        def _remove(self, *resources, **kwargs):
            pass

        def _clear(self, context=None):
            pass

        def _add_triple(self, s=None, p=None, o=None, context=None):
            pass

        def _size(self):
            pass

        def close(self):
            raise Exception(u"Some unicode: ā")

    try:
        reader = MockReader()
        store = Store(reader, MockWriter(reader), log_level=logging.NOTSET)
        logging.disable(logging.ERROR)
        store.close()
        logging.disable(logging.NOTSET)
    except Exception, e:
        pytest.fail(e.message, pytrace=True)


def test_successful_close():
    """
    Test that store handles successful reader and writer closes.
    """

    class MockReader(RDFReader):
        def _load(self, subject, direct, context):
            pass

        def _instances_by_attribute(self, concept, attributes, direct, context):
            pass

        def _is_present(self, subject, context):
            pass

        def _get(self, subject, attribute, direct, context):
            pass

        def _concept(self, subject):
            pass

        def close(self):
            pass

    class MockWriter(RDFWriter):
        def _set_triple(self, s=None, p=None, o=None, context=None):
            pass

        def _update(self, *resources):
            pass

        def _save(self, *resources):
            pass

        def _remove(self, *resources, **kwargs):
            pass

        def _clear(self, context=None):
            pass

        def _add_triple(self, s=None, p=None, o=None, context=None):
            pass

        def _size(self):
            pass

        def close(self):
            pass

    try:
        reader = MockReader()
        store = Store(reader, MockWriter(reader), log_level=logging.NOTSET)
        store.close()
    except Exception, e:
        pytest.fail(e.message, pytrace=True)
