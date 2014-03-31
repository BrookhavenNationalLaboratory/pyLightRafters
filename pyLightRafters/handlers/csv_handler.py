"""
A set of sources and sinks for handling distributions saved as csv files
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from ..handler_base import (DistributionSource,
                            DistributionSink,
                            require_active)
from .base_file_handlers import SingleFileHandler


from six.moves import zip
import csv
import numpy as np


class csv_dist_source(SingleFileHandler, DistributionSource):
    """
    A source for reading distribution data out of csv (or tab or what ever)
    separated files.
    """
    _extension_filters = {'csv',
                          'txt'} | SingleFileHandler.handler_extensions()

    # local stuff
    def __init__(self, fname, right=False, csv_kwargs=None):
        """
        kwargs are passed to `csv.reader`

        Parameters
        ----------
        fname : string
            sufficiently qualified path to file to read
        """
        super(csv_dist_source, self).__init__(fname=fname)
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

    # distribution methods
    @require_active
    def values(self):
        return self._vals

    @require_active
    def bin_edges(self, include_right=False):
        if include_right:
            raise NotImplementedError("don't support right kwarg yet")
        return self._edges

    @require_active
    def bin_centers(self, include_right=False):
        # if we have a right edge
        if len(self._edges) > len(self._vals):
            return self._edges[:-1] + np.diff(self._edges)
        elif len(self._edges) == len(self._vals):
            bin_diff = np.diff(self._edges)
            return self._edges + np.r_[bin_diff, np.mean(bin_diff)]

    @property
    def kwarg_dict(self):
        md = super(csv_dist_source, self).kwarg_dict
        md.update({'right': self._right,
                    'csv_kwargs': self._kwargs})
        return md


class csv_dist_sink(SingleFileHandler, DistributionSink):
    """
    A sink for writing distribution data to a csv file.
    """
    _extension_filters = {'csv',
                          'txt'} | SingleFileHandler.handler_extensions()

    def __init__(self, fname, right=False, csv_kwargs=None):
        super(csv_dist_sink, self).__init__(fname=fname)
        # distribution stuff
        self._right = right
        # csv stuff
        if csv_kwargs is None:
            csv_kwargs = {}
        self._kwargs = csv_kwargs

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
    def kwarg_dict(self):
        md = super(csv_dist_sink, self).kwarg_dict
        md.update({'right': self._right,
                    'csv_kwargs': self._kwargs})
        return md

    def make_source(self, klass=None):
        if klass is not None:
            raise NotImplementedError("don't support this yet")

        return csv_dist_source(self.backing_file,
                               right=self._right,
                               csv_kwargs=self._kwargs)
