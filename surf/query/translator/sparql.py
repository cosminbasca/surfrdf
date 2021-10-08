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
from surf.query.translator import QueryTranslator
from surf.query import Query, SELECT, ASK, DESCRIBE, CONSTRUCT, Group
from surf.query import NamedGroup, OptionalGroup, Union, Filter
from surf.rdf import BNode, Literal, URIRef
from surf.util import is_uri

__author__ = 'Cosmin Basca'

#TODO: move the translators in the future in a pluggable architecture

class SparqlTranslator(QueryTranslator):
    '''translates a query to SPARQL'''

    def translate(self):
        if self.query.query_type in [SELECT, DESCRIBE]:
            return self._translate(self.query)
        elif self.query.query_type == ASK:
            return self._translate_ask(self.query)

    def _translate(self, query):

        query_type = "SELECT"
        if query.query_type == DESCRIBE:
            query_type = "DESCRIBE"

        rep = u'%(query_type)s %(modifier)s %(vars)s %(from_)s %(from_named)s WHERE { %(where)s } %(order_by)s %(limit)s %(offset)s '
        modifier = query.query_modifier and query.query_modifier.upper() or ''
        limit = query.query_limit and ' LIMIT %d ' % (query.query_limit) or ''
        offset = query.query_offset and ' OFFSET %d ' % (query.query_offset) or ''        
        where = '. '.join([self._statement(stmt) for stmt in self.query.query_data])
        vars = ' '.join([var for var in query.query_vars])
        from_ = ' '.join([ "FROM <%s>" % uri for uri in query.query_from])
        from_named = ' '.join([ "FROM NAMED <%s>" % uri for uri in query.query_from_named])
        if len(self.query.query_order_by) > 0:
            order_by = ' ORDER BY %s' % (' '.join([var for var in self.query.query_order_by]))
        else:
            order_by = ''

        return rep % ({'query_type'   : query_type,
                     'modifier'     : modifier,
                     'vars'         : vars,
                     'from_'        : from_,
                     'from_named'   : from_named,
                     'where'        : where,
                     'limit'        : limit,
                     'offset'       : offset,
                     'order_by'     : order_by, })

    def _translate_ask(self, query):
        rep = u'ASK %(from_)s %(from_named)s { %(where)s }'
        from_ = ' '.join([ "FROM <%s>" % uri for uri in query.query_from])
        from_named = ' '.join([ "FROM NAMED <%s>" % uri for uri in query.query_from_named])
        where = '. '.join([self._statement(stmt) for stmt in self.query.query_data])
        return rep % ({'from_'        : from_,
                     'from_named'   : from_named,
                     'where'        : where, })

    def _term(self, term):
        if isinstance(term, (URIRef, BNode)):
            return '%s' % (term.n3())
        elif isinstance(term, str):
            if term.startswith('?'):
                return '%s' % term
            elif is_uri(term):
                return '<%s>' % term
            else:
                return '"%s"' % term
        elif type(term) is Literal:
            return term.n3()
        elif isinstance(term, (list, tuple)):
            return '"%s"@%s' % (term[0], term[1])
        elif type(term) is type and hasattr(term, 'uri'):
            return '%s' % term.uri().n3()
        elif hasattr(term, 'subject'):
            return '%s' % term.subject.n3()
        return term.__str__()

    def _triple_pattern(self, statement):
        return ' %(s)s %(p)s %(o)s ' % ({'s':self._term(statement[0]),
                                        'p':self._term(statement[1]),
                                        'o':self._term(statement[2])})

    def _group(self, g):
        return ' { %s } ' % ('. '.join([self._statement(stmt) for stmt in g]))

    def _named_group(self, g):
        return ' GRAPH %(name)s { %(pattern)s } ' % ({'name':self._term(g.name),
                                                    'pattern': '. '.join([self._statement(stmt) for stmt in g])})

    def _optional_group(self, g):
        return ' OPTIONAL {%s} ' % ('. '.join([self._statement(stmt) for stmt in g]))

    def _union(self, g):
        return ' UNION '.join(['{ %s }' % self._statement(stmt) for stmt in g])

    def _filter(self, stmt):
        return ' FILTER %s ' % (stmt)

    def _subquery(self, stmt):
        return ' { %s } ' % (SparqlTranslator(stmt).translate())

    def _statement(self, statement):
        if type(statement) is Group:
            return self._group(statement)
        elif type(statement) is NamedGroup:
            return self._named_group(statement)
        elif type(statement) is OptionalGroup:
            return self._optional_group(statement)
        elif type(statement) is Union:
            return self._union(statement)
        elif type(statement) is Filter:
            return self._filter(statement)
        elif type(statement) is Query:
            return self._subquery(statement)
        elif isinstance(statement, (list, tuple)):
            # Moved this at the bottom because other classes are list/tuple desc
            return self._triple_pattern(statement)
