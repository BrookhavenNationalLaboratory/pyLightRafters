# Copyright Dan Allan 2014
# BSD License, sourced from pims.frame
# Adapted by Thomas Caswell
# Copyright Brookhaven National lab 2014
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
from six.moves import range, zip
from numpy import ndarray, asarray
import numpy as np
from itertools import chain
from functools import wraps

# code relies on order of these tuples, do not change it
# added attributes which know about the axis information
_axis_attrs = ('axis_labels', 'axis_units', 'axis_offsets',
          'voxel_size')
# added attributes which know about the whole frame
_array_attrs = ('metadata', 'label_data', 'd_id')


def _make_default_md(obj, axis_labels, axis_units,
                axis_offsets, voxel_size, metadata,
                label_data, d_id):
    """
    Helper function for setting sensible defaults
    """
    # walk through the inputs and assign default values
    # axis_labels is the names of the axis ex (x, y)
    if axis_labels is None:
        # if not specified, then just use numbers
        axis_labels = tuple(str(n) for n in range(obj.ndim))
    # default to assuming units of pixels
    if axis_units is None:
        axis_units = ('pix',) * obj.ndim
    # axis_offsets is a tuple of the location in unit-space of
    # the origin in pixel space
    if axis_offsets is None:
        # default to no offset
        axis_offsets = asarray((0, ) * obj.ndim)

    # the axial size of the voxels
    if voxel_size is None:
        # if not given, default to 1 to match the assumption of pixels
        voxel_size = asarray((1, ) * obj.ndim)

    # deal with arbitrary pass-through meta-data
    if metadata is None:
        # if not given, make an empty dict
        metadata = dict()

    # label data specifies if this array is continuous data or label data
    if label_data is None:
        # assume that data is sampling of a continuous field (not label data)
        label_data = False

    # don't do anything to _id, just let it pass through

    return (axis_labels, axis_units, axis_offsets,
            voxel_size, metadata, label_data, d_id)

# template for error message
_validate_err_msg = "length of {k} much match ndims len: {ln} ndims: {ndim}"


def _validate_md(obj, axis_labels, axis_units,
                axis_offsets, voxel_size, metadata,
                label_data, d_id):
    ndims = obj.ndim
    # do not attempt to modify these values, only look at them
    ld = locals()
    # validate the things that need to match the dimension
    for k in _axis_attrs:
        print((k, len(ld[k]), ndims))
        if len(ld[k]) != ndims:
            raise ValueError(_validate_err_msg.format(
                k=k, ln=len(ld[k]), ndim=ndims))

    # validate that md is a dict
    if not isinstance(metadata, dict):
        raise ValueError("meta-data must be a dict")

    # don't bother to validate the bool, everything is truthy enough


