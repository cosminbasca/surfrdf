""" Conditionally import rdflib classes. """

import rdflib

# 2.4 style imports
if rdflib.__version__.startswith("2.4"):
    from rdflib.BNode import BNode
    from rdflib.Graph import Graph, ConjunctiveGraph
    from rdflib.Literal import Literal
    from rdflib.Namespace import Namespace
    from rdflib.Namespace import Namespace as ClosedNamespace
    from rdflib.URIRef import URIRef

    from rdflib.RDF import RDFNS as RDF
    from rdflib.RDFS import RDFSNS as RDFS

# 3.0 style imports
if rdflib.__version__.startswith("2.5") or rdflib.__version__.startswith("3.0"):
    from rdflib.term import BNode
    from rdflib.graph import Graph, ConjunctiveGraph
    from rdflib.term import Literal
    from rdflib.namespace import ClosedNamespace, Namespace
    from rdflib.namespace import RDF, RDFS
    from rdflib.term import URIRef

__exports__ = [BNode, ClosedNamespace, ConjunctiveGraph, Graph, Literal,
               Namespace, RDF, RDFS, URIRef]
