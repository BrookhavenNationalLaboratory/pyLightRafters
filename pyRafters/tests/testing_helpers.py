from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from six.moves import range
import tempfile
import os
from functools import wraps


def namedtmpfile(suffix, n=1):
    def outer(fun):
        @wraps(fun)
        def inner():
            fnames = []
            for j in range(n):
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                fnames.append(tmp.name)
                tmp.close()
            try:
                fun(*fnames)
            finally:
                for fname in fnames:
                    os.remove(fname)
        return inner
    return outer
