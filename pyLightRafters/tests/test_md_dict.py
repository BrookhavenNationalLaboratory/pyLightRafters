from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six

import h5py

from six.moves import xrange
from nose.tools import assert_equal

from pyLightRafters.utils import MD_dict, md_value


def test_string():
    test = MD_dict()
    test['a.b.c'] = 'test'
    assert_equal('test', test['a.b.c'][0])
    assert_equal('text', test['a.b.c'][1])


def test_no_units():
    test = MD_dict()
    test['a.b.c'] = 1
    assert_equal(1, test['a.b.c'][0])
    assert_equal(None, test['a.b.c'][1])


def test_units():
    test = MD_dict()
    test['a.b.c'] = (1, 'm')
    assert_equal(1, test['a.b.c'][0])
    assert_equal('m', test['a.b.c'][1])


def test_md_value():
    test = MD_dict()
    test['a.b.c'] = md_value(1, 'm')
    assert_equal(1, test['a.b.c'][0])
    assert_equal('m', test['a.b.c'][1])


def _gen_levels(n):
    name = '.'.join(['a'] * n)
    test = MD_dict()
    test[name] = md_value(1, 'm')
    assert_equal(test[name], md_value(1, 'm'))
    assert_equal(len(test), 1)


def test_nesting():
    for j in xrange(5):
        yield _gen_levels, j


def test_hdf_simple_roundtrip():
    # make file in memory
    F = h5py.File('test.h5', driver='core', mode='w', backing_store=False)
    tt = MD_dict()
    tt['name'] = 'test'
    tt['a.a'] = 1
    tt['a.b'] = md_value(2, 'counts')
    tt['a.c.d'] = md_value(.5, 'm')

    g = F.require_group('md_test')
    tt.write_hdf(g)

    tt2 = MD_dict.read_hdf_group(g)

    assert_equal(tt, tt2)
