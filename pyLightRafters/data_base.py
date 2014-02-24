"""

A set of base classes to abstract away loading data.

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
from six import with_metaclass
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import defaultdict

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

    @abstractmethod
    def _register(self):
        pass


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
    @abstractproperty
    def backing_file(self):
        """
        return the path to the backing file
        """
        pass

    @abstractproperty
    def extension_filters(self):
        """
        Return a list of file extension
        """
        pass


class InterfaceRegistry(object):
    """
    A singleton class to keep track of what handler classes implement
    which interfaces
    """
    def __init__(self):
        # the dict to keep track of everything
        self._handlers = defaultdict(list)

    # decorator function
    def register(self, iface_list):

        def wrapper(inner_class):
            # sub-class the input class from all of the
            # interfaces passed in
            wrapped_klass = type(inner_class.__name__,
                            (inner_class,) + tuple(iface_list),
                            {})
            # add the wrapped class to the handler list for each
            # interface
            for iface in iface_list:
                self._handlers[iface].append(wrapped_klass)
            # return the new sub-class
            return wrapped_klass
        # return the function so the decorator warks
        return wrapper

#set up singleton
IR = InterfaceRegistry()
