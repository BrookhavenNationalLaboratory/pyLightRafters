"""
A set of traitlets extensions for pyLightRafters
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import IPython.utils.traitlets as traitlets


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
