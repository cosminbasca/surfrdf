Install and Configure `OpenLink Virtuoso` RDF Store
---------------------------------------------------

Installing on Windows
=====================

The instructions and documentation on how to run `SuRF` on top of `OpenLink Virtuoso`
were contributed by `Peteris Caune <mailto:cuu508@gmail.com>`_ further updates and
information can be read `here <http://cuu508.wordpress.com/>`_ .


    1. Download `virtuoso-opensource-win32-5.0.11.zip <http://go2.wordpress.com/?id=725X1342&site=cuu508.wordpress.com&url=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fvirtuoso%2Ffiles%2Fvirtuoso%2F5.0.11%2Fvirtuoso-opensource-win32-5.0.11.zip%2Fdownload>`_
    
    .. note:: For the purpose of this example version 5.0.11 of `virtuoso` was used, any
                other version can be used instead.
    
    2. Extract it to c:\\virtuoso
    
    3. Add c:\\virtuoso to system *PATH*
    
        3.1. **Optional** Adjust c:\\virtuoso\\database\\virtuoso.ini as needed ou can
        change port number for Virtuoso’s web interface, how much memory it uses,
        which plugins it loads and so forth, `documentation <http://go2.wordpress.com/?id=725X1342&site=cuu508.wordpress.com&url=http%3A%2F%2Fdocs.openlinksw.com%2Fvirtuoso%2Fdatabaseadmsrv.html>`_
        here.
        
    4. Execute from shell:
    
    .. code-block:: bat
        
        $ cd c:\virtuoso\database
        $ virtuoso-t -f virtuoso.ini
        
    .. note:: the *-f* flag sets `virtuoso` to run in the foreground
    
    5. Go explore web frontend at http://localhost:8890. Default
    *username/password* for administrator is *dba/dba*.
    
    6. To communicate with Virtuoso, SuRF will use it’s SPARQL endpoint at http://localhost:8890/sparql.
    By default this endpoint has no write rights. To grant these rights,
    launch *isql* utility from shell and execute this line in it:
    
    .. code-block:: sql
    
        grant SPARQL_UPDATE to "SPARQL";
        

Such a setup configuration is fine for development and testing, but having a
public writable `SPARQL` endpoint on production system is probably not a good idea.
