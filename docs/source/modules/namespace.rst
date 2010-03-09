The :mod:`surf.namespace` Module
--------------------------------

.. automodule:: surf.namespace
   :members:
   :inherited-members:
   :show-inheritance:

Registered general purpose namespaces
=====================================

The description of each registered `namespace` was collected from the respective URL
describing the ontology / vocabulary

.. data:: XMLNS

    http://www.w3.org/XML/1998/namespace
    
    The "xml:" Namespace
   
.. data:: SKOS

    http://www.w3.org/2004/02/skos/core#
    
    SKOS Simple Knowledge Organization System Namespace Document
   
.. data:: XSD

    http://www.w3.org/2001/XMLSchema#
    
    XML Schema
    
.. data:: OWL

    http://www.w3.org/2002/07/owl#
    
    The Web Ontology Language, This file specifies in RDF Schema format the
    built-in classes and properties that together form the basis of
    the RDF/XML syntax of OWL Full, OWL DL and OWL Lite.
    We do not expect people to import this file
    explicitly into their ontology. People that do import this file
    should expect their ontology to be an OWL Full ontology.

.. data:: VS

    http://www.w3.org/2003/06/sw-vocab-status/ns#
    
    SemWeb Vocab Status ontology, An RDF vocabulary for relating SW vocabulary
    terms to their status.

.. data:: WOT

    http://xmlns.com/wot/0.1/
    
    Web Of Trust RDF Ontology

.. data:: DC

    http://purl.org/dc/elements/1.1/
    
    DCMI Namespace for the Dublin Core Metadata Element Set, Version 1.1

.. data:: IBIS

    http://purl.org/ibis#
    
    IBIS Vocabulary, Issue-Based Information Systems (IBIS) is a collaborative
    problem analysis and solving technique. 

.. data:: SIOC

    http://rdfs.org/sioc/ns#
    
    SIOC (Semantically-Interlinked Online Communities) is an ontology for describing
    the information in online communities.

.. data:: SIOC_TYPES

    http://rdfs.org/sioc/types#
    
    Extends the SIOC Core Ontology (Semantically-Interlinked Online Communities)
    by defining subclasses and subproperties of SIOC terms.

.. data:: SIOC_SERVICES

    http://rdfs.org/sioc/services#
    
    Extends the SIOC Core Ontology (Semantically-Interlinked Online Communities)
    by defining basic information on community-related web services.

.. data:: ATOM

    http://atomowl.org/ontologies/atomrdf#
    
    The ATOM OWL vocabulary

.. data:: EXIF

    http://www.w3.org/2003/12/exif/ns/
    
    Vocabulary to describe an Exif format picture data. All Exif 2.2 tags are
    defined as RDF properties, as well as several terms to help this schema.

.. data:: ANNOTEA

    http://www.w3.org/2002/01/bookmark#
    
    The Annotea Bookmark Schema, describing properties used to define instances
    of bookmarks, topics, and shortcuts.

.. data:: RESUME

    http://captsolo.net/semweb/resume/cv.rdfs#
    
    the Resume RDF schema

.. data:: REVIEW

    http://www.isi.edu/webscripter/communityreview/abstract-review-o#
    
    The upper ontology for all semantic web community reviews

.. data:: CALENDAR

    http://www.w3.org/2002/12/cal/icaltzd#
    
    W3C Calendar vocabulary

.. data:: ANNOTATION

    http://www.w3.org/2000/10/annotation-ns#
    
    Annotea Annotation Schema

.. data:: DOAP

    http://usefulinc.com/ns/doap#
    
    Description of a Project (DOAP) vocabulary, The Description of a Project (DOAP)
    vocabulary, described using W3C RDF Schema and the Web Ontology Language.

.. data:: FOAF

    http://xmlns.com/foaf/0.1/
    
    FOAF Vocabulary Specification. FOAF is a collaborative effort amongst Semantic
    Web developers on the FOAF (foaf-dev@lists.foaf-project.org) mailing list. The
    name 'FOAF' is derived from traditional internet usage, an acronym for "Friend of a Friend"

