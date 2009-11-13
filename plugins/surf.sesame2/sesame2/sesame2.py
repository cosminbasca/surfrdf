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

import httplib
import logging
from urllib import urlencode
from xml.dom.minidom import parseString, getDOMImplementation

from surf.rdf import BNode, ConjunctiveGraph, Graph, Literal, Namespace, URIRef

def parse_sparql_xml(response):
        def get_text(node):
            t = ""
            for n in node.childNodes:
                if n.nodeType == n.TEXT_NODE:
                    t += n.nodeValue
            return t
    
        def get_binding(node):
            cnt = None
            for cn in node.childNodes:
                if cn.nodeType == cn.ELEMENT_NODE:
                    cnt = cn
                    break
            if cnt:
                txt = get_text(cnt)
                if cnt.nodeName == 'uri':
                    return URIRef(txt)
                elif cnt.nodeName == 'literal':
                    return Literal(txt)
                elif cnt.nodeName == 'bnode':
                    return BNode(txt)
            else:
                return None
            
        #print 'response ,',response
        
        try:
            doc = parseString(response)
            head = doc.getElementsByTagName('head')[0]
            headers = []
            for h in head.childNodes:
                if h.nodeType == h.ELEMENT_NODE:
                    headers.append(h.getAttribute('name'))
            results = doc.getElementsByTagName('results')[0]
            res_list = []
            for result in results.childNodes:
                if result.nodeType == result.ELEMENT_NODE:
                    res = {}
                    for binding in result.childNodes:
                        if binding.nodeType == binding.ELEMENT_NODE:
                            res[binding.getAttribute('name')] = get_binding(binding)
                    res_list.append(res)
            return res_list
        except:
            print 'NOT XML Response: %s'%response
            return []
    
'''
represents an RDF Transaction object
'''
class RDFTransaction(object):
    mime                = 'application/x-rdftransaction'
    
    def __init__(self):
        impl = getDOMImplementation()
        self.transaction = impl.createDocument(None,'transaction',None)
        self.root = self.transaction.documentElement
    
    def _rdf_node(self,entity):
        node = None
        if type(entity) is URIRef:
            node = self.transaction.createElement('uri')
            node.appendChild(self.transaction.createTextNode(str(entity)))
        elif type(entity) is BNode:
            node = self.transaction.createElement('bnode')
            node.appendChild(self.transaction.createTextNode(str(entity)))
        elif type(entity) is Literal:
            node = self.transaction.createElement('literal')
            node.appendChild(self.transaction.createTextNode(str(entity)))
            if entity.lang:
                node.setAttribute('xml:lang',entity.lang)
            if entity.datatype:
                node.setAttribute('datatype',entity.datatype)
        return node
    
    def add_triple(self,s,p,o,context=None):
        try:
            node = self.transaction.createElement('add')
            node.appendChild(self._rdf_node(s))
            node.appendChild(self._rdf_node(p))
            node.appendChild(self._rdf_node(o))
            if context:
                node.appendChild(self.transaction.createTextNode(str(context)))
            self.root.appendChild(node)
        except:
            pass
    
    def add(self,graph,context=None):
        try:
            node = self.transaction.createElement('add')
            for s,p,o in graph:
                node.appendChild(self._rdf_node(s))
                node.appendChild(self._rdf_node(p))
                node.appendChild(self._rdf_node(o))
                if context:
                    node.appendChild(self.transaction.createTextNode(str(context)))
            self.root.appendChild(node)
        except:
            pass
    
    def remove(self,graph,context=None):
        try:
            node_name = 'removeFromNamedContext' if context else 'remove'
            node = self.transaction.createElement(node_name)
            for s,p,o in graph:
                node.appendChild(self._rdf_node(s))
                node.appendChild(self._rdf_node(p))
                node.appendChild(self._rdf_node(o))
                if context:
                    node.appendChild(self.transaction.createTextNode(str(context)))
            self.root.appendChild(node)
        except:
            pass
        
    def clear(self,context=None):
        node = self.transaction.createElement('clear')
        if context:
            node.appendChild(self.transaction.createTextNode(str(context)))
        self.root.appendChild(node)

    
    def add_namespace(self,**namespaces):
        for prefix in namespaces:
            node = self.transaction.createElement('setNamespace')
            node.setAttribute('prefix',prefix)
            node.setAttribute('name',str(namespaces[prefix]))
            self.root.appendChild(node)
    
    def remove_namespace(self,*namespaces):
        for prefix in namespaces:
            node = self.transaction.createElement('removeNamespace')
            node.setAttribute('prefix',prefix)
            self.root.appendChild(node)
        
    def __str__(self):
        self.xml()
    
    def xml(self):
        return self.transaction.toxml()
    

class Sesame2Exception(Exception):
    def __init__(self,response):
        self._response = response
    
    def __str__(self):
        return 'Sesame 2 exception, response = [%d, %s, %s]'%(self._response.status,self._response.reason,self._response.read())

