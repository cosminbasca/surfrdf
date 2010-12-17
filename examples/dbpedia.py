import surf

store = surf.Store(reader = 'sparql_protocol',
                   endpoint = 'http://dbpedia.org/sparql',
                   default_graph = 'http://dbpedia.org')

print 'Create the session'
session = surf.Session(store, {})
session.enable_logging = False

PhilCollinsAlbums = session.get_class(surf.ns.YAGO['PhilCollinsAlbums'])

all_albums = PhilCollinsAlbums.all()

print 'Phil Collins has %d albums on dbpedia' % len(all_albums)

first_album = all_albums.first()
# This loads all direct atributes for first_album, so
# each subsequent attribute access doesn't require HTTP call. 
first_album.load()

print 'All covers'
for a in all_albums:
    if a.dbpedia_name and a.dbpedia_cover:
        # Resource attributes are list-like, with convenience 
        # properties "first" and "one". 
        print '\tCover %s for "%s"' % (a.dbpedia_cover.first, 
                                       a.dbpedia_name.first)
