Queries
=======

`SuRF` aims to integrate **RDF** with the `object-oriented` paradigm so that manual 
writing and execution of **SPARQL** queries is seldom needed. Resources and
classes provide a higher level of abstraction than queries do and they
should cover the most common use cases. 

Executing arbitrary SPARQL queries
----------------------------------

It is still possible to execute arbitrary queries in the cases where this is needed.
The :class:`surf.store.Store` class provides the method:
:meth:`surf.store.Store.execute_sparql` which accepts the query 
as a string. This method will return raw results, and `SuRF` will make no attempt to
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
    
Constructing queries in a programmatic way
------------------------------------------

`SuRF` also provides utilities for programmatic construction of dynamic **SPARQL** 
queries in the :mod:`surf.query` module. Using them can sometimes result in 
cleaner code than constructing queries by string concatenation. 
Here's an example on how to use the tools available in the :mod:`surf.query` module:

.. doctest::

    >>> import surf
    >>> from surf.query import a, select
    >>> query = select("?s", "?src")
    >>> query.named_group("?src", ("?s", a, surf.ns.FOAF['Person']))
    >>> print unicode(query)
    SELECT  ?s ?src  WHERE {  GRAPH ?src {  ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person>  }  }
