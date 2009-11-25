# Copyright (c) 2009, Digital Enterprise Research Institute (DERI),
# NUI Galway
# All rights reserved.

# author: Cosmin Basca
# email: cosmin.basca@gmail.com

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer
#      in the documentation and/or other materials provided with
#      the distribution.
#    * Neither the name of DERI nor the
#      names of its contributors may be used to endorse or promote  
#      products derived from this software without specific prior
#      written permission.

# THIS SOFTWARE IS PROVIDED BY DERI ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DERI BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

# -*- coding: utf-8 -*-
__author__ = 'Cosmin Basca'

try:
    from franz.openrdf.model.value import URI as fURIRef
    from franz.openrdf.model.value import BNode as fBNode
    from franz.openrdf.model.literal import Literal as fLiteral
    
    from surf.rdf import BNode, Literal, URIRef
    
    '''
    helper functions that convert between rdflib concepts and sesame2 api concepts
    '''
    
    # TERMS
    def toRdfLib(term):
        if type(term) is fURIRef:
            return URIRef(term.getURI())
        elif type(term) is fLiteral:
            try:
                if term.getDatatype():
                    dtype = term.getDatatype().getURI()
                    if dtype.startswith('<') and dtype.endswith('>'):
                        dtype = dtype.strip('<>')
                        dtype = URIRef(dtype)
                    else:
                        dtype = URIRef(dtype)
                    
                    return Literal(term.getLabel(), lang=term.getLanguage(),
                                   datatype=dtype)
                    
            except Exception, e:
                print e
        elif type(term) is fBNode:
            return BNode(term.getID())
        elif type(term) in [list,tuple]:
            return map(toRdfLib, term)
        return term
    
    def toSesame(term,factory):
        if type(term) is URIRef:
            return factory.createURI(str(term))
        elif type(term) is Literal:
            return factory.createLiteral(str(term),datatype=term.datatype,language=term.language)
        elif type(term) is BNode:
            return factory.createBNode(str(term))
        elif type(term) in [list, tuple]:
            return map(lambda item: toSesame(item,factory), term)
        return term
    
    
    # STATEMENTS
    def toStatement((s,p,o),factory,context=None):
        return factory.createStatement(s,p,o,context)
        
    def toTuple(statement):
        return (statement.getSubject(),statement.getPredicate(),statement.getObject(),statement.getContext())
except ImportError, e:
    print 'franz libraries not installed ',e
    def toRdfLib(term):
        pass

    def toSesame(term, factory):
        pass

    def toStatement((s,p,o),factory,context = None):
        pass

    def toTuple(statement):
        pass 
    