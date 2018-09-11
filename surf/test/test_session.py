 # coding=UTF-8
import pytest

from surf import Session, Store


def test_close_multiples_stores():
    """
    Test that closing a session with multiple stores work.
    """
    try:
        store1 = Store()
        session = Session(store1)

        store2 = Store()
        session["store2"] = store2

        # Should not fail.
        session.close()
    except Exception as e:
        pytest.fail(e.message, pytrace=True)
