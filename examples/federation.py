import surf

dbpedia = surf.Store(reader = 'sparql_protocol',
                     endpoint = 'http://dbpedia.org/sparql',
                     default_graph = 'http://dbpedia.org')

local = surf.Store(reader = 'allegro_franz',
                   writer = 'allegro_franz',
                   server = 'localhost',
                   port = 6789,
                   catalog = 'repositories',
                   repository = 'surf_test')

print 'Create the session'
session = surf.Session()
session.enable_logging = True
session['dbpedia'] = dbpedia
session['local'] = local

print '------------------------------------------------------------------------'
print 'DBPEDIA'
PhilCollinsAlbums = session.get_class(surf.ns.YAGO['PhilCollinsAlbums'],
                                      store = 'dbpedia')

all_albums = PhilCollinsAlbums.all()

print 'Phill Collins has %d albums on dbpedia' % len(all_albums)
first_album = all_albums.first()
first_album.load()

print 'All covers'
for a in all_albums:
    if a.dbpedia_name:
        print '\tCover %s for "%s"' % (a.dbpedia_cover.first, 
                                       a.dbpedia_name.first)

print '------------------------------------------------------------------------'
print 'LOCAL'

local.clear()

print 'Define a namespace'
surf.ns.register(surf = 'http://surf.test/ns#')

print 'Create some classes'
Actor = session.get_class(surf.ns.SURF['Actor'], store = 'local')
Movie = session.get_class(surf.ns.SURF['Movie'], store = 'local')

print Actor, Actor.uri
print Movie, Movie.uri

print 'Create some instances'
m1 = Movie('http://baseuri/m1')
m1.surf_title = "Movie 1"

m2 = Movie('http://baseuri/m2')
m2.surf_title = "Movie 2"

m3 = Movie('http://baseuri/m3')
m3.surf_title = "Movie 3"

m4 = Movie('http://baseuri/m4')
m4.surf_title = "Movie 4"

m5 = Movie('http://baseuri/m5')
m5.surf_title = "Movie 5"

a1 = Actor('http://baseuri/a1')
a1.surf_name = "Actor 1"
a1.surf_adress = "Some drive 35"
a1.surf_movies = [m1, m2, m3]

a2 = Actor('http://baseuri/a2')
a2.surf_name = "Actor 2"
a2.surf_adress = "A different adress"
a2.surf_movies = [m3, m4, m5]

# saving
print 'Comitting ... '
session.commit()


print 'Retrieving from store'
actors = list(Actor.all())
movies = list(Movie.all())

print 'Actor 1 cmp: ', a1 == actors[0]
print 'Actor 1 cmp: ', a1 == actors[1]
print 'Actor in list : ', a1 in actors

print 'All movies %d' % len(movies)
for m in movies:
    print m.surf_title

print 'All actors %d' % len(actors)
for a in actors:
    print a.surf_name
    actor_movies = a.surf_movies
    for am in actor_movies:
        print '\tStarred in %s' % am.surf_title

print "Done."