"""
A set of sources and sinks for handling
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six

from ..handler_base import (ImageSource, SingleFileHandler, require_active)
from ..extern import tifffile


class tifffile_read_Handler(SingleFileHandler, ImageSource):
    # this list should probably be expanded
    _extension_filters = {'tif', 'tiff', 'stk',
                          } | SingleFileHandler._extension_filters

    def __init__(self, fname):
        # don't need to do anything but pass up the MRO
        super(tifffile_read_Handler, self).__init__(fname=fname)

    @require_active
    def __len__(self):
        # TODO make this not hard-coded
        return len(self._tifffile)

    def activate(self):
        # pass up the mro stack to make sure the active flag gets flipped
        super(tifffile_read_Handler, self).activate()
        self._tifffile = tifffile.TiffFile(self.backing_file)

    @require_active
    def get_frame(self, n):
        return self._tifffile[n].ararray()

    def deactivate(self):
        if not self.activate:
            # no need to deactivate an inactive handler
            return
        # close the open TiffFile object
        self._tifffile.close()
        # delete TiffFile object
        del self._tifffile
        super(tifffile_read_Handler, self).deactivate()
