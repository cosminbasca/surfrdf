import pytest

import decimal
import surf
from surf.rdf import Literal
from surf.util import attr2rdf, rdf2attr, single, value_to_rdf


def test_rdf2attr():
    uri = "http://www.w3.org/2000/01/rdf-schema#label"
    assert rdf2attr(uri, True) == "rdfs_label"


def test_attr2rdf_period():
    """
    Check that attr2rdf handles minus symbol in predicate names.
    """

    uriref, _ = attr2rdf("surf_predicate-with-minus")
    assert uriref == surf.ns.SURF["predicate-with-minus"]


def test_single():
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
        assert instance.name == "v1"

        # Test setting "name" property.
        instance.name = "v2"
        assert instance.foaf_name == "v2"

        # Test deleting "name"
        del instance.name
        assert instance.foaf_name == []


def test_decimal_to_rdf():
    """
    Test conversion from decimal.Decimal to Literal.
    """

    v = value_to_rdf(decimal.Decimal("12.34"))
    assert type(v) == Literal


def test_rdf2attr_surf():
    """
    Test rdf2attr with SURF namespace.

    This once had a bug which generated attribute names
    like "__fallback_namespace_label"
    instead of "surf_label".
    """

    uri = "http://code.google.com/p/surfrdf/label"
    assert rdf2attr(uri, True) == "surf_label"
