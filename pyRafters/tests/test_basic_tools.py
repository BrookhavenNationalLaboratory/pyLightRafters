from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from six.moves import range
from pyRafters.handlers.np_handler import (NPImageSource,
                                                NPImageSink)

from pyRafters.tools import basic

import numpy as np

from nose.tools import assert_true

# shape for testing data
_shape = (3, 11, 13)


def _check_binary_op(op, tool, a, b):
    # set up constant arrays as testing sources, use floats
    srcA = NPImageSource(a * np.ones(_shape, dtype=np.float))
    srcB = NPImageSource(b * np.ones(_shape, dtype=np.float))
    # set up a sink
    snkC = NPImageSink()
    # init the tool and assign input/output
    T = tool()
    T.A = srcA
    T.B = srcB
    T.out = snkC
    # run the tool
    T.run()
    # compute what the answer should be
    c = op(a, b)
    # make and activate a source from the sink
    with snkC.make_source() as C:
        # loop over the output and check each frame
        for j in range(_shape[0]):
            # assert that all of the entries are equal
            # to the 'true' result
            assert_true(np.all(c == C.get_frame(j)))

# re-format the list of auto-generated tools from basic
# so that we can test them all
# each entry should be (operation, tool, value_a, value_b)
# if you want to add not-auto-generated tools to this
# set of tests use append to add them to the list
_bin_test_list = [(op, getattr(basic, tool_name), 2, 3)
                  for op, _, tool_name in basic._bin_op_list]


# generator test function, nose will test them all
def test_binary_ops():
    for op, tool, a, b in _bin_test_list:
        yield _check_binary_op, op, tool, a, b
