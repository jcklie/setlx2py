#------------------------------------------------------------------------------
# setlx2py: test_list.py
#
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from nose.tools import eq_, raises

from setlx2py.builtin.setlx_set import SetlxSet
from setlx2py.builtin.setlx_functions import stlx_pow

def test_create():
    x = SetlxSet([5,4,4,2,5,1])
    eq_(len(x), 4)

@raises(Exception)    
def test_get_by_int_key():
    x = SetlxSet([[4,3,2,1]])
    x[3]

def test_get_map_by_int_key():
    x = SetlxSet([[1,2], [3,4]])
    eq_(x[1], 2)
    eq_(x[3], 4)
    
def test_get_duplicate():
    x = SetlxSet([[1,1], [1,4], [3,3]])
    eq_(x[1], None)
    eq_(x[2], None)  
    
def test_set_value():
    x = SetlxSet( [ [1,2], [3,4] ] )
    x[5] = 6
    eq_(x[5], 6)    
    
def test_set_operations():
    s1 = SetlxSet([1,2])
    s2 = SetlxSet([2,3])
    
    eq_(s1 + s2, SetlxSet([1,2,3]))
    eq_(s1 - s2, SetlxSet([1]))
    eq_(s1 * s2, SetlxSet([2]))
    eq_(s1 % s2, SetlxSet([1, 3]) )
    eq_(stlx_pow(s1, 2), SetlxSet([(1, 1), (1, 2), (2, 1), (2, 2)]))
    eq_(stlx_pow(2, s2), SetlxSet([(), (2,), (2,3), (3,)]))    
    

    
