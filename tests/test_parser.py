from nose.tools import eq_, with_setup, nottest

from setlx2py.setlx_lexer import Lexer
from setlx2py.setlx_parser import Parser
from setlx2py.setlx_ast import *

######################--   TEST UTIL --######################

parser = Parser()

def setup_func():
    global parser
    parser = Parser()

def teardown_func():
    parser = None

##
## Misc helper
##


##
## Parse helper
##

@with_setup(setup_func, teardown_func)        
def parse_statements(text):    
    root = parser.parse(text) # FileAST
    return root # List of statements

def parse_single_statement(text):
    return parse_statements(text).stmts[0] # first statement after FileAST

##
## Custom asserts
##

def assert_unop(text, operator, val):
    node = parse_single_statement(text)
    eq_(node.op, operator)
    eq_(node.expr.value, val)

def assert_binop_from_node(node, operator, left, right):    
    eq_(node.op, operator)
    eq_(node.left.value, left)
    eq_( node.right.value, right)
    
def assert_binop(text, operator, left, right):
    node = parse_single_statement(text)
    assert_binop_from_node(node, operator, left, right)

def assert_binop_triade(text, op1, op2, left, middle, right):
    """
    Asserts whether an expression of three operands
    and two binary operations are parsed as expected.

    The tree representation tested looks like the following:

    BinaryOp: op2
      BinaryOp: op1
        Constant: left
        Constant: middle
      Constant: right
    """
    binop1 = parse_single_statement(text)
    binop2 = binop1.left
    const = binop1.right
    try:
        eq_(binop1.op, op2)
        eq_(binop2.op, op1)
        eq_(binop2.left.value, left)
        eq_(binop2.right.value, middle)
        eq_(binop1.right.value, right)
    except AssertionError as e:
        binop1.show()
        raise e

def assert_assignment(text, operator, left, right):
    """ Asserts that a given assignment has the
    expected operator, left- and ride hand side.

    Args:
        text: The string containing an assignment
        operator: The expected assignment operator 
        left: The expected left hand side variable
        right: The expected right hand side variable
    Raises:
        AssertionError: if result != expected
    """
    try:
        node = parse_single_statement(text)
        eq_(node.op, operator)
        eq_(node.left.name, left)
        eq_( node.right.value, right)
    except AssertionError as e:
        node.show()
        raise e

def assert_member_access_equals(node, obj=None, field=None):
    """ Asserts that a given member access (e.g. foo.bar,
    where name=foo, bar=field) has the expected name and
    field.

    Args:
        node: The MemberAccess AST node
        obj: Name of the object accessed
        field: Name of the field accessed
    Raises:
        AssertionError: if result != expected
    """

    if obj is not None: eq_(node.obj.name, obj)
    if field is not None: eq_(node.field.name, field)

def assert_array_ref_equals(node, obj=None, subscript=None):
    """ Asserts that a given array reference (e.g. foo[0],
    where name=foo, subscript=0), has the expected name
    and subscript.

    Args:
        node: The ArrayRef AST node
        obj: The object which is accessed by subscript
        subscript: The subscript of the access
    Raises:
        AssertionError: if result != expected
    """
    try:
        if obj is not None: eq_(node.obj.name, obj)
        if subscript is not None: eq_(node.subscript.value, subscript)
    except AssertionError as e:
        node.show()
        raise e

def assert_assignment_explicit(text, operator, left, right):
    node = parse_single_statement(text)
    eq_(node.op, operator)
    for var, l in zip(node.left.assignments, left):
        eq_(var.name, l)
    eq_(node.right.value, right)
    
##
## Tests
##

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
    assert_binop_triade('4 + 2 + 0;', '+', '+', 4, 2, 0)
    assert_binop_triade('true || false || true;', '||', '||', True, False, True)
    assert_binop_triade('true && false && true;', '&&', '&&', True, False, True)
    assert_binop_triade('4 % 2 * 0;', '%', '*', 4, 2, 0)
    assert_binop_triade('4 +/ 2 */ 0;', '+/', '*/', 4, 2, 0)

def test_more_than_one_statement_simple():
    nodes = parse_statements('1 + 2; 3 * 4;')
    stmt1,stmt2 = nodes.stmts
    assert_binop_from_node(stmt1, '+', 1, 2)
    assert_binop_from_node(stmt2, '*', 3, 4)   

def test_term_single_arg():
    node = parse_single_statement('F(true);')
    eq_(True, isinstance(node, Term))
    expression = node.args
    eq_(True, expression.value)

def test_term_multi_arg():
    node = parse_single_statement('F(true, false);')
    eq_(True, isinstance(node, Term))
    e1, e2 = node.args.exprs
    eq_(True, e1.value)
    eq_(False, e2.value)

def test_assignable_member_access():
    """
    Assignment: :=
        MemberAccess:
            Variable: foo
            Variable: bar
        Constant: int, 42
    """
    assignment = parse_single_statement('foo.bar := true;')
    member_access = assignment.left

    assert_member_access_equals(member_access, 'foo', 'bar')


def test_assignable_member_access_chained():
    """
    Assignment: :=
        MemberAccess:            #1
            MemberAccess:        #2
                Variable: foo
                Variable: bar
        Variable: baz
        Constant: int, 42
    """
    assignment = parse_single_statement('foo.bar.baz := 42;')
    member_access1 = assignment.left
    member_access2 = member_access1.obj

    assert_member_access_equals(member_access2, 'foo', 'bar')
    assert_member_access_equals(member_access1, field='baz')

def test_assignable_array_ref():
    assignment = parse_single_statement('foo[0] := true;')
    array_ref = assignment.left

    assert_array_ref_equals(array_ref, 'foo', 0)

def test_assignable_array_ref_chained():
    """ 
    ArrayRef:                    #1
        ArrayRef:                #2
            Variable: foo
            Constant: int, 0
        Constant: int, 1
    """
    assignment = parse_single_statement('foo[0][1] := true;')
    array_ref1 = assignment.left
    array_ref2 = array_ref1.obj

    assert_array_ref_equals(array_ref2, 'foo', 0)
    assert_array_ref_equals(array_ref1, subscript=1)
    
def test_assignment():
    assert_assignment('foo := 42;', ':=',  'foo', 42)
    assert_assignment('_ := true;', ':=',  'unused', True)
    assert_assignment('foo += 42;', '+=',  'foo', 42)
    assert_assignment('foo -= 1;',  '-=',  'foo', 1)
    assert_assignment('foo *= 2;',  '*=',  'foo', 2)
    assert_assignment('foo /= 2;',  '/=',  'foo', 2)
    assert_assignment('foo \\= 3;', '\\=', 'foo', 3)
    assert_assignment('foo %= 10;', '%=',  'foo', 10)

def test_assignment_explicit():
    assert_assignment('[foo] := 42;', ':=', 'foo', 42)
    assert_assignment_explicit('[foo, bar] := 42;', ':=', ['foo', 'bar'], 42)