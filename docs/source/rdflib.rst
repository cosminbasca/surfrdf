Installing `rdflib`
-------------------

1. Download and install `MinGW` from here http://www.mingw.org/

2. Make sure `gcc` is installed

3. Add the `[MinGW]\\bin` folder to system Path

4. Edit (create if it does not exist) the following file `[Python 2.5 dir]\\lib\\distutils\\distutils.cfg`

.. code-block:: ini

    [build]
    compiler = mingw32
    
**Optional**: If you have `setuptools` installed run the following command (or simply install `surf` - it
will install `rdflib` for you automatically)

::
    
    >>> easy_install -U rdflib>=2.4.2
    

Further information can be found here:

    - http://code.google.com/p/rdflib/wiki/SetupOnWindows