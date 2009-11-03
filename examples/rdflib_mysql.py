import rdflib
import surf

# mysql connection string that will be passed to rdflib's mysql plugin
DB_CONN = 'host=localhost,user=surf,password=password,db=rdfstore'


def get_rdflib_store():
    store = rdflib.plugin.get('MySQL', rdflib.store.Store)('rdfstore')
    
    # rdflib can create necessary structures if the store is empty
    rt = store.open(DB_CONN, create=False)
    if rt == rdflib.store.VALID_STORE:
        pass
    elif rt == rdflib.store.NO_STORE:
        store.open(DB_CONN, create=True)
    elif rt == rdflib.store.CORRUPTED_STORE:
        store.destroy(DB_CONN)    
        store.open(DB_CONN, create=True)

    return store



store = surf.Store(reader='rdflib',
                   writer='rdflib',
                   rdflib_store = get_rdflib_store())
session = surf.Session(store)

