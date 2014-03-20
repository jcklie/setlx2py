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