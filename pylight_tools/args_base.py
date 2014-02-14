"""
A set of tools for manipulating distributions
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six


class ArgSpec(object):
    """
    Base class for specifying argument meta-data

    This could be replaced with a named tuple + ABC magic for
    setting up the class structure.  Using real classes for now
    because it is simpler and unlikely that this will be a
    major performance bottle neck.
    """
    def __init__(self, dtype, name, label=None, tooltip='', **kwargs):
        self._dtype = dtype
        self._label = label
        self._name = name
        self._tooltip = tooltip

    @property
    def dtype(self):
        return self._dtype

    @property
    def label(self):
        if self._label is not None:
            return self._label
        return self.name

    @property
    def name(self):
        return self._name

    @property
    def tool_tip(self):
        return self._tooltip


class RangeArgSpec(ArgSpec):
    """
    A class for encapsulating arguments which have bounded ranges
    of valid values
    """
    def __init__(self, dtype, name, min_val, max_val,
                 **kwargs):
        # correctly pass tooltip up
        ArgSpec.__init__(self, dtype, name, **kwargs)
        self._min = min_val
        self._max = max_val

    @property
    def min_val(self):
        return self._min

    @property
    def max_val(self):
        return self._max


class EnumArgSpec(ArgSpec):
    """
    A class to deal with enumerated values
    """
    def __init__(self, dtype, name, valid_vals, **kwargs):
        ArgSpec.__init__(self, dtype, name, **kwargs)
        self._vals = valid_vals

    @property
    def valid_vals(self):
        return self._valid_vals
