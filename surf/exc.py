""" Module for SuRF exceptions. """

class CardinalityException(Exception):
    """ Used by ResultProxy.one() and ResultValue.one when list length != 1. """

    pass
