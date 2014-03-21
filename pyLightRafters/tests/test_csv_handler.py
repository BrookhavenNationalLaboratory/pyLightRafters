from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six

from testing_helpers import namedtmpfile
from numpy.testing import assert_almost_equal
import numpy as np

from pyLightRafters.handler_base import RequireActive

from pyLightRafters.handlers.csv_handler import (csv_dist_sink,
                                                 csv_dist_source)
from nose.tools import raises
from six.moves import cPickle as pickle


@namedtmpfile('.csv')
def test_round_trip_float_nr(fname):
    # test data
    np.random.seed(0)
    edges = np.linspace(0, 1, 100)
    vals = np.random.rand(100)
    # write to disk
    sn = csv_dist_sink(fname)
    sn.activate()
    sn.write_dist(edges, vals)
    sn.deactivate()
    # read from disk
    sr = csv_dist_source(fname)
    sr.activate()
    read_edges = sr.read_edges()
    read_vals = sr.read_values()
    sr.deactivate()

    assert_almost_equal(read_vals, vals)
    assert_almost_equal(read_edges, edges)


@namedtmpfile('.csv')
def test_round_trip_int_nr(fname):
    # test data
    np.random.seed(0)
    edges = np.arange(100)
    vals = np.arange(100)
    # write to disk
    sn = csv_dist_sink(fname)
    sn.activate()
    sn.write_dist(edges, vals)
    sn.deactivate()
    # read from disk
    sr = csv_dist_source(fname)
    sr.activate()
    read_edges = sr.read_edges()
    read_vals = sr.read_values()
    sr.deactivate()

    assert_almost_equal(read_vals, vals)
    assert_almost_equal(read_edges, edges)


@raises(RequireActive)
@namedtmpfile('.csv')
def test_snk_active(fname):
    # test data
    np.random.seed(0)
    edges = np.linspace(0, 1, 100)
    vals = np.random.rand(100)
    # write to disk
    sn = csv_dist_sink(fname)
    sn.write_dist(edges, vals)


@raises(RequireActive)
@namedtmpfile('.csv')
def test_src_active(fname):
    # write to disk
    sn = csv_dist_source(fname)
    sn.read_values()


@namedtmpfile('.csv')
def test_src_pickle(fname):
    sr = csv_dist_source(fname)
    ck = pickle.dumps(sr)
    pickle.loads(ck)


@namedtmpfile('.csv')
def test_snk_pickle(fname):
    sn = csv_dist_sink(fname)
    ck = pickle.dumps(sn)
    pickle.loads(ck)
