"""

A set of base classes to abstract away loading data.

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import cPickle as pickle

from six import with_metaclass
from abc import ABCMeta, abstractmethod, abstractproperty
from .utils import all_subclasses as _all_subclasses


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

    @abstractmethod
    def activate(self):
        """
        Set handler up to source/sink data.  This may be a no-op or
        it may involve opening files/network connections.

        Basically deferred initialization.
        """
        pass

    @abstractmethod
    def deactivate(self):
        """
        Tear down any non-picklable structures (ex, open files)
        """
        pass

    @abstractproperty
    def metadata(self):
        """
        This should return enough information to passed to
        cls.__init__(**obj.metadata) and get back a functionally
        identical version of the object.
        """
        pass

    @abstractproperty
    def active(self):
        """
        Returns
        -------
        active : bool
            If the source/sink is 'active'
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
    pass


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

    @classmethod
    def handler_extenstions(cls):
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
        return type(self).handler_extenstions()
