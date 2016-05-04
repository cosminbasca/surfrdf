Status
======

.. image:: https://travis-ci.org/cosminbasca/surfrdf.svg?branch=master
:target: https://travis-ci.org/cosminbasca/surfrdf


Description
===========

*SuRF* is a Python library for working with RDF data in an Object-Oriented manner. In SuRF, RDF nodes (subjects and
objects) are represented as Python objects and RDF edges (predicates) as their attributes. *SuRF* is an Object RDF
Mapper (ORM), similar in concept to Object Relational Mappers like *SQLAlchemy*.


Documentation
=============

http://surf-rdf.readthedocs.io/en/latest/


Install
=======

Install SuRF:

.. code:: sh

    $ pip install --upgrade surf


Starting with version **1.1.9** the *surf.rdflib* and *surf.sparql_protocol* plugins are bundled with *SuRF*.

You'll need one of the following plugins (also installable by `pip`):

-  *surf.allegro_franz*, for the AllegroGraph RDFStore
-  *surf.sesame2*, for stores with a Sesame2 HTTP API

Example
=======

The example below shows how to query a resource using the rdflib in-memory backend:

.. code:: python

    >>> from surf import *
    >>> store = Store(reader='rdflib',
    ...               writer='rdflib',
    ...               rdflib_store='IOMemory')
    >>> session = Session(store)
    >>> store.load_triples(source='http://www.w3.org/People/Berners-Lee/card.rdf')
    True
    >>> Person = session.get_class(ns.FOAF.Person)
    >>> all_persons = Person.all()
    >>> for person in all_persons:
    ...     print person.foaf_name.first
    ...
    Timothy Berners-Lee

Documentation
=============

You can read the documentation online at http://packages.python.org/SuRF/

To build the documentation yourself, install sphinx and run the build step:

.. code:: sh

        $ pip install sphinx
        $ python setup.py build_sphinx

Testing
=======

*SuRF* uses *tox* and *py.test* for testing:

.. code:: sh

        $ tox

