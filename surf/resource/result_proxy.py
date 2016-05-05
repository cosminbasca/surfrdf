""" Module for ResultProxy. """

from surf.exceptions import NoResultFound, MultipleResultsFound
from surf.rdf import Literal
from surf.util import attr2rdf, value_to_rdf


class ResultProxy(object):
    """ Interface to :meth:`surf.store.Store.get_by`.

    ResultProxy collects filtering parameters. When iterated, it executes
    :meth:`surf.store.Store.get_by` with collected parameters and yields results.

    ResultProxy doesn't know how to convert data returned by
    :meth:`surf.store.Store.get_by` into :class:`surf.resource.Resource`, `URIRef`
    and `Literal` objects. It delegates this task to `instance_factory`
    function.

    """

    def __init__(self, params = None, store = None, instance_factory = None):
        self._params = params if params else dict()
        self._get_by_response = None

        if store is not None:
            self._params["store"] = store

        if instance_factory is not None:
            self._params["instance_factory"] = instance_factory

    def instance_factory(self, instance_factory_func):
        """ Specify the function for converting triples into instances.

        ``instance_factory_func`` function can also be specified
        as argument to constructor when instantiating :class:`ResultProxy`.

        ``instance_factory_func`` will be executed whenever
        :class:`ResultProxy` needs to return a resource. It has to accept two
        arguments: ``params`` and ``instance_data``.

        ``params`` will be a dictionary containing query parameters gathered
        by :class:`ResultProxy`. Information from ``params`` can be used
        by ``instance_factory_func``, for example, to decide what
        context should be set for created instances.

        ``instance_data`` will be a dictionary containing keys `direct` and
        `inverse`. These keys map to dictionaries describing direct and
        inverse attributes respectively.

        """

        params = self._params.copy()
        params["instance_factory"] = instance_factory_func
        return ResultProxy(params)

    def limit(self, value):
        """ Set the limit for returned result count. """

        params = self._params.copy()
        params["limit"] = value
        return ResultProxy(params)

    def offset(self, value):
        """ Set the limit for returned results. """

        params = self._params.copy()
        params["offset"] = value
        return ResultProxy(params)

    def full(self, direct_only = False, **kwargs):
        """ Enable eager-loading of resource attributes.

        With this modifier, resources will have their attributes
        already loaded.
        
        If ``only_direct`` is set to `True`, only direct attributes
        will be loaded. Accessing inverse attributes will work
        but will generate extra requests to triple store.

        Whether setting this will bring performance
        improvements depends on reader plugin implementation.
        For example, sparql_protocol plugin is capable of using SPARQL
        subqueries to fully load multiple resources in one request.

         """

        params                  = self._params.copy()
        params['full']          = True
        params['direct_only']   = direct_only
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

        params = self._params.copy()
        params["order"] = value
        return ResultProxy(params)

    def desc(self):
        """ Set sorting order to descending. """

        params = self._params.copy()
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

        params = self._params.copy()
        # Don't overwrite existing get_by parameters, just append new ones.
        # Overwriting get_by params would cause resource.some_attr.get_by()
        # to work incorrectly.
        params.setdefault("get_by", [])
        for name, value in kwargs.items():
            attr, direct = attr2rdf(name)

            if hasattr(value, "subject"):
                # If value has a subject attribute, this must be a Resource, 
                # take its subject.
                value = value.subject
            elif hasattr(value, "__iter__"):
                # Map alternatives
                value = map(lambda val: hasattr(val, "subject")
                                        and val.subject
                                        or value_to_rdf(val),
                            value)
            else:
                value = value_to_rdf(value)

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

        params = self._params.copy()
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

        params = self._params.copy()
        params["context"] = context
        return ResultProxy(params)

    def __execute_get_by(self):
        if self._get_by_response is None:
            self.__get_by_args = {}

            for key in ['limit', 'offset', 'full', 'order', 'desc', 'get_by',
                        'direct_only', 'context', 'filter']:
                if key in self._params:
                    self.__get_by_args[key] = self._params[key]

            store = self._params['store']
            self._get_by_response = store.get_by(self.__get_by_args)

        return self.__get_by_args, self._get_by_response

    def __iterator(self):
        get_by_args, get_by_response = self.__execute_get_by()

        instance_factory = self._params['instance_factory']
        for instance_data in get_by_response:
            yield instance_factory(get_by_args, instance_data)

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
        """ Return the only resource or raise if resource count != 1. 
        
        If the query matches no resources, this method will raise
        :class:`surf.exc.NoResultFound` exception. If the query matches 
        more than one resource, this method will raise
        :class:`surf.exc.MultipleResultsFound` exception. 
        
        """

        iterator = iter(self)
        try:
            item = iterator.next()
        except StopIteration:
            raise NoResultFound("List is empty")

        try:
            iterator.next()
        except StopIteration:
            # As expected, return item
            return item

        raise MultipleResultsFound("List has more than one item")