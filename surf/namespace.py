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

#TODO: better integration of the namespace manager with Allegro

import sys
from rdf.namespace import Namespace, ClosedNamespace
from rdf import namespace

__anonimous__ = 'NS'

# defined in RDFLIB
RDF = namespace.RDF
RDFS = namespace.RDFS

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

def base(property):
    if '#' in property:
        return '%s#'%property.rsplit('#',1)[0]
    return '%s/'%property.rsplit('/',1)[0]

def symbol(property):
    if '#' in property:
        return property.rsplit('#',1)[-1]
    return property.rsplit('/',1)[-1]

def register(**namespaces):
    """
    @summary: registers namespaces passed in the form of a dictionary 
    name : base uri
    @param namespaces: the namespaces (dictionary)
    @return: nothing
    """
    module = sys.modules[__name__]
    for _ns in namespaces:
        #print 'Registered :',_ns, namespaces[_ns]
        module.__dict__[_ns.upper()] = namespaces[_ns] if type(namespaces[_ns]) is Namespace else Namespace(namespaces[_ns])

def get_namespace(base):
    """
    @summary: returns a registered namespace in the module or creates an
            anonimous one if the base uri is not there
    @param base: the base uri of the namespace
    @return: a tuple consisting of (namespace key, rdfLib namespace object)
    """
    module = sys.modules[__name__]
    __anonim_cnt = 0
    for ns_key in dir(module):
        ns = module.__dict__[ns_key]
        if ns_key.startswith(__anonimous__):
            __anonim_cnt = int(ns_key.split(__anonimous__)[1])
        if type(ns) in [Namespace, ClosedNamespace] and base == str(ns):
            return ns_key,ns
    ns_key = '%s%d'%(__anonimous__,__anonim_cnt+1)
    ns = Namespace(base)
    module.__dict__[ns_key] = ns
    return ns_key, ns


def get_namespace_url(ns):
    """
    @summary: returns a rdflib namespace object by it's label
    e.g.: get_namesapce_url('rdfs') should return RDFS
    @param ns: namesapace label
    @return: rdflib Namespace coresponding to lable or None
    """
    module = sys.modules[__name__]
    if str(ns).upper() in module.__dict__:
        return module.__dict__[str(ns).upper()]
    return None
    
    
def get_name(ns):
    """
    @summary: returns the name of the namespace to be used as a label lateron
    @param ns: the namespace
    @return: the name of the namespace: e.g.: FOAF{rdf.Namespace} -> FOAF{string}
    """
    module = sys.modules[__name__]
    for key, value in module.__dict__.items():
        if value == ns:
            return key
    return None
    