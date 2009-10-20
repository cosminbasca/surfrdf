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

#try:
#    from setuptools import setup, find_packages
#except ImportError:
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
      name='SuRF',
      version='0.99.0',
      description='Object RDF Resource Mapper',
      long_description = 'This is RDF Resource Mapper to python objects, allows one to connect to various triple stores or arbitrary SPARQL endpoints. It is inspired by the work on ActiveRDF for ruby',
      license = 'New BSD SOFTWARE', 
      author="Cosmin Basca",
      author_email="cosmin.basca at google.com",
      url = 'http://code.google.com/p/surfrdf/',
      #download_url = 'http://surfrdf.googlecode.com/files/SuRF-0.4-py2.5.egg',
      platforms = ['any'], #Should be removed by PEP  314
      packages=find_packages(exclude=['ez_setup']),
      requires=['simplejson'], # Used by distutils to create metadata PKG-INFO
      install_requires=['rdflib>=2.4.2',
                        'simplejson==2.0.9',], #Used by setuptools to install the dependencies
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
      ],
      keywords = 'python SPARQL RDF resource mapper',
      requires_python = '>=2.5', # Future in PEP 345
      scripts = ['ez_setup.py']
)