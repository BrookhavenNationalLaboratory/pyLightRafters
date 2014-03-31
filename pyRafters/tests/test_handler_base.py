from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six

from nose.tools import raises, assert_equal, assert_true, assert_false
from pyRafters.handler_base import (BaseDataHandler, require_active,
        require_inactive, RequireActive, RequireInactive)

from six.moves import cPickle as pickle

# spin up a fake class to test activate/deactivate code in BaseDataHandler
foo_doc = "foo doc string"
unfoo_doc = "unfoo doc string"


class dummy_activate(BaseDataHandler):
    @property
    def kwarg_dict(self):
        return super(dummy_activate, self).kwarg_dict

    @require_active
    def foo(self):
        pass
    foo.__doc__ = foo_doc

    @require_inactive
    def unfoo(self):
        pass
    unfoo.__doc__ = unfoo_doc


def test_doc_strings():
    a = dummy_activate()
    assert_equal(a.foo.__doc__, foo_doc)
    assert_equal(a.unfoo.__doc__, unfoo_doc)


@raises(RequireActive)
def test_rqactive():
    a = dummy_activate()
    a.foo()


@raises(RequireInactive)
def test_rqinactive():
    a = dummy_activate()
    a.activate()
    a.unfoo()


def test_activate_deactivate():
    a = dummy_activate()
    assert_false(a.active)
    a.activate()
    assert_true(a.active)
    a.deactivate()
    assert_false(a.active)


@raises(pickle.PicklingError)
def test_pickle_fail():
    a = dummy_activate()
    a.activate()
    pickle.dumps(a)


def test_context():
    a = dummy_activate()
    assert_false(a.active)

    with a as tst:
        assert_true(tst.active)

    assert_false(a.active)
