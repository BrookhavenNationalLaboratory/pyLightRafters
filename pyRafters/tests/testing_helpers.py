from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
import tempfile
import os
from functools import wraps


def namedtmpfile(suffix):
    def outer(fun):
        @wraps(fun)
        def inner():
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            fname = tmp.name
            tmp.close()
            try:
                fun(fname)
            finally:
                os.remove(fname)
        return inner
    return outer
