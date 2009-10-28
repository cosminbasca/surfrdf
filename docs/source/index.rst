.. SuRF documentation master file, created by
   sphinx-quickstart on Thu Aug 06 22:30:56 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SuRF – Object RDF mapper
========================

.. image:: images/surf-logo.png
   :scale: 70
   :alt: SuRF
   :align: center

`SuRF` is an Object - RDF Mapper based on the popular `rdflib` python library.
It exposes the RDF triple sets as sets of resources and seamlessly integrates 
them into the Object Oriented paradigm of python in a similar manner 
as `ActiveRDF` does for ruby.


Documentation
-------------

.. toctree::
   :maxdepth: 2
   
   install
   examples
   store_session 
   resources_classes
   plugins

API reference
-------------

.. toctree::
   :maxdepth: 2
   
   modules/namespace
   modules/query
   modules/resource/index
   modules/resource/result_proxy
   modules/serializer
   modules/session
   modules/store
   modules/util
   modules/plugin
   modules/rest
   
Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`