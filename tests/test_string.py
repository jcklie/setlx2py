#------------------------------------------------------------------------------
# setlx2py: test_string.py
#
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from nose.tools import eq_

from setlx2py.builtin.setlx_string import SetlxString

def test_iteration():
    s = SetlxString("abc")
    res = [c for c in s]
    eq_(res, ["a", "b", "c"])
