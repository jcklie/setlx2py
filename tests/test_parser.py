from nose.tools import eq_, with_setup, nottest

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
def parse_single_statement(text):
    root = parser.parse(text) # FileAST
    return root.stmt # First statement of AST

def assert_binop(text, operator, left, right):
    node = parse_single_statement(text)
    eq_(node.op, operator)
    eq_(node.left.value, left)
    eq_( node.right.value, right)

def assert_unop(text, operator, val):
    node = parse_single_statement(text)
    eq_(node.op, operator)
    eq_(node.expr.value, val)
    
######################--   TESTS     --######################

@with_setup(setup_func, teardown_func)        
def test_should_be_creatable():
    assert parser is not None

def test_atomic_value_int():
    node = parse_single_statement('42;')
    eq_(node.value, 42)

def test_atomic_value_double():
    node = parse_single_statement('42.0;')
    assert abs(node.value - 42.0) < .001

def test_atomic_value_true():
    node = parse_single_statement('true;')
    eq_(node.value, True)

def test_atomic_value_false():
    node = parse_single_statement('false;')
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
    assert_unop('+/ 42;',  '+/', 42)
    assert_unop('*/ 42;',  '*/', 42)
    assert_unop('-  42;',   '-', 42)
    assert_unop('#  42;',   '#', 42)
    assert_unop('@  42;',   '@', 42)
    assert_unop('!true;', 'not', True)
    assert_unop('1337!;', 'fac', 1337)

def test_more_than_one_operand():
    nodes = parse_single_statement('4 + 2 + 0;')

@nottest    
def test_more_than_one_statement():
    nodes = parse_single_statement("42 + 3; 1 + 3 + 3 + 7;")