The `Store` and the `Session`
=============================

What do :class:`surf.store.Store` and :class:`surf.session.Session` do?
-----------------------------------------------------------------------

The `Session` establishes all conversations to the backend storage service. Resources 
use it to load and save their constituting triples. The `Session` keeps  
a cache of already loaded data, and it uses one or more stores to do actual  
loading and presistence of data. 

The `Store` provides functions for loading and saving data, these are divided 
into **reader** and **writer** sub-components. `Readers` and `writers` are provided by plugins.

Preparing the `store` and the `session`
---------------------------------------

The `Store` and the `Session` objects can be instantiated as any regular Python object. 
Instantiation of `store` and `session` objects is illustrated below:

.. testcode::

    import surf
    store = surf.Store(reader="rdflib", writer="rdflib")
    session = surf.Session(store)
    
the `Store` is configured using its constructor arguments. ``reader`` and ``writer``
arguments specify which plugin is to be used for reading and writing RDF
data. Possible values (but not limited to) for these two arguments are `sparql_protocol`, 
`rdflib`, `allegro_franz` and `sesame2`. Plugin-specific configuration options 
are also specified as constructor argument for Store. 
In this example, `store` is configured to use the `sparql_protocol` 
plugin and the address of the **SPARQL HTTP** endpoint is also specified:

.. testcode::

    import surf
    store = surf.Store(reader="sparql_protocol", 
                       endpoint="http://dbpedia.org/sparql")
    session = surf.Session(store)

It is often convenient to load Store configuration options from file instead
of specifying them in code. For example, consider an .ini file with 
the following contents:

.. code-block:: ini
    
    [surf]
    reader=sparql_protocol
    endpoint=http://dbpedia.org/sparql
    

The following snippet loads all configuration keys from the **[surf]** section of the **ini** file
and passes them to `Store` constructor:

.. code-block:: python
    
    import ConfigParser
    import surf
    
    config = ConfigParser.ConfigParser()
    config.readfp(open("sample.ini"))
    store_params = dict(config.items("surf"))
    store = surf.Store(**store_params)
    session = surf.Session(store)                          
    
    
    
    