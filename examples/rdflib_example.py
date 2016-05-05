import surf
from surf.log import setup_logger, set_logger_level
import logging

setup_logger()
set_logger_level(logging.DEBUG)

store = surf.Store(reader="rdflib",
                   writer="rdflib",
                   rdflib_store="IOMemory")

session = surf.Session(store)

print "Load RDF data"
store.load_triples(source="http://www.w3.org/People/Berners-Lee/card.rdf")
print len(store)

Person = session.get_class(surf.ns.FOAF["Person"])

all_persons = Person.all()

print "Found %d persons in Tim Berners-Lee's FOAF document" % (len(all_persons))
for person in all_persons:
    print person.foaf_name.first