.. data:: GR

    http://purl.org/goodrelations/v1#

    GoodRelations is a standardized vocabulary for product, price, and company data that can (1)
    be embedded into existing static and dynamic Web pages and that (2) can be processed by other
    computers. This increases the visibility of your products and services in the latest generation
    of search engines, recommender systems, and other novel applications.

.. data:: WIKIONT

    http://sw.deri.org/2005/04/wikipedia/wikiont.owl
    
    WIKI vocabulary

.. data:: WORDNET

    http://xmlns.com/wordnet/1.6/
    
    Wordnet vocabulary

.. data:: GEO

    http://www.w3.org/2003/01/geo/wgs84_pos#
    
    WGS84 Geo Positioning: an RDF vocabulary, A vocabulary for representing latitude, longitude and 
    altitude information in the WGS84 geodetic reference datum. 
    Version $Id: wgs84_pos.rdf,v 1.22 2009/04/20 15:00:30 timbl Exp $. See
    http://www.w3.org/2003/01/geo/ for more details.

.. data:: PIM

    http://www.w3.org/2000/10/swap/pim/contact#
    
    PIM vocabulary

.. data:: IMDB

    http://www.csd.abdn.ac.uk/~ggrimnes/dev/imdb/IMDB#
    
    The Internet Movie Database vocabulary, IMDB

.. data:: CONTACT

    http://www.w3.org/2000/10/swap/pim/contact#
    
    The PIM CONTACT vocabulary

.. data:: MARCONT

    http://www.marcont.org/ontology#
    
    MarcOnt Ontology Specification, The goal of MarcOnt bibliographic ontology is
    to provide a uniform bibliographic description format. It should capture concepts
    from existing formats such as Bibtex, Dublin Core, MARC21.

.. data:: XFOAF

    http://www.foafrealm.org/xfoaf/0.1/
    
    FOAFRealm Ontology Specification, Proposed FOAFRealm (Friend-of-a-Friend Realm)
    system allows to take advantage of social networks and FOAF profiles in user profile
    management systems. However, the FOAF standard must be enriched with new concepts
    and properties that are described in this document. The enriched version is called FOAFRealm. 

.. data:: JDL_STRUCTURE

    http://www.jeromedl.org/structure#
    
    JeromeDL Ontology Specification, The structure ontology is used at the bottom
    layer in JeromeDL. It is used to handle typical tasks required from a digital
    objects repository, that is, it keeps track of physical representation of resources,
    their structure and provenance. The structure ontology provides means for a flexible
    and extendable electronic representation of objects. Such flexibility is especially
    significant in expressing relations to other resources 

.. data:: JONTO_PKT

    http://www.corrib.org/jonto/pkt#
    
    JONTO PKT (JeromeDL) vocabulary

.. data:: JONTO_DDC

    http://www.corrib.org/jonto/ddc#
    
    JONTO DDC (JeromeDL) vocabulary

.. data:: CORRIB_TAX

    http://jonto.corrib.org/taxonomies#
    
    CORRIB Taxonomies (JeromeDL) vocabulary

.. data:: SERENITY3

    http://serenity.deri.org/imdb#
    
    The SERENITY vocabulary

.. data:: IDEAS

    http://protege.stanford.edu/rdf
    
    The IDEAS vocabulary, PROTEGE

.. data:: BIBO

    http://purl.org/ontology/bibo/
    
    The Bibliographic Ontology, The Bibliographic Ontology describe
    bibliographic things on the semantic Web in RDF.  This ontology can be
    used as a citation ontology, as a document classification ontology, or
    simply as a way to describe any kind of document in RDF. It has been
    inspired by many existing document description metadata formats, and
    can be used as a common ground for converting other bibliographic data
    sources.

.. data:: FRBR

    http://purl.org/vocab/frbr/core#
    
    Expression of Core FRBR Concepts in RDF, This vocabulary is an expression
    in RDF of the concepts and relations described in the IFLA report on the
    Functional Requirements for Bibliographic Records (FRBR). 

