Inegrating :mod:`surf` with `Pylons`
------------------------------------

Creating a `Pylons` Blog, on `SuRF`
===================================

The example is an adaptation of the following example
    
    - http://wiki.pylonshq.com/display/pylonscookbook/Making+a+Pylons+Blog

1. Install :mod:`pylons`

    .. code-block:: bash
    
        $ easy_install pylons
        
2. Create a `pylons` application called `MyBlog`

    .. code-block:: bash
    
        $ cd /home/user/workspace
        $ paster create -t pylons MyBlog
        $ cd MyBlog
             
3. The Models and the Data.
    
    For this example we use the `AllegroGraph` RDF store. See the :doc:`allegro` page
    The default `engine` has been left in, just as in the original example, one can take it out if
    needed.
    
    3.1. Edit the `~/MyBlog/development.ini` file and add the following lines
    
    .. code-block:: ini
    
        [app-main]
        ...
        surf.reader     = allegro_franz
        surf.writer     = allegro_franz
        surf.server     = localhost
        surf.port       = 6789
        surf.catalog    = repositories
        surf.repository = surf_blog
        surf.logging    = true
        surf.clear      = false
        myblog.namespace= http://myblog.com/ns#
        ...
        
    3.2. Edit the `~/MyBlog/myblog/config/environment.py` file
    Add the following lines at the top of the file
    
    .. code-block:: python
    
        from surf import *
        from myblog.model import *
        
    and the following at the end of the :func:`load_environment` method
    
    .. code-block:: python
    
        rdf_store = Store(reader    = config['surf.reader'],
                          writer    = config['surf.writer'],
                          server    = config['surf.server'],
                          port      = config['surf.port'],
                          catalog   = config['surf.catalog'],
                          repository= config['surf.repository'])
        
        if config['surf.clear'] == 'true':
            rdf_store.clear()
        print 'SIZE of STORE : ',rdf_store.size()
    
        # the surf session
        rdf_session = Session(rdf_store, {})
        rdf_session.enable_logging = True if config['surf.logging'] == 'true' else False
            
        # register the namespace
        ns.register(myblog=config['myblog.namespace'])
        
        init_model(rdf_session)
        
    3.3. Edit the `~/MyBlog/myblog/model/__ init __.py` file
    
    .. code-block:: python
    
        from surf import *
        
        def init_model(session):
            """Call me before using any of the tables or classes in the model"""
            global rdf_session
            rdf_session = session
            
            global Blog    
            Blog = rdf_session.get_class(ns.MYBLOG['Blog'])
        
    3.4. **Optional** You can edit `~/MyBlog/myblog/websetup.py` to add initial data in the RDF store
    or just to run maintenance tasks for your `pylons` application, but this is not needed yet

    3.5. **Optional** You can setup your application by issuing the following command:
    
    .. code-block:: bash
    
        $ paster setup-app development.ini
        
4. Putting the script together

    4.1. Creating the `blog` controller
    
    .. code-block:: bash
    
        $ paster controller blog
        
        
    4.2. Edit the `~/MyBlog/myblog/controllers/blog.py` file
    
    .. code-block:: python
    
        import logging
        
        from pylons import request, response, session, tmpl_context as c
        from pylons.controllers.util import abort, redirect_to
        
        from myblog.lib.base import *                     
        from myblog import model
        
        log = logging.getLogger(__name__)
        
        class BlogController(BaseController):
        
            def index(self):
                c.posts = model.Blog.all(limit=5)
                return render("/blog/index.html")

                
    4.3. Create the template
    
    .. code-block:: bash
            
        $ mkdir ~/MyBlog/myblog/templates/blog
        
    4.4. Edit the template `~/MyBlog/myblog/templates/blog/index.html`
    
    .. code-block:: mako
    
        <%inherit file="site.html" />
        <%def name="title()">MyBlog Home</%def>
        
        <p>${len(c.posts)} new blog posts!</p>
        
        % for post in c.posts:
        <p class="content" style="border-style:solid;border-width:1px">
                <span class="h3"> ${post.dc_title} </span>
                <span class="h4">Posted on: ${post.dc_created} by ${post.sioc_has_creator}</span>
                <br>
                  ${post.sioc_content}
        </p>
        % endfor
        
        <hr/>
        <a href="/toolkit/index">Admin</a>

    For this example the following properties were chosen to describe a blog post in this system,
    the `sioc:content` describes the content of the post, `sioc:has_author` describes the author,
    the `dc:created` describes the creation date and the `dc:title` describes the title of the post.
    
    4.5. Edit the `~/MyBlog/myblog/templates/blog/site.html` file
    
    .. code-block:: mako
    
        <%def name="title()"></%def>
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <title>MyBlog: ${self.title()}</title>
            </head>
            <body>
                <h1>${self.title()}</h1>
        
        <!-- *** BEGIN page content *** -->
        ${self.body()}
        <!-- *** END page content *** -->
        
            </body>
        </html>
        
    4.6. **Optional** Add the transaction logger to the blog system. Edit the
    `~/MyBlog/myblog/config/middleware.py` file
    
    at the begining
    
    .. code-block:: python
    
        from paste.translogger import TransLogger
    
    in the :func:`make_app` method add the following
    
    .. code-block:: python
        
        # CUSTOM MIDDLEWARE HERE    
        format = ('%(REMOTE_ADDR)s - %(REMOTE_USER)s [%(time)s] '
          '"%(REQUEST_METHOD)s %(REQUEST_URI)s %(HTTP_VERSION)s" '
          '%(status)s %(bytes)s')
        app = TransLogger(app, format=format, logger_name="access")
    
    4.7. Test the application:
    
    .. code-block:: bash
    
        $  paster serve --reload development.ini
        Starting subprocess with file monitor
        01:55:52,596 INFO  [rdflib] version: 2.4.2
        surf.plugin allegro_franz reader : franz libraries installed
        surf.plugin allegro_franz writer : franz libraries installed
        01:55:52,682 INFO  [Store] initializing the store
        01:55:52,682 INFO  [Store] registered readers : ['sparql_protocol', 'allegro_franz', 'sesame2']
        01:55:52,683 INFO  [Store] registered writer : ['allegro_franz', 'sesame2']
        01:55:52,711 INFO  [Store] store initialized
        Starting server in PID 14993.
        serving on http://127.0.0.1:5000
    
    Test the application on: http://localhost:5000/blog/index, the following should be displayed:
    
    ::
    
        MyBlog Home
        
        0 new blog posts!
        
    4.8. The home pace. Delete the `~/MyBlog/myblog/public/index.html` file. Edit the
    `~/MyBlog/myblog/config/routing.py` file
    
    After the `# CUSTOM ROUTES HERE` add this line
    
    .. code-block:: python
    
        map.connect('/', controller='blog', action='index')

