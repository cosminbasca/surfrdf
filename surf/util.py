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
import logging
from datetime import datetime, date, time
import decimal
import re
from urlparse import urlparse
from uuid import uuid4

from surf.namespace import get_namespace, get_namespace_url
from surf.namespace import get_fallback_namespace, SURF
from surf.rdf import BNode, Literal, Namespace, URIRef

__author__ = 'Cosmin Basca'

# ----------------------------------------------------------------------------------------------------------------------
#
# module constants
#
# ----------------------------------------------------------------------------------------------------------------------

#: the attribute regex pattern representing a direct edge or property: {{ATTRIBUTE_NAME}}
pattern_direct = re.compile('^[a-z0-9]+_[a-zA-Z0-9_\-]+$', re.DOTALL)
#: the attribute regex pattern representing an inverse edge or property: is_{{ATTRIBUTE_NAME}}_of
pattern_inverse = re.compile('^is_[a-z0-9]+_[a-zA-Z0-9_\-]+_of$', re.DOTALL)

DE_CAMEL_CASE_DEFAULT = 2 ** 0
DE_CAMEL_CASE_FORCE_LOWER_CASE = 2 ** 1
pattern = re.compile('([A-Z][A-Z][a-z])|([a-z][A-Z])')


# ----------------------------------------------------------------------------------------------------------------------
#
# module functions
#
# ----------------------------------------------------------------------------------------------------------------------
def string_conforms_to_base64(string):
    """
    check whether the given string conforms to the *base64* encoding.

    :param str string: the string
    :return: True if strings conforms to base64 encoding
    :rtype: bool
    """
    return (len(string) % 4 == 0) and re.match('^[A-Za-z0-9+/]+[=]{0,2}$', string)


def namespace_split(uri):
    """
    Same as :func:`uri_split`, but instead of the base of the uri, returns the
    registered `namespace` for this uri

    .. code-block:: python

        >>> print namespace_split('http://mynamespace/ns#some_property')
        (rdflib.URIRef('http://mynamespace/ns#'), 'some_property')

    :param str uri: the uri
    :return: a (namespace, predicate) tuple. Types: (:class:`rdflib.term.URIRef`, str)
    :rtype: tuple
    """

    sp = '#' if uri.rfind('#') != -1 else '/'
    base, predicate = uri.rsplit(sp, 1)
    return get_namespace('%s%s' % (base, sp))[1], predicate


def uri_split(uri):
    """
    Split the `uri` into base path and remainder,
    the base is everything that comes before the last *#*' or */* including it

    .. code-block:: python

        >>> print uri_split('http://mynamespace/ns#some_property')
        ('NS1', 'some_property')

    :param uri: the uri
    :type uri: :class:`rdflib.term.URIRef` or basestring
    :return: a (base, remainder) tuple. Types: (str, str)
    :rtype: tuple
    """

    sp = '#' if uri.rfind('#') != -1 else'/'
    base, predicate = uri.rsplit(sp, 1)
    return get_namespace('%s%s' % (base, sp))[0], predicate


def uri_to_classname(uri):
    """
    Handy function to convert a `uri` to a Python valid `class name`

    .. code-block:: python

        >>> # prints Ns1some_class, where Ns1 is the namespace (not registered, assigned automatically)
        >>> print uri_to_classname('http://mynamespace/ns#some_class')
        Ns1some_class

    :param str uri: the uri
    :return: a valid python class name for the given uri
    :rtype: str
    """
    ns_key, predicate = uri_split(uri)
    return '%s%s' % (ns_key.title().replace('-', '_'), predicate)


def attr2rdf(attr_name):
    """
    Convert an `attribute name` in the form:

    .. code-block:: python

        # direct predicate
        instance1.foaf_name
        # inverse predicate
        instance2.if_foaf_title_of

    to

    .. code-block:: xml

        <!-- direct predicate -->
        <http://xmlns.com/foaf/spec/#term_name>
        <!-- inverse predicate -->
        <http://xmlns.com/foaf/spec/#term_title>


    :param str attr_name: the attribute name to convert to *RDF*
    :return: a (uri representation, True if it's a direct predicate or False if its an inverse predicate) tuple.
    :rtype: tuple
    """
    
    def to_rdf(attr_name):
        prefix, predicate = attr_name.split('_', 1)
        ns = get_namespace_url(prefix)
        try:
            return ns[predicate]
        except:
            return None

    if pattern_inverse.match(attr_name):
        return to_rdf(attr_name.replace('is_', '').replace('_of', '')), False
    elif pattern_direct.match(attr_name):
        return to_rdf(attr_name), True
    return None, None


def rdf2attr(uri, direct):
    """
    Inverse of `attr2rdf`, return the attribute name, given the `uri` and whether it is `direct` or not.

    .. code-block:: python

        >>> print rdf2attr('http://xmlns.com/foaf/spec/#term_name',True)
        foaf_name
        >>> print rdf2attr('http://xmlns.com/foaf/spec/#term_title',False)
        if_foaf_title_of

    :param uri: the given `uri`
    :type uri: :class:`rdflib.term.URIRef` or str
    :param bool direct: whether this is a direct or inverse edge or property
    :return: the python attribute name
    :rtype: str
    """
    ns, predicate = uri_split(uri)
    attribute = '%s_%s' % (ns.lower(), predicate)
    return direct and attribute or 'is_%s_of' % attribute


def is_attr_direct(attr_name):
    """
    Checks whether this is a direct or inverse edge / property. The naming convention defined by the
    :attr:`pattern_direct` and :attr:`pattern_inverse` regex patterns.

    .. code-block:: python

        >>> is_attr_direct('foaf_name')
        True
        >>> is_attr_direct('is_foaf_name_of')
        False

    :param str attr_name: the attribute name to convert to *RDF*
    :return: True if `attr_name` is a direct edge / property
    :rtype: bool
    """
    return not pattern_inverse.match(attr_name)


