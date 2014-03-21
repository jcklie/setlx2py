#------------------------------------------------------------------------------
# setlx2py: test_parser.py
#
# Unit tests for the Parser class in setlx_parser.py
# Beware: Only the syntax is tested here!
#         Some of the code does not make semantically sense at all!
#
# Copyright (C) 2013, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from nose.tools import eq_, with_setup, nottest

from setlx2py.setlx_lexer import Lexer
from setlx2py.setlx_parser import Parser
from setlx2py.setlx_ast import *

##
## Test housekeeping
##

parser = Parser()

##
## Parse helper
##

def parse_statements(text):    
    root = parser.parse(text) # FileAST
    return root # List of statements

def parse_single_statement(text):
    return parse_statements(text).stmts[0] # first statement after FileAST

##
## Custom asserts
##

def assert_unop(text, operator, typ, val):
    node = parse_single_statement(text)
    eq_(node.to_tuples(),
        ('UnaryOp', operator, ('Constant', typ, val)))

def assert_binop_from_node(node, operator, left, right):    
    eq_(node.op, operator)
    eq_(node.left.value, left)
    eq_( node.right.value, right)
    
def assert_binop(text, operator, left, right):
    node = parse_single_statement(text)
    assert_binop_from_node(node, operator, left, right)

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
        eq_(node.target.name, left)
        eq_( node.right.value, right)
    except AssertionError as e:
        node.show()
        raise e

def assert_assignment_explicit(text, operator, left, right):
    node = parse_single_statement(text)
    eq_(node.op, operator)
    for var, l in zip(node.left.assignments, left):
        eq_(var.name, l)
    eq_(node.right.value, right)

#    _______       _
#   |__   __|     | |
#      | | ___ ___| |_ ___
#      | |/ _ / __| __/ __|
#      | |  __\__ | |_\__ \
#      |_|\___|___/\__|___/
                                       
def test_should_be_creatable():
    assert parser is not None
    
##
## Atomic Values
##    

def test_atomic_value_int():
    node = parse_single_statement('42;')
    eq_(node.to_tuples(), ('Constant', 'int', 42))

def test_atomic_value_double():
    node = parse_single_statement('42.0;')
    eq_(node.to_tuples(), ('Constant', 'double', 42.0))

def test_atomic_value_true():
    node = parse_single_statement('true;')
    eq_(node.to_tuples(), ('Constant', 'bool', True))

def test_atomic_value_false():
    node = parse_single_statement('false;')
    eq_(node.to_tuples(), ('Constant', 'bool', False))

##
## Collections
##

# List

def test_list_minimal():
    node = parse_single_statement('[];')

def test_list_single_element():
    node = parse_single_statement('[foo];')
    eq_(node.to_tuples(),
        ('List',
         ('Identifier', 'foo')))

def test_list_two_elements():
    node = parse_single_statement('[foo,bar];')
    eq_(node.to_tuples(),
        ('List',
         ('Identifier', 'foo'),
         ('Identifier', 'bar')))

def test_list_three_elements():
    node = parse_single_statement('[foo,bar,baz];')
    eq_(node.to_tuples(),
        ('List',
         ('Identifier', 'foo'),
         ('Identifier', 'bar'),
         ('Identifier', 'baz')))

def test_list_head_tail():
    node = parse_single_statement('[h|t];')
    eq_(node.to_tuples(),
        ('Pattern',
         ('Identifier', 'h'),
         ('Identifier', 't')))

# Set

def test_set_minimal():
    node = parse_single_statement('{};')

def test_set_single_element():
    node = parse_single_statement('{foo};')
    eq_(node.to_tuples(),
        ('Set',
         ('Identifier', 'foo')))

def test_set_two_elements():
    node = parse_single_statement('{foo,bar};')
    eq_(node.to_tuples(),
        ('Set',
         ('Identifier', 'foo'),
         ('Identifier', 'bar')))

def test_set_three_elements():
    node = parse_single_statement('{foo,bar,baz};')
    eq_(node.to_tuples(),
        ('Set',
         ('Identifier', 'foo'),
         ('Identifier', 'bar'),
         ('Identifier', 'baz')))

def test_set_head_tail():
    node = parse_single_statement('{h|t};')
    eq_(node.to_tuples(),
        ('Pattern',
         ('Identifier', 'h'),
         ('Identifier', 't')))
    
##
## Ranges
##

# List

def test_atomic_value_list_ab():
    node = parse_single_statement('[1 .. 10];')
    eq_(node.to_tuples(),
        ('Range', 'list',
         ('Constant', 'int', 1),
         ('Constant', 'int', 10)))

def test_atomic_value_list_abc():
    node = parse_single_statement('[a,b..c];')
    eq_(node.to_tuples(),
        ('Range', 'list',
         ('Identifier', 'a'),
         ('Identifier', 'b'),
         ('Identifier', 'c')))    
    
# Set

def test_atomic_value_set_ab():
    node = parse_single_statement('{a..b};')
    eq_(node.to_tuples(),
        ('Range', 'set',
         ('Identifier', 'a'),
         ('Identifier', 'b')))

def test_atomic_value_set_abc():
    node = parse_single_statement('{a,b..c};')
    eq_(node.to_tuples(),
        ('Range', 'set',
         ('Identifier', 'a'),
         ('Identifier', 'b'),
         ('Identifier', 'c')))

##
## Comprehension
##

# Set

def test_set_comprehension_minimal():
    node = parse_single_statement('{p: p in x};')
    eq_(node.to_tuples(),
        ('Comprehension', 'set',
         ('Identifier', 'p'),
         ('Iterator',
          ('Identifier', 'p'),
          ('Identifier', 'x'))))

