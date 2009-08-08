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

'''
The `namespace` manager module of `surf`.
The manager holds a dictionary of the form {short_hand_notation : namespace_uri,
                                            ...}
For performance reasons an inverted index is also kept

Usage example
=============

.. code-block:: python
    
    from surf import *
    
    ns.register(my_namespace='http://mynamespace.com/')
'''

import sys

#the rdf way (rdflib 2.5.x, 3x)
#from rdf.namespace import Namespace, ClosedNamespace, RDF, RDFS
#the rdflib 2.4.x way
from rdflib.Namespace import Namespace
from rdflib.Namespace import Namespace as ClosedNamespace
from rdflib.RDF import RDFNS as RDF
from rdflib.RDFS import RDFSNS as RRDFS

__anonimous = 'NS'
__anonimous_count = 0

# others
XMLNS = Namespace('http://www.w3.org/XML/1998/namespace')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")            
OWL = Namespace('http://www.w3.org/2002/07/owl#')
VS = Namespace('http://www.w3.org/2003/06/sw-vocab-status/ns#')
WOT = Namespace('http://xmlns.com/wot/0.1/')
DC = Namespace('http://purl.org/dc/elements/1.1/')
IBIS = Namespace('http://purl.org/ibis#')
SIOC = Namespace('http://rdfs.org/sioc/ns#')
SIOC_TYPES = Namespace('http://rdfs.org/sioc/types#')
SIOC_SERVICES = Namespace('http://rdfs.org/sioc/services#')
ATOM = Namespace('http://atomowl.org/ontologies/atomrdf#')
EXIF = Namespace('http://www.w3.org/2003/12/exif/ns/')
ANNOTEA = Namespace('http://www.w3.org/2002/01/bookmark#')
RESUME = Namespace('http://captsolo.net/semweb/resume/cv.rdfs#')
REVIEW = Namespace('http://www.isi.edu/webscripter/communityreview/abstract-review-o#')
CALENDAR = Namespace('http://www.w3.org/2002/12/cal/icaltzd#')
ANNOTATION = Namespace('http://www.w3.org/2000/10/annotation-ns#')
DOAP = Namespace('http://usefulinc.com/ns/doap#')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
WIKIONT = Namespace('http://sw.deri.org/2005/04/wikipedia/wikiont.owl')
WORDNET = Namespace('http://xmlns.com/wordnet/1.6/')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
PIM = Namespace('http://www.w3.org/2000/10/swap/pim/contact#')
IMDB = Namespace('http://www.csd.abdn.ac.uk/~ggrimnes/dev/imdb/IMDB#')
CONTACT = Namespace('http://www.w3.org/2000/10/swap/pim/contact#')
MARCONT = Namespace('http://www.marcont.org/ontology#')
XFOAF = Namespace('http://www.foafrealm.org/xfoaf/0.1/')
JDL_STRUCTURE = Namespace('http://www.jeromedl.org/structure#')
JONTO_PKT = Namespace('http://www.corrib.org/jonto/pkt#')
JONTO_DDC = Namespace('http://www.corrib.org/jonto/ddc#')
CORRIB_TAX = Namespace('http://jonto.corrib.org/taxonomies#')
SERENITY3 = Namespace('http://serenity.deri.org/imdb#')
IDEAS = Namespace('http://protege.stanford.edu/rdf')
BIBO = Namespace('http://purl.org/ontology/bibo/')
FRBR = Namespace('http://purl.org/vocab/frbr/core#')
MO = Namespace('http://purl.org/ontology/mo/')
VCARD = Namespace('http://nwalsh.com/rdf/vCard#')
VANN = Namespace('http://purl.org/vocab/vann/')
EVENT = Namespace('http://purl.org/NET/c4dm/event.owl#')
VS = Namespace('http://www.w3.org/2003/06/sw-vocab-status/ns#')
TIME = Namespace('http://www.w3.org/2006/time#')
WGS84_POS = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
BIBO_ROLES = Namespace('http://purl.org/ontology/bibo/roles/')
BIBO_DEGREES = Namespace('http://purl.org/ontology/bibo/degrees/')
BIBO_EVENTS = Namespace('http://purl.org/ontology/bibo/events/')
BIBO_STATUS = Namespace('http://purl.org/ontology/bibo/status/')
FRESNEL = Namespace('http://www.w3.org/2004/09/fresnel#')
DCTERMS = Namespace('http://purl.org/dc/terms/')
# others
DBPEDIA = Namespace('http://dbpedia.org/property/')
YAGO = Namespace('http://dbpedia.org/class/yago/')
LUBM = Namespace('http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl#')
DBLP = Namespace('http://www4.wiwiss.fu-berlin.de/dblp/terms.rdf#')
# FRANZ
FTI = Namespace('http://franz.com/ns/allegrograph/2.2/textindex/')

# an internal inverted dict - for fast access 
__inverted_dict__ = {}
for k,v in sys.modules[__name__].__dict__.items():
    if type(v) in [Namespace, ClosedNamespace]:
         __inverted_dict__[v.__str__()] = k
         
def __add_inverted(prefix):
    ns_dict = sys.modules[__name__].__dict__
    __inverted_dict__[ns_dict[prefix].__str__()] = prefix

def base(property):
    '''
    returns the base part of a URI, `property` is a string denoting a URI
    '''
    if '#' in property:
        return '%s#'%property.rsplit('#',1)[0]
    return '%s/'%property.rsplit('/',1)[0]

def symbol(property):
    '''
    returns the part of a URI after the last **/** or *#*, `property` is a
    string denoting a URI
    '''
    if '#' in property:
        return property.rsplit('#',1)[-1]
    return property.rsplit('/',1)[-1]

def register(**namespaces):
    '''
    registers a namespace with a shorthand notation with the `namespace` manager
    the arguments are passed in as key-value pairs.
    '''
    ns_dict = sys.modules[__name__].__dict__
    for key in namespaces:
        uri = namespaces[key]
        prefix = key.upper()
        ns_dict[prefix] = uri if type(uri) in [Namespace, ClosedNamespace] else Namespace(uri)
        # also keep inverted dict presistent
        __add_inverted(prefix)
        
def get_namespace(base):
    '''
    returns the `namespace` short hand notation and the uri based on the uri `base`.
    The namespace is a `rdf.namespace.Namespace`.
    '''
    global __anonimous_count
    ns_dict = sys.modules[__name__].__dict__
    base = base if type(base) in [str, unicode] else base.__str__()
    try:
        prefix = __inverted_dict__[base]
        uri = ns_dict[prefix]
    except:
        prefix = '%s%d'%(__anonimous,__anonimous_count + 1)
        __anonimous_count += 1
        uri = Namespace(base)
        register(**{prefix:uri})
    return prefix, uri

def get_namespace_url(prefix):
    '''
    returns the `namespace` URI registered under the specified `prefix`
    '''
    ns_dict = sys.modules[__name__].__dict__
    try:
        return ns_dict[prefix.__str__().upper()]
    except:
        return None
    
    
def get_prefix(uri):
    '''
    the inverse function of `get_namespace_url(prefix)`, returns the `prefix`
    of a `namespace` based on its URI
    '''
    try:
        return __inverted_dict__[uri.__str__()]
    except:
        return None

    
    
    
    