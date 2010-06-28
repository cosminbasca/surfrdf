""" Module for SuRF exceptions. """

class CardinalityException(Exception):
    """ Raised when list length != 1.   
    
    Subclasses of this exception are raised by 
    :meth:`surf.resource.result_proxy.ResultProxy.one()` and 
    :meth:`surf.resource.value.ResultValue.get_one()`. 
    
    """

    pass

class NoResultFound(CardinalityException):
    """ Raised when list length == 0. 

    This exception is raised by 
    :meth:`surf.resource.result_proxy.ResultProxy.one()` and 
    :meth:`surf.resource.value.ResultValue.get_one()`. 
    
    """

    pass

class MultipleResultsFound(CardinalityException):
    """ Raised when list length > 1.  
 
    This exception is raised by 
    :meth:`surf.resource.result_proxy.ResultProxy.one()` and 
    :meth:`surf.resource.value.ResultValue.get_one()`. 

    """

    pass