def test_set_comprehension_two_iterators():
    node = parse_single_statement('{a * b: a in {1..3}, b in {1..3}};')
    eq_(node.to_tuples(),
        ('Comprehension', 'set',
         ('BinaryOp', '*',
          ('Identifier', 'a'),
          ('Identifier', 'b')),
         ('IteratorChain', 'cartesian',
          ('Iterator',
           ('Identifier', 'a'),
           ('Range', 'set',
            ('Constant', 'int', 1),
            ('Constant', 'int', 3))),
          ('Iterator',
           ('Identifier', 'b'),
           ('Range', 'set',
            ('Constant', 'int', 1),
            ('Constant', 'int', 3))))))

def test_set_comprehension_prime():
    s = """{ p : p in {2..100} | { x : x in {1..p} | p % x == 0 } == {1, p} };"""
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Comprehension', 'set',
         ('Identifier', 'p'),
         ('Iterator',
          ('Identifier', 'p'),
          ('Range', 'set',
           ('Constant', 'int', 2),
           ('Constant', 'int', 100))),
         ('BinaryOp', '==',
          ('Comprehension', 'set',
           ('Identifier', 'x'),
           ('Iterator',
            ('Identifier','x'),
            ('Range', 'set',
             ('Constant', 'int', 1),
             ('Identifier', 'p'))),
           ('BinaryOp', '==',
            ('BinaryOp', '%',
             ('Identifier', 'p'),
             ('Identifier', 'x')),
            ('Constant', 'int', 0))),
          ('Set',
           ('Constant', 'int', 1),
           ('Identifier', 'p')))))

# List

def test_list_comprehension_minimal():
    node = parse_single_statement('[p: p in x];')
    eq_(node.to_tuples(),
        ('Comprehension', 'list',
         ('Identifier', 'p'),
         ('Iterator',
          ('Identifier', 'p'),
          ('Identifier', 'x'))))

def test_list_comprehension_two_iterators():
    node = parse_single_statement('[a * b: a in {1..3}, b in {1..3}];')
    eq_(node.to_tuples(),
        ('Comprehension', 'list',
         ('BinaryOp', '*',
          ('Identifier', 'a'),
          ('Identifier', 'b')),
         ('IteratorChain', 'cartesian',
          ('Iterator',
           ('Identifier', 'a'),
           ('Range', 'set',
            ('Constant', 'int', 1),
            ('Constant', 'int', 3))),
          ('Iterator',
           ('Identifier', 'b'),
           ('Range', 'set',
            ('Constant', 'int', 1),
            ('Constant', 'int', 3))))))

def test_list_comprehension_prime():
    s = """[ p : p in {2..100} | [ x : x in {1..p} | p % x == 0 ] == {1, p} ];"""
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Comprehension', 'list',
         ('Identifier', 'p'),
         ('Iterator',
          ('Identifier', 'p'),
          ('Range', 'set',
           ('Constant', 'int', 2),
           ('Constant', 'int', 100))),
         ('BinaryOp', '==',
          ('Comprehension', 'list',
           ('Identifier', 'x'),
           ('Iterator',
            ('Identifier','x'),
            ('Range', 'set',
             ('Constant', 'int', 1),
             ('Identifier', 'p'))),
           ('BinaryOp', '==',
            ('BinaryOp', '%',
             ('Identifier', 'p'),
             ('Identifier', 'x')),
            ('Constant', 'int', 0))),
          ('Set',
           ('Constant', 'int', 1),
           ('Identifier', 'p')))))
    
##
## Variables
##

def test_variables():
    node = parse_single_statement('foo;')
    eq_(node.to_tuples(),
        ('Identifier', 'foo'))

##    
## Binary Operations
##

def test_binop_boolean():
    assert_binop('true <==> true;', '<==>', True, True)
    assert_binop('true <!=> true;', '<!=>', True, True)    
    assert_binop('true => true;',     '=>', True, True)    
    assert_binop('true || false;',    '||', True, False)
    assert_binop('true && false;',    '&&', True, False)
    assert_binop('"foo" == \'bar\';', '==', "foo", "bar")
    assert_binop('true != false;',    '!=', True, False)
    assert_binop('1 <  2;',            '<', 1, 2)
    assert_binop('true <= false;',    '<=', True, False)
    assert_binop('true >  false;',     '>', True, False)
    assert_binop('true >= false;',    '>=', True, False)    

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

def test_expr_paren_simple():
    node = parse_single_statement('(foo + bar);')
    eq_(node.to_tuples(),
        ('BinaryOp', '+',
         ('Identifier', 'foo'),
         ('Identifier', 'bar')))

##    
## Precedence
##

def test_three_operands_precedence_and_or():
    node = parse_single_statement('true && false || true;')
    eq_(node.to_tuples(),
        ('BinaryOp', '||',
         ('BinaryOp', '&&',
          ('Constant', 'bool', True),
          ('Constant', 'bool', False)),
         ('Constant', 'bool', True)))

def test_three_operands_precedence_minus_divide():
    node = parse_single_statement('8 - 4 / 2.0;')
    eq_(node.to_tuples(),
        ('BinaryOp', '-',
         ('Constant', 'int', 8),
         ('BinaryOp', '/',
          ('Constant', 'int', 4 ),
          ('Constant', 'double', 2.0 ))))

def test_precendce_arithmetic():
    node = parse_single_statement('a + b  * c / ( d - e );')
    eq_(node.to_tuples(),
        ('BinaryOp', '+',
         ('Identifier', 'a'),
         ('BinaryOp', '/',
          ('BinaryOp', '*',
           ('Identifier', 'b'),
           ('Identifier', 'c')),
          ('BinaryOp', '-',
           ('Identifier', 'd'),
           ('Identifier', 'e')))))    

##
## Unary operations
##
    
def test_unop():
    assert_unop('+/ 42;',  '+/', 'int', 42)
    assert_unop('*/ 42;',  '*/', 'int', 42)
    assert_unop('-  42;',   '-', 'int', 42)
    assert_unop('#  42;',   '#', 'int', 42)
    assert_unop('@  42;',   '@', 'int', 42)
    assert_unop('!true;', 'not', 'bool', True)
    assert_unop('1337!;', 'fac', 'int', 1337)

