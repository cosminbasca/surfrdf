Installation of SuRF
--------------------

to install **SuRF** execute the following commands (if you have `setuptools` installed)

::

    >>> easy_install -U surf
    >>> easy_install -U surf.allegro_franz
    >>> easy_install -U surf.rdflib
    >>> easy_install -U surf.sesame2
    >>> easy_install -U surf.sparql_protocol
    
`surf` depends on `rdflib` version 2.4.x, on **windows** platforms the `rdflib` package
requires python to be configured with a c/c++ compiler in order to build native extensions.
Read the following section to see how to configure python to use `mingw` as the compiler
for native extensions.
    
.. toctree::
   :maxdepth: 2
   
   rdflib