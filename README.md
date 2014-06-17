*SuRF* is a Python library for working with RDF data in an Object-Oriented manner.
In SuRF, RDF nodes (subjects and objects) are represented as Python objects and
RDF edges (predicates) as their attributes. *SuRF* is an Object RDF Mapper (ORM),
similar in concept to Object Relational Mappers like *SQLAlchemy*.


Install
=======

Install SuRF:

```sh
$ # with easy_install ... 
$ easy_install -U surf

$ # or with pip ... 
$ pip install --upgrade surf
```


You'll need one of the following plugins (also installable by easy_install):

  * _surf.sparql_protocol_,
    for stores with a SPARQL Protocol endpoint (e.g. Virtuoso)
  * _surf.allegro_franz_,
    for the AllegroGraph RDFStore
  * _surf.sesame2_,
    for stores with a Sesame2 HTTP API
  * _surf.rdflib_,
    for the experimental store implementation of rdflib (via rdfextras)


Example
=======

The example below shows how to query a resource using the rdflib in-memory
backend:

```python
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
```

Documentation
=============

You can read the documentation online at http://packages.python.org/SuRF/ 

To build the documentation yourself, install sphinx and run the build step::

```sh
    $ pip install sphinx
    $ python setup.py build_sphinx
```

Unit tests
==========

Run unit tests from the source directory:

```sh
    $ python setup.py test
```

Test plugins from their respective source directory, e.g.:

```sh
    $ cd plugins/surf.sparql_protocol/
    $ python setup.py test
```

