#------------------------------------------------------------------------------
# setlx2py: test_codegen.py
#
# Unit tests for the Codegen class in setlx_codegen.py
# These are very shallow and cover only a small area
# Acceptance tests for code generation is seperate
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from nose.tools import nottest, eq_

from setlx2py.setlx_builtin import builtin
from setlx2py.setlx_parser import Parser
from setlx2py.setlx_codegen import Codegen

generator = Codegen()
parser = Parser()

##
## Helper methods
##

import sys

def run(source, ns={}, verbose=False):
    ns.update(builtin)
    ast = parser.parse(source)
    compiled = generator.visit(ast)
    if verbose:
        print('Source: ' + source)
        print('Target: ' + compiled)
    code = compile(compiled, '<string>', 'exec')
    exec(code, ns)

def assert_res(source, variables):
    ns = {}
    run(source, ns)
    for key, value in variables.items():
        eq_(ns[key], value)
        
##
## Tests
##

def test_is_creatable():
    assert generator is not None

def test_identifier():
    ns = {'a' : 42}
    run('a;', ns)

def test_constant():
    run('42;')

## Assignment

def test_assignment_simple():
    assert_res('x := 1;', {'x' : 1})

def test_assignment_augmented():
    assert_res('x := 1; x += 2;', {'x' : 3})
    assert_res('x := 3; x -= 2;', {'x' : 1})
    assert_res('x := 1; x *= 2;', {'x' : 2})
    assert_res('x := 6; x /= 2;', {'x' : 3})
    assert_res('x := 5; x %= 2;', {'x' : 1})

## Binop

def test_binop_simple():
    assert_res('x := 1;', {'x' : 1})

def test_binop_add_three():
    assert_res('x := 1 + 2 + 3;', {'x' : 6})
    
def test_binop_mult_before_add():
    assert_res('x := 4 + 3 * 2;', {'x' : 10})
    assert_res('x := (4 + 3) * 2;', {'x' : 14})

def test_binop_power():
    assert_res('x :=  2 * 3  ** 2;', {'x' : 18})
    assert_res('x := (2 * 3) ** 2;', {'x' : 36})

def test_binop_precedence():
    assert_res('x := 2 +3 * 4;'   , {'x' : 2 + ( 3 * 4)})
    assert_res('x := 10 - 4 - 2;' , {'x' : ( 10 - 4 ) - 2})
    assert_res('x := 12 / 3 + 3;' , {'x' : (12 / 3) + 3})
    assert_res('x := 2 ** 3 + 3;' , {'x' : (2 ** 3) + 3 })
    assert_res('x := 12 / 2 * 3;' , {'x' : (12 / 2) * 3})
    assert_res('x := 12 / 2 / 3;' , {'x' : (12 / 2) / 3})
    assert_res('x := 18 / 3 ** 2;', {'x' : 18 /( 3 **2 )})

def test_binop_comparison():
    assert_res('x := 1 > 2;', {'x' : False})
    assert_res('x := 1 < 2;', {'x' : True})
    assert_res('x := 1 >= 1;', {'x' : True})
    assert_res('x := 1 <= 1;', {'x' : True})
    assert_res('x := 1 == 2;', {'x' : False})
    assert_res('x := 1 != 2;', {'x' : True})

def test_binop_logic_basic():
    assert_res('x := true && false;', {'x' : False})
    assert_res('x := true || false;', {'x' : True})

def test_binop_logic_complex():
    assert_res('x := true => false;',    {'x' : False})
    assert_res('x := false <==> false;', {'x' : True})
    assert_res('x := true <!=> false;',  {'x' : True})

@nottest    
def test_binop_comparison_set():
    assert_res('x := 2 in {1..42};', {'x' : True})

def test_unary_simple():
    assert_res('x := 5!;', {'x' : 120})
    assert_res('x := -5;', {'x' : -5})