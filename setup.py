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
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import setup, find_packages


__author__ = 'Cosmin Basca'

NAME = 'surf'
PY2 = sys.version_info[0] == 2

str_version = None
if PY2:
    execfile('{0}/__version__.py'.format(NAME))
else:
    exec(open('{0}/__version__.py'.format(NAME)).read())

# Load up the description from README
with open('README.rst') as f:
    DESCRIPTION = f.read()

with open('CHANGELOG.rst') as f:
    LONG_DESCRIPTION = '{0}\n{1}'.format(DESCRIPTION, f.read())

deps = [
    'rdflib>=4.2.1',
    'SPARQLWrapper>=1.7.6',
]

test_deps = [
    'pytest>=2.9.1',
    'pytest-ordering>=0.4'
]

setup(
    name='SuRF',
    version=str_version,
    description='Object RDF Mapper',
    long_description=LONG_DESCRIPTION,
    license='New BSD SOFTWARE',
    author='Cosmin Basca',
    author_email='cosmin.basca at google.com',
    url='http://code.google.com/p/surfrdf/',
    download_url='http://pypi.python.org/pypi/SuRF/',
    platforms=['any'],
    packages=find_packages(exclude=['surf.test']),
    install_requires=deps,
    tests_require=deps + test_deps,
    test_suite='surf.test',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='Python SPARQL RDF resource mapper ORM query Semantic Web RDFS rdflib Object-Oriented',
)
