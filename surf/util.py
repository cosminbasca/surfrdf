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
__author__ = 'Cosmin Basca'

from datetime import datetime, date, time
import new
import re
from urlparse import urlparse
from uuid import uuid4

from surf.namespace import get_namespace, get_namespace_url
from surf.namespace import get_fallback_namespace, SURF
from surf.rdf import Literal, Namespace, URIRef

pattern_direct = re.compile('^[a-z0-9]{1,}_[a-zA-Z0-9_]{1,}$', re.DOTALL)
pattern_inverse = re.compile('^is_[a-z0-9]{1,}_[a-zA-Z0-9_]{1,}_of$', re.DOTALL)

def namespace_split(uri):
    """ Same as `uri_split`, but instead of the base of the uri, returns the
    registered `namespace` for this uri

    .. code-block:: python

        >>> print util.namespace_split('http://mynamespace/ns#some_property')
        (rdflib.URIRef('http://mynamespace/ns#'), 'some_property')

    """

    sp = uri.rfind('#') != -1 and '#' or '/'
    base, predicate = uri.rsplit(sp, 1)
    return get_namespace('%s%s' % (base, sp))[1], predicate

def uri_split(uri):
    """ Split the `uri` into base path and remainder,
    the base is everything that comes before the last *#*' or */* including it

    .. code-block:: python

        >>> print util.uri_split('http://mynamespace/ns#some_property')
        ('NS1', 'some_property')

    """

    sp = uri.rfind('#') != -1 and '#' or '/'
    base, predicate = uri.rsplit(sp, 1)
    return get_namespace('%s%s' % (base, sp))[0], predicate

def uri_to_classname(uri):
    '''handy function to convert a `uri` to a Python valid `class name`

    .. code-block:: python

        >>> # prints Ns1some_class, where Ns1 is the namespace (not registered, assigned automatically)
        >>> print util.uri_to_classname('http://mynamespace/ns#some_class')
        Ns1some_class

    '''
    ns_key, predicate = uri_split(uri)
    return '%s%s' % (ns_key.title().replace('-', '_'), predicate)

def attr2rdf(attrname):
    '''converts an `attribute name` in the form:

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


    the function returns two values, the `uri` representation and True if it's a
    direct predicate or False if its an inverse predicate
    '''
    def tordf(attrname):
        prefix, predicate = attrname.split('_', 1)
        ns = get_namespace_url(prefix)
        try:
            return ns[predicate]
        except:
            return None

    if pattern_inverse.match(attrname):
        return  tordf(attrname.replace('is_', '').replace('_of', '')), False
    elif pattern_direct.match(attrname):
        return  tordf(attrname), True
    return None, None

def rdf2attr(uri, direct):
    """ Inverse of `attr2rdf`, return the attribute name,
    given the URI and whether it is `direct` or not.

    .. code-block:: python

        >>> print rdf2attr('http://xmlns.com/foaf/spec/#term_name',True)
        foaf_name
        >>> print rdf2attr('http://xmlns.com/foaf/spec/#term_title',False)
        if_foaf_title_of

    """

    ns, predicate = uri_split(uri)
    attribute = '%s_%s' % (ns.lower(), predicate)
    return direct and attribute or 'is_%s_of' % attribute


def is_attr_direct(attrname):
    """ True if it's a direct `attribute`

    .. code-block:: python

        >>> util.is_attr_direct('foaf_name')
        True
        >>> util.is_attr_direct('is_foaf_name_of')
        False

    """

    return not pattern_inverse.match(attrname)

def uri_to_class(uri):
    '''returns a `class object` from the supplied `uri`, used `uri_to_class` to
    get a valid class name

    .. code-block:: python

        >>> print util.uri_to_class('http://mynamespace/ns#some_class')
        surf.util.Ns1some_class

    '''
    return new.classobj(str(uri_to_classname(uri)), (), {'uri':uri})

def uuid_subject(namespace = None):
    '''the function generates a unique subject in the provided `namespace` based on
    the :func:`uuid.uuid4()` method,
    If `namespace` is not specified than the default `SURF` namespace is used

    .. code-block:: python

        >>>  print util.uuid_subject(ns.SIOC)
        http://rdfs.org/sioc/ns#1b6ca1d5-41ed-4768-b86a-42185169faff

    '''

    if not namespace:
        namespace = get_fallback_namespace()

    if not isinstance(namespace, Namespace):
        namespace = Namespace(namespace)

    return namespace[str(uuid4())]

DE_CAMEL_CASE_DEFAULT = 2 ** 0
DE_CAMEL_CASE_FORCE_LOWER_CASE = 2 ** 1
pattern = re.compile('([A-Z][A-Z][a-z])|([a-z][A-Z])')

def de_camel_case(camel_case, delim = ' ', method = DE_CAMEL_CASE_FORCE_LOWER_CASE):
    '''Adds spaces to a camel case string.  Failure to space out string returns the original string.'''
    if camel_case is None:
        return None
    normalize = lambda s:s
    if (method == DE_CAMEL_CASE_FORCE_LOWER_CASE):
        normalize = lambda s:s.lower()

    return normalize(pattern.sub(lambda m: m.group()[:1] + delim + m.group()[1:], camel_case))


def is_uri(uri):
    '''True if the specified string is a URI reference False otherwise'''
    scheme, netloc, path, params, query, fragment = urlparse(uri)
    if scheme and netloc and path:
        return True
    return False


def pretty_rdf(uri):
    '''Returns a string of the given URI under the form `namespace:symbol`, if `namespace` is registered,
    else returns an empty string'''
    if hasattr(uri, 'subject'):
        uri = uri.subject
    if type(uri) is URIRef:
        NS, symbol = uri_split(uri)
        if str(NS).startswith('NS'):
            pretty = symbol
        else:
            pretty = NS.lower() + ':' + symbol
        return pretty
    return ''

def value_to_rdf(value):
    """ Convert the value to an `rdflib` compatible type if appropriate. """

    if type(value) in [str, unicode, basestring, float, int, long, bool, datetime, date, time]:
        return Literal(value)
    elif type(value) in [list, tuple]:
        language = len(value) > 1 and value[1] or None
        datatype = len(value) > 2 and value[2] or None
        return Literal(value[0], lang = language, datatype = datatype)
    elif type(value) is dict:
        val = value.get("value")
        language = value.get("language")
        datatype = value.get("datatype")
        if val:
            return Literal(val, lang = language, datatype = datatype)
        return value
    return value

class single(object):
    """ Descriptor for easy access to attributes with single value. """

    def __init__(self, attr):
        if isinstance(attr, URIRef):
            attr = rdf2attr(attr, True)
        self.attr = attr

    def __get__(self, obj, type = None):
        return getattr(obj, self.attr).first

    def __set__(self, obj, value):
        setattr(obj, self.attr, value)

    def __delete__(self, obj):
        setattr(obj, self.attr, [])

