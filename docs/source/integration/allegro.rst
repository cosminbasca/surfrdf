Install and Configure `AllegroGraph` RDF Store
----------------------------------------------

Download `AllegroGraph` from here http://www.franz.com/downloads/clp/ag_survey
after you complete the Franz online survey. The free version of `AllegroGraph` is
limited to 50.000.000 RDF triples.

Installing on Windows
=====================

`AllegroGraph` is installed as a `windows service`. After the installation if complete
one must proceed to configure the RDF store

    1. Create a folder on disk where the store `repositories` will reside, say
    D:\\repositories
    
    
    2. Open and edit the `[AllegroGraph installation directory]\\agraph.cfg` file and
    change it accordingly
    
    
    .. code-block:: common-lisp
    
        ;; This file contains the configuration options for AllegroGraph.
        ;; Please refer to the installation documentation for the
        ;; AllegroGraph server for information on valid values for these options.
        ;;
        ;; Comments start with a semicolon (;).
        (
        ;; Please do not change the following line:
        (:agraph-server-config 5)
        ;; User-settable options start here:
        :direct nil
        :new-http-port 6789
        :new-http-auth nil
        :new-http-catalog ("D:/repositories")
        :http-port -1
        :http-init-file nil
        :http-only nil
        :idle-life 86400
        :eval-in-server-file nil
        :pid-file "sys:agraph.pid"
        :client-prolog nil
        :index -1
        :init-file "sys:aginit.cl"
        :lease -1
        :limit -1
        :log-file "sys:agraph.log"
        :no-direct nil
        :no-java nil
        :port 4567
        :port2 4568
        :res -1
        :repl-port nil
        :standalone t
        :timeout 60
        :error-log nil
        :users 50
        :verbose t
        )
        ;;END OF CONFIG
    
    the location of the repositories folder can be any, so can the port
    
    3. Copy the `[AllegroGraph installation directory]\\python\\franz` directory to
    `[Python installation directory]\\lib\\site-packages` and install the required
    python libs as requested in the documentation
    
    
    4. Update `AllegroGraph` and restart the service

Installing on Linux
===================

Extract `AllegroGraph` to a location of your choosing

    1. Create a folder on disk where the store `repositories` will reside, say
    /home/user/repositories
    
    
    2. Open and edit the `[AllegroGraph installation directory]/agraph.cfg` file and
    change it accordingly
    
    .. code-block:: common-lisp
    
        ;; This file contains the configuration options for AllegroGraph.
        ;; Please refer to the installation documentation for the
        ;; AllegroGraph server for information on valid values for these options.
        ;;
        ;; Comments start with a semicolon (;).
        (
        ;; Please do not change the following line:
        (:agraph-server-config 5)
        ;; User-settable options start here:
        :direct nil
        :new-http-port 6789
        :new-http-auth nil
        :new-http-catalog ("/home/user/repositories")
        :http-port -1
        :http-init-file nil
        :http-only nil
        :idle-life 86400
        :eval-in-server-file nil
        :pid-file "sys:agraph.pid"
        :client-prolog nil
        :index -1
        :init-file "sys:aginit.cl"
        :lease -1
        :limit -1
        :log-file "sys:agraph.log"
        :no-direct nil
        :no-java nil
        :port 4567
        :port2 4568
        :res -1
        :repl-port nil
        :standalone t
        :timeout 60
        :error-log nil
        :users 50
        :verbose t
        )
        ;;END OF CONFIG
    
    the location of the repositories folder can be any, so can the port
    
    3. Copy the `[AllegroGraph installation directory]/python/franz` directory to
    `[Python installation directory]/site-packages` and install the required
    python libs as requested in the documentation
    
    
    4. Update `AllegroGraph` and restart the service
