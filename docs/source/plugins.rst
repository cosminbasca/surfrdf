The default SuRF plugins
------------------------

by default surf supports the following plugins:

- :doc:`plugins/allegro_franz` (AllegroGraph)
- :doc:`plugins/rdflib` (rdflib)
- :doc:`plugins/sparql_protocol` (SPARQL HTTP protocol)
- :doc:`plugins/sesame2` (Sesame2 HTTP protocol)

The plugins are installed in the following manner 
(they are available on **pypi**)::

    >>> easy_install -U surf.allegro_franz
    >>> easy_install -U surf.rdflib
    >>> easy_install -U surf.sesame2
    >>> easy_install -U surf.sparql_protocol