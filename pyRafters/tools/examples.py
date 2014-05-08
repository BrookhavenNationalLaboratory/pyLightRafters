# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from six.moves import zip
from six.moves import xrange

import numpy as np

from ..tools_base import ToolBase
from ..handler_base import (DistributionSource, DistributionSink,
                            ImageSource)
from ..handlers.base_file_handlers import (OpaqueFigure, OpaqueFileSource,
                                           OpaqueFileSink)

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

        # grab data from input
        with self.input_dist as src:
            tmp_val = np.array(src.values(), dtype='float')
            edges = src.bin_edges()

        # scale data
        tmp_val *= self.norm_val / np.sum(tmp_val)

        # write results out
        with self.output_dist as snk:
            snk.write_dist(edges, tmp_val)


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
        try:
            # import mpl and set non-gui backend
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            # activate and grab input data
            with self.input_dist as src:
                tmp_val = src.values()
                edges = src.bin_edges()

            # set up the plot
            fig, ax = plt.subplots(1, 1)
            ax.set_xlabel('bins')
            ax.set_ylabel('vals')
            # plot
            ax.step(edges, tmp_val, where='post', color='k')

            #
            with self.out_file as snk:
                fname = snk.backing_file
                fig.savefig(fname)

        except Exception as e:
            print(e)


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
        with self.input_file as src:
            im = src.get_frame(0)

        # set up matplotlib figure + axes
        fig, ax = plt.subplots(1, 1)
        ax.set_xlabel('count')
        ax.set_ylabel('vals')

        # if rgb image, do each channel separately
        if len(im.shape) == 3 and im.shape[2] in (3, 4):
            # assume rgb
            # loop over colors
            for j, c in zip(xrange(3), ('r', 'g', 'b')):
                # compute histogram for channel
                vals, edges = np.histogram(im[..., j].flat, bins=100)
                # add line to graph
                ax.step(edges[:-1], vals, where='post', color=c, label=c)
        # other wise, treat as gray scale
        else:
            # compute histogram of image
            vals, edges = np.histogram(im.flat, bins=100)
            # add line to graph
            ax.step(edges[:-1], vals, where='post')

        # grab path of where to save figure
        with self.out_file as snk:
            fname = snk.backing_file
        # save the figure
        fig.savefig(fname)
        # clean up
        plt.close('all')


class FileRepeat(ToolBase):
    """
    This is an example tool that takes in an OpaqueFileSource,
    OpaqueFileSink, and an integer.  The contents of the first file are
    repeated that number of times into the output file.
    """
    src_file = traitlets.Instance(klass=OpaqueFileSource,
                                  tooltip='source file',
                                  label='input')

    snk_file = traitlets.Instance(klass=OpaqueFileSink,
                                  tooltip='source file',
                                  label='output')
    repeat_count = traitlets.Integer(1, tooltip='number of times to repeat',
                                     label='input')

    def run(self):
        # grab the backing file of the source.  In general, source/sinks
        # need to be activated before they can be used, but you don't need to
        # in this case because you just need to get a string out.
        src_fname = self.src_file.backing_file
        # grab the backing file for the destination file
        snk_fname = self.snk_file.backing_file

        # open the output file for writing
        with open(snk_fname, 'w') as snk:
            # loop over the number of times to repeat
            for j in range(self.repeat_count):
                # open the source read only
                with open(src_fname, 'r') as src:
                    # copy all of the lines to the new file
                    for ln in src.readlines():
                        snk.write(ln)
