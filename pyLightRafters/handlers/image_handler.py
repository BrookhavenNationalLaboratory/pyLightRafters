from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six

from ..handler_base import ImageSource, SingleFileHandler, require_active

try:
    from scipy.misc import imread
except ImportError:
    imread = None


class scipy_imread_Handler(SingleFileHandler, ImageSource):
    @classmethod
    def available(cls):
        # if we can't import scipy, not available
        return (imread is not None and
                super(scipy_imread_Handler, cls).available())

    _extension_filters = {'png', 'jpg',
                          'jpeg', 'tiff',
                          'bnp'} | SingleFileHandler._extension_filters

    def __init__(self, fname):
        # don't need to do anything but pass up the MRO
        super(scipy_imread_Handler, self).__init__(fname=fname)

    def __len__(self):
        # TODO make this not hard-coded
        return 1

    def activate(self):
        # pass up the mro stack to make sure the active flag gets flipped
        super(scipy_imread_Handler, self).activate()
        self._cache = imread(self._fname)

    @require_active
    def get_frame(self, n):
        if n != 0:
            raise NotImplementedError("multi-plane not implemented yet")
        return self._cache
