import pytest
import surf


def test_rdflib_store():
    """
    Create a SuRF rdflib based store
    """

    kwargs = {"reader": "rdflib", "writer": "rdflib"}

    if False:  # use_default_context:
        kwargs["default_context"] = "http://surf_test_graph/dummy2"

    try:
        store = surf.Store(**kwargs)
        session = surf.Session(store)

        # clean store
        store.clear()
    except Exception, e:
        pytest.fail(e.message, pytrace=True)
