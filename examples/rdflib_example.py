import surf

store = surf.Store(reader = 'rdflib',
                   writer = 'rdflib',
                   rdflib_store = 'IOMemory')

session = surf.Session(store)

#print 'load : http://bigasterisk.com/foaf.rdf'
#store.load_triples(source='http://bigasterisk.com/foaf.rdf')
print 'load : http://www.w3.org/People/Berners-Lee/card.rdf'
store.load_triples(source='http://www.w3.org/People/Berners-Lee/card.rdf')
print 'load : http://danbri.livejournal.com/data/foaf'
store.load_triples(source="http://danbri.livejournal.com/data/foaf")

#print 'loading http://irc.sioc-project.org/users/CaptSolo#user '
#store.load_triples(source='http://irc.sioc-project.org/users/CaptSolo#user')

Person = session.get_class(surf.ns.FOAF['Person'])

all_persons = Person.all()

print 'Found %d persons' % (len(all_persons))
for person in all_persons:
    print person.foaf_name, ' knows ', person.foaf_knows
    
#for s,p,o in store.reader.graph:
#    print s,p,o

