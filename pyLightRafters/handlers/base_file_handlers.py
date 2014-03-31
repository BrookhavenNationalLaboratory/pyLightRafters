from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
from ..handler_base import BaseSink, BaseSource
import os


class FileHandler(object):
    """
    Mix-in class for providing information about the file
    extensions that the handler can deal with.  This by it's self
    is not particularly useful, however this will save some code.
    """
    _extension_filters = set()

    @classmethod
    def handler_extensions(cls):
        return cls._extension_filters

    @property
    def extension_filters(self):
        """
        Return a list of file extension
        """
        return type(self).handler_extensions()


class SingleFileHandler(FileHandler):
    """
    Mix-in class for keeping track of a single file
    """
    def __init__(self, fname=None, *args, **kwargs):
        """
        Parameters
        ----------
        fname : str
            Absolute path to file
        """
        if fname is None:
            raise ValueError("must provide a valid path")
        # TODO put (optional?) validation here
        # pass remaining input up the mro chain
        super(SingleFileHandler, self).__init__(*args, **kwargs)
        # set the fname storage
        self._fname = fname

    @property
    def backing_file(self):
        """
        return the full path to the backing file

        Returns
        -------
        fpath : str
            Absolute path of file
        """
        return self._fname

    @property
    def kwarg_dict(self):
        # polymorphic properties!
        try:
            md = super(SingleFileHandler, self).kwarg_dict
        except AttributeError:
            md = dict()
        md['fname'] = self._fname
        return md


class SequentialSetFileHandler(FileHandler):
    """
    Mix-in class for dealing with sequentially named files ex
    (frame_01.png, frame_02.png, ...).

    It takes in a new-style format string (uses {} and .format) for the
    name and the base path.  The format string must take a single label `n`
    which is the number.

    The base path an the format string are joined using `os.path.join`, but
    there is no reason that format_str can not contain '/'.  Ex
    `set_{n}/a.png` is a valid (pull a file from a collection
    of systematically named folders)

    """
    def __init__(self, base_path=None, format_str=None, *args, **kwargs):
        """
        Parameters
        ----------
        base_path : str
             base path for files
        """
        if base_path is None:
            base_path = ''  # convert None to empty string.  Do this
                            # instead of using '' as the default value
                            # so that we can un-ambiguously differentiate
                            # between user input and 'default' input

        if format_str is None:
            raise ValueError("must provide a pattern")
        # TODO put (optional?) validation here
        # pass up any remaining imput
        super(SequentialSetFileHandler, self).__init__(*args, **kwargs)
        self._base_path = base_path
        self._format_str = format_str

    @property
    def fname_format(self):
        """
        return the path to the backing file
        """
        return self._format_str

    @property
    def base_path(self):
        return self._path

    def get_fname(self, n):
        return os.path.join((self._base_path,
                            self._format_str.format(n=n)))

    @property
    def kwarg_dict(self):
        # polymorphic properties!
        try:
            md = super(SequentialSetFileHandler, self).kwarg_dict
        except AttributeError:
            md = dict()
        md['base_path'] = self._base_path
        md['format_str'] = self._format_str
        return md


class OpaqueFileSink(SingleFileHandler, BaseSink):
    """
    That is an excessively complicated way to pass a path into
    a tool.
    """
    def make_source(self):
        return OpaqueFileSource(**self.kwarg_dict)


class OpaqueFigure(OpaqueFileSink):
    _extension_filters = (set(('png', 'pdf', 'svg', 'jpg')) |
                            OpaqueFileSink.handler_extensions())
    pass


class OpaqueFileSource(SingleFileHandler, BaseSource):
    """
    That is an excessively complicated way to pass a path into
    a tool.
    """
    pass
