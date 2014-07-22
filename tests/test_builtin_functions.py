#------------------------------------------------------------------------------
# setlx2py: test_builtin_functions.py
#
# Unit tests for the builtin functions in SetlX
# (setlx2py/builtin/setlx_functions.py)
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from nose.tools import eq_, nottest

import sys
import random
import math as m

from StringIO import StringIO

from setlx2py.builtin.setlx_functions import *
from setlx2py.builtin.setlx_internals import *

# Functions and Operators on Sets and Lists
# =========================================

#7
def test_arb():
    random.seed(42)
    s = SetlxSet([42])

    result = stlx_arb(s)
    eq_(result, 42)
    eq_(s, SetlxSet([42]))

#8    
def test_collect():
    actual = stlx_collect(["a", "b", "c", "a", "b", "a"])
    expected = SetlxSet([["a", 3], ["b", 2], ["c", 1]])
    eq_(expected, actual)
    
#9
def test_first():
    eq_( stlx_first([0,1,2]), 0 )
    
#10
def test_last():
    eq_( stlx_last([0,1,2]), 2 )

#11    
def test_from():
    s = SetlxSet([42])
    expected = stlx_from(s)

    eq_(expected, 42)
    eq_(s, SetlxSet([]))  
    
#12    
def test_fromB():
    s = SetlxSet([1,2,3])
    expected = stlx_fromB(s)

    eq_(expected, 1)
    eq_(s, SetlxSet([2, 3]))  
    
#13  
@nottest  
def test_fromE():
    s = SetlxSet([1,2,3])
    expected = stlx_fromE(s)

    eq_(expected, 3)
    eq_(s, SetlxSet([1, 2]))     

#14
def test_domain():
    actual = stlx_domain( SetlxSet([[1,2],[1,3],[5,7]]) )
    expected =  SetlxSet([1,5])
    eq_(expected, actual)
    
#17
def test_powerset():
    actual = stlx_powerset( SetlxSet([1, 2, 3]) )
    expected = SetlxSet([SetlxSet(), SetlxSet([1]), SetlxSet([1, 2]), SetlxSet([1, 2, 3]), 
                         SetlxSet([1, 3]), SetlxSet([2]), SetlxSet([2, 3]), SetlxSet([3])])
    eq_(SetlxSet([1,2,3]), SetlxSet([3,2,1]))
    eq_(expected, actual)
    
#18
def test_range():    
    actual = stlx_range( SetlxSet([[1,2],[1,3],[5,7]]) )
    expected = SetlxSet([2,3,7])
    eq_(expected, actual) 