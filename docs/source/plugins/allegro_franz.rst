The `allegro_franz` Plugin
==========================

.. csv-table:: Input Parameters
    :header: "Parameter", "Default Value", "Description"
    :widths: 20, 20, 60
    
    `server`, `.localhost`, the location of the `AllegroGraph` RDF server
    `port`, `6789`, the port `AllegroGraph` is running on
    `catalog`, `None`, the catalog to use
    `repository`, `None`, the repository to use
    
the parameters are passed as key-value arguments to the :class:`surf.store.Store` class

.. code-block:: python

    s = Store(  reader      = 'allegro_franz',
                writer      = 'allegro_franz',
                server      = 'localhost',
                port        = 6789,
                catalog     = 'repositories',
                repository  = 'test_surf')
        
        
Setting up `AllegroGraph` RDF Store
-----------------------------------

.. toctree::
   :maxdepth: 2
   
   /integration/allegro
           