#------------------------------------------------------------------------------
# setlx2py: test_ast_transform.py
#
# Unit tests for the AstTransformer class in setlx_ast_transformer.py
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from nose.tools import nottest, eq_

from setlx2py.setlx_ast_transformer import AstTransformer
from setlx2py.setlx_parser import Parser

parser = Parser()
transformer = AstTransformer()

# Helper
# =========

def parse_statements(text, verbose=False):
    ast = parser.parse(text) # FileAST
    if verbose: print(ast)
    transformer.visit(ast)
    if verbose: print(ast)
    return ast # List of statements

def parse_single_statement(text):
    return parse_statements(text).stmts[0] # first statement after FileAST

# Tests
# =====

def test_is_creatable():
    assert transformer is not None

# Iterchain
# ---------

def test_iterchain_mode_for():
    s = """
    for(x in [1..10], y in {-1,-2..-10}) {
        print(x+y);
    }
    """
    node = parse_single_statement(s)
    eq_(node.iterators.mode, 'zip')
    
def test_iterchain_mode_comprehension():
    s = '{a * b: a in {1..3}, b in {1..3}};'
    node = parse_single_statement(s)
    eq_(node.iterators.mode, 'cartesian')

def test_iterchain_mode_quantor():
    s = 'forall (x in {1..10}, y in [20..30] | x < y);'
    node = parse_single_statement(s)
    eq_(node.iterators.mode, 'cartesian')
    
def test_iterchain_mode_quantor_deep():
    s = 'exists ([x, y] in [[a,b] : a in {1..10}, b in {1..10}] | 3*x - 4*y == 5);'
    node = parse_single_statement(s)
    eq_(node.iterators.expression.iterators.mode, 'cartesian')

# Procedure
# ---------

def test_procedure_name():
    s = """
    primes := procedure(n) {
        s := { 2..n };
        return s - { p*q : [p, q] in s >< s };
    };
    """
    node = parse_single_statement(s)
    eq_(node.name, 'primes')

# Pattern
# -------

def test_match_pattern():
    s = """
    match (s) {
        case [] : return s;
        case [c]: return c;
        case [a,b|r]: return b + a + reversePairs(r);
    }
    """
    node = parse_single_statement(s)
    cases = node.case_list
    pattern = cases.cases[1]
    assert True