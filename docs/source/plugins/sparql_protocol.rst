The `sparql_protocol` Plugin
----------------------------

.. csv-table:: Input Parameters
    :header: "Parameter", "Default Value", "Description"
    :widths: 20, 20, 60
    
    `endpoint`, `None`, the SPARQL http endpoint location where the server is accessible
    `default_context`, `None`, the default context (graph) to be queried against (this is useful in particular for the `virtuoso` RDF store).
    
the parameters are passed as key-value arguments to the :class:`surf.store.Store` class

.. code-block:: python

    s = Store(  reader          =   "sparql_protocol",
                writer          =   "sparql_protocol",
                endpoint        =   "http://dbpedia.org/sparql",
                default_graph   =   "http://dbpedia.org")
        
        
Setting up `OpenLink Virtuoso` RDF Store
----------------------------------------

.. toctree::
   :maxdepth: 2
   
   /integration/virtuoso