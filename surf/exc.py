""" Module for SuRF exceptions. """

class CardinalityException(Exception):
    """ Used by ResultProxy.one() and ResultValue.one when list length != 1. """

    pass

class NoResultFound(CardinalityException):
    """ Used by ResultProxy.one() and ResultValue.one when list length == 0. """

    pass

class MultipleResultsFound(CardinalityException):
    """ Used by ResultProxy.one() and ResultValue.one when list length > 1. """

    pass
