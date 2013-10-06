#------------------------------------------------------------------------------
# setlx2py: setlx_parser.py
#
# Parser class: parser for the setlx language
#
# Copyright (C) 2013, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------


from ply import yacc

from setlx2py.setlx_lexer import Lexer
from setlx2py.setlx_ast import *

class Parser():

    tokens = Lexer.tokens

    def __init__(self):

        # Lexer 
        self.lexer = Lexer()
        self.lexer.build()

        # Parser
        self.parser = yacc.yacc(module=self, start='init_expr')

    def parse(self, text):
        return self.parser.parse(input=text, lexer=self.lexer)

    def p_error(self, t):
        if t is None:
            raise SyntaxError("unexpected token", self.lexer, None)
        else:
            raise SyntaxError("unexpected token", self.lexer, t.value, t.lineno, t.lexpos)

    ##
    ## Precedence and associativity of operators
    ##
    precedence = (
    )

    ##
    ## Grammar productions
    ## Implementation of the BNF defined in Pure.g of setlx interpreter 
    ## 

    def p_init_expr(self, p):
        """ init_expr : expr """
        p[0] = p[1]

    ##
    ## Expressions
    ##

    def p_expr_1(self, p):
        """ expr : implication """
        p[0] = p[1]
        
    def p_implication_1(self, p):
        """ implication : disjunction """
        p[0] = p[1]

    def p_disjunction_1(self, p):
        """ disjunction : conjunction  """
        p[0] = p[1]

    def p_conjunction_1(self, p):
        """ conjunction : comparison """
        p[0] = p[1]

    def p_comparison_1(self, p):
        """ comparison : sum """
        p[0] = p[1]

    def p_sum_1(self, p):
        """ sum : product """
        p[0] = p[1]
        
    def p_product_1(self, p):
        """ product : reduce """
        p[0] = p[1]
        
    def p_reduce_1(self, p):
        """ reduce : prefix_operation """
        p[0] = p[1]
        
    def p_prefixOperation_1(self, p):
        """ prefix_operation : factor """
        p[0] = p[1]
        
    def p_factor_1(self, p):
        """ factor  : value """
        p[0] = p[1]
        
    def p_value_1(self, p):
        """ value  : atomic_value """
        p[0] = p[1]
        
    def p_atomic_value_1(self, p):
        """ atomic_value  : INTEGER """
        p[0] = Constant('int', int(p[1]))

        