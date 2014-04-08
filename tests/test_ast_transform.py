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
from setlx2py.setlx_ast import *

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
    short_pattern = cases.cases[1].pattern
    long_pattern = cases.cases[2].pattern
    

#    print(short_pattern.to_tuples())
#    print(long_pattern.to_tuples())

def test_assignment_list_bracketed():
    node = parse_single_statement('[x,y,z] := [1..3];')
    assert "bracketed" in node.target.tags

def test_iterator_bracketed():
    s = """
    for([x,y] in [[1..5], [1,2,3,4,5]]) {
        print(x+y);
    }
    """
    node = parse_single_statement(s)
    assert "bracketed" in node.iterators.assignable.tags

def test_string_interpolation():
    s = 's := "x = $n$";'
    node = parse_single_statement(s)
    eq_(node.to_tuples(),
        ('Assignment', ':=',
         ('Identifier', 's'),
         ('Interpolation',
          ('Constant',  'literal', 'x = {0}'),
          ('ExprList',
           ('Identifier', 'n')))))
           
    