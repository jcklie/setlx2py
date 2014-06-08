#------------------------------------------------------------------------------
# setlx2py: test_list.py
#
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from nose.tools import eq_

from setlx2py.builtin.setlx_list import SetlxList

def test_get():
    lst = SetlxList([1,2,3,4,5])
    for i, item in enumerate(lst):
        eq_(item, lst[i+1])
        
def test_set_index_gt_len():
    lst = SetlxList([1,2,3,4,5])
    lst[10] = 10
    eq_(len(lst), 10)
    eq_(lst[10], 10)

def test_slice_lower_upper():
    lst = SetlxList(range(1,10 + 1))
    sliced = lst[5:10]
    eq_(type(sliced), SetlxList) 
    eq_(sliced, SetlxList(range(5,10 + 1)))

def test_slice_lower_border_only():
    lst = SetlxList([1,2,3])
    sliced = lst[2:]
    eq_(type(sliced), SetlxList) 
    eq_(sliced, SetlxList([2, 3]))

def test_slice_upper_border_only():
    lst = SetlxList([1,2,3])
    sliced = lst[:2]
    eq_(type(sliced), SetlxList) 
    eq_(sliced, SetlxList([1, 2]))

def test_assignment_deconstruction():
    lst = SetlxList([1,2,3])
    a, b, c = lst
    eq_(a, 1)
    eq_(b, 2)
    eq_(c, 3)

def test_concat():
    lst1 = SetlxList([1,2])
    lst2 = SetlxList([3,4])
    lst = lst1 + lst2
    eq_(type(lst), SetlxList)
    eq_(lst, SetlxList([1,2,3,4]))