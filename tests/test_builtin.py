from nose.tools import eq_, nottest

from setlx2py.setlx_builtin import *

def test_implies():
    assert implies(True,True)   == True
    assert implies(True,False)  == False
    assert implies(False,True)  == True
    assert implies(False,False) == True

def test_equivalent():
    assert equivalent(True,True)   == True
    assert equivalent(True,False)  == False
    assert equivalent(False,True)  == False
    assert equivalent(False,False) == True

def test_antivalent():
    assert antivalent(True,True)   == False
    assert antivalent(True,False)  == True
    assert antivalent(False,True)  == True
    assert antivalent(False,False) == False

def test_product():
    assert product(range(1,5)) == 24
    assert product([1,5,34,5,6,8]) == (1 * 5 * 34 * 5 * 6 * 8)

# Custom/Overloaded set Operations
# ----------

def test_set_operations():
    s1 = Set([1,2])
    s2 = Set([2,3])
    
    eq_(s1 + s2, Set([1,2,3]))
    eq_(s1 - s2, Set([1]))
    eq_(s1 * s2, Set([2]))
    eq_(s1 % s2, Set([1, 3]) )
    eq_(custom_pow(s1, 2), Set([(1, 1), (1, 2), (2, 1), (2, 2)]))
    eq_(custom_pow(2, s2), Set([(), (2,), (2,3), (3,)]))
    eq_(cartesian(s1, s2), Set([(1, 2), (1, 3), (2, 2), (2, 3)]))

# Matching
# ========

def test_matches():
    # case []
    p = Pattern(0, False)
    assert matches(p , [])
    assert not matches(p, [1])                

    # case [a,b]
    assert matches(Pattern(2, False), [1, 2])           

    # case [a,b|c]
    assert matches(Pattern(2, True), [1, 2])      

    # case [a,b,c]
    p = Pattern(3, False)
    assert not matches(p, [1, 2])
    assert matches(p, [1,2,3])
    assert not matches(p, [1, 2, 3, 4])  

    # case [a,b,c|d]
    p = Pattern(3, True)
    assert matches(p, [1, 2, 3]) 
    assert not matches(p, [1, 2])

@nottest    
def test_bind():
    # match ([1,2,3]) { case [a,b,c] : .. }
    s = bind(Pattern(['a', 'b', 'c']))
    print(s)

    # match ([1..42]) { case [a,b|c] : .. }
    s = bind(Pattern(['a', 'b'], 'r' ))
    print(s)