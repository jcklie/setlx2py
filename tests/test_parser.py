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

##
## Tests
##

@with_setup(setup_func, teardown_func)        
def test_should_be_creatable():
    assert parser is not None

# Atomic Values

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

# Variables

def test_variables():
    node = parse_single_statement('foo;')
    eq_(node.to_tuples(),
        ('Variable', 'foo'))     
    
# Assert

def test_condition_simple():
    assert_stmt = parse_single_statement('assert(isOverflown, false);')
    eq_(assert_stmt.to_tuples(),
        ('Assert',
         ('Variable', 'isOverflown'),
         ('Constant', 'bool', False)))

# Statements

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

# If statements

def test_if_no_else():
    node = parse_single_statement('if(x >= 5) { return true; }')
    eq_(node.to_tuples(),
        ('If',
         ('BinaryOp', '>=',
          ('Variable', 'x'),
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
          ('Variable', 'isRaining'),
          ('Variable', 'isCold')),
         ('Block',
          ('Assignment', ':=',
           ('Variable', 'prediction'),
           ('Constant', 'string', 'Let it snow!')),
          ('Return', ('Variable', 'prediction')))))

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
           ('Variable', 'i'),
           ('Constant', 'int', 2)),
          ('Constant', 'int', 0)),
         ('Block', ('Return', ('Constant', 'string', 'Even'))),
         ('Block', ('Return', ('Constant', 'string', 'Odd')))))

