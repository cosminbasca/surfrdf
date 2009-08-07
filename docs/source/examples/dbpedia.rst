Example using the public SPARQL-endpoint from DBpedia
=====================================================

.. code-block:: python
    
    from surf import *
    
    store =  Store( reader='sparql_protocol',
                    endpoint='http://dbpedia.org/sparql',
                    default_graph='http://dbpedia.org')
    
    print 'Create the session'
    session = Session(store,{})
    session.enable_logging = False
    
    PhilCollinsAlbums = session.get_class(ns.YAGO['PhilCollinsAlbums'])
    
    all_albums = PhilCollinsAlbums.all()
    
    print 'Phill Collins has %d albums on dbpedia'%len(all_albums)
    
    first_album = all_albums[0]
    first_album.load()
    
    print 'All covers'
    for a in all_albums:
        if a.dbpedia_name:
            cvr = a.dbpedia_cover
            print '\tCover %s for "%s"'%(str(a.dbpedia_cover),str(a.dbpedia_name))