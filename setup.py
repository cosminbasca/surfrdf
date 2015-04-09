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

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
from sys import version_info

def is_python(major=2, minor=5):
    return tuple(version_info)[0:2] == (major,minor)

execfile('surf/__version__.py')

py25_install_requires = ['simplejson>=2.6.1'] if is_python(2,5) else []

setup(
      name              = 'SuRF',
      version           = get_version(full=False),
      description       = 'Object RDF Mapper',
      long_description  = open('README.txt').read() + open('NEWS.txt').read(),
      license           = 'New BSD SOFTWARE',
      author            = 'Cosmin Basca',
      author_email      = 'cosmin.basca at google.com',
      url               = 'http://code.google.com/p/surfrdf/',
      download_url      = 'http://pypi.python.org/pypi/SuRF/',
      platforms         = ['any'],
      #packages          = ['surf'],
      packages          = find_packages(exclude=['surf.test']),
      requires          = ['simplejson'] if is_python(2,5) else [],
      install_requires  = [
                              'rdflib>=3.2.1',
#                              'nose>=1.1.2',    # nosetests for testing
#                              'rednose>=0.2.5'  # a bit of coloring for nosetests
                          ] + py25_install_requires,
      tests_require     = ['surf.rdflib'],
      test_suite        = 'surf.test',
      classifiers       = [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords          = 'Python SPARQL RDF resource mapper ORM query Semantic Web RDFS rdflib Object-Oriented',
      scripts           = ['ez_setup.py']
)