class Sesame2(httplib.HTTPConnection):
    url = {
        'protocol'          : '/protocol',
        'repositories'      : '/repositories',
        'query'             : '/repositories/%(id)s',
        'contexts'          : '/repositories/%(id)s/contexts',
        'size'              : '/repositories/%(id)s/size',
        'namespaces'        : '/repositories/%(id)s/namespaces',
        'ud_namespace'      : '/repositories/%(id)s/namespaces/%(prefix)s',
        'statements'        : '/repositories/%(id)s/statements'
    }
    
    response_format = {
        'nt'        : 'application/rdf+ntriples',
        'xml'       : 'application/rdf+xml',
        'n3'        : 'text/rdf+n3',
        'turtle'    : 'application/x-turtle',
        'sparql'    : 'application/sparql-results+xml',
        'html'      : 'text/html',
        'text'      : 'text/plain'
    }
    
    request_format = {
        'nt'        : 'text/plain',
        'xml'       : 'application/rdf+xml',
        'n3'        : 'text/rdf+n3',
        'turtle'    : 'application/x-turtle',
        'sparql'    : 'application/sparql-results+xml',
        'html'      : 'text/html',
        'text'      : 'text/plain'
    }
    
    __sparql__ = {
        'SELECT'    : ['sparql','html'],
        'ASK'       : ['sparql','html'],
        'CONSTRUCT' : ['xml','n3'],
        'DESCRIBE'  : ['xml','n3']
    }
    
    def __init__(self,host,port=80,root_path='/sesame',strict=False):
        httplib.HTTPConnection.__init__(self,host,port,strict)
        self.root_path = root_path
    
    def __del__(self):
        self.close()
        
    def __deserialize(self,response):
        '''
        serializes the response based on the Content-Type or Accept header
        '''
        content_type = response.getheader('Content-type')
        content = response.read()
        
        format = 'text'
        for type in Sesame2.response_format:
            if Sesame2.response_format[type] == content_type:
                format = type
        ser_content = content
        if format in ['nt','xml','n3','turtle']:
            graph = ConjunctiveGraph()
            ser_content = graph.parse(data=content,format=format)
        elif format in ['sparql']:
            ser_content = parse_sparql_xml(content)
        return ser_content
    
    def sesame2_request(self,method,sesame2_method,sesame2_params={},body='',params={},headers={}):
        url = '%s%s'%(self.root_path,Sesame2.url[sesame2_method]%(sesame2_params))
        params = urlencode(params)
        #if method in ['GET','POST']:
        url = '%s?%s'%(url,params) if len(params) > 0 else url
        # does not work as specified ... 
        #elif method == 'POST':
        #    body = params
        #    headers['Content-type']='application/x-www-form-urlencoded'
        #print 'REQUEST = %s, %s, "%s", [%s]'%(method,url,body,str(headers))
        self.request(method,url,body,headers)
        response = self.getresponse()
        if response.status in [200,204]:
            return self.__deserialize(response)
        else:
            print response.read()
            raise Sesame2Exception(response)
    
    def protocol(self):
        protocol = self.sesame2_request('GET','protocol')
        return int(protocol)
    
    def repositories(self):
        repos = self.sesame2_request('GET','repositories')
        return repos
        
    def __query(self,id,query,infer=False,queryLn='SPARQL',limit=None,headers={}):
        params = {'queryLn':queryLn,
                  'infer':'true' if infer else 'false',
                  'query': query}
        if queryLn == 'Prolog' and limit and limit.isdigit():
            params['limit'] = limit
        results = self.sesame2_request('GET','query',{'id':str(id)},params = params, headers = headers)
        return results
    
    def prolog_query(self,id,query,infer=False,limit=None):
        return self.__query(id,query,infer=infer,queryLn='Prolog',limit=limit)
        
    def sparql_query(self,id,query,infer=False,format='sparql'):
        type = None
        if query.upper().find('SELECT ') != -1:
            type = 'SELECT'
        elif query.upper().find('ASK ') != -1:
            type = 'ASK'
        elif query.upper().find('CONSTRUCT ') != -1:
            type = 'CONSTRUCT'
        elif query.upper().find('DESCRIBE ') != -1:
            type = 'DESCRIBE'
        if type:
            format = format if format in Sesame2.__sparql__[type] else Sesame2.__sparql__[type][0]
            return self.__query(id,query,infer=infer,queryLn='SPARQL',
                                limit=None,headers={'Accept':Sesame2.request_format[format]})
        return None
    
    def contexts(self,id):
        ctx = self.sesame2_request('GET','contexts',{'id':str(id)})
        return ctx
        
    def size(self,id):
        size = self.sesame2_request('GET','size',{'id':str(id)})
        return int(size)

    def namespaces(self,id):
        ns = self.sesame2_request('GET','namespaces',{'id':str(id)})
        return ns
    
    def add_namespace(self,id,prefix,url):
        try:
            self.sesame2_request('PUT','ud_namespace',{'id':str(id), 'prefix':prefix},body = url)
        except Sesame2Exception:
            return False
        return True
        
    def remove_namespace(self,id,prefix):
        try:
            self.sesame2_request('DELETE','ud_namespace',{'id':str(id), 'prefix':prefix})
        except Sesame2Exception:
            return False
        return True
    
    def _param_stmt(self, params,s,p,o):
        if s:
            params['subj'] = s
        if p:
            params['pred'] = p
        if o:
            params['obj'] = o
        
    def statements(self,id,s=None,p=None,o=None,context=None,infer=False,format='xml'):
        format = format if format in ['nt', 'xml', 'n3', 'turtle'] else 'xml'
        params = {'infer':'true' if infer else 'false'}
        if context:
            params['context'] = context
        self._param_stmt(params,s,p,o)
        stmts = self.sesame2_request('GET','statements',{'id':id},
                                     params = params, headers={'Accept': Sesame2.request_format[format]})
        return stmts
    
    def remove_statements(self,id,s=None,p=None,o=None,context=None):
        params = {}
        if context:
            params['context'] = context
        self._param_stmt(params,s,p,o)
        try:
            self.sesame2_request('DELETE','statements',{'id':id},params = params)
        except Sesame2Exception:
            return False
        return True
    
    def remove_all_statements(self,id):
        return self.remove_statements(id)
    
    def add_statements(self,id,rdf_data=None,context=None,baseURI=None,saveStrings=False,update=True,content_type='xml'):
        # POST = ADD, PUT = Replace All contents of triplestore
        method = 'POST' if update else 'PUT'
        params = {}
        if context:
            params['context'] = context
        if content_type == 'xml' and baseURI:
            params['baseURI'] = baseURI
        if content_type == 'nt':
            params['saveStrings'] = saveStrings
        
        try:
            response = self.sesame2_request(method,'statements',{'id':id}, body = rdf_data,
                                        params = params,
                                        headers = {'Content-type': Sesame2.request_format[content_type]})
        except Sesame2Exception,e:
            return False
        return True
    
    def transaction(self,id,rdf_transaction):
        try:
            response = self.sesame2_request('POST','statements',{'id':id}, body = rdf_transaction.xml(),
                                        headers = {'Content-type': RDFTransaction.mime})
        except Sesame2Exception,e:
            return False
        return True
    