####    
##
## Simple Statements
##
####
    
def test_more_than_one_statement_simple():
    stmts = parse_statements('1 + 2; 3 * 4;')
    eq_(stmts.to_tuples(),
        ('FileAST',
         ('BinaryOp', '+',
          ('Constant', 'int', 1),
          ('Constant', 'int', 2)),
         ('BinaryOp', '*',
          ('Constant', 'int', 3),
          ('Constant', 'int', 4))))

##
## Attributeref
##

def test_attributeref_minimal():
    node = parse_single_statement('x.y;')
    eq_(node.to_tuples(),
        ('AttributeRef',
         ('Identifier', 'x'),
         ('Identifier', 'y')))

def test_attributeref_chained():
    node = parse_single_statement('x.y.z;')
    eq_(node.to_tuples(),
        ('AttributeRef',
         ('AttributeRef',
          ('Identifier', 'x'),
          ('Identifier', 'y')),
         ('Identifier', 'z')))

##
## Subscription
##

def test_subscription_minimal():
    node = parse_single_statement('x[y];')
    eq_(node.to_tuples(),
        ('Subscription',
         ('Identifier', 'x'),
         ('Identifier', 'y')))

def test_subscription_chained():
    node = parse_single_statement('x[y][0];')
    eq_(node.to_tuples(),
        ('Subscription',
         ('Subscription',
          ('Identifier', 'x'),
          ('Identifier', 'y')),
         ('Constant', 'int', 0)))    
        
##
## Call
##

def test_call_minimal():
    node = parse_single_statement('foo();')
    eq_(node.to_tuples(),
        ('Call',
         ('Identifier', 'foo'),
         ('ArgumentList', )))

def test_call_one_argument():
    node = parse_single_statement('foo(bar);')
    eq_(node.to_tuples(),
        ('Call',
         ('Identifier', 'foo'),
         ('ArgumentList',
          ('Identifier', 'bar'))))

def test_call_two_arguments():
    node = parse_single_statement('foo(bar,baz);')
    eq_(node.to_tuples(),
        ('Call',
         ('Identifier', 'foo'),
         ('ArgumentList',
          ('Identifier', 'bar'),
          ('Identifier', 'baz'))))

def test_call_two_expressions():
    node = parse_single_statement('substring(size-1,size+3);')
    eq_(node.to_tuples(),
        ('Call',
         ('Identifier', 'substring'),
         ('ArgumentList',
          ('BinaryOp', '-', ('Identifier', 'size'), ('Constant', 'int', 1)),
          ('BinaryOp', '+', ('Identifier', 'size'), ('Constant', 'int', 3)))))

def test_call_chained():
    node = parse_single_statement('getCallback("onExit")();')
    eq_(node.to_tuples(),
        ('Call',
         ('Call',
          ('Identifier', 'getCallback'),
          ('ArgumentList',
           ('Constant', 'string', 'onExit'))),
         ('ArgumentList', )))

##
## Slicing
##

def test_slicing_left():
    node = parse_single_statement('list[..b];')
    eq_(node.to_tuples(),
        ('Slice',
         ('Identifier', 'list'),
         ('Identifier', 'b')))

def test_slicing_right():
    node = parse_single_statement('list[a..];')
    eq_(node.to_tuples(),
        ('Slice',
         ('Identifier', 'list'),
         ('Identifier', 'a')))
    
def test_slicing_both():
    node = parse_single_statement('list[a..b];')
    eq_(node.to_tuples(),
        ('Slice',
         ('Identifier', 'list'),
         ('Identifier', 'a'),
         ('Identifier', 'b'))) 
##
## Lambda
##

def test_lambda_minimal_zero_params():
    node = parse_single_statement('[ ] |-> true;')
    eq_(node.to_tuples(),
        ('Lambda',
         ('ParamList', ),
         ('Constant', 'bool', True)))

def test_lamba_minimal_one_param_no_brackets():
    node = parse_single_statement("foo |-> 'bar';")
    eq_(node.to_tuples(),
        ('Lambda',
         ('ParamList', ('Identifier', 'foo')),
         ('Constant', 'literal', 'bar')))

def test_lambda_minimal_one_param_brackets():
    node = parse_single_statement('x |-> x ** x;')
    eq_(node.to_tuples(),
        ('Lambda',
         ('ParamList', ('Identifier', 'x')),
         ('BinaryOp', '**',
          ('Identifier', 'x'),
          ('Identifier', 'x'))))

def test_lambda_two_params():
    node = parse_single_statement('[x,y] |-> x+y;')
    eq_(node.to_tuples(),
        ('Lambda',
         ('ParamList', ('Identifier', 'x'), ('Identifier', 'y')),
         ('BinaryOp', '+',
          ('Identifier', 'x'),
          ('Identifier', 'y'))))
    
##
## Assignment
##

def test_assignment_minimal():
    node = parse_single_statement('foo := 42;')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('Identifier', 'foo'),
         ('Constant', 'int', 42)))    
    
def test_assignment_underscore():
    node = parse_single_statement('_ := true;')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('Identifier', '_'),
         ('Constant', 'bool', True)))    

def test_assignment_explicit_minimal():
    node = parse_single_statement('foo := 42;')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('Identifier', 'foo'),
         ('Constant', 'int', 42)))

def test_assignment_explicit_two():
    node = parse_single_statement('[foo, bar] := "xy";')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('List',
          ('Identifier', 'foo'),
          ('Identifier', 'bar')),
         ('Constant', 'string', 'xy')))
    
def test_assignment_attributeref():
    assignment = parse_single_statement('foo.bar := true;')
    eq_(assignment.to_tuples(),
        ('Assignment', ':=',
        ('AttributeRef',
          ('Identifier', 'foo'),
          ('Identifier', 'bar')),
         ('Constant', 'bool', True)))

