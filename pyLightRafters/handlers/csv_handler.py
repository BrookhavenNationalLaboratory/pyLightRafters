"""
A set of sources and sinks for handling
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from ..handler_base import (DistributionSource, FileHandler, DistributionSink,
                            require_active)

import six
from six.moves import zip
import csv
import numpy as np


class csv_dist_source(DistributionSource, FileHandler):
    """
    A source for reading distribution data out of csv (or tab or what ever)
    separated files.
    """
    _extension_filters = ['csv', 'txt']

    # local stuff
    def __init__(self, fname, right=False, csv_kwargs=None):
        """
        kwargs are passed to `csv.reader`

        Parameters
        ----------
        fname : string
            sufficiently qualified path to file to read
        """
        super(csv_dist_source, self).__init__()
        # file stuff
        self._fname = fname
        # distribution stuff
        self._right = right
        # csv stuff
        if csv_kwargs is None:
            csv_kwargs = {}
        self._kwargs = csv_kwargs
        # caching
        self._edges = None
        self._vals = None

    def activate(self):
        super(csv_dist_source, self).activate()
        with open(self._fname, 'rt') as csv_file:
            reader = csv.reader(csv_file, **self._kwargs)
            header = next(reader)

            edges, vals = [np.asarray(_, dtype=dt) for
                           _, dt in zip(zip(*reader), header)]
        self._edges = edges
        self._vals = vals

    def _clear_cache(self):
        if hasattr(self, '_edges'):
            del self._edges
        if hasattr(self, '_vals'):
            del self._vals

    def deactivate(self):
        super(csv_dist_source, self).deactivate()
        self._clear_cache()

    # FileHandler properties
    @property
    def backing_file(self):
        return self._fname

    # distribution methods
    @require_active
    def read_values(self):
        return self._vals

    @require_active
    def read_edges(self, include_right=False):
        if include_right:
            raise NotImplementedError("don't support right kwarg yet")
        return self._edges

    @property
    def metadata(self):
        return {'fname': self._fname,
                'right': self._right,
                'csv_kwargs': self._kwargs}


class csv_dist_sink(DistributionSink, FileHandler):
    """
    A sink for writing distribution data to a csv file.
    """
    _extension_filters = ['csv', 'txt']

    def __init__(self, fname, right=False, csv_kwargs=None):
        super(csv_dist_sink, self).__init__()
        # file stuff
        self._fname = fname
        # distribution stuff
        self._right = right
        # csv stuff
        if csv_kwargs is None:
            csv_kwargs = {}
        self._kwargs = csv_kwargs

    # FileHandler stuff
    @property
    def backing_file(self):
        return self._fname

    @require_active
    def write_dist(self, edges, vals, right_edge=False):
        if right_edge:
            raise NotImplementedError("don't support right edge yet")
        with open(self._fname, 'wt') as csv_file:
            writer = csv.writer(csv_file, **self._kwargs)
            header = [str(edges.dtype),
                             str(vals.dtype)]
            print(type(header[0]))
            writer.writerow(header)
            for line in zip(edges, vals):
                writer.writerow(line)

    @property
    def metadata(self):
        return {'fname': self._fname,
                'right': self._right,
                'csv_kwargs': self._kwargs}
