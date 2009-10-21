""" Module for ResultProxy. """

from surf.util import attr2rdf

class CardinalityException(Exception):
    """ Used by ResultProxy.one() when list length != 1. """

    pass

class ResultProxy(object):
    """ Interface to :meth:`surf.store.get_by()`.
    
    ResultProxy collects filtering parameters. When iterated, it executes
    :meth:`surf.store.get_by()` with collected parameters and yields results. 
    
    ResultProxy doesn't know how to convert data returned by 
    :meth:`surf.store.get_by()` into :class:`surf.Resource`, `URIRef` 
    and `Literal` objects. It delegates this task to `instancemaker`
    function.
    
    """
    
    def __init__(self, params = {}, store = None, instancemaker = None):
        self.__params = params
        self.__data_cache = None
        
        if store:
            self.__params["store"] = store

        if instancemaker:
            self.__params["instancemaker"] = instancemaker

    def instancemaker(self, instancemaker_function):
        """ Specify the function for converting triples into instances. 
        
        ``instancemaker_function`` function can also be specified 
        as argument to constructor when instantiating :class:`ResultProxy`. 

        ``instancemaker_function`` will be executed whenever 
        :class:`ResultProxy` needs to return a resource. It has to accept two 
        arguments: ``params`` and ``instance_data``.
        
        ``params`` will be a dictionary containing query parameters gathered
        by :class:`ResultProxy`. Information from ``params`` can be used 
        by ``instancemaker_function``, for example, to decide what 
        context should be set for created instances. 

        ``instance_data`` will be a dictionary containing keys `direct` and
        `inverse`. These keys map to dictionaries describing direct and 
        inverse attributes respectively.
        
        """
         
        params = self.__params.copy()
        params["instancemaker"] = instancemaker_function
        return ResultProxy(params)

    def limit(self, value):
        """ Set the limit for returned result count. """
         
        params = self.__params.copy()
        params["limit"] = value
        return ResultProxy(params)

    def offset(self, value):
        params = self.__params.copy()
        params["offset"] = value
        return ResultProxy(params)
    
    def full(self, only_direct = False):
        params = self.__params.copy()
        params["full"] = True
        params["only_direct"] = only_direct
        return ResultProxy(params)
    
    def order(self, value = True):
        params = self.__params.copy()
        params["order"] = value
        return ResultProxy(params)
    
    def desc(self):
        params = self.__params.copy()
        params["desc"] = True
        return ResultProxy(params)
    
    def get_by(self, **kwargs):
        params = self.__params.copy()
        params["get_by"] = []
        for name, value in kwargs.items():
            attr, direct = attr2rdf(name)
            params["get_by"].append((attr, value, direct))
        return ResultProxy(params)

    def context(self, context):
        params = self.__params.copy()
        params["context"] = context
        return ResultProxy(params)
    
    def __get_data_cache(self):
        if self.__data_cache is None:
            self.__execute()
        
        return self.__data_cache
    
    def __execute(self):
        store = self.__params["store"]

        get_by_args = {}
        for key in ["limit", "offset", "full", "order", "desc", "get_by", 
                    "only_direct", "context"]:
            if key in self.__params:
                get_by_args[key] = self.__params[key]
        
        if self.__data_cache is None:
            self.__data_cache = store.get_by(get_by_args)

        instancemaker = self.__params["instancemaker"]
        for instance_data in self.__get_data_cache():
            yield instancemaker(get_by_args, instance_data)

        
    def __iter__(self):
        return self.__execute()

    def first(self):
        """ Return first resource or None if there aren't any. """
        
        item = None
        try:
            item = iter(self).next()
        except StopIteration:
            pass
        
        return item

    def one(self):
        """ Return the only resource or raise if resource count != 1. """
        
        iterator = iter(self)
        try:
            item = iterator.next()
        except StopIteration:
            raise CardinalityException("List is empty")
        
        try:
            iterator.next()
        except StopIteration:
            # As expected, return item
            return item
        
        raise CardinalityException("List has more than one item")
        
        
        
        
        