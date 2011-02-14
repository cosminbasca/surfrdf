from surf.rdf import BNode, Literal, URIRef

def toRdflib(obj):
    """Convert the json result entry to rdfLib type."""
    try:
        type = obj["type"]
    except KeyError:
        raise ValueError("No type specified")

    if type == 'uri':
        return URIRef(obj["value"])
    elif type == 'literal':
        if "xml:lang" in obj:
            return Literal(obj["value"], lang=obj['xml:lang'])
        else:
            return Literal(obj["value"])
    elif type == 'typed-literal':
        return Literal(obj["value"], datatype=URIRef(obj['datatype']))
    elif type == 'bnode':
        return BNode(obj["value"])
    else:
        return None

