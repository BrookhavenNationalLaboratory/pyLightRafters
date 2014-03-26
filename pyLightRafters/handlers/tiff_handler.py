"""
A set of sources and sinks for handling
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six

from ..handler_base import (ImageSource, SingleFileHandler,
                            require_active, VolumeSource, FrameSink)
from ..extern import tifffile


class _tifffile_read_Handler(SingleFileHandler):
    # this list should probably be expanded
    _extension_filters = {'tif', 'tiff', 'stk',
                          } | SingleFileHandler._extension_filters

    def __init__(self, fname, resolution=None, resolution_units=None):
        # don't need to do anything but pass up the MRO
        super(_tifffile_read_Handler, self).__init__(fname=fname,
                                            resolution_units=resolution_units,
                                            resolution=resolution)

    def activate(self):
        # pass up the mro stack to make sure the active flag gets flipped
        super(_tifffile_read_Handler, self).activate()
        self._tifffile = tifffile.TiffFile(self.backing_file)

    def deactivate(self):
        if not self.activate:
            # no need to deactivate an inactive handler
            return
        # close the open TiffFile object
        self._tifffile.close()
        # delete TiffFile object
        del self._tifffile
        super(_tifffile_read_Handler, self).deactivate()


class tifffile_read2D_Handler(_tifffile_read_Handler, ImageSource):
    # this list should probably be expanded
    @require_active
    def get_frame(self, n):
        return self._tifffile[n].asarray()

    @require_active
    def __len__(self):
        return len(self._tifffile)


class tifffile_read3D_Handler(_tifffile_read_Handler, VolumeSource):
    # this list should probably be expanded
    @require_active
    def get_frame(self, n):
        return self._tifffile.asarray()

    @require_active
    def __len__(self):
        return 1


class tifffile_Sink(SingleFileHandler, FrameSink):
    def __init__(self, fname, resolution=None, resolution_units=None):
        super(tifffile_Sink, self).__init__(fname=fname,
                                            resolution_units=resolution_units,
                                            resolution=resolution)

    @require_active
    def record_frame(self, img, frame_number, frame_md=None):
        if frame_number != 0:
            raise NotImplementedError("have not written this code yet")
        tifffile.imsave(self.backing_file, img)

    def set_metadata(self, md_dict):
        raise NotImplementedError("have not done this yet")
