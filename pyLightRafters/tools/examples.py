from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
import numpy as np

from ..tools_base import ToolBase
from ..data_base import DistributionSource, DistributionSink

import IPython.utils.traitlets as traitlets


class NormalizeDist(ToolBase):
    """
    A simple example Tool.

    This tool re-scales the input distribution so that the sum
    is equal to `norm_val`.


    """
    norm_val = traitlets.Float(1, tool_tip='new sum', label='norm')
    input_dist = traitlets.Instance(klass=DistributionSource,
                                tool_tip='input distribution',
                                label='input')
    output_dist = traitlets.Instance(klass=DistributionSink,
                                tool_tip='output distribution',
                                label='output')

    def run(self):
        # sanity checks
        if self.input_dist is None:
            raise ValueError("input source must be not-none")
        if self.output_dist is None:
            raise ValueError("output sink must be not-none")
        # activate i/o
        self.input_dist.activate()
        self.output_dist.activate()
        # grab data from input
        tmp_val = np.array(self.input_dist.read_values(), dtype='float')
        # scale data
        tmp_val *= self.norm_val / np.sum(tmp_val)
        # get the edges
        edges = self.input_dist.read_edges()

        # write results out
        self.output_dist.write_dist(edges, tmp_val)

        # shut down the i/o
        self.input_dist.deactivate()
        self.output_dist.deactivate()
