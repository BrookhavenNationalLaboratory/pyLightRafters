from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import numpy as np

from pyRafters.core import sparray, _axis_attrs, _array_attrs
from numpy import ndarray
from numpy.testing import assert_array_equal
from nose.tools import assert_equal


def test_explicit_creation():
    base = np.arange(30).reshape(5, 6)
    tt = sparray(base)
    assert_array_equal(base, tt.view(ndarray))


def test_view_creation():
    base = np.arange(30).reshape(5, 6)
    tt = base.view(sparray)
    assert_array_equal(base, tt.view(ndarray))


def test_transpose():
    base = sparray(np.arange(30).reshape(5, 6),
                   axis_labels=('x', 'y'),
                   axis_units=('a', 'b'),
                   voxel_size=(1, 2),
                   axis_offsets=(1, 0))

    for tt in [base.T, base.transpose()]:
        for k in _axis_attrs:
            assert_equal(getattr(tt, k), getattr(base, k)[::-1])
