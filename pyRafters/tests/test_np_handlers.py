from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from six.moves import range
from pyRafters.handlers.np_handler import (NPFrameSink,
                                                np_frame_source,
                                                NPImageSource,
                                                NPImageSink)
import numpy as np
from numpy.testing import assert_array_equal
from nose.tools import assert_true, assert_equal, raises


def test_np_framesource():
    shape = (13, 17)
    test_data = np.array([np.ones(shape) * j for j in range(11)])
    with np_frame_source(test_data, 2) as np_src:
        for j in range(11):
            assert_true(np.all(np_src.get_frame(j) == j))
            assert_array_equal(np_src.get_frame(j), test_data[j])


def test_np_framesrouce_rt():
    shape = (13, 17)
    test_data = np.array([np.ones(shape) * j for j in range(11)])
    np_snk = NPFrameSink(2)
    with np_snk as snk:
        for j in range(11):
            snk.record_frame(test_data[j], j, {'md': j})
    np_src = np_snk.make_source()
    with np_src as src:
        for j in range(11):
            assert_true(np.all(src.get_frame(j) == j))
            assert_array_equal(src.get_frame(j), test_data[j])
            assert_equal(src.get_frame_metadata(j, 'md'), j)


def test_np_imagesource():
    shape = (13, 17)
    test_data = np.array([np.ones(shape) * j for j in range(11)])
    with NPImageSource(test_data) as np_src:
        for j in range(11):
            assert_true(np.all(np_src.get_frame(j) == j))
            assert_array_equal(np_src.get_frame(j), test_data[j])


def test_np_imagesrouce_rt():
    shape = (13, 17)
    test_data = np.array([np.ones(shape) * j for j in range(11)])
    np_snk = NPImageSink()
    with np_snk as snk:
        for j in range(11):
            snk.record_frame(test_data[j], j, {'md': j})
    np_src = np_snk.make_source()
    with np_src as src:
        for j in range(11):
            assert_true(np.all(src.get_frame(j) == j))
            assert_array_equal(src.get_frame(j), test_data[j])
            assert_equal(src.get_frame_metadata(j, 'md'), j)


@raises(ValueError)
def test_np_framesink_noncontig():
    np_snk = NPFrameSink(2)
    with np_snk as snk:
        snk.record_frame(np.zeros((5, 5)), 0)
        snk.record_frame(np.zeros((5, 5)), 5)

    snk.make_source()
