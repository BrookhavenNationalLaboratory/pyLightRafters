from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six

from pyRafters.handlers.tiff_handler import (tifffile_read2D_Handler,
                                                  tifffile_Sink)
import synthetic_data as sd
from testing_helpers import namedtmpfile
import numpy as np
from numpy.testing import assert_array_equal


@namedtmpfile('.tif')
def test_tiff_int_roundtrip(fname):
    test_img = sd.random((256, 256), scale=256, dtype=np.uint8)
    h_out = tifffile_Sink(fname)
    with h_out as snk:
        snk.record_frame(test_img, 0)

    h_in = tifffile_read2D_Handler(fname)
    with h_in as src:
        im_ret = src.get_frame(0)

    assert_array_equal(test_img, im_ret)