def uri_to_class(uri):
    """
    returns a `class object` from the supplied `uri`. A valid class name is retrieved using the
    :func:`uri_to_classname` method.

    .. code-block:: python

        >>> print uri_to_class('http://mynamespace/ns#some_class')
        surf.util.Ns1some_class

    :param str uri: the given `uri`
    :return: the python class for the given `uri`
    :rtype: type
    """
    return type(str(uri_to_classname(uri)), (), {'uri': uri})


def uuid_subject(namespace=None):
    """
    This function generates a unique subject in the provided `namespace` based on the :func:`uuid.uuid4()` method,
    If `namespace` is not specified than the default `SURF` namespace is used

    .. code-block:: python

        >>> from surf import namespace as ns
        >>> print uuid_subject(ns.SIOC)
        http://rdfs.org/sioc/ns#1b6ca1d5-41ed-4768-b86a-42185169faff

    :param namespace: the given namespace
    :type namespace: None or :class:`rdflib.namespace.Namespace` or str or unicode
    :return: the *RDF* subject identifier in the specified namespace
    :rtype: :class:`rdflib.term.URIRef`
    """

    if not namespace:
        namespace = get_fallback_namespace()

    if not isinstance(namespace, Namespace):
        namespace = Namespace(namespace)

    return namespace[str(uuid4())]


def de_camel_case(camel_case, delim=' ', method=DE_CAMEL_CASE_FORCE_LOWER_CASE):
    """
    Adds spaces to a camel case string.  Failure to space out string returns the original string.

    :param str camel_case: the camel cased string
    :param str delim: the delimiter
    :param int method: the method
    :return: the normalized string
    :rtype: str
    """
    if camel_case is None:
        return None

    def normalize(string):
        if method == DE_CAMEL_CASE_FORCE_LOWER_CASE:
            return string.lower()
        return string

    return normalize(pattern.sub(lambda m: m.group()[:1] + delim + m.group()[1:], camel_case))


def is_uri(uri):
    """
    Checks whether the given `uri` is a *URI* reference

    :param str uri: the given `uri`
    :return: True if a *URI* reference
    :rtype: bool
    """
    scheme, netloc, path, params, query, fragment = urlparse(uri)
    if scheme and netloc and path:
        return True
    return False


def pretty_rdf(uri):
    """
    Returns a string of the given URI under the form `namespace:symbol`, if `namespace` is registered,
    else returns an empty string

    :param str uri: the given `uri`
    :return: the python prettified `uri` representation
    :rtype: str
    """
    if hasattr(uri, 'subject'):
        uri = uri.subject
    if type(uri) is URIRef:
        NS, symbol = uri_split(uri)
        if unicode(NS).startswith('NS'):
            pretty = symbol
        else:
            pretty = NS.lower() + ':' + symbol
        return pretty
    return ''


def value_to_rdf(value):
    """
    Convert the value to an :mod:`rdflib` compatible type if appropriate.

    :param object value: the value
    :return: the converted value (if possible)
    :rtype: :class:`rdflib.term.Literal` or :class:`rdflib.term.BNode` or :class:`rdflib.term.URIRef` or object
    """
    if isinstance(value, (URIRef, BNode)):
        return value
    elif isinstance(value, (basestring, str, unicode, float, int, long, bool, datetime, date, time, decimal.Decimal)):
        if type(value) is basestring and string_conforms_to_base64(value):
            return Literal(value, datatype=URIRef('http://www.w3.org/2001/XMLSchema#base64Binary'))
        return Literal(value)

    elif isinstance(value, (list, tuple)):
        language = value[1] if len(value) > 1 else None
        datatype = value[2] if len(value) > 2 else None
        return Literal(value[0], lang=language, datatype=datatype)

    elif isinstance(value, dict):
        val = value.get("value")
        language = value.get("language")
        datatype = value.get("datatype")
        if val:
            return Literal(val, lang=language, datatype=datatype)
        return value

    return value


def json_to_rdflib(json_object):
    """
    Convert a json result entry to an :mod:`rdfLib` type.

    :param dict json_object: the *JSON* object
    :return: the converted value (if possible)
    :rtype: :class:`rdflib.term.Literal` or :class:`rdflib.term.BNode` or :class:`rdflib.term.URIRef` or None
    """
    try:
        type = json_object["type"]
    except KeyError:
        raise ValueError("No type specified")

    if type == 'uri':
        return URIRef(json_object["value"])

    elif type == 'literal':
        if "xml:lang" in json_object:
            return Literal(json_object["value"], lang=json_object['xml:lang'])
        else:
            return Literal(json_object["value"])

    elif type == 'typed-literal':
        return Literal(json_object["value"], datatype=URIRef(json_object['datatype']))

    elif type == 'bnode':
        return BNode(json_object["value"])

    else:
        return None


class Single(object):
    """
    Descriptor for easy access to attributes with single value.
    """

    def __init__(self, attr):
        if isinstance(attr, URIRef):
            attr = rdf2attr(attr, True)

        self.attr = attr

    def __get__(self, obj, type=None):
        return getattr(obj, self.attr).first

    def __set__(self, obj, value):
        setattr(obj, self.attr, value)

    def __delete__(self, obj):
        setattr(obj, self.attr, [])


def single(attr):
    """
    alias for :class:`Single`

    :param attr: the given attribute
    :type attr: :class:`rdflib.term.URIRef` or str
    :return: a :class:`Single` instance
    :rtype: :class:`Single`
    """
    return Single(attr)