def test_assignment_member_access_chained():
    assignment = parse_single_statement('foo.bar.baz := 42;')
    eq_(assignment.to_tuples(),
        ('Assignment', ':=',
         ('AttributeRef',
          ('AttributeRef',
           ('Identifier', 'foo'),
           ('Identifier', 'bar')),
          ('Identifier', 'baz')),
         ('Constant', 'int', 42)))

def test_assignment_subscription():
    node = parse_single_statement('foo[0] := true;')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('Subscription',
          ('Identifier', 'foo'),
          ('Constant', 'int', 0)),
         ('Constant', 'bool', True)))

def test_assignment_subscription_chained():
    node = parse_single_statement('foo[0][1] := true;')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('Subscription',
          ('Subscription',
           ('Identifier', 'foo'),
           ('Constant', 'int', 0)),
          ('Constant', 'int', 1)),
         ('Constant', 'bool', True)))

def test_assignment_mixed_attributeref_subscription():
    node = parse_single_statement('foo[x+1].bar.baz[42][y**2] := z;')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('Subscription',
          ('Subscription',
           ('AttributeRef',
            ('AttributeRef',
             ('Subscription',
              ('Identifier', 'foo'),
              ('BinaryOp', '+', ('Identifier', 'x'), ('Constant', 'int', 1))),
             ('Identifier', 'bar')),
            ('Identifier', 'baz')),
           ('Constant', 'int', 42)),
          ('BinaryOp', '**', ('Identifier', 'y'), ('Constant', 'int', 2))),
         ('Identifier', 'z')))

##
## Augmented Assignment
##

def test_augmented_assignment():
    assert_assignment('foo += 42;', '+=',  'foo', 42)
    assert_assignment('foo -= 1;',  '-=',  'foo', 1)
    assert_assignment('foo *= 2;',  '*=',  'foo', 2)
    assert_assignment('foo /= 2;',  '/=',  'foo', 2)
    assert_assignment('foo \\= 3;', '\\=', 'foo', 3)
    assert_assignment('foo %= 10;', '%=',  'foo', 10)

##    
## Assert
##

def test_assert_simple():
    assert_stmt = parse_single_statement('assert(isOverflown, false);')
    eq_(assert_stmt.to_tuples(),
        ('Assert',
         ('Identifier', 'isOverflown'),
         ('Constant', 'bool', False)))

##
## Jump statements
##

def test_backtrack_statement():
    node = parse_single_statement('backtrack;')
    eq_(node.to_tuples(),
        ('Backtrack',))

def test_break_statement():
    node = parse_single_statement('break;')
    eq_(node.to_tuples(),
        ('Break',))

def test_continue_statement():
    node = parse_single_statement('continue;')
    eq_(node.to_tuples(),
        ('Continue',))

def test_break_statement():
    node = parse_single_statement('exit;')
    eq_(node.to_tuples(),
        ('Exit',))

def test_return_statement_void():
    node = parse_single_statement('return;')
    eq_(node.to_tuples(),
        ('Return',))

def test_return_statement_const():
    node = parse_single_statement('return 42;')
    eq_(node.to_tuples(),
        ('Return',
         ('Constant', 'int', 42)))

def test_return_statement_binop():
    node = parse_single_statement('return 42 ** 2;')
    eq_(node.to_tuples(),
        ('Return',
         ('BinaryOp', '**',
          ('Constant', 'int', 42),
          ('Constant', 'int', 2))))

##    
## Terms
##

def test_term_no_arguments():
    node = parse_single_statement('F();')
    eq_(node.to_tuples(),
        ('Term', 'F', ('ArgumentList',)))

def test_term_single_arg():
    node = parse_single_statement('F(true);')
    eq_(node.to_tuples(),
        ('Term', 'F',
         (('ArgumentList'),
          ('Constant', 'bool', True))))

def test_term_multi_arg():
    node = parse_single_statement('F(true, false);')
    eq_(node.to_tuples(),
        ('Term', 'F',
         ('ArgumentList', 
          ('Constant', 'bool', True),
          ('Constant', 'bool', False))))

##
## Quantifier
##

def test_quantifier_all():
    node =  parse_single_statement('forall (x in 1 | true);')
    eq_(node.to_tuples(),
        ('Quantor', 'all',
         ('Iterator',
          ('Identifier', 'x'),
          ('Constant', 'int', 1)),
         ('Constant', 'bool', True)))
    

def test_quantifier_exists():
    node =  parse_single_statement('exists (x in 1 | true);')
    eq_(node.to_tuples(),
        ('Quantor', 'any',
         ('Iterator',
          ('Identifier', 'x'),
          ('Constant', 'int', 1)),
         ('Constant', 'bool', True)))

def test_quantifier_cray():
    node = parse_single_statement('forall (n in [1 .. 10] | n**2 <= 2**n);')
    eq_(node.to_tuples(),
        ('Quantor', 'all',
         ('Iterator',
          ('Identifier', 'n'),
          ('Range', 'list',
           ('Constant', 'int', 1),
           ('Constant', 'int', 10))),
         ('BinaryOp', '<=',
          ('BinaryOp', '**',
           ('Identifier', 'n'),
           ('Constant', 'int', 2)),
          ('BinaryOp', '**',
           ('Constant', 'int', 2),
           ('Identifier', 'n')))))
    
####
##
## Compound Statements
##
####
    
##
## If statements
##

def test_if_minimal():
    node = parse_single_statement('if(true) {}')
    eq_(node.to_tuples(),
        ('If',
         ('Constant', 'bool', True),
         ('Block', )))

def test_if_no_else():
    node = parse_single_statement('if(x >= 5) { return true; }')
    eq_(node.to_tuples(),
        ('If',
         ('BinaryOp', '>=',
          ('Identifier', 'x'),
          ('Constant', 'int', 5)),
         ('Block',
          ('Return', ('Constant', 'bool', True)))))

