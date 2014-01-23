#------------------------------------------------------------------------------
# setlx2py: test_parser.py
#
# Unit tests for the Parser class in setlx_parser.py
# Beware: Only syntax is tested here!
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

def setup_func():
    global parser
    parser = Parser()

def teardown_func():
    parser = None

##
## Parse helper
##

@with_setup(setup_func, teardown_func)        
def parse_statements(text):    
    root = parser.parse(text) # FileAST
    return root # List of statements

@with_setup(setup_func, teardown_func)    
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
        eq_(node.left.name, left)
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
                                       
@with_setup(setup_func, teardown_func)        
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
    node = parse_single_statement('[foo] := 42;')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('Identifier', 'foo'),
         ('Constant', 'int', 42)))

def test_assignment_explicit_two():
    node = parse_single_statement('[foo,bar] := "xy";')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('TargetList',
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
@nottest
def test_assignment_array_ref():
    node = parse_single_statement('foo[0] := true;')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('ArrayRef',
          ('Identifier', 'foo'),
          ('Constant', 'int', 0)),
         ('Constant', 'bool', True)))
@nottest
def test_assignment_array_ref_chained():
    node = parse_single_statement('foo[0][1] := true;')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('ArrayRef',
          ('ArrayRef',
           ('Identifier', 'foo'),
           ('Constant', 'int', 0)),
          ('Constant', 'int', 1)),
         ('Constant', 'bool', True)))
@nottest    
def test_assignment_mixed_attributeref_subscription():
    node = parse_single_statement('foo[x+1].bar.baz[42][y**2] := z')

##
## Augmented Assignment
##

@nottest
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

def test_term_single_arg():
    term = parse_single_statement('F(true);')
    eq_(term.to_tuples(),
        ('Term', 'F',
         ('Constant', 'bool', True)))

def test_term_multi_arg():
    term = parse_single_statement('F(true, false);')
    eq_(term.to_tuples(),
        ('Term', 'F',
         ('ExprList', 
          ('Constant', 'bool', True),
          ('Constant', 'bool', False))))

##
## Quantifier
##
@nottest
def test_quantifier_all():
    quantor =  parse_single_statement('forall (x in 1 | true);')
    iterator = quantor.lhs
    condition = quantor.cond

    eq_(quantor.name, 'all')
    eq_(iterator.assignable.name, 'x')
    eq_(iterator.expression.value, 1)
    eq_(condition.value, True)
@nottest
def test_quantifier_exists():
    quantor =  parse_single_statement('exists (x in 1 | true);')
    eq_(quantor.to_tuples(),
        ('Quantor', 'any',
         ('Iterator',
          ('Identifier', 'x'),
          ('Constant', 'int', 1)),
         ('Constant', 'bool', True)))

@nottest
def test_quantifier_cray():
    quantor = parse_single_statement('forall (n in [1..10] | n**2 <= 2**n);')
    
####
##
## Compound Statements
##
####
    
##
## If statements
##

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

def test_if_single_else_empty():
    node = parse_single_statement("if(foo) {} else {}")
    eq_(node.to_tuples(),
        ('If',
         ('Identifier', 'foo'),
         ('Block',),
         ('Block',)))


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
    pass

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
## While-Loop
##

def test_while_minimal():
    node = parse_single_statement("while(!empty) {}")
    eq_(node.to_tuples(),
        ('While',
         ('UnaryOp', 'not', ('Identifier', 'empty')),
         ('Block',)))

@nottest    
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
@nottest
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
@nottest
def test_for_loop_minimal():
    node = parse_single_statement("for(x in primes) {}")
    eq_(node.to_tuples(),
        ('For',
         ('Iterator',
          ('Identifier', 'x'),
          ('Identifier', 'primes')),
         ('Block', )))
@nottest
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
@nottest
def test_for_loop_three_iterators():
    s = """
    for(i in uids, s in street, n in street_number) {
        address[i] := "$street$ $street_number$";
    }
    """
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('For',
         ('IteratorChain',
          ('Iterator', ('Identifier', 'i'), ('Identifier', 'uids')),
          ('Iterator', ('Identifier', 's'), ('Identifier', 'street')),
          ('Iterator', ('Identifier', 'n'), ('Identifier', 'street_number'))),
         ('Block',
          ('Assignment', ':=',
           ('ArrayRef',
            ('Identifier', 'address'),
            ('Identifier', 'i')),
           ('Constant', 'string', "$street$ $street_number$")))))
               
##
## Assignments
##


##
## Procedures
##
@nottest
def test_procedure_minimal():
    node = parse_single_statement('procedure() {};')
    eq_(node.to_tuples(), ('Procedure', ('ParamList',), ('Block',)))
@nottest
def test_procedure_square():
    node = parse_single_statement('procedure(x) { return x ** x; };')
    eq_(node.to_tuples(),
        ('Procedure',
         ('ParamList', ('Param', 'x')),
         ('Block', ('Return',
           ('BinaryOp', '**',
            ('Identifier', 'x'),
            ('Identifier', 'x'))))))
@nottest
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
@nottest
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
@nottest
def test_cached_procedure_minimal():
    node = parse_single_statement('cachedProcedure() {};')
    eq_(node.to_tuples(), ('CachedProcedure', ('ParamList',), ('Block',)))
@nottest
def test_cached_procedure_square():
    node = parse_single_statement('cachedProcedure(x) { return x ** x; };')
    eq_(node.to_tuples(),
        ('CachedProcedure',
         ('ParamList', ('Param', 'x')),
         ('Block', ('Return',
           ('BinaryOp', '**',
            ('Identifier', 'x'),
            ('Identifier', 'x'))))))
@nottest
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
@nottest
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
## Lambda
##
@nottest
def test_lambda_minimal_zero_params():
    node = parse_single_statement('< > |-> true;')
    eq_(node.to_tuples(),
        ('Lambda',
         ('ParamList', ),
         ('Constant', 'bool', True)))

@nottest
def test_lamba_minimal_one_param_no_brackets():
    node = parse_single_statement("foo |-> 'bar';")
    eq_(node.to_tuples(),
        ('Lambda',
         ('ParamList', ('Param', 'foo')),
         ('Constant', 'literal', 'bar')))
@nottest    
def test_lambda_minimal_one_param_brackets():
    node = parse_single_statement('x |-> x ** x;')
    eq_(node.to_tuples(),
        ('Lambda',
         ('ParamList', ('Param', 'x')),
         ('BinaryOp', '**',
          ('Identifier', 'x'),
          ('Identifier', 'x'))))
@nottest
def test_lambda_two_params():
    node = parse_single_statement('<x,y> |-> x+y;')
    eq_(node.to_tuples(),
        ('Lambda',
         ('ParamList', ('Param', 'x'), ('Param', 'y')),
         ('BinaryOp', '+',
          ('Identifier', 'x'),
          ('Identifier', 'y'))))
    