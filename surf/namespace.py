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


import sys

#the rdf way (rdflib 2.5.x, 3x)
#from rdf.namespace import Namespace, ClosedNamespace, RDF, RDFS
#the rdflib 2.4.x way
from rdflib.Namespace import Namespace
from rdflib.Namespace import Namespace as ClosedNamespace
from rdflib.RDF import RDFNS as RDF
from rdflib.RDFS import RDFSNS as RDFS

__anonymous = 'NS'
__anonymous_count = 0

ANNOTATION    = Namespace('http://www.w3.org/2000/10/annotation-ns#')
ANNOTEA       = Namespace('http://www.w3.org/2002/01/bookmark#')
ATOM          = Namespace('http://atomowl.org/ontologies/atomrdf#')
BIBO          = Namespace('http://purl.org/ontology/bibo/')
BIBO_DEGREES  = Namespace('http://purl.org/ontology/bibo/degrees/')
BIBO_EVENTS   = Namespace('http://purl.org/ontology/bibo/events/')
BIBO_ROLES    = Namespace('http://purl.org/ontology/bibo/roles/')
BIBO_STATUS   = Namespace('http://purl.org/ontology/bibo/status/')
CALENDAR      = Namespace('http://www.w3.org/2002/12/cal/icaltzd#')
CONTACT       = Namespace('http://www.w3.org/2000/10/swap/pim/contact#')
CORRIB_TAX    = Namespace('http://jonto.corrib.org/taxonomies#')
DBLP          = Namespace('http://www4.wiwiss.fu-berlin.de/dblp/terms.rdf#')
DBPEDIA       = Namespace('http://dbpedia.org/property/')
DC            = Namespace('http://purl.org/dc/elements/1.1/')
DCTERMS       = Namespace('http://purl.org/dc/terms/')
DOAP          = Namespace('http://usefulinc.com/ns/doap#')
EVENT         = Namespace('http://purl.org/NET/c4dm/event.owl#')
EXIF          = Namespace('http://www.w3.org/2003/12/exif/ns/')
FOAF          = Namespace('http://xmlns.com/foaf/0.1/')
FRBR          = Namespace('http://purl.org/vocab/frbr/core#')
FRESNEL       = Namespace('http://www.w3.org/2004/09/fresnel#')
FTI           = Namespace('http://franz.com/ns/allegrograph/2.2/textindex/')
GEO           = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
IBIS          = Namespace('http://purl.org/ibis#')
IDEAS         = Namespace('http://protege.stanford.edu/rdf')
IMDB          = Namespace('http://www.csd.abdn.ac.uk/~ggrimnes/dev/imdb/IMDB#')
JDL_STRUCTURE = Namespace('http://www.jeromedl.org/structure#')
JONTO_DDC     = Namespace('http://www.corrib.org/jonto/ddc#')
JONTO_PKT     = Namespace('http://www.corrib.org/jonto/pkt#')
LUBM          = Namespace('http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl#')
MARCONT       = Namespace('http://www.marcont.org/ontology#')
MO            = Namespace('http://purl.org/ontology/mo/')
OWL           = Namespace('http://www.w3.org/2002/07/owl#')
PIM           = Namespace('http://www.w3.org/2000/10/swap/pim/contact#')
RESUME        = Namespace('http://captsolo.net/semweb/resume/cv.rdfs#')
REVIEW        = Namespace('http://www.isi.edu/webscripter/communityreview/abstract-review-o#')
SERENITY3     = Namespace('http://serenity.deri.org/imdb#')
SIOC          = Namespace('http://rdfs.org/sioc/ns#')
SIOC_SERVICES = Namespace('http://rdfs.org/sioc/services#')
SIOC_TYPES    = Namespace('http://rdfs.org/sioc/types#')
SKOS          = Namespace('http://www.w3.org/2004/02/skos/core#')
SURF          = Namespace('http://code.google.com/p/surfrdf/')
TIME          = Namespace('http://www.w3.org/2006/time#')
VANN          = Namespace('http://purl.org/vocab/vann/')
VCARD         = Namespace('http://nwalsh.com/rdf/vCard#')
VS            = Namespace('http://www.w3.org/2003/06/sw-vocab-status/ns#')
WGS84_POS     = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
WIKIONT       = Namespace('http://sw.deri.org/2005/04/wikipedia/wikiont.owl')
WORDNET       = Namespace('http://xmlns.com/wordnet/1.6/')
WOT           = Namespace('http://xmlns.com/wot/0.1/')
XFOAF         = Namespace('http://www.foafrealm.org/xfoaf/0.1/')
XMLNS         = Namespace('http://www.w3.org/XML/1998/namespace')
XSD           = Namespace("http://www.w3.org/2001/XMLSchema#")
YAGO          = Namespace('http://dbpedia.org/class/yago/')


