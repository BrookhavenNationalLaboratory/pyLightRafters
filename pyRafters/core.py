# Copyright Dan Allan 2014
# BSD License, sourced from pims.frame
# Adapted by Thomas Caswell
# Copyright Brookhaven National lab 2014
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
from six.moves import range, zip
from numpy import ndarray, asarray, array
import numpy as np
from itertools import chain

# added attributes which know about the axis information
_axis_attrs = ('axis_labels', 'axis_units', 'axis_offsets',
          'voxel_size')
# added attributes which know about the whole frame
_array_attrs = ('metadata', 'label_data', 'd_id', 'data_unit')


def _make_default_md(obj, axis_labels, axis_units,
                axis_offsets, voxel_size, metadata,
                label_data, d_id, data_unit):
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
        axis_offsets = np.zeros(obj.ndim, dtype=np.float64)
    axis_offsets = asarray(axis_offsets)

    # the axial size of the voxels
    if voxel_size is None:
        # if not given, default to 1 to match the assumption of pixels
        voxel_size = np.ones(obj.ndim, dtype=np.float64)
    voxel_size = asarray(voxel_size)

    # deal with arbitrary pass-through meta-data
    if metadata is None:
        # if not given, make an empty dict
        metadata = dict()

    # label data specifies if this array is continuous data or label data
    if label_data is None:
        # assume that data is sampling of a continuous field (not label data)
        label_data = False

    # don't do anything to _id, just let it pass through

    if data_unit is None:
        data_unit = ''

    return (axis_labels, axis_units, axis_offsets,
            voxel_size, metadata, label_data, d_id, data_unit)

# template for error message
_validate_err_msg = "length of {k} much match ndims len: {ln} ndims: {ndim}"


def _validate_md(obj, axis_labels, axis_units,
                axis_offsets, voxel_size, metadata,
                label_data, d_id, data_unit):
    ndims = obj.ndim
    # do not attempt to modify these values, only look at them
    ld = locals()
    # validate the things that need to match the dimension
    for k in _axis_attrs:
        if len(ld[k]) != ndims:
            raise ValueError(_validate_err_msg.format(
                k=k, ln=len(ld[k]), ndim=ndims))

    # validate that md is a dict
    if not isinstance(metadata, dict):
        raise ValueError("meta-data must be a dict")

    # don't bother to validate the bool, everything is truthy enough
    # don't bother to validate the id, anything is good enough
    # don't bother to validate the units, don't know how we want to
    #     constrain that one yet


def _np_down_cast(func):
    """
    helper function that generates a down-casting function
    for operations that
    """

    def inner(self, *args, **kwargs):
        print('down casting')
        return func(self.view(ndarray), *args, **kwargs)
    inner.__name__ = func.__name__
    inner.__doc__ = func.__doc__

    return inner


def _other_reduce_wrapper(func):
    """
    Helper function for wrapping functions that collapse axis.

    They must take the kwargs `axis` and do not take keepdims
    """
    def inner(self, axis=None, *args, **kwargs):
        if axis is None:
            # if axis is None, just down-cast as the array is
            # getting raveled
            return func(self.view(ndarray), axis, *args, **kwargs)
        else:
            # call the underlying function
            res = func(self.view(ndarray), axis, *args, **kwargs)
            res = asarray(res).view(GridData)
            # ptp is a special snow flake, does not take iterables
            # for axis, does not take keepdims, but _does_ eat an axis
            if func.__name__ == 'ptp':
                return self._truncate_axis_md(res, set((axis, )))
            # The other functions in this family (cumsum, cumprod) don't
            # take iterables for axis, don't take keepdims, and _do not_
            # eat an axis, so just finalize
            else:
                res.__array_finalize__(self)
                return res

    inner.__name__ = func.__name__
    inner.__doc__ = func.__doc__

    return inner


def _np_reduce_axis(func):
    """
    Helper function for wrapping functions that collapse axis.

    They must take the kwargs `axis` and `keepdims`
    """
    def inner(self, axis=None, keepdims=None, *args, **kwargs):
        # TODO fix default behavior for cumsum, cumprod, ptp
        if axis is None:
            # default to reducing along all axes
            axis = tuple(range(self.ndim))
        else:
            axis = tuple(np.atleast_1d(axis))
        if keepdims is None:
            # default to dropping dimensions
            # We may want to do this, but numpy functions will assume
            # the default is False which may break things
            keepdims = False

        print(axis)
        print(keepdims)
        # down cast to ndarray to call function
        tmp_res = func(self.view(ndarray), axis=axis,
                       keepdims=keepdims, *args, **kwargs)
        # up-cast the result
        res = asarray(tmp_res).view(GridData)

        # propagate the axis meta-data
        if keepdims:
            # in this case, preserve labels, but
            # squash
            res.__array_finalize__(self)
            print(res)
            for ax in axis:
                print(ax)
                old_offset = self.axis_offsets[ax]
                old_count = self.shape[ax]
                old_voxel_size = self.voxel_size[ax]

                res.voxel_size[ax] = (old_voxel_size * old_count)
                res.axis_offsets[ax] = (old_offset - old_voxel_size/2 +
                                        res.voxel_size[ax]/2)

            return self.__array_wrap__(res)

        else:
            # so we have lost some axis
            # make sure the axis labels are sorted
            res.d_id = self.d_id
            res.label_data = self.label_data
            # make sure we make a copy of the dict, not just keep a ref
            res.metadata = dict()
            res.metadata.update(self.metadata)

            # set of axis we will be skipping
            if np.isscalar(axis):
                axis_set = set([axis, ])
            else:
                axis_set = set(axis)

            return self._truncate_axis_md(res, axis_set)

    inner.__name__ = func.__name__
    inner.__doc__ = func.__doc__

    return inner


