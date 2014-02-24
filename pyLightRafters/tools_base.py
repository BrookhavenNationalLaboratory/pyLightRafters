"""

A set of base classes to provide the interface
between the front-end frame work and the back-end tools.

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six

import IPython.utils.traitlets as traitlets
from . import args_base


## a set of custom triatlets
class IntRange(traitlets.Int):
    """
    An integer traitlet with a limited range.
    """
    _err_str = ("Value must be between {_min} and {_max}.  " +
                "The value {val} was given.")

    def __init__(self, min_max, **kwargs):
        if min_max is None:
            raise ValueError("min_max must be non-None")
        self._min, self._max = min_max
        traitlets.Int.__init__(self, self._min, **kwargs)

    def validate(self, obj, value):
        # call base validate, either an Int or dead
        value = traitlets.Int.validate(self, obj, value)
        if value < self._min or value > self._max:
            raise traitlets.TraitError(self._err_str.format(
                _min=self._min, _max=self._max, val=value))
        return value


def _trait_mapper(trait_in):
    if isinstance(trait_in, traitlets.Int):
        return int
    elif isinstance(trait_in, traitlets.Float):
        return float
    elif isinstance(trait_in, traitlets.Instance):
        return trait_in.klass
    else:
        raise ValueError("Can not map trait to underlying type")


def _trait_to_arg(trait_in):
    t_dtype = _trait_mapper(trait_in)
    return args_base.ArgSpec(t_dtype, trait_in.name,
                             trait_in.get_metadata('label'),
                             trait_in.get_metadata('tooltip'))


def _get_label(key, trait):
    label = trait.get_metadata('label')
    if label:
        return label
    return key


# classes for defining tools
class ToolBase(traitlets.HasTraits):
    """
    Base class for `Tool` objects.

    These are objects that will hold the meta-data about the tool
    (such as input data types, required parameters, output types etc),
    accumulate inputs/parameters, validate the inputs provide tools for
    introspection, and run the tool when called.
    """

    _registry = {}

    @classmethod
    def register(cls, sub_class):
        """

        """
        cls._registry[sub_class.__name__] = sub_class

    @property
    def id(self):
        """
        Return the 'id' of the tool.

        Returns
        -------
        id : str
           The id of the tool
        """
        return self.__class__.__name__.lower()

    @property
    def params(self):
        """
        Returns a list of (key, value) pairs for the
        traits with the role 'param'
        """
        return [(k, v) for k, v in six.iteritems(self.traits())
                if v.get_metadata('role') == 'param']

    @property
    def input_files(self):
        """
        Returns a list of (key, value) pairs for the
        traits with the role 'input_file'
        """
        return [(k, v) for k, v in six.iteritems(self.traits())
                if v.get_metadata('role') == 'input_file']

    @property
    def output_files(self):
        """
        Returns a list of (key, value) pairs for the
        traits with the role 'input_file'
        """
        return [(k, v) for k, v in six.iteritems(self.traits())
                if v.get_metadata('role') == 'output_file']

    @property
    def title(self):
        """
        Returns the title of the Tool.  Defaults to using the class name.
        """
        return self.__class__.__name__

    @property
    def tutorial(self):
        """
        Return the tutorial, a short description of what the tool is.
        """
        raise NotImplementedError()

    def run(self):
        """
        Runs the tool on the data using the set parameters.  Takes no
        arguments and returns no values.  All non-handled exceptions
        will be raised.
        """
        raise NotImplementedError()
