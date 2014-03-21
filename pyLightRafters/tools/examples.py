# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from six.moves import zip
from six.moves import xrange

import numpy as np

from ..tools_base import ToolBase
from ..handler_base import (DistributionSource, DistributionSink,
                            OpaqueFigure, ImageSource)

import IPython.utils.traitlets as traitlets


class NormalizeDist(ToolBase):
    """
    A simple example Tool.

    This tool re-scales the input distribution so that the sum
    is equal to `norm_val`.


    """
    norm_val = traitlets.Float(1, tooltip='new sum', label='norm')
    input_dist = traitlets.Instance(klass=DistributionSource,
                                tooltip='input distribution',
                                label='input')
    output_dist = traitlets.Instance(klass=DistributionSink,
                                tooltip='output distribution',
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


class PlotDist(ToolBase):
    """
    Loads a distribution and then saves a plot of it
    """
    input_dist = traitlets.Instance(klass=DistributionSource,
                                    tooltip='input distribution',
                                    label='input')
    out_file = traitlets.Instance(klass=OpaqueFigure,
                                    tooltip='Figure File',
                                    label='output')

    def run(self):
        # import mpl and set non-gui backend
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        # activate and grab input data
        self.input_dist.activate()
        tmp_val = self.input_dist.read_values()
        edges = self.input_dist.read_edges()

        fig, ax = plt.subplots(1, 1)
        ax.set_xlabel('bins')
        ax.set_ylabel('vals')

        ax.step(edges, tmp_val, where='post')

        self.out_file.activate()
        fname = self.out_file.backing_file
        fig.savefig(fname)
        self.input_dist.deactivate()
        self.out_file.deactivate()


class HelloWorld(ToolBase):
    """
    A parameter-less tool that just says hi
    """
    def run(self):
        print("Hello World")
        print("שלום עולם")
        print("你好世界")
        print("안녕하세요!")


class ImageHistogram(ToolBase):
    out_file = traitlets.Instance(klass=OpaqueFigure,
                                    tooltip='Figure File',
                                    label='output')
    input_file = traitlets.Instance(klass=ImageSource,
                                    tooltip='Image File',
                                    label='input')

    def run(self):
        # import mpl and set non-gui backend
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        import numpy as np

        # activate and grab input data
        self.input_file.activate()
        im = self.input_file.get_frame(0)

        fig, ax = plt.subplots(1, 1)
        ax.set_xlabel('count')
        ax.set_ylabel('vals')

        if len(im.shape) == 3 and im.shape[2] in (3, 4):
            # assume rgb
            for j, c in zip(xrange(3), ('r', 'g', 'b')):
                vals, edges = np.histogram(im[..., j].flat, bins=100)
                ax.step(edges[:-1], vals, where='post', color=c, label=c)
        else:
            vals, edges = np.histogram(im.flat, bins=100)
            ax.step(edges[:-1], vals, where='post', color=c, label=c)

        self.out_file.activate()
        fname = self.out_file.backing_file
        fig.savefig(fname)
        self.input_file.deactivate()
        self.out_file.deactivate()