def test_if_single_else_empty():
    node = parse_single_statement("if(foo) {} else {}")
    eq_(node.to_tuples(),
        ('If',
         ('Variable', 'foo'),
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
         ('Variable', 'isGreen'),
         ('Block',
          ('Return', ('Constant', 'string', 'Green'))),
         ('If',
          ('Variable', 'isRed'),
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
                 ('Variable', 'grade'),
                 ('Constant', 'string', 'A')),
          ('Block', ('Return', ('Constant', 'string', 'Excellent'))),
          ('If', ('BinaryOp', '==',
                  ('Variable', 'grade'),
                  ('Constant', 'string', 'B')),
           ('Block', ('Return', ('Constant', 'string', 'Good'))),
           ('If', ('BinaryOp', '==',
                   ('Variable', 'grade'),
                   ('Constant', 'string', 'C')),
            ('Block', ('Return', ('Constant', 'string', 'Satisfactory'))),
            ('If', ('BinaryOp', '==',
                    ('Variable', 'grade'),
                    ('Constant', 'string', 'D')),
             ('Block', ('Return', ('Constant', 'string', 'Pass'))),
             ('If', ('BinaryOp', '==',
                     ('Variable', 'grade'),
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
         ('BinaryOp', '==', ('Variable', 'num1'), ('Variable', 'num2')), 
         ('Block', ('Return', ('Constant', 'string', 'Equal'))),  
         ('Block',
          ('If',
           ('BinaryOp', '>', ('Variable', 'num1'), ('Variable', 'num2')),
           ('Block', ('Return', ('Constant', 'string', 'Num1 greater'))),
           ('Block', ('Return', ('Constant', 'string', 'Num2 greater')))))))

# Loops

def test_while_minimal():
    node = parse_single_statement("while(!empty) {}")
    eq_(node.to_tuples(),
        ('While',
         ('UnaryOp', 'not', ('Variable', 'empty')),
         ('Block',)))

def test_while_bigger_body():
    node = parse_single_statement('while(i < n) { x *= 2; i -= 1;}')
    eq_(node.to_tuples(),
        ('While',
         ('BinaryOp', '<', ('Variable', 'i'), ('Variable', 'n')),
         ('Block',
          ('Assignment', '*=', ('Variable', 'x'), ('Constant', 'int', 2)),
          ('Assignment', '-=', ('Variable', 'i'), ('Constant', 'int', 1)))))
    
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

def test_expr_paren_simple():
    node = parse_single_statement('(foo + bar);')
    eq_(node.to_tuples(),
        ('BinaryOp', '+',
         ('Variable', 'foo'),
         ('Variable', 'bar')))

# Precedence

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
         ('Variable', 'a'),
         ('BinaryOp', '/',
          ('BinaryOp', '*',
           ('Variable', 'b'),
           ('Variable', 'c')),
          ('BinaryOp', '-',
           ('Variable', 'd'),
           ('Variable', 'e')))))    
          
# Unary operations

def test_unop():
    assert_unop('+/ 42;',  '+/', 'int', 42)
    assert_unop('*/ 42;',  '*/', 'int', 42)
    assert_unop('-  42;',   '-', 'int', 42)
    assert_unop('#  42;',   '#', 'int', 42)
    assert_unop('@  42;',   '@', 'int', 42)
    assert_unop('!true;', 'not', 'bool', True)
    assert_unop('1337!;', 'fac', 'int', 1337)
        
# Terms
    
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

# Jump statements

def test_jump_statement_backtrack():
    node = parse_single_statement('backtrack;')
    eq_(node.to_tuples(),
        ('Backtrack',))
    
def test_jump_statement_break():
    node = parse_single_statement('break;')
    eq_(node.to_tuples(),
        ('Break',))

def test_jump_statement_continue():
    node = parse_single_statement('continue;')
    eq_(node.to_tuples(),
        ('Continue',))

def test_jump_statement_break():
    node = parse_single_statement('exit;')
    eq_(node.to_tuples(),
        ('Exit',))

def test_jump_statement_return_void():
    node = parse_single_statement('return;')
    eq_(node.to_tuples(),
        ('Return',))

def test_jump_statement_return_expr_const():
    node = parse_single_statement('return 42;')
    eq_(node.to_tuples(),
        ('Return',
         ('Constant', 'int', 42)))

def test_jump_statement_return_expr_calc():
    node = parse_single_statement('return 42 ** 2;')
    eq_(node.to_tuples(),
        ('Return',
         ('BinaryOp', '**',
          ('Constant', 'int', 42),
          ('Constant', 'int', 2))))
    
# Assignments

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

def test_assignable_member_access():
    assignment = parse_single_statement('foo.bar := true;')
    eq_(assignment.to_tuples(),
        ('Assignment', ':=',
        ('MemberAccess',
          ('Variable', 'foo'),
          ('Variable', 'bar')),
         ('Constant', 'bool', True)))

def test_assignable_member_access_chained():
    assignment = parse_single_statement('foo.bar.baz := 42;')
    eq_(assignment.to_tuples(),
        ('Assignment', ':=',
         ('MemberAccess',
          ('MemberAccess',
           ('Variable', 'foo'),
           ('Variable', 'bar')),
          ('Variable', 'baz')),
         ('Constant', 'int', 42)))

def test_assignable_array_ref():
    node = parse_single_statement('foo[0] := true;')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('ArrayRef',
          ('Variable', 'foo'),
          ('Constant', 'int', 0)),
         ('Constant', 'bool', True)))

def test_assignable_array_ref_chained():
    node = parse_single_statement('foo[0][1] := true;')
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('ArrayRef',
          ('ArrayRef',
           ('Variable', 'foo'),
           ('Constant', 'int', 0)),
          ('Constant', 'int', 1)),
         ('Constant', 'bool', True)))

# Quantifier    

def test_quantifier_all():
    quantor =  parse_single_statement('forall (x in 1 | true);')
    iterator = quantor.lhs
    condition = quantor.cond

    eq_(quantor.name, 'all')
    eq_(iterator.assignable.name, 'x')
    eq_(iterator.expression.value, 1)
    eq_(condition.value, True)

def test_quantifier_exists():
    quantor =  parse_single_statement('exists (x in 1 | true);')
    eq_(quantor.to_tuples(),
        ('Quantor', 'any',
         ('Iterator',
          ('Variable', 'x'),
          ('Constant', 'int', 1)),
         ('Constant', 'bool', True)))

@nottest
def test_quantifier_cray():
    quantor = parse_single_statement('forall (n in [1..10] | n**2 <= 2**n);')

    