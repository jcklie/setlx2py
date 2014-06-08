#------------------------------------------------------------------------------
# setlx2py: test_list.py
#
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from nose.tools import eq_

from setlx2py.builtin.setlx_set import SetlxSet
from setlx2py.builtin.setlx_functions import stlx_pow

def test_create():
    x = SetlxSet([5,4,4,2,5,1])
    eq_(len(x), 4)

def test_get_by_int_key_legit():
    x = SetlxSet([[1,2], [3,4]])
    eq_(x[1], 2)
    eq_(x[3], 4)
    
def test_set_operations():
    s1 = SetlxSet([1,2])
    s2 = SetlxSet([2,3])
    
    eq_(s1 + s2, SetlxSet([1,2,3]))
    eq_(s1 - s2, SetlxSet([1]))
    eq_(s1 * s2, SetlxSet([2]))
    eq_(s1 % s2, SetlxSet([1, 3]) )
    eq_(stlx_pow(s1, 2), SetlxSet([(1, 1), (1, 2), (2, 1), (2, 2)]))
    eq_(stlx_pow(2, s2), SetlxSet([(), (2,), (2,3), (3,)]))    
    
