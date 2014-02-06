"""
A set of base classes to provide the interface between the frame
work and the tools.
"""
#from abc import ABCMeta, abstractmethod, abstractproperty
import IPython.utils.traitlets as traitlets


class ToolBase:
    """
    Base class for `Tool` objects.

    These are objects that will hold the meta-data about the tool
    (such as input data types, required parameters, output types etc),
    accumulate inputs/parameters, validate the inputs provide tools for
    introspection, and run the tool when called.
    """

    def run(self):
        """
        Runs the tool on the data using the set parameters.  Takes no
        arguments and returns no values.  All non-handled exceptions
        will be raised.
        """
        raise NotImplementedError()


class IntRange(traitlets.Int):
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


class Addition(traitlets.HasTraits):
    a = traitlets.Int(0, desc='first integer')
    b = traitlets.Int(2, desc='second integer')
    c = IntRange(min_max=(0, 5), desc='limit range demo')

    def __init__(self):
        pass

    def run(self):
        return self.a + self.b
