Installing SuRF
===============

SuRF is can be most easily installed with setuptools 
(`setuptools installation <http://peak.telecommunity.com/DevCenter/EasyInstall#installation-instructions>`_).
Run this command-line::

    easy_install surf

Installing rdflib
-----------------

`SuRF` depends on `rdflib` version 2.4.x. On **Windows** platforms the 
`rdflib` package requires python to be configured with a c/c++ compiler in 
order to build native extensions. Here are the steps to set up rdflib 
on Windows:

#. Download and install `MinGW` from http://www.mingw.org/

#. Make sure `gcc` is installed

#. Add the `[MinGW]\\bin` folder to system Path

#. Edit (create if it does not exist) the 
   following file `[Python 2.5 dir]\\lib\\distutils\\distutils.cfg`::

    [build]
    compiler = mingw32

#. Run this from command-line (or simply install `surf` - it will 
   install `rdflib` for you automatically)::

    easy_install rdflib>=2.4.2
    

Further information can be found here:

    - http://code.google.com/p/rdflib/wiki/SetupOnWindows

Installing SuRF plugins
-----------------------

SuRF can access and manipulate RDF data in several different ways. Each data 
access method is available in a separate plugin. You can install all or 
just some of the plugins. Currently available plugins are:
      
* :doc:`plugins/sparql_protocol`. Use this plugin to access data from  
  SPARQL HTTP endpoints. Install it by running this from command-line:: 

    easy_install -U surf.sparql_protocol
    
* :doc:`plugins/rdflib`. This plugin uses rdflib for data access and manipulation. 
  Install it by running this from command-line::

    easy_install -U surf.rdflib
  
* :doc:`plugins/allegro_franz`. Use this plugin to access Franz AllegroGraph  
  triple store. Install it by running this from command-line::

    easy_install -U surf.allegro_franz

* :doc:`plugins/sesame2`. Use this plugin to access data using Sesame2 HTTP 
  protocol. Install it by running this from command-line::

    easy_install -U surf.sesame2

Setting up development version
------------------------------

To get latest development version of SuRF, checkout it from subversion and 
install it using `setup.py` script. Plugins live in the same subversion 
tree but each has separate `setup.py` script so needs to be 
installed separately. 

Instructions for getting code from subversion are here:
    
    http://code.google.com/p/surfrdf/source/checkout
    
Commands for building eggs, installing in development mode, generating 
documentation: 
    
    .. csv-table:: 
        :header: "Command", "Task"
        :widths: 40, 60
        
        **python** setup.py bdist_egg, Build the SuRF egg file
        **python** setup.py bdist_egg register upload, Build and register with *pypi* SuRF if you have access rights
        **python** setup.py develop, Install SuRF in development mode
        **make.bat** html, regenerate the documentation
        
