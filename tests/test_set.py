#------------------------------------------------------------------------------
# setlx2py: test_list.py
#
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from nose.tools import eq_

from setlx2py.builtin.setlx_set import SetlxSet

def test_create():
    x = SetlxSet([5,4,4,2,5,1])
    eq_(len(x), 4)

def test_get_by_int_key_legit():
    x = SetlxSet([[1,2], [3,4]])
    eq_(x[1], 2)
    eq_(x[3], 4)
    
    
