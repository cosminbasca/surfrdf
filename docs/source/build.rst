Build SuRF and the plugins from source
--------------------------------------

1. Check out SuRF from source
    see the instructions available here:
    http://code.google.com/p/surfrdf/source/checkout
    
2. In the `source` folder (the one that contains the `surf` folder) execute the following commands
    
    .. csv-table:: build commands
        :header: "Command", "Description"
        :widths: 40, 60
        
        **python** setup.py bdist_egg, Build the SuRF egg file
        **python** setup.py bdist_egg register upload, Build and register with *pypi* SuRF if you have access rights
        **python** setup.py develop, Run :mod:`surf` in development mode
        **make.bat** html, regenerate the documentation
        
    the same commands can be executed for the plugins