def test_if_no_else_longer_block():
    s = """
    if(isRaining && isCold) {
        prediction := "Let it snow!";
        return prediction;
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('If',
         ('BinaryOp', '&&',
          ('Identifier', 'isRaining'),
          ('Identifier', 'isCold')),
         ('Block',
          ('Assignment', ':=',
           ('Identifier', 'prediction'),
           ('Constant', 'string', 'Let it snow!')),
          ('Return', ('Identifier', 'prediction')))))

# If-Else

def test_if_else_minimal():
    node = parse_single_statement("if(foo) {} else {}")
    eq_(node.to_tuples(),
        ('If',
         ('Identifier', 'foo'),
         ('Block',),
         ('Block',)))
    

def test_if_single_else():
    s = """
    if(i % 2 == 0) {
        return "Even";
    } else {
        return "Odd";
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('If',
         ('BinaryOp', '==',
          ('BinaryOp', '%',
           ('Identifier', 'i'),
           ('Constant', 'int', 2)),
          ('Constant', 'int', 0)),
         ('Block', ('Return', ('Constant', 'string', 'Even'))),
         ('Block', ('Return', ('Constant', 'string', 'Odd')))))

def test_if_else_if_else_simple():
    s = """
    if(isGreen) {
        return "Green";
    } else if(isRed) {
        return "Red";
    } else {
        return "Not green nor red";
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('If',
         ('Identifier', 'isGreen'),
         ('Block',
          ('Return', ('Constant', 'string', 'Green'))),
         ('If',
          ('Identifier', 'isRed'),
          ('Block',
           ('Return', ('Constant', 'string', 'Red'))),
          ('Block',
           ('Return', ('Constant', 'string', 'Not green nor red'))))))


def test_if_four_else_if_else():
    s = """
    if(grade == "A") {
        return "Excellent";
    } else if(grade == "B") {
        return "Good";
    } else if(grade == "C") {
        return "Satisfactory";
    } else if(grade == "D") {
        return "Pass";
    } else if(grade == "F") {
        return "Fail";
    } else {
        return "Invalid input";
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(), 
         ('If', ('BinaryOp', '==',
                 ('Identifier', 'grade'),
                 ('Constant', 'string', 'A')),
          ('Block', ('Return', ('Constant', 'string', 'Excellent'))),
          ('If', ('BinaryOp', '==',
                  ('Identifier', 'grade'),
                  ('Constant', 'string', 'B')),
           ('Block', ('Return', ('Constant', 'string', 'Good'))),
           ('If', ('BinaryOp', '==',
                   ('Identifier', 'grade'),
                   ('Constant', 'string', 'C')),
            ('Block', ('Return', ('Constant', 'string', 'Satisfactory'))),
            ('If', ('BinaryOp', '==',
                    ('Identifier', 'grade'),
                    ('Constant', 'string', 'D')),
             ('Block', ('Return', ('Constant', 'string', 'Pass'))),
             ('If', ('BinaryOp', '==',
                     ('Identifier', 'grade'),
                     ('Constant', 'string', 'F')),
              ('Block', ('Return', ('Constant', 'string', 'Fail'))),
              ('Block', ('Return', ('Constant', 'string', 'Invalid input')))))))))


def test_if_nested_else():
    s = """
    if(num1 == num2) {
        return "Equal";
    } else {
        if(num1 > num2) { 
            return "Num1 greater";
        } else {
            return "Num2 greater";
        }
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('If',
         ('BinaryOp', '==', ('Identifier', 'num1'), ('Identifier', 'num2')), 
         ('Block', ('Return', ('Constant', 'string', 'Equal'))),  
         ('Block',
          ('If',
           ('BinaryOp', '>', ('Identifier', 'num1'), ('Identifier', 'num2')),
           ('Block', ('Return', ('Constant', 'string', 'Num1 greater'))),
           ('Block', ('Return', ('Constant', 'string', 'Num2 greater')))))))

##
## Switch/Case
##

def test_switch_case_minimal():
    node = parse_single_statement('switch {}')
    eq_(node.to_tuples(),
        ('Switch',
         ('CaseList', )))

def test_switch_case_simple_no_default():
    s = """
    // Check whether an integer n is even
    switch {
        case n % 2 == 0 : return 'Even';
        case n % 2 == 1 : return 'Odd';
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Switch',
         ('CaseList',
          ('Case',
           ('BinaryOp', '==',
            ('BinaryOp', '%', ('Identifier', 'n'), ('Constant', 'int', 2)),
            ('Constant', 'int', 0)),
           ('Block', ('Return', ('Constant', 'literal', 'Even')))),
          ('Case',
           ('BinaryOp', '==',
            ('BinaryOp', '%', ('Identifier', 'n'), ('Constant', 'int', 2)),
            ('Constant', 'int', 1)),
           ('Block', ('Return', ('Constant', 'literal', 'Odd')))))))
    
