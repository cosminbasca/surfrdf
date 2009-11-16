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

from simplejson import dumps

from surf.rdf import BNode, Literal, URIRef

def to_json(graph):
    '''
    serializes a `rdflib` `Graph` or `ConjunctiveGraph` to **JSON** according to
    the specification of rdf-json for further details please see the following:
        http://n2.talis.com/wiki/RDF_JSON_Specification
    '''
    value_types = {URIRef:'uri',Literal:'literal',BNode:'bnode'}

    json_root = {}
    subjects = []
    # group subjects
    for s in graph.subjects():
        if s not in subjects:
            subjects.append(s)

    for s in subjects:
        json_subjects = {}
        predicates = []
        # group predicates
        for p in graph.predicates(s):
            if p not in predicates:
                predicates.append(p)

        for p in predicates:
            json_values = []

            for v in graph.objects(s,p):
                value = {}
                value['value'] = v
                value['type'] = value_types[type(v)]
                if type(v) is Literal and v.language:
                    value['lang'] = str(v.language)
                if type(v) is Literal and v.datatype:
                    value['datatype'] = str(v.datatype)

                json_values.append(value)
            json_subjects[str(p)] = json_values
        json_root[str(s)] = json_subjects

    return dumps(json_root)