if __name__ == '__main__':
    allegro = Sesame2('localhost',5678,'/sesame')
     
    
    print 'Protocol : ',allegro.protocol()
    print 'Repositories : ',allegro.repositories()
    '''
    print 'Add ns : ',allegro.add_namespace(1,'foaf','http://xmlns.com/foaf/0.1/')
    print 'Namespaces : ',allegro.namespaces(1)
    #print 'Remove ns : ',allegro.remove_namespace(1,'foaf')
    #print 'Namespaces : ',allegro.namespaces(1)
    #print 'Contexts : ',allegro.contexts(1)
    print 'Size : ',allegro.size(1),' triples'
    print 'QUERY : ',allegro.sparql_query(1,'SELECT ?s WHERE {?s <http://xmlns.com/foaf/0.1/name> "Edd Dumbill".}')
    #print 'TRIPLES : ',allegro.statements(1,p='<http://xmlns.com/foaf/0.1/name>',format='xml')
    # other formats from xml seem not be parsable
    print 'TRIPLES 2 : ',allegro.statements(1,s='<file://c:/Temp/foaf.rdf#edd>',format='xml')
    print '---------------'
    print 'QUERY2 : ',allegro.sparql_query(1,'SELECT ?s WHERE {?s <http://xmlns.com/foaf/0.1/name> "Cosmin".}')
    print 'ADD "Cosmin" : ',allegro.add_statements(1,'<http://domeniu.ro/personal#cosmin> <http://xmlns.com/foaf/0.1/name> "Cosmin"', content_type='nt')
    '''
    
    #print 'ADD : ',allegro.add_statements(1,'''<http://t/cosmin>  <http://t/is> <http://xmlns.com/foaf/0.1/Person>
    #                                      <http://t/cosmin> <http://t/worksFor> <http://t/DERI>
    #                                      <http://t/DERI> <http://t/in> "GALWAY"
    #                                      ''',content_type='nt')
    #
    #print 'RESULTS : ',allegro.sparql_query(1,'''
    #                                        SELECT ?s WHERE
    #                                        {
    #                                            ?s <http://t/is> <http://xmlns.com/foaf/0.1/Person>.
    #                                            ?s <http://t/worksFor> ?c.
    #                                            ?c <http://t/in> "GALWAY".
    #                                        }
    #                                        ''',infer=True)