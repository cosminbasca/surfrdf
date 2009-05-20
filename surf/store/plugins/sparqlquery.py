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

from rdf.graph import Graph, ConjunctiveGraph
from rdf.term import URIRef, Literal, BNode, RDF, RDFS
from rdf.namespace import Namespace
from surf.query import Query

'''
translates Query instances to SPARQL strings
'''

__all__ = ['translate']

def translate(q):
    if type(q) is not Query:
        raise Exception('Invalid parameter type, must be a Query instance')
    return __translate(q)

def __tosparql(term):
    if type(term) in [URIRef,BNode]:
        return '%s'%(term.n3())
    elif type(term) in [str, unicode]: # also accomodate SPARQL variables represented as strings but starting with '?'
        return '%s'%term if term.startswith('?') else '"%s"'%term
    elif type(term) is Literal:
        return term.n3()
    elif type(term) in [list,tuple]:
        return '"%s"@%s'%(term[0],term[1])
    elif type(term) is type and hasattr(term, 'uri'):
        return '%s'%term.uri().n3()
    elif hasattr(term, 'subject'):
        return '%s'%term.subject().n3()
    return term.__str__()

def __filter(filter):
    return ' FILTER %(filter)s '%({'filter':filter}) if filter and filter.strip() != '' else ''

def __pattern((s,p,o,optional,filter)):
    ptrn = ' OPTIONAL {%(ptrn)s}' if optional else '%(ptrn)s'
    _ptrn = ' %(s)s %(p)s %(o)s. %(filter)s '%({'s':__tosparql(s),
                                               'p':__tosparql(p),
                                               'o':__tosparql(o),
                                               'filter':__filter(filter)})
    return ptrn%({'ptrn':_ptrn})

def __basic_pattern((s,p,o)):
    ptrn = '%(ptrn)s'
    _ptrn = ' %(s)s %(p)s %(o)s. '%({'s':__tosparql(s),
                                    'p':__tosparql(p),
                                    'o':__tosparql(o),
                                    })
    return ptrn%({'ptrn':_ptrn}) 
   
def __translate(q):
    s = ''
    if q.query_type not in ['select','construct','ask','describe']:
        raise InvalidTypeQueryException('Unsupported sparql query type ')
    
    if q.query_type in ['select','construct','describe']:
        # the select clauses
        _select = ' '.join([var for var in q.select_clauses])
        _distinct = ' '.join([var for var in q.distinct_clauses])
        s = '%(type)s %(select)s DISTINCT %(distinct)s'%({'type':q.query_type.upper(),
                                                 'select':_select,
                                                 'distinct':_distinct})
        # the where clauses
        _patterns = ''
        _graphs = {}
        
        for ctx in q.where_clauses:
            _graphs[ctx] = ''.join([__pattern(ptrn) for ptrn in q.where_clauses[ctx]])
        for ctx in q.filter_clauses:
            _graphs[ctx]+= ' '.join(__filter(filter) for filter in q.filter_clauses)
        
        for ctx in _graphs:
            g = ' GRAPH %(ctx)s { %(ptrn)s } ' if ctx else ' { %(ptrn)s } '
            _patterns += g%({'ctx':ctx,
                            'ptrn':_graphs[ctx]})
        
        s += ' WHERE { %(patterns)s }'%({'patterns':_patterns})
        if q.limit_value != None and str.isdigit(str(q.limit_value)):
            s += ' LIMIT %d '%(q.limit_value)
        if q.offset_value != None and str.isdigit(str(q.offset_value)):
            s += ' OFFSET %d '%(q.offset_value)
        
    elif q.query_type == 'ask':
        s = '%(type)s '%({'type':q.query_type.upper()})
        
        _patterns = ''
        _graphs = {}
        
        for ctx in q.ask_clauses:
            _graphs[ctx] = ''.join([__basic_pattern(ptrn) for ptrn in q.ask_clauses[ctx]])
        
        for ctx in _graphs:
            g = ' GRAPH %(ctx)s { %(ptrn)s } ' if ctx else ' { %(ptrn)s } '
            _patterns += g%({'ctx':ctx,
                            'ptrn':_graphs[ctx]})
        
        s += ' { %(patterns)s }'%({'patterns':_patterns})
        
    return s