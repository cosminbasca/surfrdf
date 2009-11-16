The `sparql_protocol` Plugin
----------------------------

`sparql_protocol` plugin reads data from SPARQL endpoints.
It also implements writing to endpoints using SPARQL-Update language.
This plugin is known to work with endpoints supplied by 
`OpenLink Virtuoso <http://www.openlinksw.com/virtuoso/>`_ and
`4store <http://4store.org/>`_. It currently cannot access endpoints that 
require authorization.

`SPARQLWrapper <http://sparql-wrapper.sourceforge.net/>`_ library is used 
for actually making requests and converting data from and to Python structures.   

.. csv-table:: Initialization Parameters
    :header: "Parameter", "Default Value", "Description"
    :widths: 20, 20, 60
    
    `endpoint`, `None`, Address of SPARQL HTTP endpoint.
    `default_context`, `None`, The default context (graph) to be queried against (this is useful in particular for the Virtuoso RDF store).
    `use_subqueries`,`None`, whether use of SPARQL 1.1 subqueries is allowed (whether SPARQL endpoint supports that)
    
The parameters are passed as key-value arguments to the 
:class:`surf.store.Store` class::

    s = Store(  reader          =   "sparql_protocol",
                writer          =   "sparql_protocol",
                endpoint        =   "http://dbpedia.org/sparql",
                default_graph   =   "http://dbpedia.org")
        
        
Setting up `OpenLink Virtuoso` RDF Store
----------------------------------------

.. toctree::
   :maxdepth: 2
   
   /integration/virtuoso