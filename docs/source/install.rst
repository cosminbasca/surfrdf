Installing SuRF
===============

`SuRF` can be most easily installed with setuptools 
(`setuptools installation <http://peak.telecommunity.com/DevCenter/EasyInstall#installation-instructions>`_),
by running this from command-line:

    .. code-block:: bash
    
        $ easy_install surf
        
alternativelly, `SuRF` can be downloaded and the following command executed:

    .. code-block:: bash
    
        $ sudo python setup.py install
        

if you choose the second option, than the dependencies must be installed beforehand. `SuRF` depends on
`rdflib` and `simplejson`.

Installing rdflib
-----------------

`SuRF` depends on `rdflib` version 2.4.x or 3.x.x. On **Windows** platforms the 
`rdflib` package requires python to be configured with a c/c++ compiler in 
order to build native extensions. Here are the steps to required set up `rdflib` 
on Windows:

#. Download and install `MinGW` from http://www.mingw.org/

#. Make sure `gcc` is installed

#. Add the `[MinGW]\\bin` folder to system Path

#. Edit (create if it does not exist) the 
   following file `[Python 2.X dir]\\lib\\distutils\\distutils.cfg`:

    .. code-block:: ini
        
        [build]
        compiler = mingw32
        

#. Run this from command-line (or simply install `surf` - it will 
   install `rdflib` for you automatically):

    .. code-block:: bash
        
        $ easy_install rdflib>=2.4.2
        

Further information can be found here:

    - http://code.google.com/p/rdflib/wiki/SetupOnWindows

Installing SuRF plugins
-----------------------

SuRF can access and manipulate RDF data in several different ways. Each data 
access method is available in a separate plugin. You can install all or 
just some of the plugins. Currently available plugins are:
      
* :doc:`plugins/sparql_protocol`. Use this plugin to access data from  
  **SPARQL HTTP** endpoints. Install it by running this from command-line:

    .. code-block:: bash
        
        $ easy_install -U surf.sparql_protocol
        
    
* :doc:`plugins/rdflib`. This plugin uses `rdflib` for data access and manipulation. 
  Install it by running this from command-line:
    
    .. code-block:: bash
        
        $ easy_install -U surf.rdflib
        
  
* :doc:`plugins/allegro_franz`. Use this plugin to access **Franz AllegroGraph**  
  triple store. Install it by running this from command-line:

    .. code-block:: bash
        
        $ easy_install -U surf.allegro_franz
        

* :doc:`plugins/sesame2`. Use this plugin to access data using **Sesame2 HTTP** 
  protocol. Install it by running this from command-line:

    .. code-block:: bash
        
        $ easy_install -U surf.sesame2
        

Loading plugins from path
-------------------------
In the cases where `SuRF` is distributed bundled with an application, one can choose to load the
plugins from a specific location. You can do so via the :meth:`surf.plugin.manager.add_plugin_path` method, as
in the code snippet below:

.. code-block:: python
    
    from surf.plugin import manager
    
    #setup a local folder where the plugins are stored
    manager.add_plugin_path('/path/to/plugins')
    # reload plugins if, allready loaded
    manager.load_plugins(reload=True)
    
    # the rest of the application logic
    ...


Setting up `SuRF` in development mode
-------------------------------------

To get the latest development version of `SuRF`, check it out from subversion and 
install it using the `setup.py` script. Plugins live in the same subversion 
tree but each has it's separate `setup.py` script, so they need to be 
installed separately. 

Instructions for getting the code from subversion can be found here:
    
    http://code.google.com/p/surfrdf/source/checkout
    
Here is a brief and useful list of **commands** for building eggs, installing in development mode and generating 
documentation: 
    
    .. csv-table:: 
        :header: "Command", "Task"
        :widths: 40, 60
        
        **python** setup.py bdist_egg, Build the SuRF egg file
        **python** setup.py bdist_egg register upload, Build and register with *pypi* SuRF if you have access rights
        **python** setup.py develop, Install SuRF in development mode
        **make.bat** html, regenerate the documentation
        
