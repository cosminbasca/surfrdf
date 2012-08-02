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
from surf.log import deprecation
from surf.util import LogMixin
import logging

__author__ = 'Cosmin Basca'


class Plugin(LogMixin):
    """
    Super class for all SuRF plugins, provides basic instantiation
    and `logging`.
    """

    def __init__(self, *args, **kwargs):
        super(Plugin, self).__init__()
        self.log_level = logging.NOTSET

        self.__inference = False

    def enable_logging(self, enable = True):
        """ Enables or disable `logging` for the current `plugin`. """
        #TODO: -------------------[remove in v1.2.0]------------------------
        deprecation('the enable_logging method will be removed in version 1.2.0, use the logging and log_level properties instead!')
        #TODO: -------------------[remove in v1.2.0]------------------------

        level = enable and logging.DEBUG or logging.NOTSET
        self.log.setLevel(level)

    def is_enable_logging(self):
        """ `True` if `logging` is enabled. """
        #TODO: -------------------[remove in v1.2.0]------------------------
        deprecation('the is_enabled_logging method will be removed in version 1.2.0, use the logging and log_level properties instead!')
        #TODO: -------------------[remove in v1.2.0]------------------------

        return (self.log.level == logging.DEBUG)

    def close(self):
        """ Close the `plugin` and free any resources it may hold. """

        pass

    def __set_inference(self, val):
        """ Setter method for the `inference` property.

        Do not use this method, use the `inference` property instead.

        """

        if not isinstance(val, bool):
            val = False
        
        self.__inference = val

    inference = property(fget = lambda self:self.__inference,
                         fset = __set_inference)
    """ Toggle `logical inference` on / off. The property has any effect
    only if such functionality is supported by the underlying data `store`. """
