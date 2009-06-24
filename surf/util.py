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

import namespace as NS
import re
import new

pattern_direct = re.compile('^[a-z0-9]{1,}_[a-zA-Z0-9_]{1,}$', re.DOTALL)
pattern_inverse = re.compile('^is_[a-z0-9]{1,}_[a-zA-Z0-9_]{1,}_of$', re.DOTALL)

def namespace_split(uri):
    sp = '#' if '#' in uri else '/'
    base, predicate = uri.rsplit(sp,1)
    base = base+sp
    return NS.get_namespace(base)[1], predicate

def uri_split(uri):
    sp = '#' if '#' in uri else '/'
    base, predicate = uri.rsplit(sp,1)
    base = base+sp
    return NS.get_namespace(base)[0], predicate

def uri_to_classname(uri):
    ns_key, predicate = uri_split(uri)
    return '%s%s'%(ns_key.title().replace('-','_'),predicate)

def attr2rdf(attrname):
    def tordf(attrname):
        ns, predicate = attrname.split('_',1)
        ns = NS.get_namespace_url(ns)
        return ns[predicate] if ns!=None else None
    
    if pattern_inverse.match(attrname):
        return  tordf(attrname.replace('is_','').replace('_of','')), False
    elif pattern_direct.match(attrname):
        return  tordf(attrname), True
    return None, None

def rdf2attr(uri,direct):
    ns, predicate = uri_split(uri)
    attribute = '%s_%s'%(ns.lower(),predicate)
    return attribute if direct else 'is_%s_of'%attribute


def is_attr_direct(attrname):
    return True if pattern_direct.match(attrname) else False
    
def uri_to_class(uri):
    return new.classobj(str(uri_to_classname(uri)),(),{'uri':uri})