def test_switch_case_with_default():
    s = """
    switch {
        case grade == 'A' : return 'Excellent';
        case grade == 'B' : return 'Good';
        case grade == 'C' : return 'Satisfactory';
        case grade == 'D' : return 'Pass';
        case grade == 'F' : return 'Fail';
        default           : return 'Invalid input';
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Switch',
         ('CaseList',
          ('Case',
           ('BinaryOp', '==', ('Identifier', 'grade'), ('Constant', 'literal', 'A')),
          ('Block', ('Return', ('Constant', 'literal', 'Excellent')))),
          ('Case',
           ('BinaryOp', '==', ('Identifier', 'grade'), ('Constant', 'literal', 'B')),
          ('Block', ('Return', ('Constant', 'literal', 'Good')))),
          ('Case',
           ('BinaryOp', '==', ('Identifier', 'grade'), ('Constant', 'literal', 'C')),
          ('Block', ('Return', ('Constant', 'literal', 'Satisfactory')))),
          ('Case',
           ('BinaryOp', '==', ('Identifier', 'grade'), ('Constant', 'literal', 'D')),
          ('Block', ('Return', ('Constant', 'literal', 'Pass')))),
          ('Case',
           ('BinaryOp', '==', ('Identifier', 'grade'), ('Constant', 'literal', 'F')),
          ('Block', ('Return', ('Constant', 'literal', 'Fail'))))),
          ('Default', ('Block', ('Return', ('Constant', 'literal', 'Invalid input'))))))

##
## Match
##


def test_match_minimal():
    s = """
    match(s) {
        case [] : return s;
    }

    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Match',
         ('Identifier', 's'),
         ('CaseList',
          ('MatchCase',
           ('List', ),
           ('Block',
            ('Return', ('Identifier', 's')))))))

def test_match_one_pattern():
    s = """
    match(s) {
        case [h|t] : return h;
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Match',
         ('Identifier', 's'),
         ('CaseList',
          ('MatchCase',
           ('Pattern',
            ('Identifier', 'h'),
            ('Identifier', 't')),
           ('Block',
            ('Return', ('Identifier', 'h')))))))

def test_match_one_pattern_default():
    s = """
    match(s) {
        case [h|t] : return 'Not empty!';
        default    : return 'Empty!';
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Match',
         ('Identifier', 's'),
         ('CaseList',
          ('MatchCase',
           ('Pattern',
            ('Identifier', 'h'),
            ('Identifier', 't')),
           ('Block',
            ('Return', ('Constant', 'literal', 'Not empty!'))))),
         ('Default',
          ('Block',
           ('Return', ('Constant', 'literal', 'Empty!'))))))

def test_match_two_cases():
    s = """
    match (s) {
      case [] : return "Empty";
      case [h|t]: return "Not empty";
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Match',
         ('Identifier', 's'),
         ('CaseList',
          ('MatchCase',
           ('List',),
           ('Block', ('Return', ('Constant', 'string', 'Empty')))),
          ('MatchCase',
           ('Pattern',
            ('Identifier', 'h'),
            ('Identifier', 't')),
           ('Block',
            ('Return', ('Constant', 'string', 'Not empty')))))))

def test_match_two_cases_default():
    s = """
    match (s) {
      case [h] : return h;
      case [h|t]: return t;
      default : return "Error!";
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Match',
         ('Identifier', 's'),
         ('CaseList',
          ('MatchCase',
           ('List', ('Identifier', 'h')),
           ('Block', ('Return', ('Identifier', 'h')))),
          ('MatchCase',
           ('Pattern',
            ('Identifier', 'h'),
            ('Identifier', 't')),
           ('Block',
            ('Return', ('Identifier', 't'))))),
          ('Default',
           ('Block',
            ('Return', ('Constant', 'string', 'Error!'))))))

def test_match_pattern_condition():
    s = """
    match(s) {
        case [h|t] | h != null: return h;
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Match',
         ('Identifier', 's'),
         ('CaseList',
          ('MatchCase',
           ('Pattern',
            ('Identifier', 'h'),
            ('Identifier', 't')),
           ('BinaryOp', '!=',
            ('Identifier', 'h'),
            ('Identifier', 'null')),
           ('Block',
            ('Return', ('Identifier', 'h')))))))
    
# Regex

def test_match_one_regex():
    s = """
    match(s) {
        regex 'foo' : return "bar";
    }
    """    
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Match',
         ('Identifier', 's'),
         ('CaseList',
          ('Regex',
           ('Constant', 'literal', 'foo'),
           ('Block',
            ('Return', ('Constant', 'string', 'bar')))))))

def test_match_one_regex_as():
    s = """
    match(s) {
        regex 'foo' as [ bar ] : return "baz";
    }
    """    
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Match',
         ('Identifier', 's'),
         ('CaseList',
          ('Regex',
           ('Constant', 'literal', 'foo'),
           ('As',
            ('List', ('Identifier', 'bar'))),
           ('Block',
            ('Return', ('Constant', 'string', 'baz')))))))

def test_match_regex_condition():
    s = """
    match(s) {
        regex '\w+' as x | # x >= 42: return x;
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Match',
         ('Identifier', 's'),
         ('CaseList',
          ('Regex',
           ('Constant', 'literal', '\w+'),
           ('As', ('Identifier', 'x')),
           ('BinaryOp', '>=',
            ('UnaryOp', '#', ('Identifier', 'x')),
            ('Constant', 'int', 42)),
           ('Block',
            ('Return', ('Identifier', 'x')))))))

# Case + Regex

def test_match_pattern_regex_as():
    s = """
    match(s) {
        regex 'foo' as [ bar ] : return "baz";
        case [h|t] : return 'Not empty!';
    }
    """    
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Match',
         ('Identifier', 's'),
         ('CaseList',
          ('Regex',
           ('Constant', 'literal', 'foo'),
           ('As',
            ('List', ('Identifier', 'bar'))),
           ('Block',
            ('Return', ('Constant', 'string', 'baz')))),
          ('Case',
           ('Pattern',
            ('Identifier', 'h'),
            ('Identifier', 't')),
           ('Block',
            ('Return', ('Constant', 'literal', 'Not empty!')))))))

def test_match_pattern_regex_as():
    s = """
    match(s) {
        regex 'foo' as [ bar ] : return "baz";
        case [h|t] : return 'Not empty!';
    }
    """    
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Match',
         ('Identifier', 's'),
         ('CaseList',
          ('Regex',
           ('Constant', 'literal', 'foo'),
           ('As',
            ('List', ('Identifier', 'bar'))),
           ('Block',
            ('Return', ('Constant', 'string', 'baz')))),
          ('MatchCase',
           ('Pattern',
            ('Identifier', 'h'),
            ('Identifier', 't')),
           ('Block',
            ('Return', ('Constant', 'literal', 'Not empty!')))))))
    
