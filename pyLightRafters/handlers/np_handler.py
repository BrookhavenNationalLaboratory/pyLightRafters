"""
A set of sources and sinks for handling in-memory nparrays
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from six.moves import range
import numpy as np

from ..handler_base import (DistributionSource, DistributionSink, require_active,
                            ImageSource, ImageSink, FrameSource)


class np_dist_source(DistributionSource):
    """
    A source for reading distribution data out of csv (or tab or what ever)
    separated files.
    """

    # local stuff
    def __init__(self, edges, vals):
        """
        Wrapper for in-memory work

        Parameters
        ----------
        edges : nparray
            The bin edges

        vals : nparray
            The bin values
        """
        # base stuff
        super(np_dist_source, self).__init__()
        # np stuff, make local copies
        self._edges = np.array(edges)
        self._vals = np.array(vals)
        # sanity checks
        if self._edges.ndim != 1:
            raise ValueError("edges must be 1D")
        if self._vals.ndim != 1:
            raise ValueError("vals must be 1D")

        # distribution stuff
        if (len(edges) - 1)  == len(vals):
            self._right = True
        else:
            raise ValueError("the length of `edges` must be " +
                "one greater than the length of the vals. " +
                "Not len(edges): {el} and len(vals): {vl}".format(
                    el=len(edges), vl=len(vals)))

    @require_active
    def values(self):
        return self._vals

    @require_active
    def bin_edges(self):
        return self._edges

    @require_active
    def bin_centers(self):
        return self._edges[:-1] + np.diff(self._edges)

    @property
    def kwarg_dict(self):
        md = super(np_dist_source, self).kwarg_dict
        md.update({'edges': self._edges,
                    'vals': self._vals})
        return md


class np_dist_sink(DistributionSink):
    """
    A sink for writing distribution data to memory
    """
    def __init__(self):
        # base stuff
        super(np_dist_sink, self).__init__()
        self._vals = None
        self._edges = None

    # np parts
    @require_active
    def write_dist(self, edges, vals, right_edge=False):
        self._edges = np.array(edges)
        self._vals = np.array(vals)

    @property
    def kwarg_dict(self):
        return super(np_dist_sink, self).kwarg_dict

    def make_source(self, klass=None):
        if klass is None:
            klass = np_dist_source
        else:
            raise NotImplementedError("have not implemented class selection")

        return klass(self._edges, self._vals)


_dim_err = ("wrong dimensions, data_array should have ndim = {fd} " +
             "or {fdp1}, not {ndim}")


class np_frame_source(FrameSource):
    """
    A source backed by a numpy arrays for in-memory image work

    """
    def __init__(self, data_array, frame_dim, meta_data=None,
                 frame_meta_data=None, resolution=None,
                 resolution_units=None):
        """
        Parameters
        ----------

        data_array : ndarray
            The image stack

        meta_data : dict or None
        """
        super(np_frame_source, self).__init__(resolution=resolution,
                                        resolution_units=resolution_units)
        # make a copy of the data
        data_array = np.array(data_array)
        # if have a non-sensible number of dimensions raise
        if data_array.ndims < frame_dim or data_array.ndims > frame_dim + 1:
            raise ValueError(_dim_err.format(fd=frame_dim,
                                            fdp1=frame_dim+1,
                                            ndim=data_array.ndim))
        # if only one frame, upcast dimensions
        elif data_array.ndims == frame_dim:
            data_array.shape = (1, ) + data_array.shape

        # save the data
        self._data = data_array

        # keep a copy of the length
        self._len = data_array.shape[0]

        # deal with set-level meta-data
        if meta_data is None:
            meta_data = dict()

        self._meta_data = meta_data

        if frame_meta_data is None:
            frame_meta_data = [dict() for _ in xrange(self._len)]

        if len(frame_meta_data) != self._len:
            raise ValueError(("number of frames and number of" +
                             " md dicts must match"))

        self._frame_meta_data = frame_meta_data

    def len(self):
        return self._len

    @require_active
    def get_frame(self, n):
        # make a copy of the array before handing it out so we don't get
        # odd in-place operation bugs
        return np.array(self._data[n])

    def get_frame_metadata(self, frame_num, key):
        return self._frame_meta_data[frame_num][key]

    def get_metadata(self, key):
        return self._meta_data[key]

    @require_active
    def __iter__(self):
        # leverage the numpy iterable
        return iter(self._data)

    @require_active
    def __getitem__(self, arg):
        # leverage the numpy slicing magic
        return self._data[arg]

    def kwarg_dict(self):
        dd = super(np_frame_source, self).kwarg_dict
        dd.update({'data_array': self._data,
                   'frame_dim': self._data.ndim - 1,
                   'meta_data': self._meta_data,
                   'frame_meta_data': self._frame_meta_data})
        return dd