class sparray(ndarray):
    "Extends a numpy array with meta information"
    # See http://docs.scipy.org/doc/numpy/user/basics.subclassing.html

    def __new__(cls, input_array, axis_labels=None, axis_units=None,
                axis_offsets=None, voxel_size=None, metadata=None,
                label_data=False, d_id=None):
        print("__new__")
        # grab version of input as a numpy array
        obj = asarray(input_array).view(cls)
        # probably a better way to write this
        args = _make_default_md(obj, axis_labels,
                                axis_units, axis_offsets,
                                voxel_size, metadata,
                                label_data, d_id)
        _validate_md(obj, *args)
        # this relies on magic ordering of the attribute lists
        # and the args
        for k, v in zip(chain(_axis_attrs, _array_attrs), args):
            setattr(obj, k, v)
        return obj

    def __array_finalize__(self, obj):
        print("__array_finalize__")
        print("   obj:" + str(type(obj)))
        print("   self:" + str(type(self)))
        # if obj is None, then coming from __new__, return
        if obj is None:
            return
        print(self)
        print(obj)
        # if obj is not none, then either view or template
        # as obj can be _any_ subclass of ndarray,
        input_args = {k: getattr(obj, k, None) for k in
                      chain(_axis_attrs, _array_attrs)}
        print(input_args)
        args = _make_default_md(self, **input_args)
        print(args)
        _validate_md(self, *args)
        print('validated')
        for k, v in zip(chain(_axis_attrs, _array_attrs), args):
            setattr(self, k, v)

    # bump up priority
    __array_priority__ = 1.5

    def __array_prepare__(self, output, context=None):
        print("__array_prepare__")
        # if the shape changes, give up and down cast
        if self.shape != output.shape:
            print('bailing down')
            return output.view(ndarray)
        return output

    def __array_wrap__(self, out_arr, context=None):
        # Handle scalars so as not to break ndimage.
        # See http://stackoverflow.com/a/794812/1221924
        print("__array_wrap__")

        # still have no sorted out why this happens for ndarrays, but not
        # sub-classes.  However, this seems like the correct behavior as it
        # will not silently clobber subclasses -> scalars
        if out_arr.size == 1:
            # explicitly clobber subclass -> scalar
            return out_arr[()]
        return ndarray.__array_wrap__(self, out_arr, context)

    def __reduce__(self):
        """Necessary for making this object picklable"""
        print("__reduce__")

        object_state = list(ndarray.__reduce__(self))
        saved_attr = chain(_axis_attrs, _array_attrs)
        subclass_state = {a: getattr(self, a) for a in saved_attr}
        object_state[2] = (object_state[2], subclass_state)
        return tuple(object_state)

    def __setstate__(self, state):
        """Necessary for making this object picklable"""
        print("__setstate__")
        nd_state, own_state = state
        ndarray.__setstate__(self, nd_state)

        for attr, val in own_state.items():
            setattr(self, attr, val)

    def __getitem__(self, key):
        #print("__getitem__")
        # if all slices, be smart
        if (isinstance(key, tuple) and len(key) == self.ndim
             and all(isinstance(_, slice) for _ in key)):
            res = ndarray.__getitem__(self, key)
            starts, _, stride = list(zip(*[slc.indices(n) for
                                           slc, n in zip(key, self.shape)]))
            res.axis_offsets = (asarray(self.axis_offsets) +
                                asarray(starts) * asarray(self.voxel_size))
            res.voxel_size = asarray(self.voxel_size) * asarray(stride)
            return res
        # if not, then down cast first
        else:
            return self.view(ndarray)[key]

    def __repr__(self):
        reprs = ["{k}: {rp}".format(k=k, rp=repr(getattr(self, k)))
                 for k in chain(_axis_attrs, _array_attrs)]
        reprs += [repr(self.view(ndarray)), ]
        return '\n'.join(reprs)

    def transpose(self, *args, **kwargs):
        print('in transpose')
        print(args)
        print(kwargs)
        ret = super(sparray, self).transpose(*args, **kwargs)
        if len(args) == 0:
            for k in _axis_attrs:
                setattr(ret, k, getattr(self, k)[::-1])
        else:
            raise NotImplemented('write swap-axis case')
        return ret

    # TODO sort out how this really works for ndarrays
    @property
    def T(self):
        return self.transpose()

    # set of functions that are run through reduce,
    # there should be a way to deal with all of these
    # the same
    def max(self, **kwargs):
        raise NotImplemented()

    def min(self, **kwargs):
        raise NotImplemented()

    def mean(self, **kwargs):
        raise NotImplemented()

    def prod(self, **kwargs):
        raise NotImplemented()

    def sum(self, **kwargs):
        raise NotImplemented()

    def var(self, **kwargs):
        raise NotImplemented()

    def swapaxes(self, a, b):
        raise NotImplemented()

    def cumsum(self, **kwargs):
        raise NotImplemented()

    def cumprod(self, **kwargs):
        raise NotImplemented()

    def ptp(self, *args, **kwargs):
        raise NotImplemented()

    # specializations
    def tofile(self, *args, **kwargs):
        # wrap to include MD if possible
        raise NotImplemented()


_down_cast_fun = ('argpartition', 'compress', 'choose', 'dot',
                   'partition', 'sort', 'argsort', 'repeat',
                   'reshape', 'take', 'argmax', 'argmin', 'diagonal',
                    'flatten', 'nonzero', 'ravel', 'trace')


def _np_down_cast(func):
    """
    helper function that generates a down-casting function
    for operations that
    """
    @wraps(func)
    def inner(self, *args, **kwargs):
        func(self.view(ndarray), *args, **kwargs)



# _dontunderstand = ('setfield', 'getfieild')

# _should_work = ('astype', 'fill', 'put', 'dump',  'searchsorted', 'clip',
#                'item', 'itemset',)
