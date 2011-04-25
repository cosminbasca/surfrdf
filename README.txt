SuRF is a Python library for working with RDF data in an Object-Oriented way.
In SuRF, RDF nodes (subjects and objects) are represented as Python objects and
RDF arcs (predicates) as their attributes. SuRF is an Object RDF Mapper (ORM),
similar in concept to Object Relational Mappers like SQLAlchemy.


Install
=======

Install SuRF::

    $ easy_install -U surf

You'll need one of the following plugins (also installable by easy_install):

  * ``surf.sparql_protocol``,
    for stores with a SPARQL Protocol endpoint (e.g. Virtuoso)
  * ``surf.allegro_franz``,
    for the AllegroGraph RDFStore
  * ``surf.sesame2``,
    for stores with a Sesame2 HTTP API
  * ``surf.rdflib``,
    for the experimental store implementation of rdflib (via rdfextras)


Example
=======

The example below shows how to query a resource using the rdflib in-memory
backend:

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

You can read the documentation online at http://packages.python.org/SuRF/ or
download from http://code.google.com/p/surfrdf/downloads/list.


Unit tests
==========

Run unit tests from the source directory::

    $ python setup.py test

Test plugins from their respective source directory, e.g.::

    $ cd plugins/surf.sparql_protocol/
    $ python setup.py test


Contact
=======

Please report bugs to http://code.google.com/p/surfrdf/issues/list.
There is a mailing list at surfrdf@googlegroups.com
(http://groups.google.com/group/surfrdf).

