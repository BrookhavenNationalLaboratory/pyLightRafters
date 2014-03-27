"""
A set of sources and sinks for handling in-memory nparrays
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six

import numpy as np

from ..handler_base import DistributionSource, DistributionSink, require_active


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
