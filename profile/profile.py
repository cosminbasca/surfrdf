import os
import sys
# make sure we profile the development version not the current installed one of surf
sys.path.insert(0,os.getcwd())

import psyco


from surf import *

rdf_store = Store(  reader      =   'allegro_franz',
                    writer      =   'allegro_franz',
                    server      =   'localhost',
                    port        =   6789,
                    catalog     =   'repositories',
                    repository  =   'tagbuilder')
# the surf session
rdf_session = Session(rdf_store, {})
ns.register(tagbuilder='http://tagbuilder.deri.ie/ns#')

Logic = rdf_session.get_class(ns.TAGBUILDER['Logic'])

def profile_collection(n=50):
  products = Logic.all(0,n)
  return products
  
def profile_collection_iterate(products):
  for i in range(0,len(products)):
    products[i].load()
    #print products[i].tagbuilder_descriptionLevel3

def profile_uri_split(products):
  from surf import util
  for i in range(0,1000):
    for p in products:
      util.uri_split(p.subject)
      
import cProfile
#print '-----------------------------------------------------------'
#print 'Profile Collection'
#cProfile.run('test_collection()')

products = profile_collection(600)

print '-----------------------------------------------------------'
print 'Profile iterate Collection size = %d'%(len(products))

command = 'profile_collection_iterate(products)'
#command = 'profile_uri_split(products)'

cProfile.runctx( command, globals(), locals(), filename="surf.profile" )