##
## Scan
##

def test_scan_one_regex():
    s = """
    scan(s) {
        regex 'foo' : return "bar";
    }
    """    
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Scan',
         ('Identifier', 's'),
         ('CaseList',
          ('Regex',
           ('Constant', 'literal', 'foo'),
           ('Block',
            ('Return', ('Constant', 'string', 'bar')))))))

def test_scan_one_regex_using():
    s = """
    scan(x) using y {
        regex 'foo' : return "bar";
    }
    """    
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Scan',
         ('Identifier', 'x'),
         ('As', ('Identifier', 'y')),
         ('CaseList',
          ('Regex',
           ('Constant', 'literal', 'foo'),
           ('Block',
            ('Return', ('Constant', 'string', 'bar')))))))

    
def test_match_one_regex_as():
    s = """
    scan(s) {
        regex 'foo' as [ bar ] : return "baz";
    }
    """    
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Scan',
         ('Identifier', 's'),
         ('CaseList',
          ('Regex',
           ('Constant', 'literal', 'foo'),
           ('As',
            ('List', ('Identifier', 'bar'))),
           ('Block',
            ('Return', ('Constant', 'string', 'baz')))))))

def test_scan_two_regex():
    s = """
    scan(s) {
        regex 'foo' : return "bar";
        regex 'bar' : return "baz";
    }
    """    
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Scan',
         ('Identifier', 's'),
         ('CaseList',
          ('Regex',
           ('Constant', 'literal', 'foo'),
           ('Block',
            ('Return', ('Constant', 'string', 'bar')))),
          ('Regex',
           ('Constant', 'literal', 'bar'),
           ('Block',
            ('Return', ('Constant', 'string', 'baz')))))))

def test_scan_two_regex_using_default():
    s = """
    scan(c) using chr {
        regex '[0-9]' : return "Number";
        regex '[a-zA-Z]' : return "Character";
        default: return "Neither number nor character";
    }
    """    
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Scan',
         ('Identifier', 'c'),
         ('As', ('Identifier','chr')),
         ('CaseList',
          ('Regex',
           ('Constant', 'literal', '[0-9]'),
           ('Block',
            ('Return', ('Constant', 'string', 'Number')))),
          ('Regex',
           ('Constant', 'literal', '[a-zA-Z]'),
           ('Block',
            ('Return', ('Constant', 'string', 'Character'))))),
          ('Default',
           ('Block',
            ('Return', ('Constant', 'string', 'Neither number nor character'))))))
    
##
## Try/Catch
##    
    
##
## While-Loop
##

def test_while_minimal():
    node = parse_single_statement("while(!empty) {}")
    eq_(node.to_tuples(),
        ('While',
         ('UnaryOp', 'not', ('Identifier', 'empty')),
         ('Block',)))

def test_while_bigger_body():
    node = parse_single_statement('while(i < n) { x *= 2; i -= 1;}')
    eq_(node.to_tuples(),
        ('While',
         ('BinaryOp', '<', ('Identifier', 'i'), ('Identifier', 'n')),
         ('Block',
          ('Assignment', '*=', ('Identifier', 'x'), ('Constant', 'int', 2)),
          ('Assignment', '-=', ('Identifier', 'i'), ('Constant', 'int', 1)))))
##
## Do-While-Loop
##

def test_do_while_loop_minimal():
    node = parse_single_statement("do {} while(!empty); ")
    eq_(node.to_tuples(),
        ('DoWhile',
         ('UnaryOp', 'not', ('Identifier', 'empty')),
         ('Block',)))

def test_do_while_loop_bigger_body():
    node = parse_single_statement('do { x *= 2; i -= 1;} while(i < n);')
    eq_(node.to_tuples(),
        ('DoWhile',
         ('BinaryOp', '<', ('Identifier', 'i'), ('Identifier', 'n')),
         ('Block',
          ('Assignment', '*=', ('Identifier', 'x'), ('Constant', 'int', 2)),
          ('Assignment', '-=', ('Identifier', 'i'), ('Constant', 'int', 1)))))

##
## For-Loop
##

def test_for_loop_minimal():
    node = parse_single_statement("for(x in primes) {}")
    eq_(node.to_tuples(),
        ('For',
         ('Iterator',
          ('Identifier', 'x'),
          ('Identifier', 'primes')),
         ('Block', )))

def test_for_loop_bigger_body():
    s = """
    // Finds the first vowel in a list of characters
    // and returns it
    for(c in characters) {
        if(c in vowels) {
            return c;
        }
    }

    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('For',
         ('Iterator',
          ('Identifier', 'c'),
          ('Identifier', 'characters')),
         ('Block',
          ('If',
           ('BinaryOp', 'in',
            ('Identifier', 'c'),
            ('Identifier', 'vowels')),
           ('Block', ('Return', ('Identifier', 'c')))))))

def test_for_loop_three_iterators():
    s = """
    for(i in uids, s in street, n in street_number) {
        address[i] := "$street$ $street_number$";
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('For',
         ('IteratorChain', 'zip',
          ('Iterator', ('Identifier', 'i'), ('Identifier', 'uids')),
          ('Iterator', ('Identifier', 's'), ('Identifier', 'street')),
          ('Iterator', ('Identifier', 'n'), ('Identifier', 'street_number'))),
         ('Block',
          ('Assignment', ':=',
           ('Subscription',
            ('Identifier', 'address'),
            ('Identifier', 'i')),
           ('Constant', 'string', "$street$ $street_number$")))))

##
## Procedures
##

def test_procedure_minimal():
    node = parse_single_statement('procedure() {};')
    eq_(node.to_tuples(), ('Procedure', ('ParamList',), ('Block',)))

