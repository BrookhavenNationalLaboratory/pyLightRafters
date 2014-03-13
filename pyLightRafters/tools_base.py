"""

A set of base classes to provide the interface
between the front-end frame work and the back-end tools.

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import six
import hashlib
from collections import namedtuple

import IPython.utils.traitlets as traitlets

from . import traitlets as plr_traitlets
from . import args_base
from . import handler_base

from .utils import all_subclasses as _all_subclasses


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
    # class level-functions
    @classmethod
    def tool_id(cls):
        """
        Return the 'id' of the tool.

        Returns
        -------
        id : str
           The id of the tool
        """

        return cls.__name__.lower()

    @classmethod
    def tool_params(cls):
        """
        Returns the parameters the tool requires

        Returns
        -------
        """
        all_traits = cls.class_traits()
        return tuple(_trait_to_arg(t)
                     for t in six.itervalues(all_traits)
                       if _param_filter(t))

    @classmethod
    def tool_sources(cls):
        """
        Returns the data sources the tool requires.

        Returns
        -------
        sources : tuple
            Tuple of ArgSpec objects representing the data sources
        """
        all_traits = cls.class_traits()
        return tuple(_trait_to_arg(t) for t in six.itervalues(all_traits)
                        if _source_filter(t))

    @classmethod
    def tool_sinks(cls):
        """
        Returns the data sinks the tool requires.

        Returns
        -------
        sinks : tuple
            Tuple of ArgSpec objects representing the data sinks
        """
        all_traits = cls.class_traits()
        return tuple(_trait_to_arg(t) for t in six.itervalues(all_traits)
                        if _sink_filter(t))

    @classmethod
    def tool_title(cls):
        """
        Returns the title of the Tool.  Defaults to using the class name.

        Returns
        -------
        title : str
           Title of tool
        """
        return cls.__name__

    @classmethod
    def tool_tutorial(cls):
        """
        Returns a long description of the tool and it's use.  By default
        returns the de-dented doc-string.

        Returns
        -------
        tutorial : str
            Tutorial for tool.
        """
        ret_val = cls.__doc__
        if ret_val is None:
            ret_val = ''
        return _pep257_trim(ret_val)

    @classmethod
    def tool_args(cls):
        """
        Returns a `ToolArgs` of tuples of ArgSpec objects
        for this tool.

        Returns
        -------
        class_args : ToolArgs (namedtuple)
            Each entry is a tuple ArgSpec objects.
        """
        # filter three times, sadly don't see a better way to do this
        params = cls.tool_params()
        sources = cls.tool_sources()
        sinks = cls.tool_sinks()
        # return the information
        return ToolArgs(params, sources, sinks)

    # instance level functions
    # convince functions that just call class-level versions
    @property
    def id(self):
        return type(self).tool_id()

    @property
    def params(self):
        return type(self).tool_params()

    @property
    def sources(self):
        return type(self).tool_sources()

    @property
    def sinks(self):
        return type(self).tool_sinks()

    @property
    def title(self):
        return type(self).tool_title()

    @property
    def tutorial(self):
        return type(self).tool_tutorial()

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

    def run(self):
        """
        Runs the tool on the data using the set parameters.  Takes no
        arguments and returns no values.  All non-handled exceptions
        will be raised.
        """
        raise NotImplementedError()

    def __call__(self):
        """
        Make instances callable.  Just calls `run`

        This is so that ToolBase instances can be shipped off via pickle
        to `apply`.  It turns out that bound instances are not pickable
        (see http://stackoverflow.com/q/1816958/380231).  A lazy solution
        which works in this case is to make the instance callable and then
        just pass the object over the wire.
        """
        return self.run()


def _param_filter(trait_in):
    """
    Returns True if it looks like the trait is not a DataSource or DataSink
    else False
    """
    if not isinstance(trait_in, traitlets.TraitType):
            raise TypeError("input is not a sub-class of TraitType")
    if ((not isinstance(trait_in, traitlets.Instance)) or
           (not issubclass(trait_in.klass, handler_base.BaseDataHandler))):
        return True
    return False


def _source_filter(trait_in):
    """
    Returns True if the trait looks like it is a DataSource, else False
    """
    if not isinstance(trait_in, traitlets.TraitType):
        raise TypeError("input is not a sub-class of TraitType")
    if (isinstance(trait_in, traitlets.Instance) and
          issubclass(trait_in.klass, handler_base.BaseSource)):
        return True
    return False


def _sink_filter(trait_in):
    """
    Return True if it looks like the trait is a DataSink, else False
    """
    if not isinstance(trait_in, traitlets.TraitType):
            raise TypeError("input is not a sub-class of TraitType")
    if (isinstance(trait_in, traitlets.Instance) and
          issubclass(trait_in.klass, handler_base.BaseSink)):
        return True
    return False


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


def _pep257_trim(docstring):
    # lifted from http://legacy.python.org/dev/peps/pep-0257/
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)
