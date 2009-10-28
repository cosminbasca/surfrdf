Store and Session
=================

What do store and session do?
-----------------------------

Session establishes all conversations to backend storage service. Resources 
use it to load and save their constituting triples. Session keeps  
cache of already loaded data, and it uses one or more stores to do actual  
loading and saving of data. 

Store provides functions for loading and saving data, these are divided 
into "reader" and "writer" parts. Readers and writers are provided by plugins.

Preparing store and session
-------------------------------

Store and Session can be instantiated as any regular Python object. 
Instantiation of store and session is illustrated below:

.. testcode::

    import surf
    store = surf.Store(reader = "rdflib", writer = "rdflib")
    session = surf.Session(store)
    
Store is configured using its constructor arguments. ``reader`` and ``writer``
arguments specify which plugin is to be used for reading and writing RDF
data. Possible values for these two arguments are `sparql_protocol`, 
`rdflib`, `allegro_franz` and `sesame2`. Plugin-specific configuration options 
are also specified as constructor argument for Store. 
In this example, store is configured to use `sparql_protocol` 
plugin and address of SPARQL HTTP endpoint is also specified:

.. testcode::

    import surf
    store = surf.Store(reader = "sparql_protocol", 
                       endpoint = "http://dbpedia.org/sparql")
    session = surf.Session(store)

It is often convenient to load Store configuration options from file instead
of specifying them in code. For example, consider an .ini file with 
the following contents::

    [surf]
    reader=sparql_protocol
    endpoint=http://dbpedia.org/sparql 

This snippet loads all keys from "[surf]" section of that file and passes them
to Store constructor::

    import ConfigParser
    import surf
    
    config = ConfigParser.ConfigParser()
    config.readfp(open("sample.ini"))
    store_params = dict(config.items("surf"))
    store = surf.Store(**store_params)
    session = surf.Session(store)                          


