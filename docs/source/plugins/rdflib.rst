The `rdflib` Plugin
----------------------------

.. csv-table:: Input Parameters
    :header: "Parameter", "Default Value", "Description"
    :widths: 20, 20, 60
    
    `rdflib_store`, `IOMemory`, Default rdflib storage backend to use
    `rdflib_identifier`, `None`, Identifier to use for default graph
    
    
The parameters are passed as key-value arguments to the 
:class:`surf.store.Store` class.

.. code-block:: python

    s = Store(  reader            =   "rdflib",
                writer            =   "rdflib",
                rdflib_store      =   "IOMemory",
                rdflib_identifier =   URIRef("http://my_graph_uri"))
                
                
        
        
