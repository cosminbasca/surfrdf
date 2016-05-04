import pytest

from surf import ns
from surf.rdf import Namespace
from surf.util import get_namespace as util_get_namespace


@pytest.mark.run(order=1)
def test_register():
    ns.register(test='http://sometest.ns/ns#')
    assert ns.TEST == Namespace('http://sometest.ns/ns#')


@pytest.mark.run(order=2)
def test_get_namespace():
    key, namespace = ns.get_namespace('http://sometest.ns/ns#')
    assert key == 'TEST'
    assert namespace == Namespace('http://sometest.ns/ns#')

    key1, namespace1 = ns.get_namespace('http://sometest1.ns/ns#')
    assert key1 == 'NS1'
    assert namespace1 == Namespace('http://sometest1.ns/ns#')


@pytest.mark.run(order=3)
def test_get_namespace_url():
    url = ns.get_namespace_url('TEST')
    assert url == Namespace('http://sometest.ns/ns#')

    url1 = ns.get_namespace_url('NS1')
    assert url1 == Namespace('http://sometest1.ns/ns#')


@pytest.mark.run(order=4)
def test_get_prefix():
    name = ns.get_prefix(Namespace('http://sometest.ns/ns#'))
    assert name == 'TEST'

    name1 = ns.get_prefix('http://sometest1.ns/ns#')
    assert name1 == 'NS1'


@pytest.mark.last
def test_get_prefix_predefined():
    """
    Test get_prefix with predefined namespaces.
    """
    prefix, _ = util_get_namespace(ns.RDFS)
    assert prefix == "RDFS"

    prefix, _ = util_get_namespace(ns.GEO)
    assert prefix == "GEO"