class GridData(ndarray):
    "Extends a numpy array with meta information"
    # See http://docs.scipy.org/doc/numpy/user/basics.subclassing.html

    def __new__(cls, input_array, axis_labels=None, axis_units=None,
                axis_offsets=None, voxel_size=None, metadata=None,
                label_data=False, d_id=None, data_unit=None):
        print("__new__")
        # grab version of input as a numpy array
        obj = asarray(input_array).view(cls)
        # probably a better way to write this
        args = _make_default_md(obj, axis_labels,
                                axis_units, axis_offsets,
                                voxel_size, metadata,
                                label_data, d_id, data_unit)
        _validate_md(obj, *args)
        # this relies on magic ordering of the attribute lists
        # and the args
        for k, v in zip(chain(_axis_attrs, _array_attrs), args):
            setattr(obj, k, v)
        return obj

    def __array_finalize__(self, obj):
        print("__array_finalize__")
        # if obj is None, then coming from __new__, return
        if obj is None:
            return
        # if obj is not none, then either view or template
        # as obj can be _any_ subclass of ndarray,
        input_args = {k: getattr(obj, k, None) for k in
                      chain(_axis_attrs, _array_attrs)}
        args = _make_default_md(self, **input_args)
        _validate_md(self, *args)
        for k, v in zip(chain(_axis_attrs, _array_attrs), args):
            if isinstance(v, ndarray):
                # if an array, make a copy
                v = array(v)

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
        if out_arr.ndim == 0:
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
             and len(key) > 0
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
        ret = super(GridData, self).transpose(*args, **kwargs)
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

    def swapaxes(self, a, b):
        raise NotImplemented()

    # specializations
    def tofile(self, *args, **kwargs):
        # wrap to include MD if possible
        raise NotImplemented()

    def _truncate_axis_md(self, res, axis_set):
        """
        Private helper function to deal with copy only _some_ of the
        information across when a function reduces the number of axis
        """
        _res_axis = 0
        new_units = []
        new_labels = []
        for ax in range(self.ndim):
            # pull all the data from the current object
            old_offset = self.axis_offsets[ax]
            old_voxel_size = self.voxel_size[ax]
            old_label = self.axis_labels[ax]
            old_unit = self.axis_units[ax]
            # sort out what to do with it
            if ax in axis_set:
                # then we are dropping this axis
                # TODO make sure this does not clobber MD
                old_count = self.shape[ax]

                res.metadata[old_label + '_avg'] = (
                    (old_offset - old_voxel_size/2 +
                        (old_voxel_size * old_count)/2))
                res.metadata[old_label + '_unit'] = old_unit
            else:
                # we are keeping this axis!
                new_labels.append(old_label)
                new_units.append(old_unit)
                res.voxel_size[_res_axis] = old_voxel_size
                res.axis_offsets[_res_axis] = old_offset
                _res_axis += 1

        res.axis_labels = new_labels
        res.axis_units = new_units
        return self.__array_wrap__(res)


# function we just want to down-cast to returning numpy arrays these are
# functions where it is not obvious (reshaping) or impossible
# (voxel would no longer be evenly spaced) to generate a proper
# GridData object to return
_down_cast_fun = ('argpartition', 'compress', 'choose', 'dot',
                   'partition', 'sort', 'argsort', 'repeat',
                   'reshape', 'take', 'argmax', 'argmin', 'diagonal',
                    'flatten', 'nonzero', 'ravel', 'trace', 'setfield',
                    'getfield')

# do some meta-programming magic to grab, wrap and assign the
# function to the GridData class
for func_name in _down_cast_fun:
    func = getattr(ndarray, func_name)
    setattr(GridData, func_name, _np_down_cast(func))


# first set of functions which get run through the reduce framework
# these functions default to calling the function on all axis if
# axis = None
_array_reduce_func = ('max', 'min', 'mean', 'prod', 'sum', 'var')

# some meta-programming tricks as above
for func_name in _array_reduce_func:
    func = getattr(ndarray, func_name)
    setattr(GridData, func_name, _np_reduce_axis(func))


# second set of functions that get run through reduce, they seem to
# work by defaulting to calling the function on d.ravel() and do
# not accept the keepdims kwarg
_array_reduce_func_other = ('cumsum', 'cumprod', 'ptp')

# some meta-programming tricks as above
for func_name in _array_reduce_func_other:
    func = getattr(ndarray, func_name)
    setattr(GridData, func_name, _other_reduce_wrapper(func))

# TODO sort out what these functions are and how they work
# _dontunderstand = ('setfield', 'getfieild')
