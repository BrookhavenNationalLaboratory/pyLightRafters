"""
A set of sources and sinks for handling in-memory nparrays
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from six.moves import range
import numpy as np

from ..handler_base import (DistributionSource, DistributionSink,
                            require_active, ImageSink,
                            ImageSource, FrameSink, FrameSource)


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
    def __init__(self, data_array=None, frame_dim=None, meta_data=None,
                 frame_meta_data=None, *args, **kwargs):
        """
        Parameters
        ----------

        data_array : ndarray
            The image stack

        meta_data : dict or None
        """
        super(np_frame_source, self).__init__(*args, **kwargs)
        if data_array is None:
            raise ValueError("data_array must be not-None")

        # make a copy of the data
        data_array = np.array(data_array)
        if frame_dim is None:
            frame_dim = data_array.ndim - 1

        # if have a non-sensible number of dimensions raise
        if data_array.ndim < frame_dim or data_array.ndim > frame_dim + 1:
            raise ValueError(_dim_err.format(fd=frame_dim,
                                            fdp1=frame_dim+1,
                                            ndim=data_array.ndim))
        # if only one frame, upcast dimensions
        elif data_array.ndim == frame_dim:
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
            frame_meta_data = [dict() for _ in range(self._len)]

        if len(frame_meta_data) != self._len:
            raise ValueError(("number of frames and number of" +
                             " md dicts must match"))

        self._frame_meta_data = frame_meta_data

    def __len__(self):
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


class NPImageSource(np_frame_source, ImageSource):
    def __init__(self, *args, **kwargs):
        ndim = kwargs.pop('frame_dim', 2)
        if ndim != 2:
            raise RuntimeError("frame_dim should be 2")
        kwargs['frame_dim'] = ndim
        super(NPImageSource, self).__init__(*args, **kwargs)


_im_dim_error = "img.ndim must equal {snk} not {inp}"


class NPFrameSink(FrameSink):
    def __init__(self, frame_dim, *args, **kwargs):
        super(NPFrameSink, self).__init__(*args, **kwargs)
        self._frame_store = dict()
        self._md_store = dict()
        self._md = dict()
        self._frame_dim = frame_dim

    def record_frame(self, img, frame_number, frame_md=None):
        if img.ndim != self._frame_dim:
            raise ValueError(_im_dim_error.format(self._frame_dim,
                                                  img.ndim))
        # TODO add checking on shape based on first frame or
        # init arg
        self._frame_store[frame_number] = img
        if frame_md is None:
            frame_md = dict()
        self._md_store[frame_number] = frame_md

    def set_metadata(self, md_dict):
        self._md.update(md_dict)

    def _clean(self):
        frames = np.array(list(
            six.iterkeys(self._frame_store)))
        if (np.min(frames) != 0 or
              np.max(frames) != len(frames) - 1):
            raise ValueError("did not provide continuous frames")
        data = np.array([self._frame_store[j]
                         for j in range(len(frames))])
        frame_md = [self._md_store[j]
                         for j in range(len(frames))]

        return {'data_array': data,
                'frame_dim': self._frame_dim,
                'meta_data': self._md,
                'frame_meta_data': frame_md}

    @property
    def kwarg_dict(self):
        dd = super(NPFrameSink, self).kwarg_dict
        dd['frame_dim'] = self._frame_dim
        return dd

    def make_source(self):
        return np_frame_source(**self._clean())


class NPImageSink(NPFrameSink, ImageSink):
    def __init__(self, *args, **kwargs):

        ndim = kwargs.pop('frame_dim', 2)
        if ndim != 2:
            raise RuntimeError("frame_dim should be 2")
        kwargs['frame_dim'] = ndim
        super(NPImageSink, self).__init__(*args, **kwargs)

    def make_source(self):
        return NPImageSource(**self._clean())