def test_procedure_square():
    node = parse_single_statement('procedure(x) { return x ** x; };')
    eq_(node.to_tuples(),
        ('Procedure',
         ('ParamList', ('Param', 'x')),
         ('Block', ('Return',
           ('BinaryOp', '**',
            ('Identifier', 'x'),
            ('Identifier', 'x'))))))

def test_procedure_max():
    s = """
    max := procedure(a, b) {
        if(a > b) {
            return a;
        } else {
            return b;
        }
    };
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('Identifier', 'max'),
         ('Procedure',
          ('ParamList', ('Param', 'a'), ('Param', 'b')),
          ('Block',
           ('If',
            ('BinaryOp', '>', ('Identifier', 'a'), ('Identifier', 'b')),
            ('Block', ('Return', ('Identifier', 'a'))),
            ('Block', ('Return', ('Identifier', 'b'))))))))

def test_procedure_fac():
    s = """
    fac := procedure(n) {
        i := 1;
        while(n >= 1) {
            i *= n;
            n -= 1;
        }
        return i;
    };
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('Identifier', 'fac'),
         ('Procedure',
          ('ParamList', ('Param', 'n')),
          ('Block',
           ('Assignment', ':=', ('Identifier', 'i'), ('Constant', 'int', 1)),
           ('While',
            ('BinaryOp', '>=', ('Identifier', 'n'), ('Constant', 'int', 1)),
            ('Block',
             ('Assignment', '*=', ('Identifier', 'i'), ('Identifier', 'n')),
             ('Assignment', '-=', ('Identifier', 'n'), ('Constant', 'int', 1)))),
            ('Return', ('Identifier', 'i'))))))

##
## Cached procedures
##

def test_cached_procedure_minimal():
    node = parse_single_statement('cachedProcedure() {};')
    eq_(node.to_tuples(), ('CachedProcedure', ('ParamList',), ('Block',)))

def test_cached_procedure_square():
    node = parse_single_statement('cachedProcedure(x) { return x ** x; };')
    eq_(node.to_tuples(),
        ('CachedProcedure',
         ('ParamList', ('Param', 'x')),
         ('Block', ('Return',
           ('BinaryOp', '**',
            ('Identifier', 'x'),
            ('Identifier', 'x'))))))

def test_cached_procedure_max():
    s = """
    max := cachedProcedure(a, b) {
        if(a > b) {
            return a;
        } else {
            return b;
        }
    };
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('Identifier', 'max'),
         ('CachedProcedure',
          ('ParamList', ('Param', 'a'), ('Param', 'b')),
          ('Block',
           ('If',
            ('BinaryOp', '>', ('Identifier', 'a'), ('Identifier', 'b')),
            ('Block', ('Return', ('Identifier', 'a'))),
            ('Block', ('Return', ('Identifier', 'b'))))))))

def test_cached_procedure_fac():
    s = """
    fac := cachedProcedure(n) {
        i := 1;
        while(n >= 1) {
            i *= n;
            n -= 1;
        }
        return i;
    };
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('Identifier', 'fac'),
         ('CachedProcedure',
          ('ParamList', ('Param', 'n')),
          ('Block',
           ('Assignment', ':=', ('Identifier', 'i'), ('Constant', 'int', 1)),
           ('While',
            ('BinaryOp', '>=', ('Identifier', 'n'), ('Constant', 'int', 1)),
            ('Block',
             ('Assignment', '*=', ('Identifier', 'i'), ('Identifier', 'n')),
             ('Assignment', '-=', ('Identifier', 'n'), ('Constant', 'int', 1)))),
            ('Return', ('Identifier', 'i'))))))

##
##
##

def test_class_minimal():
    node = parse_single_statement('class point() {}')
    eq_(node.to_tuples(),
        ('Class',
         ('Identifier', 'point'),
         ('ParamList', ),
         ('Block', ),
         ('Block', )))

def test_class_with_parameters():
    node = parse_single_statement('class point(x,y) {}')
    eq_(node.to_tuples(),
        ('Class',
         ('Identifier', 'point'),
         ('ParamList',
          ('Param', 'x'),
          ('Param', 'y')),
         ('Block', ),
         ('Block', )))

def test_class_with_parameters_and_body():
    s = """
    class point(x,y) {
        mX := x;
        mY := y;
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Class',
         ('Identifier', 'point'),
         ('ParamList',
          ('Param', 'x'),
          ('Param', 'y')),
         ('Block',
          ('Assignment', ':=',
           ('Identifier', 'mX'),
           ('Identifier', 'x')),
          ('Assignment', ':=',
           ('Identifier', 'mY'),
           ('Identifier', 'y'))),
         ('Block', )))

def test_class_with_static_body():
    s = """
    class universal() {
        static {
            gAnswer := 42;
        }
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Class',
         ('Identifier', 'universal'),
         ('ParamList', ),
         ('Block', ),
         ('Block', 
          ('Assignment', ':=',
           ('Identifier', 'gAnswer'),
           ('Constant', 'int', 42)))))

##
## Try/Catch
##

def test_try_catch_minimal():
    s = """
    try {
    } catch(e) {
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Try',
         ('Block', ),
         ('Catches',
          ('CatchClause',
           'catch',
           ('Identifier', 'e'),
           ('Block', )))))

def test_try_catch_usr_minimal():
    s = """
    try {
    } catchUsr(e) {
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Try',
         ('Block', ),
         ('Catches',
          ('CatchClause',
           'catchUsr',
           ('Identifier', 'e'),
           ('Block', )))))

def test_try_catch_lng_minimal():
    s = """
    try {
    } catchLng(e) {
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Try',
         ('Block', ),
         ('Catches',
          ('CatchClause',
           'catchLng',
           ('Identifier', 'e'),
           ('Block', )))))

##
## Backtrack
##

def test_check_minimal():
    node =  parse_single_statement('check {}')
    eq_(node.to_tuples(),
        ('Check',
         ('Block',)))