from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import h5py

from .base_file_handlers import SingleFileHandler
from ..handler_base import (TableSource,
                            TableSink,
                            require_active)

from six.moves import zip
import csv
import numpy as np

class BaseHdf(SingleFileHandler):
    _extension_filters = set(('h5', 'hdf'))

    def __init__(self, base_group_name=None, h5_kwargs=None,
                 *args, **kwargs):
        # pass up the call stack
        super(BaseHdf, self).__init__(*args, **kwargs)
        # sort out default values
        if base_group_name is None:
            base_group_name = ''
        if h5_kwargs is None:
            h5_kwargs = dict()
        # the base group in this file to work on
        # essentially like chroot
        self._group_name = base_group_name
        # the kwargs to pass to the File call
        self._h5_kwargs = h5_kwargs

        # place holders for file and group objects
        self._group = None
        self._File = None

    @property
    def kwarg_dict(self):
        # polymorphic properties!
        try:
            md = super(BaseHdf, self).kwarg_dict
        except AttributeError:
            md = dict()
        md['base_group_name'] = self._group_name
        md['h5_kwarg'] = self._h5_kwargs
        return md

    def activate(self):
        if self._group is not None or self._File is not None:
            raise RuntimeError("partially or fully initialized, can't re-run")

        self._File = h5py.File(self.backing_file, **self._h5_kwargs)
        self._group = self._File.ensure_group(self._group_name)


class HdfTableSink(BaseHdf, TableSink):
    def activate(self):
        if self.activate:
            # if already active, no-op
            return

        # finally pass up the call stack
        super(HdfTableSink, self).activate()
