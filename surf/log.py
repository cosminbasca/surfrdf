# Copyright (c) 2012, University of Zurich,
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
#    * Neither the name of University of Zurich nor the
#      names of its contributors may be used to endorse or promote
#      products derived from this software without specific prior
#      written permission.

# THIS SOFTWARE IS PROVIDED BY UNIVERSITY OF ZURICH ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UNIVERSITY OF ZURICH BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import warnings
import logging

__author__ = 'Cosmin Basca'


__levels__ = {
    'debug'     :logging.DEBUG,
    'info'      :logging.INFO,
    'warning'   :logging.WARNING,
    'error'     :logging.ERROR,
    'critical'  :logging.CRITICAL,
}

surf_logger     = logging.getLogger('surf')
surf_logger.addHandler(logging.StreamHandler())
surf_logger.setLevel(logging.NOTSET)

# enable deprecation warnings to show up
#TODO: turn off when no more deprecated functions are in use!
warnings.simplefilter('always')

logging.root.disabled = True

def set_loglevel(level='info'):
    global surf_logger
    if isinstance(level, basestring):
        surf_logger.setLevel(__levels__.get(level, 'info'))
    else:
        surf_logger.setLevel(level)

def enable_root_logger():
    logging.root.disabled = False

def disable_root_logger():
    logging.root.disabled = True

def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used.

    the function is included *as is* from:
    http://code.activestate.com/recipes/391367/"""
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc