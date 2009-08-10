The `sesame2` Plugin
--------------------------

.. csv-table:: Input Parameters
    :header: "Parameter", "Default Value", "Description"
    :widths: 20, 20, 60
    
    `server`, `.localhost`, the location of the `AllegroGraph` RDF server
    `port`, `6789`, the port `AllegroGraph` is running on
    `catalog`, `None`, the catalog to use
    `repository`, `None`, the repository to use
    `root_path`, `/sesame`, the sesame http api root path pf the server
    `repository_path`, , the location on disk of the directory holding the repository
        
the parameters are passed as key-value arguments to the :class:`surf.store.Store` class

.. code-block:: python

    s = Store(  reader          = 'sesame2',
                writer          = 'sesame2',
                server          = 'localhost',
                port            = 6789,
                catalog         = 'repositories',
                repository      = 'test_surf',
                root_path       = '/sesame',
                repository_path =   r'D:\repositories')
        