.. data:: MO

    http://purl.org/ontology/mo/
    
    Music Ontology Specification, The Music Ontology Specification provides main
    concepts and properties fo describing music (i.e. artists, albums, tracks, but
    also performances, arrangements, etc.) on the Semantic Web. This document
    contains a detailed description of the Music Ontology.

.. data:: VCARD

    http://nwalsh.com/rdf/vCard#
    
    This ontology attempts to model a subset of vCards
    in RDF using modern (circa 2005) RDF best practices. The subset selected
    is the same subset that the microformats community has adopted for use in
    hCard

.. data:: VANN

    http://purl.org/vocab/vann/
    
    VANN: A vocabulary for annotating vocabulary descriptions, This document describes
    a vocabulary for annotating descriptions of vocabularies with examples and usage notes.

.. data:: EVENT

    http://purl.org/NET/c4dm/event.owl#
    
    The Event Ontology, This document describes the Event ontology developed in the
    Centre for Digital Music in Queen Mary, University of London. 

.. data:: VS

    http://www.w3.org/2003/06/sw-vocab-status/ns#
    
    SemWeb Vocab Status ontology, An RDF vocabulary for relating SW vocabulary
    terms to their status.

.. data:: TIME

    http://www.w3.org/2006/time#
    
    An OWL Ontology of Time (OWL-Time), A paper, "An Ontology of Time for the Semantic Web", 
    that explains in detail about a first-order logic axiomatization of OWL-Time can
    be found at:
        
        - http://www.isi.edu/~pan/time/pub/hobbs-pan-TALIP04.pdf
    
    More materials about OWL-Time:
        
        - http://www.isi.edu/~pan/OWL-Time.html
        - http://www.w3.org/TR/owl-time

.. data:: WGS84_POS

    http://www.w3.org/2003/01/geo/wgs84_pos#
    
    WGS84 Geo Positioning: an RDF vocabulary, A vocabulary for representing latitude, longitude
    and  altitude information in the WGS84 geodetic reference datum. See http://www.w3.org/2003/01/geo/
    for more details.

.. data:: BIBO_ROLES

    http://purl.org/ontology/bibo/roles/
    
    The BIBO Roles vocabulary

.. data:: BIBO_DEGREES

    http://purl.org/ontology/bibo/degrees/
    
    The BIBO Degrees vocabulary

.. data:: BIBO_EVENTS

    http://purl.org/ontology/bibo/events/
    
    The BIBO Events vocabulary

.. data:: BIBO_STATUS

    http://purl.org/ontology/bibo/status/
    
    The BIBO Status vocabulary

.. data:: FRESNEL

    http://www.w3.org/2004/09/fresnel#
    
    Fresnel Lens and Format Core Vocabulary, OWL Full vocabulary for defining lenses
    and formats on RDF models.

.. data:: DCTERMS

    http://purl.org/dc/terms/
    
    DCMI Namespace for metadata terms in the http://purl.org/dc/terms/ namespace

.. data:: DBPEDIA

    http://dbpedia.org/property/
    
    DBpedia, An Entity in Data Space: dbpedia.org

.. data:: YAGO

    http://dbpedia.org/class/yago/
    
    DBpedia YAGO Classes, An Entity in Data Space: dbpedia.org

.. data:: LUBM

    http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl#
    
    Univ-bench Ontology, An university ontology for benchmark tests

.. data:: DBLP

    http://www4.wiwiss.fu-berlin.de/dblp/terms.rdf#
    
    DBLP vocabulary

.. data:: FTI

    http://franz.com/ns/allegrograph/2.2/textindex/
    
    Franz AllegroGraph, namespace for Free Text Indexing, used by AllegroGraph to
    specify predicates that can be used in SPARQL queries to perform free text indexing

.. data:: SURF

    http://code.google.com/p/surfrdf/
    
    The SuRF namespace is used internally by :mod:`surf` to generate unique subjects for
    `resources` if a subject is not provided
