# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
from six.moves import zip
from six.moves import xrange

import numpy as np

from ..tools_base import ToolBase
from ..handler_base import (ImageSource, ImageSink)

import IPython.utils.traitlets as traitlets


def _generic_thresh(img, min_val=None, max_val=None):
    if min_val is None and max_val is None:
        raise ValueError("must give at least one side")

    if min_val is not None:
        tmp_min = img > min_val
    else:
        tmp_min = True

    if max_val is not None:
        tmp_max = img < max_val
    else:
        tmp_max = True

    return np.logical_and(tmp_min, tmp_max)


class BoundedThreshold(ToolBase):
    """
    Select a band of thresholds

    """
    input_file = traitlets.Instance(klass=ImageSource,
                                    tooltip='Image File',
                                    label='input')
    output_file = traitlets.Instance(klass=ImageSink,
                                    tooltip='Image File',
                                    label='output')
    min_val = traitlets.Float(0, tooltip='Minimum Value', label='min_val')
    max_val = traitlets.Float(1, tooltip='Maximum Value', label='max_val')

    def run(self):
        with self.input_file as src:
            # grab the input data
            res = _generic_thresh(src.get_frame(0),
                                  min_val=self.min_val,
                                  max_val=self.max_val)
        self.output_file.set_resolution(self.input_file.resolution,
                                        self.input_file.resolution_units)
        with self.output_file as snk:
            snk.record_frame(res, 0)


class LTThreshold(ToolBase):
    """
    Pixels less than value

    """
    input_file = traitlets.Instance(klass=ImageSource,
                                    tooltip='Image File',
                                    label='input')
    output_file = traitlets.Instance(klass=ImageSink,
                                    tooltip='Image File',
                                    label='output')
    max_val = traitlets.Float(1, tooltip='Maximum Value', label='max_val')

    def run(self):
        with self.input_file as src:
            # grab the input data
            res = _generic_thresh(src.get_frame(0),
                                  min_val=self.min_val)

        self.output_file.set_resolution(self.input_file.resolution,
                                        self.input_file.resolution_units)
        with self.output_file as snk:
            snk.record_frame(res, 0)


class GTThreshold(ToolBase):
    """
    Pixels greater than value


    """
    input_file = traitlets.Instance(klass=ImageSource,
                                    tooltip='Image File',
                                    label='input')
    output_file = traitlets.Instance(klass=ImageSink,
                                    tooltip='Image File',
                                    label='output')
    max_val = traitlets.Float(1, tooltip='Maximum Value', label='max_val')

    def run(self):
        with self.input_file as src:
            # grab the input data
            res = _generic_thresh(src.get_frame(0),
                                  max_val=self.max_val)

        self.output_file.set_resolution(self.input_file.resolution,
                                        self.input_file.resolution_units)
        with self.output_file as snk:
            snk.record_frame(res, 0)
