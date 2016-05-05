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
__author__ = 'Cosmin Basca'

LOGGER_NAME = 'surf'

_logger = None

DISABLED = 100
CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0


def debug(msg, *args):
    if __debug__:
        if _logger:
            _logger.log(DEBUG, msg, *args)


def info(msg, *args):
    if _logger:
        _logger.log(INFO, msg, *args)


def warn(msg, *args):
    if _logger:
        _logger.log(WARNING, msg, *args)


def error(msg, *args):
    if _logger:
        _logger.log(ERROR, msg, *args)


def get_logger(name=LOGGER_NAME, handler=None):
    import logging

    LOG_FORMAT = '%(asctime)s %(levelname)-8s %(name)-7s %(message)s'
    logging._acquireLock()
    try:
        # general setup
        formatter = logging.Formatter(LOG_FORMAT)

        if not handler:
            handler = [logging.StreamHandler()]
        elif not isinstance(handler, (list, tuple)):
            handler = [handler]

        logger = logging.getLogger(name)
        logger.propagate = 0
        for hndlr in handler:
            hndlr.setFormatter(formatter)
            logger.addHandler(hndlr)
    finally:
        logging._releaseLock()

    return logger


def setup_logger(name=LOGGER_NAME, handler=None):
    global _logger
    _logger = get_logger(name=name, handler=handler)


def uninstall_logger():
    global _logger
    _logger = None


def set_logger(logger):
    global _logger
    if logger:
        _logger = logger


def set_logger_level(level, name=None):
    import logging

    logging._acquireLock()
    try:
        logger = logging.getLogger(name) if name else logging.root
        if isinstance(level, basestring):
            level = level.upper()
        logger.setLevel(level)
    finally:
        logging._releaseLock()


def disable_logger(name=None):
    set_logger_level(DISABLED, name=name)
