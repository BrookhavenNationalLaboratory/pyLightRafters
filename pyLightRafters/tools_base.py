"""

A set of base classes to provide the interface
between the front-end frame work and the back-end tools.

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import hashlib
from collections import namedtuple

import IPython.utils.traitlets as traitlets

from . import traitlets as plr_traitlets
from . import args_base
from . import data_base


def list_of_tools():
    tool_list = []
    _all_subclasses(ToolBase, tool_list)
    return tool_list

ToolArgs = namedtuple('ToolArgs', ['params', 'sources', 'sinks'])


# classes for defining tools
class ToolBase(traitlets.HasTraits):
    """
    Base class for `Tool` objects.

    These are objects that will hold the meta-data about the tool
    (such as input data types, required parameters, output types etc),
    accumulate inputs/parameters, validate the inputs provide tools for
    introspection, and run the tool when called.
    """
    @classmethod
    def class_args(cls):
        """
        Returns a `ToolArgs` of tuples of ArgSpec objects
        for this tool.

        Returns
        -------
        class_args : ToolArgs (namedtuple)
            Each entry is a tuple ArgSpec objects.
        """
        # get the traits
        all_traits = cls.class_traits()
        # filter three times, sadly don't see a better way to do this
        params = tuple(_trait_to_arg(t) for t in six.itervalues(all_traits)
                       if _param_filter(t))
        sources = tuple(_trait_to_arg(t) for t in six.itervalues(all_traits)
                        if _source_filter(t))
        sinks = tuple(_trait_to_arg(t) for t in six.itervalues(all_traits)
                      if _sink_filter(t))
        # return the information
        return ToolArgs(params, sources, sinks)

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
        return [_trait_to_arg(v) for v in six.itervalues(self.traits())
                if _param_filter(v)]

    @property
    def input_files(self):
        """
        Returns a list of (key, value) pairs for the
        traits with the role 'input_file'
        """
        return [_trait_to_arg(v) for v in six.itervalues(self.traits())
                if _source_filter(v)]

    @property
    def output_files(self):
        """
        Returns a list of (key, value) pairs for the
        traits with the role 'input_file'
        """
        return [_trait_to_arg(v) for v in six.itervalues(self.traits())
                if _sink_filter(v)]

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

    def phash(self):
        """
        returns as SHA-1 hash of the tool name + the current values of the
        parameters (excluding input and output data handlers)
        """
        traits = [v for v in six.itervalues(self.traits())
                        if _param_filter(v)]
        traits.sort(key=lambda v: v.name)
        m = hashlib.sha1()
        for v in traits:
            m.update(v.name)
            m.update(str(getattr(self, v.name)))
        return m.hexdigest()


def _source_filter(trait_in):
    """
    Returns True if the trait looks like it is a DataSource, else False
    """
    if (isinstance(trait_in, traitlets.Instance) and
          issubclass(trait_in.klass, data_base.BaseSource)):
        return True
    return False


def _param_filter(trait_in):
    """
    Returns True if it looks like the trait is not a DataSource or DataSink
    else False
    """
    if ((not isinstance(trait_in, traitlets.Instance)) or
           (not issubclass(trait_in.klass, data_base.BaseDataHandler))):
        return True
    return False


def _sink_filter(trait_in):
    """
    Return True if it looks like the trait is a DataSink, else False
    """
    if (isinstance(trait_in, traitlets.Instance) and
          issubclass(trait_in.klass, data_base.BaseSink)):
        return True
    return False


def _all_subclasses(in_c, sc_lst):
    t = in_c.__subclasses__()
    if len(t) > 0:
        sc_lst.extend(t)
        for _sc in t:
            _all_subclasses(_sc, sc_lst)


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
