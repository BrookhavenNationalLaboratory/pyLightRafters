"""

A set of base classes to abstract away loading data.

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import inspect
from six.moves import cPickle as pickle

from six import with_metaclass
from abc import ABCMeta, abstractmethod, abstractproperty
from .utils import all_subclasses as _all_subclasses
from functools import wraps


class RequireActive(Exception):
    """
    Exception sub-class to be raised when a function which
    requires the handler to be active is called on an inactive
    handler
    """
    pass


class RequireInactive(Exception):
    """
    Exception sub-class to be raised when a function which
    requires the handler to be inactive is called on an active
    handler
    """
    pass


def available_handler_list(base_handler, filter_list=None):
    """
    Returns a list of handlers which are sub-classes of `base_handler`.

    The list is then filtered to include only classes which are sub-classes
    of any of the classes in `filter_list.

    The thought is to use this something like

    >>> d_sinks = available_handler_list(DistributionSink)

    returns a list of all of the distribution sink handlers and

    >>> d_file_sinks = available_handler_list(DistributionSink, [FileHandler,])

    Parameters
    ----------
    base_handler : type
        The base-class to find sub-classes of

    filter_list : list of type
        Only return handlers which are a subclass of any of the
        elements in filter_list (OR logic).
    """
    # grab the sub-classes
    h_lst = []
    # if base class is not abstract, keep it too
    if not inspect.isabstract(base_handler):
        h_lst.append(base_handler)
    # yay recursion
    _all_subclasses(base_handler, h_lst)
    # list comprehension logic
    return [h for h in h_lst if filter_list is None or
            any(issubclass(h, filt) for filt in filter_list)]


class BaseDataHandler(with_metaclass(ABCMeta, object)):
    """
    An ABC for all data source and sink objects.

    This exists because the minimal required functions for
    both source and sink are the same.

    In both cases the `__init__` function should capture enough
    information to set up the sourcing/sinking of data, but not
    preform any initialization until `activate` is called.  This is
    to allow complex handlers to be shipped via pickle over the network
    (ex ipython parallel on remote machines) or via command line arguments
    for scripts (ex current pyLight frame work or cluster scheduling system).

    The consumers of these objects should take care of calling
    `activate` and `deactivate`.
    """
    @classmethod
    def available(cls):
        """
        Return if this handler is available for use.  This is to smooth
        over import and configuration issues.  Sub-classes should over-ride
        this function, by default the handlers are assumed to be usable if
        they are imported.

        Returns
        -------
        available : bool
            If the handler class is able to be used.
        """
        return True

    @classmethod
    def id(cls):
        return cls.__name__.lower()

    def __init__(self):
        self._active = False

    def activate(self):
        """
        Sub-classes should extend this to set handler up to source/sink
        data. This may be a no-op or it may involve opening files/network
        connections. Basically deferred initialization.
        """
        self._active = True

    def deactivate(self):
        """
        Sub-classes will need to extend this method to tear down any
        non-picklable structures (ex, open files)
        """

        self._active = False

    @property
    def active(self):
        """
        Returns
        -------
        active : bool
            If the source/sink is 'active'
        """

        return self._active

    @abstractproperty
    def metadata(self):
        """
        This should return enough information to passed to
        cls.__init__(**obj.metadata) and get back a functionally
        identical version of the object.
        """
        pass

    def __getstate__(self):
        """
        Return metadata dict

        Part of over-riding default pickle/unpickle behavior

        Raise exception if trying to pickle and active handler
        """
        if self.active:
            raise pickle.PicklingError("can not pickle active handler")
        return self.metadata

    def __setstate__(self, in_dict):
        """
        Over ride the default __setstate__ behavior and force __init__
        to be called
        """
        self.__init__(**in_dict)


def require_active(fun):
    """
    A decorator to use on functions which require the handler to
    be active
    """
    @wraps(fun)
    def inner(self, *args, **kwargs):
        if not self.active:
            raise RequireActive("Handler must be active")
        return fun(self, *args, **kwargs)

    return inner


def require_inactive(fun):
    """
    A decorator to use on functions which require the handler to
    be active
    """
    @wraps(fun)
    def inner(self, *args, **kwargs):
        if self.active:
            raise RequireInactive("Handler must be inactive")
        return fun(self, *args, **kwargs)

    return inner


class BaseSource(BaseDataHandler):
    """
    An ABC for all data source classes.

    This layer exists so that the `isinstace(obj, BaseSource)` will
    work.
    """
    pass


class BaseSink(BaseDataHandler):
    """
    An ABC for all data sing classes.

    This layer exists so that the `isinstace(obj, BaseSink)` will
    work.
    """
    def make_source(self, source_klass=None):
        """
        Returns a source object which will access the data written
        into this sink object.  The optional kwarg `source_klass`
        provides a hint as to what type of source to create (this
        will be relevant/useful with we end up with sources that
        step through the same data in different ways (exposures vs
        sinograms) or maybe not)

        Parameters
        ----------
        source_klass : None or type
            if not-None, what class to use to build the source object
        """
        raise NotImplementedError('will be made abstract method')


class DistributionSource(BaseSource):
    """
    An ABC to specify the interface for reading in distributions.

    Distributions are an output data type which are assumed to have two
    sets of values, `bin_edges` and `bin_values`.  Bin edges is assumed to
    be monotonic and increasing.

    `bin_edges` can be the same length as `bin_values`, denoting the left edges
    of the bins or one element longer with the last element marking the right
    edge of the last bin.
    """
    @abstractmethod
    def read_values(self):
        """
        Return the `bin_values` as an array-like object

        Returns
        -------
        bin_values : np.ndarray like
            The value of the bins
        """
        pass

    @abstractmethod
    def read_edges(self, include_right=False):
        """
        Return the `bin_edges` as an array-like object

        Parameters
        ----------
        include_right : bool, optional
            if True, then return the right edge of the last bin as the
            last element

        Returns
        -------
        bin_edges : np.ndarray like
            The location of the bin edges
        """
        pass


class ImageSource(BaseSource):
    """
    An ABC for the interface to read in images

    Images are N-D arrays of any type.

    All handlers are assumed to wrap a sequence of images, but may be
    length 1.

    The first pass will only have a single access function
    'get_frame` which will return what ever the natural 'frame'
    is.  More specific sub-classes should provide a way to more
    sensibly slice volumes (ex iterate over sinograms or projections).

    Still up in the air on if we want to do this with a few class
    with lots of functions or many classes with a few functions.
    Leaning toward lots of simple classes
    """
    @abstractmethod
    def get_frame(self, frame_num):
        """
        Returns what ever the sub-class thinks is 'frame'.

        Parameters
        ----------
        frame_num : uint
            The frame to extract
        """
        pass

    @abstractmethod
    def __len__(self):
        """
        Length is obligatory.
        """
        pass

    @abstractmethod
    def __getitem__(self, arg):
        """
        Defining __getitem__ is mandatory so that source[j] works
        """
        pass

    @abstractmethod
    def __iter__(self):
        """
        Defining __iter__ so source is iterable is mandatory
        """
        pass


class DistributionSink(BaseSink):
    """
    An ABC for specifying the interface for writing distributions.

    See DistributionSource for more.
    """
    @abstractmethod
    def write_dist(self, bins, vals, right_edge=False):
        """
        Sink the bin edges and values.

        Parameters
        ----------
        bins : iterable
           bin edges

        vals : iterable
           bin values

        right_edge : bool, optional
           if True, include the right edge of the last bin in the data.
        """
        pass


class FileHandler(with_metaclass(ABCMeta, object)):
    _extension_filters = set()

    @classmethod
    def handler_extensions(cls):
        return cls._extension_filters

    @abstractproperty
    def backing_file(self):
        """
        return the path to the backing file
        """
        pass

    @property
    def extension_filters(self):
        """
        Return a list of file extension
        """
        return type(self).handler_extensions()


class OpaqueFile(BaseSink, FileHandler):
    """
    That is an excessively complicated way to pass a path into
    a tool.
    """
    def __init__(self, fname):
        self._fname = fname
        self._active = False

    # fileHandler stuff
    @property
    def backing_file(self):
        return self._fname

    # base stuff
    def activate(self):
        self._active = True

    def deactivate(self):
        self._active = False

    @property
    def active(self):
        return self._active

    @property
    def metadata(self):
        return {'fname': self._fname}


class OpaqueFigure(OpaqueFile):
    _extension_filters = (set(('png', 'pdf', 'svg', 'jpg')) |
                            OpaqueFile.handler_extensions())
