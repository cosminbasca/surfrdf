Queries
=======

SuRF aims to integrate RDF with object-oriented paradigm so that manual 
writing and execution of SPARQL queries is seldom needed. Resources and
classes provide higher level of abstraction than queries do and they
should cover the most common use cases. 

Executing arbitrary SPARQL queries
----------------------------------

For cases when you need to execute arbitrary queries, it is still possible.
:class:`surf.store.Store` has method 
:meth:`surd.store.Store.execute_sparql(query_string)` which accepts query 
as string. This method will return raw results, SuRF will make no attempt to
represent returned data as resource objects.

.. doctest::

	>>> import surf
	>>> from surf.rdf import URIRef
	>>> sess = surf.Session(surf.Store(reader="rdflib", writer="rdflib"))
	>>> sess.default_store.add_triple(URIRef("http://s"), URIRef("http://p"), "value!")
	
	>>> sess.default_store.execute_sparql("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
	<rdflib.sparql.QueryResult.SPARQLQueryResult object at ...>
	
	>>> list(sess.default_store.execute_sparql("SELECT ?s ?p ?o WHERE { ?s ?p ?o }"))
	[(rdflib.URIRef('http://s'), rdflib.URIRef('http://p'), 'value!')] 
    
Constructing queries in programmatic way
----------------------------------------

SuRF provides utilities for programmatic construction of dynamic SPARQL 
queries in :mod:`surf.query` module. Using them can sometimes result in 
cleaner code than constructing queries by string concatenation. 
Here's an example how to use tools in :mod:`surf.query`:

.. doctest::

    >>> import surf
    >>> from surf.query import a, select
    >>> from surf.query.translator.sparql import SparqlTranslator
    >>> query = select("?s", "?src")
    >>> query.named_group("?src", ("?s", a, surf.ns.FOAF['Person']))
    >>> SparqlTranslator(query).translate()
    u'SELECT  ?s ?src  WHERE {  GRAPH ?src {  ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person>  }  }    '
