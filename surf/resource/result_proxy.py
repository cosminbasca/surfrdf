""" Module for ResultProxy. """

from surf.rdf import Literal
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
        self.__get_by_response = None

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
        """ Set the limit for returned results. """

        params = self.__params.copy()
        params["offset"] = value
        return ResultProxy(params)

    def full(self, only_direct = False):
        """ Enable eager-loading of resource attributes.

        If ``full`` is set to `True`, returned resources will have attributes
        already loaded.

        Whether setting this will bring performance
        improvements depends on reader plugin implementation.
        For example, sparql_protocol plugin is capable of using SPARQL
        subqueries to fully load multiple resources in one request.

         """

        params = self.__params.copy()
        params["full"] = True
        params["only_direct"] = only_direct
        return ResultProxy(params)

    def order(self, value = True):
        """ Request results to be ordered.

        If no arguments are specified, resources will be ordered by their
        subject URIs.

        If ``value`` is set to an URIRef, corresponding attribute will be
        used for sorting. For example, sorting persons by surname::

            FoafPerson = session.get_class(surf.ns.FOAF.Person)
            for person in FoafPerson.all().order(surf.ns.FOAF.surname):
                print person.foaf_name.first, person.foaf_surname.first

        Currently only one sorting key is supported.

        """

        params = self.__params.copy()
        params["order"] = value
        return ResultProxy(params)

    def desc(self):
        """ Set sorting order to descending. """

        params = self.__params.copy()
        params["desc"] = True
        return ResultProxy(params)

    def get_by(self, **kwargs):
        """ Add filter conditions.

        Arguments are expected in form::

            foaf_name = "John"

        Multiple arguments are supported.
        An example that retrieves all persons named "John Smith"::

            FoafPerson = session.get_class(surf.ns.FOAF.Person)
            for person in FoafPerson.get_by(foaf_name = "John", foaf_surname = "Smith"):
                print person.subject

        """

        params = self.__params.copy()
        # Don't overwrite existing get_by parameters, just append new ones.
        # Overwriting get_by params would cause resource.some_attr.get_by()
        # to work incorrectly.
        params.setdefault("get_by", [])
        for name, value in kwargs.items():
            attr, direct = attr2rdf(name)
            # Assume by plain strings user means literals
            if type(value) in [str, unicode]:
                value = Literal(value)
            
            # If value has subject attribute, this must be Resource, 
            # take its subject.
            if hasattr(value, "subject"):
                value = value.subject
             
            params["get_by"].append((attr, value, direct))
        return ResultProxy(params)

    def filter(self, **kwargs):
        """ Add filter conditions.

        Expects arguments in form::

            ns_predicate = "(%s > 15)"

        ``ns_predicate`` specifies which predicate will be used for
        filtering, a query variable will be bound to it. `%s` is a placeholder
        for this variable.

        Filter expression (in example: "(%s > 15)") must follow SPARQL
        specification, on execution "%s" will be substituted with variable
        and the resulting string will be placed in query as-is. Because of
        string substitution percent signs need to be escaped. For example::

            Person.all().filter(foaf_name = "(%s LIKE 'J%%')")

        This Virtuoso-specific filter is intended to select persons with names starting with
        "J". In generated query it will look like this::

            ...
            ?s <http://xmlns.com/foaf/0.1/name> ?f1 .
            FILTER (?f1 LIKE 'J%')
            ...

        """

        params = self.__params.copy()
        params.setdefault("filter", [])
        for name, value in kwargs.items():
            attr, direct = attr2rdf(name)
            assert direct, "Only direct attributes can be used for filters"
            # Assume by plain strings user means literals
            if type(value) in [str, unicode]:
                value = Literal(value)
            params["filter"].append((attr, value, direct))
        return ResultProxy(params)

    def context(self, context):
        """ Specify context/graph that resources should be loaded from. """

        params = self.__params.copy()
        params["context"] = context
        return ResultProxy(params)

    def __execute_get_by(self):
        if self.__get_by_response is None:
            self.__get_by_args = {}

            for key in ["limit", "offset", "full", "order", "desc", "get_by",
                        "only_direct", "context", "filter"]:
                if key in self.__params:
                    self.__get_by_args[key] = self.__params[key]

            store = self.__params["store"]
            self.__get_by_response = store.get_by(self.__get_by_args)

        return self.__get_by_args, self.__get_by_response

    def __iterator(self):
        get_by_args, get_by_response = self.__execute_get_by()

        instancemaker = self.__params["instancemaker"]
        for instance_data in get_by_response:
            yield instancemaker(get_by_args, instance_data)


    def __iter__(self):
        """ Return iterator over resources in this collection. """

        return self.__iterator()

    def __len__(self):
        """ Return count of resources in this collection. """

        _, get_by_response = self.__execute_get_by()
        return len(get_by_response)

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