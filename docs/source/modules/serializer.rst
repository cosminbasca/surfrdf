The :mod:`surf.serializer` Module
---------------------------------

.. automodule:: surf.serializer
   :members:
   :inherited-members:

Serialization Example
=====================

.. code-block:: xml

    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:foaf="http://xmlns.com/foaf/0.1/"
      xmlns:dc="http://purl.org/dc/elements/1.1/">
      <rdf:Description rdf:about="http://example.org/about">
        <dc:creator>Anna Wilder</dc:creator>
        <dc:title xml:lang="en">Anna's Homepage</dc:title>
        <foaf:maker rdf:nodeID="person" />
      </rdf:Description>
      <rdf:Description rdf:nodeID="person">
        <foaf:homepage rdf:resource="http://example.org/about" />
        <foaf:made rdf:resource="http://example.org/about" />
        <foaf:name>Anna Wilder</foaf:name>
        <foaf:firstName>Anna</foaf:firstName>
        <foaf:surname>Wilder</foaf:surname>
        <foaf:depiction rdf:resource="http://example.org/pic.jpg" />
        <foaf:nick>wildling</foaf:nick>
        <foaf:nick>wilda</foaf:nick>
        <foaf:mbox_sha1sum>69e31bbcf58d432950127593e292a55975bc66fd</foaf:mbox_sha1sum>
      </rdf:Description>
    </rdf:RDF>

is represented in **RDF-JSON** as

.. code-block:: javascript

    {
        "http://example.org/about" : {
            "http://purl.org/dc/elements/1.1/creator" : [ { "value" : "Anna Wilder", "type" : "literal" } ],
            "http://purl.org/dc/elements/1.1/title"   : [ { "value" : "Anna's Homepage", "type" : "literal", "lang" : "en" } ] ,
            "http://xmlns.com/foaf/0.1/maker"         : [ { "value" : "_:person", "type" : "bnode" } ]
        } ,
     
        "_:person" : {
            "http://xmlns.com/foaf/0.1/homepage"      : [ { "value" : "http://example.org/about", "type" : "uri" } ] ,
            "http://xmlns.com/foaf/0.1/made"          : [ { "value" : "http://example.org/about", "type" : "uri" } ] ,
            "http://xmlns.com/foaf/0.1/name"          : [ { "value" : "Anna Wilder", "type" : "literal" } ] ,
            "http://xmlns.com/foaf/0.1/firstName"     : [ { "value" : "Anna", "type" : "literal" } ] ,
            "http://xmlns.com/foaf/0.1/surname"       : [ { "value" : "Wilder", "type" : "literal" } ] , 
            "http://xmlns.com/foaf/0.1/depiction"     : [ { "value" : "http://example.org/pic.jpg", "type" : "uri" } ] ,
            "http://xmlns.com/foaf/0.1/nick"          : [ 
                                                          { "type" : "literal", "value" : "wildling"} , 
                                                          { "type" : "literal", "value" : "wilda" } 
                                                        ] ,
            "http://xmlns.com/foaf/0.1/mbox_sha1sum"  : [ {  "value" : "69e31bbcf58d432950127593e292a55975bc66fd", "type" : "literal" } ] 
        }
    }

for a more detailed description and the serialization algorithm please visit:
    - http://n2.talis.com/wiki/RDF_JSON_Specification