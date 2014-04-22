from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import numpy as np

from pyRafters.core import GridData, _axis_attrs, _array_attrs
from numpy import ndarray
from numpy.testing import assert_array_equal
from nose.tools import assert_equal


def test_explicit_creation():
    base = np.arange(30).reshape(5, 6)
    tt = GridData(base)
    assert_array_equal(base, tt.view(ndarray))


def test_view_creation():
    base = np.arange(30).reshape(5, 6)
    tt = base.view(GridData)
    assert_array_equal(base, tt.view(ndarray))


def test_transpose():
    base = GridData(np.arange(30).reshape(5, 6),
                   axis_labels=('x', 'y'),
                   axis_units=('a', 'b'),
                   voxel_size=(1, 2),
                   axis_offsets=(1, 0))

    for tt in [base.T, base.transpose()]:
        for k in _axis_attrs:
            a = getattr(tt, k)
            b = getattr(base, k)[::-1]
            if isinstance(a, ndarray):
                assert_array_equal(a, b)
            else:
                assert_equal(a, b)


def _arg_func(func, *args):
    base = GridData(np.arange(30).reshape(5, 6),
                   axis_labels=('x', 'y'),
                   axis_units=('a', 'b'),
                   voxel_size=(1, 2),
                   axis_offsets=(1, 0))

    r = getattr(base, func)(*args)
    r2 = getattr(base.view(ndarray), func)(*args)
    assert_array_equal(r, r2)


def _arg_func_keepdims(func, *args):
    base = GridData(np.arange(30).reshape(5, 6),
                   axis_labels=('x', 'y'),
                   axis_units=('a', 'b'),
                   voxel_size=(1, 2),
                   axis_offsets=(1, 0))

    r = getattr(base, func)(*args, keepdims=True)
    r2 = getattr(base.view(ndarray), func)(*args, keepdims=True)
    assert_array_equal(r, r2)


def test_downcast():
    _down_cast_fun = ('sort', 'argsort', 'argmax', 'argmin', 'diagonal',
                    'flatten', 'nonzero', 'ravel', 'trace')

    for func in _down_cast_fun:
        yield _arg_func, func

    _arg_dc = (('argpartition', 1), ('compress', (0, 2, 5)),
                ('partition', 3),
                ('repeat', 2),
                ('reshape', (2, -1)),
                ('take', 1))

    for func, arg in _arg_dc:
        yield _arg_func, func, arg


# the point of this test is to make sure we match numpy behavior
def simple_test_reduction():
    _array_reduce_func = ('max', 'min', 'mean', 'prod', 'sum', 'var')

    # test with selecting axis, with and with out keepdims
    for _func in (_arg_func, _arg_func_keepdims):
        for func in _array_reduce_func:
            yield _func, func
            yield _func, func, 1,
            yield _func, func, (0,)
            yield _func, func, (1, 0)


def other_simple_test_reduction():
    _array_reduce_func = ('cumsum', 'cumprod', 'ptp')
    for func in _array_reduce_func:
        yield _arg_func, func, 1,
        yield _arg_func, func, 0,


# TODO add tests for these functions
# _ = ('dot', ('choose', (1, 2)),)
# TODO add tests
# _should_work = ('astype', 'fill', 'put', 'dump',  'searchsorted', 'clip',
#                'item', 'itemset',)

# TODO add tests to make sure the meta-data is getting transformed correctly
