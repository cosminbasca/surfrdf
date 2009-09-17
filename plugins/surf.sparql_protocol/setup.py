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
"""
SuRF plugin

Support for the SPARQL HTTP Protocol

to develop run the folowing command:
python setup.py develop -d .. -m
"""
from setuptools import setup

setup(
    name='surf.sparql_protocol',
    version='0.3.1',
    description='surf SPARQL protocol plugin',
    long_description = 'provides access to SPARQL protocol endpoints',
    license = 'New BSD SOFTWARE', 
    author="Cosmin Basca",
    author_email="cosmin.basca at google.com",
    url = 'http://code.google.com/p/surfrdf/',
    #download_url = 'http://surfrdf.googlecode.com/files/SuRF-0.4-py2.5.egg',
    platforms = ['any'], #Should be removed by PEP  314
    requires=['simplejson'], # Used by distutils to create metadata PKG-INFO
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 2.5',
    ],
    keywords = 'python SPARQL RDF resource mapper',
    requires_python = '>=2.5', # Future in PEP 345
    packages=['sparql_protocol'],
    install_requires=['surf>=0.6.0',
                      'sparqlwrapper==1.3.1',],
    entry_points={
    'surf.plugins.reader': 'sparql_protocol = sparql_protocol.reader:ReaderPlugin',
    'surf.plugins.writer': 'sparql_protocol = sparql_protocol.writer:WriterPlugin',
    }
)