5. Adding a toolkit. The `admin` frontend

    5.1. Add the `toolkit` controller
    
    .. code-block:: bash
    
        $ paster controller toolkit
    
    5.2. Create the `toolkit` templates
    
    .. code-block:: bash
    
        $ mkdir ~/MyBlog/myblog/templates/toolkit

    edit `~/MyBlog/myblog/templates/toolkit/index.html`
    
    .. code-block:: mako
    
        <%inherit file="/blog/site.html" />
        <%def name="title()">Admin Control Panel</%def>
        
        This is home of the toolkit. <br>
        For now you can only 
        <a href="${h.url_for(controller="toolkit", action="blog_add")}">add</a>
        blog posts.
        <p>
        Later on you'll be able to delete and edit also.

    edit `~/MyBlog/myblog/templates/toolkit/add.html`
    
    .. code-block:: mako
    
        <%inherit file="/blog/site.html" />
        <%def name="title()">Add Blog Post</%def>
        
        <span class="h3"> Post a Comment </span>
        ${h.form('/toolkit/blog_add_process')}
        <label>Subject: ${h.text('title')}</label><br>
        <label>Author: ${h.text('author')}</label><br>
        <label>Post Content: ${h.textarea('content')}</label><br>
        ${h.submit('Submit','Post New Page')}
        ${h.end_form()}

    5.3. Change the controller so that it handles the new actions. Edit
    `~/MyBlog/myblog/controllers/toolkit.py`
    
    .. code-block:: python
    
        import datetime
        import logging
        
        from pylons import request, response, session, tmpl_context as c
        from pylons.controllers.util import abort, redirect_to
        from myblog.lib.base import *
        from myblog import model
        from surf import *
        
        log = logging.getLogger(__name__)
        
        class ToolkitController(BaseController):
        
            def index(self):
                return render('/toolkit/index.html')
        
            def blog_add(self):
                return render('/toolkit/add.html')
        
            def blog_add_process(self):
                # Create a new Blog object and populate it.
                # if you do not specify a subject, one will automatically be generated for you
                # in the surf namespace
                newpost = model.Blog()
                newpost.dc_created = datetime.datetime.now()
                newpost.sioc_content = request.params['content']
                newpost.sioc_has_creator = request.params['author']
                newpost.dc_title = request.params['title']
                
                # commit the changes - the session tracks Resources automatically
                model.rdf_session.commit()
        
                # Redirect to the blog home page.
                redirect_to("/")
                
    5.4. Edit  the `~/MyBlog/myblog/lib/helpers.py` file, add the line in the import section
    
    .. code-block:: python
    
        from routes import url_for
        from webhelpers.html.tags import *
        
    edit the `~/MyBlog/myblog/lib/base.py` file, add the line in the import section
    
    .. code-block:: python
    
        import helpers as h

    5.5. Thant's it :), Try it out.
    Test the toolkit interface on:
        
        - http://localhost:5000/toolkit/index
        
    **Important** This was tested with `pylons 0.9.7`
    
    