# an internal inverted dict - for fast access 
__inverted_dict__ = {}
for k,v in sys.modules[__name__].__dict__.items():
    if type(v) in [Namespace, ClosedNamespace]:
         __inverted_dict__[v.__str__()] = k
         
def __add_inverted(prefix):
    ns_dict = sys.modules[__name__].__dict__
    __inverted_dict__[ns_dict[prefix].__str__()] = prefix

def base(property):
    '''returns the base part of a URI, `property` is a string denoting a URI
    
    .. code-block:: python
    
        >>> print ns.base('http://sometest.ns/ns#symbol')
        http://sometest.ns/ns#
        
    '''
    if '#' in property:
        return '%s#'%property.rsplit('#',1)[0]
    return '%s/'%property.rsplit('/',1)[0]

def symbol(property):
    '''returns the part of a URI after the last **/** or *#*, `property` is a
    string denoting a URI
    
    .. code-block:: python
    
        >>> print ns.symbol('http://sometest.ns/ns#symbol')
        symbol
        
    '''
    if '#' in property:
        return property.rsplit('#',1)[-1]
    return property.rsplit('/',1)[-1]

def register(**namespaces):
    '''registers a namespace with a shorthand notation with the `namespace` manager
    the arguments are passed in as key-value pairs
    
    .. code-block:: python
    
        >>> ns.register(test='http://sometest.ns/ns#')
        >>> print ns.TEST 
        http://sometest.ns/ns#
        
    '''
    ns_dict = sys.modules[__name__].__dict__
    for key in namespaces:
        uri = namespaces[key]
        prefix = key.upper()
        ns_dict[prefix] = uri if type(uri) in [Namespace, ClosedNamespace] else Namespace(uri)
        # also keep inverted dict presistent
        __add_inverted(prefix)
        
def get_namespace(base):
    '''returns the `namespace` short hand notation and the uri based on the uri `base`.
    The namespace is a `rdf.namespace.Namespace`
    
    .. code-block:: python
    
        >>> key, namespace = ns.get_namespace('http://sometest.ns/ns#')
        >>> print key, namespace
        TEST, http://sometest.ns/ns#
        
    '''
    global __anonymous_count
    ns_dict = sys.modules[__name__].__dict__
    base = base if type(base) in [str, unicode] else base.__str__()
    try:
        prefix = __inverted_dict__[base]
        uri = ns_dict[prefix]
    except:
        prefix = '%s%d'%(__anonymous,__anonymous_count + 1)
        __anonymous_count += 1
        uri = Namespace(base)
        register(**{prefix:uri})
    return prefix, uri

def get_namespace_url(prefix):
    '''returns the `namespace` URI registered under the specified `prefix`
    
    .. code-block:: python
    
        >>> url = ns.get_namespace_url('TEST')
        >>> print url 
        http://sometest.ns/ns#
        
    '''
    ns_dict = sys.modules[__name__].__dict__
    try:
        return ns_dict[prefix.__str__().upper()]
    except:
        return None
    
    
def get_prefix(uri):
    '''the inverse function of `get_namespace_url(prefix)`, returns the `prefix`
    of a `namespace` based on its URI
    
    .. code-block:: python
    
        >>> name = ns.get_prefix(Namespace('http://sometest.ns/ns#'))
        >>> # true, if one registered the uri to the "test" prefix beforehand
        >>> print name 
        TEST
        
    '''
    try:
        return __inverted_dict__[uri.__str__()]
    except:
        return None

    
    
    
    
