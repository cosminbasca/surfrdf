# Copyright (c) 2009, Digital Enterprise Research Institute (DERI),
# NUI Galway
# All rights reserved.

# author: Cosmin Basca
# email: cosmin.basca@gmail.com

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer
#      in the documentation and/or other materials provided with
#      the distribution.
#    * Neither the name of DERI nor the
#      names of its contributors may be used to endorse or promote
#      products derived from this software without specific prior
#      written permission.

# THIS SOFTWARE IS PROVIDED BY DERI ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DERI BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from surf.plugin.reader import RDFReader
from surf.query import Query, Union
from surf.query import a, ask, select, optional_group, named_group
from surf.rdf import URIRef
from surf.log import *

__author__ = 'Cosmin Basca'


def query_sp(s, p, direct, context):
    """
    Construct :class:`surf.query.Query` with `?v` and `?c` as unknowns.

    :param s: the `subject`
    :param p: the `predicate`
    :param bool direct: whether the predicate is direct or inverse
    :param context: the context
    :return: the query
    :rtype: :class:`surf.query.Query`
    """
    s, v = (s, '?v') if direct else ('?v', s)
    query = select('?v', '?c').distinct()
    query.where((s, p, v)).optional_group(('?v', a, '?c'))
    if context:
        query.from_(context)

    return query


def query_s(s, direct, context):
    """
    Construct :class:`surf.query.Query` with `?p`, `?v` and `?c` as unknowns.

    :param s: the `subject`
    :param bool direct: whether the predicate is direct or inverse
    :param context: the context
    :return: the query
    :rtype: :class:`surf.query.Query`
    """
    s, v = (s, '?v') if direct else ('?v', s)
    query = select('?p', '?v', '?c').distinct()
    query.where((s, '?p', v)).optional_group(('?v', a, '?c'))
    if context:
        query.from_(context)

    return query


def query_ask(s, context):
    """
    Construct :class:`surf.query.Query` of type **ASK**.

    :param s: the `subject`
    :param context: the context
    :return: the query
    :rtype: :class:`surf.query.Query`
    """
    query = ask()
    if context:
        pattern = named_group(context, (s, '?p', '?o'))
        query.where(pattern)
    else:
        query.where((s, '?p', '?o'))

    return query


def query_p_s(c, p, direct, context):
    """
    Construct :class:`surf.query.Query` with `?s` and `?c` as unknowns.

    :param c: the `class`
    :param p: the `predicate`
    :param bool direct: whether the predicate is direct or inverse
    :param context: the context
    :return: the query
    :rtype: :class:`surf.query.Query`
    """

    query = select('?s', '?c').distinct()
    if context:
        query.from_(context)

    for i in range(len(p)):
        s, v = ('?s', '?v{0:d}'.format(i)) if direct else ('?v{0:d}'.format(i), '?s')
        if type(p[i]) is URIRef:
            query.where((s, p[i], v))

    query.optional_group(('?s', a, '?c'))

    return query


def query_concept(s):
    """
    Construct :class:`surf.query.Query` with `?c` as the unknown.

    :param s: the `subject`
    :return: the query
    :rtype: :class:`surf.query.Query`
    """

    return select('?c').distinct().where((s, a, '?c'))


def _apply_solution_modifiers(params, query):
    """
    Apply limit, offset, order parameters to query.
    """
    if "limit" in params:
        query.limit(params["limit"])

    if "offset" in params:
        query.offset(params["offset"])

    if "get_by" in params:
        def order_terms(s, p, o):
            return (s, p, o) if direct else (o, p, s)

        for attribute, values, direct in params["get_by"]:
            if hasattr(values, "__iter__"):
                where_clause = Union()
                for value in values:
                    where_clause.append(order_terms("?s", attribute, value))
            else:
                where_clause = order_terms("?s", attribute, values)

            query.where(where_clause)

    if "filter" in params:
        filter_idx = 0
        for attribute, value, direct in params["filter"]:
            filter_idx += 1
            filter_variable = "?f%d" % filter_idx
            query.where(("?s", attribute, filter_variable))
            query.filter(value % filter_variable)

    if "order" in params:
        if params["order"]:
            # Order by subject URI
            if "desc" in params and params["desc"]:
                query.order_by("DESC(?s)")
            else:
                query.order_by("?s")
        else:
            # Match another variable, order by it
            query.optional_group(("?s", params["order"], "?o"))
            if "desc" in params and params["desc"]:
                query.order_by("DESC(?o)")
            else:
                query.order_by("?o")

    return query


