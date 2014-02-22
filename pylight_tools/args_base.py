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
    def __init__(self, dtype, name, label=None, tooltip=None, **kwargs):
        self._dtype = dtype
        self._label = label
        self._name = name
        self._tooltip = tooltip

    @property
    def dtype(self):
        """
        the data type of this argument

        Not sure how to deal with polymorphic arguments, possibly via
        ABC registration magic.

        Returns
        -------
        dtype : type
            The data type of the argument
        """
        return self._dtype

    @property
    def label(self):
        """
        A human-readable name for the argument (used to label UI elements)

        May contain spaces, utf-8 characters, etc

        Returns
        -------
        label : string
            The label for UI elements for this argument
        """
        # if we have not explicitly set a label
        if self._label is None:
            # return the name instead
            return self.name
        # return the label
        return self._label

    @property
    def name(self):
        """
        Valid variable name for the argument.

        Can not contain spaces, must not start with an integer, no
        unicode (in py2) etc.


        Returns
        -------
        name : string
           variable name of argument
        """
        return self._name

    @property
    def tool_tip(self):
        """
        A longer description of the argument.

        Text for a tool tip in a UI.

        Returns
        -------
        tool_tip : string
            long description of argument
        """
        # if tooltip is not explicitly set
        if self._tooltip is None:
            # return the label
            return self.label
        # return the tooltip
        return self._tooltip

    @property
    def json_entry(self):
        tmp_dict = {}
        tmp_dict['label'] = self.label
        tmp_dict['type'] = str(self.dtype)
        return tmp_dict


class RangeArgSpec(ArgSpec):
    """
    A class for encapsulating arguments which have bounded ranges
    of valid values

    TODO make able to be one-sided
    """
    def __init__(self, dtype, name, min_val, max_val,
                 **kwargs):
        # correctly pass tooltip up
        ArgSpec.__init__(self, dtype, name, **kwargs)
        self._min = min_val
        self._max = max_val

    @property
    def min_val(self):
        """
        Returns
        -------
        min_val : self.dtype or None
            the minimum value
        """
        return self._min

    @property
    def max_val(self):
        """
        Returns
        -------
        max_val : self.dtype or None
            the maximum value
        """
        return self._max

    @property
    def json_entry(self):
        tmp_dict = ArgSpec.json_entry(self)
        tmp_dict['min'] = self.min_val
        tmp_dict['max'] = self.max_val
        return tmp_dict


class EnumArgSpec(ArgSpec):
    """
    A class to deal with enumerated values
    """
    def __init__(self, dtype, name, valid_vals, **kwargs):
        # TODO add check that valid_vals makes sense
        ArgSpec.__init__(self, dtype, name, **kwargs)
        self._vals = valid_vals

    @property
    def valid_vals(self):
        """
        Returns
        -------
        valid_vals : iterable
            The valid values
        """
        return self._valid_vals

    @property
    def json_entry(self):
        tmp_dict = ArgSpec.json_entry(self)
        tmp_dict['valid_vals'] = self.valid_vals
        return tmp_dict
