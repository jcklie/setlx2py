from nose.tools import eq_, nottest

import sys
import random
import math as m

from StringIO import StringIO

from setlx2py.builtin.setlx_functions import *

def assert_almost_equals(a, b):
    assert abs(a-b) < 0.0001

# Functions and Operators on Sets and Lists

def test_arb():
    random.seed(42)
    s = SetlxSet([42])

    result = stlx_arb(s)
    eq_(result, 42)
    eq_(s, SetlxSet([42]))
    
def test_from():
    s = SetlxSet([42])
    result = stlx_from(s)

    eq_(result, 42)
    eq_(s, SetlxSet([]))  

# Mathematical Functions

def test_implies():
    assert stlx_implies(True,True)   == True
    assert stlx_implies(True,False)  == False
    assert stlx_implies(False,True)  == True
    assert stlx_implies(False,False) == True

def test_equivalent():
    assert stlx_equivalent(True,True)   == True
    assert stlx_equivalent(True,False)  == False
    assert stlx_equivalent(False,True)  == False
    assert stlx_equivalent(False,False) == True

def test_antivalent():
    assert stlx_antivalent(True,True)   == False
    assert stlx_antivalent(True,False)  == True
    assert stlx_antivalent(False,True)  == True
    assert stlx_antivalent(False,False) == False

def test_product():
    assert stlx_product(range(1,5)) == 24
    assert stlx_product([1,5,34,5,6,8]) == (1 * 5 * 34 * 5 * 6 * 8)
    
def test_trigonometric():
    X = 0.42
    assert_almost_equals(stlx_sin(X), m.sin(X))
    assert_almost_equals(stlx_cos(X), m.cos(X))
    assert_almost_equals(stlx_tan(X), m.tan(X))
    assert_almost_equals(stlx_asin(X), m.asin(X))
    assert_almost_equals(stlx_acos(X), m.acos(X))
    assert_almost_equals(stlx_atan(X), m.atan(X))
    
def test_domain():
    eq_(stlx_domain( SetlxSet([[1,2],[1,3],[5,7]]) ), SetlxSet([1,5]))
    
# Custom/Overloaded set Operations
# ----------

def test_cartesian_two():
    s1 = SetlxSet([1,2])
    s2 = SetlxSet([2,3])
    result = SetlxSet(stlx_cartesian(s1, s2))
    eq_(result, SetlxSet([(1, 2), (1, 3), (2, 2), (2, 3)]))

def test_cartesian_three():
    expected = [(1, 'a', 4), (1, 'a', 5), (1, 'b', 4), (1, 'b', 5),
                (2, 'a', 4), (2, 'a', 5), (2, 'b', 4), (2, 'b', 5),
                (3, 'a', 4), (3, 'a', 5), (3, 'b', 4), (3, 'b', 5)]
    eq_(stlx_cartesian([1,2,3],['a','b'],[4,5]), SetlxSet(expected))
        
# ========

def test_matches():
    # case []
    p = Pattern(0, False)
    assert stlx_matches(p , [])
    assert not stlx_matches(p, [1])                

    # case [a,b]
    assert stlx_matches(Pattern(2, False), [1, 2])           

    # case [a,b|c]
    assert stlx_matches(Pattern(2, True), [1, 2])      

    # case [a,b,c]
    p = Pattern(3, False)
    assert not stlx_matches(p, [1, 2])
    assert stlx_matches(p, [1,2,3])
    assert not stlx_matches(p, [1, 2, 3, 4])  

    # case [a,b,c|d]
    p = Pattern(3, True)
    assert stlx_matches(p, [1, 2, 3]) 
    assert not stlx_matches(p, [1, 2])

def test_bind_list_simple():
    # match ([1,2,3]) { case [a,b,c] : .. }
    matchee = SetlxList([1,2,3])
    a, b, c = stlx_bind(Pattern(3, False), matchee)
    eq_(a,1)
    eq_(b,2)
    eq_(c,3)

def test_bind_list_tail():
    # match ([1..5]) { case [a,b|c] : .. }
    matchee = SetlxList([1,2,3,4,5])
    a, b, c = stlx_bind(Pattern(2, True), matchee)
    eq_(a,1)
    eq_(b,2)
    eq_(c,SetlxList([3,4,5]))

def test_bind_string_single():
    # match ("a") { case [a] : .. }
    matchee = SetlxString("a")
    a, = stlx_bind(Pattern(1, False), matchee)
    eq_(a, SetlxString("a"))

def test_bind_string_single_tail():
    # match ("a") { case [a] : .. }
    matchee = SetlxString("a")
    a, b = stlx_bind(Pattern(1, True), matchee)
    eq_(a, SetlxString("a"))
    eq_(b, Bumper())

def test_bind_string_three():
    # match ("abc") { case [a,b,c] : .. }
    matchee = SetlxString("abc")
    a, b, c = stlx_bind(Pattern(3, False), matchee)
    eq_(a, SetlxString("a"))
    eq_(b, SetlxString("b"))
    eq_(c, SetlxString("c"))

def test_bind_string_tail_minimal():
    # match ("ab") { case [a|b] : .. }
    matchee = SetlxString("ab")
    a, b = stlx_bind(Pattern(1, True), matchee)
    eq_(a, SetlxString("a"))
    eq_(b, SetlxString("b"))

def test_bind_string_tail_longer_string():
    # match ("abcdef") { case [a|b] : .. }
    matchee = SetlxString("abcdef")
    a, b = stlx_bind(Pattern(1, True), matchee)
    eq_(a, SetlxString("a"))
    eq_(b, SetlxString("bcdef"))

def test_print():
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    stlx_print('Foo ', 'Bar ', 'baz')
    result =  mystdout.getvalue()
    sys.stdout = old_stdout
    eq_(result, 'Foo Bar baz\n')

def test_range():
    eq_( SetlxList(stlx_range(0,5)), SetlxList([0, 1, 2, 3, 4, 5]))
    eq_( SetlxList(stlx_range(0,2,5)), SetlxList([0,2,4]))
    eq_( SetlxList(stlx_range(-3,-1)), SetlxList([-3, -2, -1]))
    eq_( SetlxList(stlx_range(10,8,1)), SetlxList([10, 8, 6, 4, 2]))
    