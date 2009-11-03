Resources and Classes
=====================
 
SuRF Resource objects are the core part of SuRF. In SuRF, RDF data is queried, 
accessed and modified by working with attributes of Resource objects.
Here's how SuRF Resource maps to RDF triples at conceptual level:

.. image:: images/resources_triples.png
   :alt: Resource - Triple mapping
   :align: center

Getting a single Resource object
--------------------------------

If type and URI of resource is known, resource can be loaded using session's 
:meth:`surf.session.Session.get_class` and 
:meth:`surf.session.Session.get_resource` methods::

	# Create FoafPerson class:
	FoafPerson = session.get_class(surf.ns.FOAF.Person)
	# Create instance of FoafPerson class:
	john = session.get_resource("http://john.com/me", FoafPerson) 

Loading multiple resources
--------------------------

Getting all instances of `FoafPerson` class, in undefined order::

	FoafPerson = session.get_class(surf.ns.FOAF.Person)
	for person in FoafPerson.all():
		print "Found person:", person.foaf_name.first
	
Getting instances of `FoafPerson` class named "John"::  

	FoafPerson = session.get_class(surf.ns.FOAF.Person)
	for person in FoafPerson.get_by(foaf_name = "John"):
		print "Found person:", person.foaf_name.first, person.foaf_surname.first
		
Getting ordered and limited list of persons::		

	FoafPerson = session.get_class(surf.ns.FOAF.Person)
	for person in FoafPerson.all().limit(10).order(surf.ns.FOAF.name):
		print "Found person:", person.foaf_name.first, person.foaf_surname.first

Other modifiers accepted by ``all()`` and ``get_by`` are described in
:mod:`surf.resource.result_proxy` module.

Using resource attributes
-------------------------

A SuRF resource represents a single RDF resource. Its URI is stored in
``subject`` attribute::

	>>> FoafPerson = session.get_class(surf.ns.FOAF.Person)
	>>> john = session.get_resource("http://john.com/me", FoafPerson)
	>>> print john.subject 
	"http://john.com/me"

RDF triples that describe this resource are also available as attributes.
SuRF follows "namespace_predicate" convention for attribute names, thus::

	# Print all foaf:name values:
	>>> print john.foaf_name
	# Print first foaf:name value or None if there aren't any:
	>>> print john.foaf_name.first
	# Print first foaf:name value or raise exception if there aren't any or 
	# there are more than one:
	>>> print john.foaf_name.one

Attributes can also be used as starting points for more involved querying::

	# Get ordered list of all friends named "Jane": 
	>>> john.foaf_knows.get_by(foaf_name = "Jane").order()

Saving, deleting resources
--------------------------

Saving a resource::

	resource.save()
	
Deleting a resource::

	resource.remove()	
