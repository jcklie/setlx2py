from nose.tools import with_setup, eq_

from setlx2py.setlx_lexer import Lexer
from setlx2py.setlx_parser import Parser

######################--   TEST UTIL --######################

global parser

def setup_func():
    global parser
    parser = Parser()

def teardown_func():
    parser = None

def assert_binop(text, operator, left, right):
    node = parser.parse(text)
    assert node.op == operator
    assert node.left.value == left
    assert node.right.value == right

######################--   ASSERTS   --######################  


######################--   TESTS     --######################

@with_setup(setup_func, teardown_func)
def test_should_be_creatable():
    assert parser is not None

def test_atomic_value_int():
    node = parser.parse("42;")
    assert node.value == 42

def test_atomic_value_double():
    node = parser.parse("42.0;")
    assert abs(node.value - 42.0) < .001

def test_atomic_value_true():
    node = parser.parse("true;")
    assert node.value is True

def test_atomic_value_false():
    node = parser.parse("false;")
    assert node.value is False

# Binary Operations

def test_binop_equivalence():
    assert_binop("true <==> true;", '<==>', True, True)

def test_binop_antivalence():
    assert_binop("true <!=> true;", '<!=>', True, True)    

def test_binop_implication():
    assert_binop("true => true;", '=>', True, True)    

def test_binop_or():
    assert_binop("true || false;", '||', True, False)

def test_binop_and():
    assert_binop("true && false;", '&&', True, False)

def test_binop_rel():
    assert_binop("true == false;", '==', True, False)
    assert_binop("true != false;", '!=', True, False)
    assert_binop("true <  false;",  '<', True, False)
    assert_binop("true <= false;", '<=', True, False)
    assert_binop("true >  false;",  '>', True, False)
    assert_binop("true >= false;", '>=', True, False)

def test_binop_contain():
    assert_binop("true    in false;", 'in',    True, False)
    assert_binop("true notin false;", 'notin', True, False)    