class RDFQueryReader(RDFReader):
    """
    Super class for SuRF Reader plugins that wrap queryable `stores`.
    """

    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        super(RDFQueryReader, self).__init__(*args, **kwargs)
        self.use_subqueries = kwargs.get('use_subqueries', False)
        if isinstance(self.use_subqueries, str):
            self.use_subqueries = (self.use_subqueries.lower() == 'true')
        elif not isinstance(self.use_subqueries, bool):
            raise ValueError('The use_subqueries parameter must be a bool or a string set to "true" or "false"')

    def _get(self, subject, attribute, direct, context):
        query = query_sp(subject, attribute, direct, context)
        result = self._execute(query)
        return self.convert(result, 'v', 'c')

    def _load(self, subject, direct, context):
        query = query_s(subject, direct, context)
        result = self._execute(query)
        return self.convert(result, 'p', 'v', 'c')

    def _is_present(self, subject, context):
        query = query_ask(subject, context)
        result = self._execute(query)
        return self._ask(result)

    def _concept(self, subject):
        query = query_concept(subject)
        result = self._execute(query)
        return self.convert(result, 'c')

    def _instances_by_attribute(self, concept, attributes, direct, context):
        query = query_p_s(concept, attributes, direct, context)
        result = self._execute(query)
        return self.convert(result, 's', 'c')

    def _get_by(self, params):
        # Decide which loading strategy to use
        if "full" in params:
            if self.use_subqueries:
                return self._get_by_subquery(params)
            else:
                return self._get_by_n_queries(params)

        # No details, just subjects and classes
        query = select("?s", "?c")
        _apply_solution_modifiers(params, query)
        query.optional_group(("?s", a, "?c"))

        context = params.get("context", None)
        if not (context is None):
            query.from_(context)

        # Load just subjects and their types
        table = self._to_table(self._execute(query))

        # Create response structure, preserve order, don't include
        # duplicate subjects if some subject has multiple types
        subjects = {}
        results = []
        for match in table:
            subject = match["s"]
            if subject not in subjects:
                instance_data = {"direct": {a: {}}}
                subjects[subject] = instance_data
                results.append((subject, instance_data))

            if "c" in match:
                concept = match["c"]
                subjects[subject]["direct"][a][concept] = []

        return results

    def _get_by_n_queries(self, params):
        context = params.get("context", None)

        query = select("?s")
        if not (context is None):
            query.from_(context)

        _apply_solution_modifiers(params, query)

        # Load details, for now the simplest approach with N queries.
        # Use _to_table instead of convert to preserve order.
        results = []
        for match in self._to_table(self._execute(query)):
            subject = match["s"]
            instance_data = {}

            result = self._execute(query_s(subject, True, context))
            result = self.convert(result, 'p', 'v', 'c')
            instance_data["direct"] = result

            if not params.get("direct_only"):
                result = self._execute(query_s(subject, False, context))
                result = self.convert(result, 'p', 'v', 'c')
                instance_data["inverse"] = result

            results.append((subject, instance_data))

        return results

    def _get_by_subquery(self, params):
        context = params.get("context", None)

        inner_query = select("?s")
        inner_params = params.copy()
        if "order" in params:
            # "order" needs to stay in subquery,
            # but doesn't do anything useful in main query
            del params["order"]
        _apply_solution_modifiers(inner_params, inner_query)

        if params.get('direct_only'):
            query = select("?s", "?p", "?v", "?c").distinct()
            query.group(('?s', '?p', '?v'), optional_group(('?v', a, '?c')))
        else:
            direct_query = select("?s", "?p", "?v", "?c", '("0" AS ?i)')
            direct_query.distinct()
            direct_query.group(('?s', '?p', '?v'),
                               optional_group(('?v', a, '?c')))

            indirect_query = select("?s", "?p", "?v", "?c", '("1" AS ?i)')
            indirect_query.distinct()
            indirect_query.group(('?v', '?p', '?s'),
                                 optional_group(('?v', a, '?c')))

            query = select("?s", "?p", "?v", "?c", "?i")
            query.union(direct_query, indirect_query)

        query.where(inner_query)
        if not (context is None):
            query.from_(context)

        # Need ordering in outer query
        if "order" in params:
            if params["order"]:
                # Order by subject URI
                query.order_by("?s")
            else:
                # Match another variable, order by it
                query.optional_group(("?s", params["order"], "?order"))
                query.order_by("?order")

        table = self._to_table(self._execute(query))
        subjects = {}
        results = []
        for match in table:
            # Make sure subject and predicate are URIs (they have to be!),
            # this works around bug in Virtuoso -- it sometimes returns
            # URIs as Literals.
            subject = URIRef(match["s"])
            predicate = URIRef(match["p"])
            value = match["v"]
            # Inverse given if direct_only is False
            inverse = match.get("i") == "1"

            # Add subject to result list if it's not there
            if subject not in subjects:
                instance_data = {"direct": {}, "inverse": {}}
                subjects[subject] = instance_data
                results.append((subject, instance_data))

            if inverse:
                attributes = subjects[subject]["inverse"]
            else:
                attributes = subjects[subject]["direct"]
            # Add predicate to subject's predicates if it's not there
            if predicate not in attributes:
                attributes[predicate] = {}

            # Add value to subject->predicate if ...
            predicate_values = attributes[predicate]
            if value not in predicate_values:
                predicate_values[value] = []

            # Add RDF type of the value to subject->predicate->value list
            if "c" in match:
                predicate_values[value].append(match["c"])

        return results

    @abstractmethod
    def _ask(self, result):
        """ Return boolean value of an **ASK** query. """

        return False

    @abstractmethod
    def _execute(self, query):
        """ To be implemented by classes the inherit from `RDFQueryReader`.

        This method is called internally by :meth:`execute`.

        """

        return None

    @abstractmethod
    def _to_table(self, result):
        return []

    def _convert(self, query_result, *keys):
        results_table = self._to_table(query_result)

        if len(keys) == 1:
            return [row[keys[0]] for row in results_table]

        last = len(keys) - 2
        results = {}
        for row in results_table:
            data = results
            for i in range(len(keys) - 1):
                k = keys[i]
                if k not in row:
                    continue
                v = row[k]
                if i < last:
                    if v not in data:
                        data[v] = {}
                    data = data[v]
                elif i == last:
                    if v not in data:
                        data[v] = []

                    value = row.get(keys[i + 1])
                    if value:
                        data[v].append(value)

        return results

    def execute(self, query):
        """
        Execute a `query` of type :class:`surf.query.Query`.
        """

        if isinstance(query, Query):
            return self._execute(query)

        return None

    # noinspection PyBroadException
    def convert(self, query_result, *keys):
        """
        Convert the results from the query to a multilevel dictionary.

        This method is used by the :class:`surf.resource.Resource` class.
        """

        try:
            return self._convert(query_result, *keys)
        except Exception:
            error("Error on convert")
        return []
