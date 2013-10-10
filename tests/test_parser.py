from nose.tools import eq_, with_setup

from setlx2py.setlx_lexer import Lexer
from setlx2py.setlx_parser import Parser

######################--   TEST UTIL --######################

parser = Parser()

def setup_func():
    global parser
    parser = Parser()

def teardown_func():
    parser = None
  
@with_setup(setup_func, teardown_func)    
def assert_binop(text, operator, left, right):
    node = parser.parse(text)
    eq_(node.op, operator)
    eq_(node.left.value, left)
    eq_( node.right.value, right)

@with_setup(setup_func, teardown_func)
def assert_unop(text, operator, val):
    node = parser.parse(text)
    eq_(node.op, operator)
    eq_(node.expr.value, val)
    
######################--   TESTS     --######################

def test_should_be_creatable():
    assert parser is not None

def test_atomic_value_int():
    node = parser.parse('42;')
    eq_(node.value, 42)

def test_atomic_value_double():
    node = parser.parse('42.0;')
    assert abs(node.value - 42.0) < .001

def test_atomic_value_true():
    node = parser.parse('true;')
    eq_(node.value, True)

def test_atomic_value_false():
    node = parser.parse('false;')
    eq_(node.value,  False)

# Binary Operations

def test_binop_boolean():
    assert_binop('true <==> true;', '<==>', True, True)
    assert_binop('true <!=> true;', '<!=>', True, True)    
    assert_binop('true => true;', '=>', True, True)    
    assert_binop('true || false;', '||', True, False)
    assert_binop('true && false;', '&&', True, False)
    assert_binop('true == false;', '==', True, False)
    assert_binop('true != false;', '!=', True, False)
    assert_binop('true <  false;',  '<', True, False)
    assert_binop('true <= false;', '<=', True, False)
    assert_binop('true >  false;',  '>', True, False)
    assert_binop('true >= false;', '>=', True, False)

def test_binop_contain():
    assert_binop('true    in false;',    'in', True, False)
    assert_binop('true notin false;', 'notin', True, False)

def test_binop_sum():
    assert_binop('42 + 43;', '+', 42, 43)
    assert_binop('42 - 43;', '-', 42, 43)

def test_binop_product():
    assert_binop('42 *  43;',  '*', 42, 43)
    assert_binop('42 /  43;',  '/', 42, 43)
    assert_binop('42 \  43;', '\\', 42, 43)
    assert_binop('42 %  43;',  '%', 42, 43)
    assert_binop('42 >< 43;', '><', 42, 43)
    assert_binop('42 ** 43;', '**', 42, 43)

def test_binop_reduce():
    assert_binop('42 +/ 43;', '+/', 42, 43)
    assert_binop('42 */ 43;', '*/', 42, 43)

# Unary operations

def test_unop_prefix():
    assert_unop('+/ 42;', '+/', 42)
    assert_unop('*/ 42;', '*/', 42)
    assert_unop('-  42;',  '-', 42)
    assert_unop('#  42;',  '#', 42)
    assert_unop('@  42;',  '@', 42)
                