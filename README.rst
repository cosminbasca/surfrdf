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

You can read the latest documentation online at: http://surf-rdf.readthedocs.io/en/latest/
When building from source, you can build your own documentation by following these steps:

.. code:: sh

    $ cd docs
    $ pip install -r requirements.txt
    $ make html

Install
=======

Install SuRF:

.. code:: sh

    $ pip install --upgrade surf


Starting with version **1.1.9** the *surf.rdflib* and *surf.sparql_protocol* plugins are bundled with *SuRF*.

You might need one of the following plugins (also installable with *pip*) for stores not supported by *rdflib* or
which do not expose a *SPARQL* endpoint:

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


Testing
=======

*SuRF* uses *tox* and *py.test* for testing:

.. code:: sh

    $ # test over multiple python versions with tox
    $ tox
    $ # or run the tests in surf
    $ py.test surf


If you have host running *Docker* you can easily test against different interpreters with

.. code:: sh

    $ ./run-docker-tests.sh

If you have a ``.tox`` folder in the project-directory, it will be used to keep the tox-environments.
