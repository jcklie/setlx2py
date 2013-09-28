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
        self.parser = yacc.yacc(module=self, start='translation_unit_or_empty')

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
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE')
    )

    ##
    ## Grammar productions
    ## Implementation of the BNF defined in Pure.g of setlx interpreter 
    ## 

    def p_translation_unit_or_empty(self, p):
        """ translation_unit_or_empty   : translation_unit
                                        | empty
        """
        p[0] = p[1]

    def p_empty(self, p):
        'empty : '
        p[0] = None
    
    def p_translation_unit(self, p):
        """ translation_unit : init_block
                             | init_expr
        """
        p[0] = p[1] 

    def p_init_block(self, p):
        """ init_block       : constant """
        p[0] = None

    def p_init_expr(self, p):
        """ init_expr       : binary_expression SEMICOLON
        """
        p[0] = p[1]

    def p_binary_expression_1(self, p):
        """ binary_expression   : binary_expression TIMES binary_expression
                                | binary_expression DIVIDE binary_expression
                                | binary_expression PLUS binary_expression
                                | binary_expression MINUS binary_expression
        """
        p[0] = BinaryOp(p[2], p[1], p[3], "Foo")

    def p_binary_expression_2(self, p):
        """ binary_expression   : constant
        """
        p[0] = p[1]

    def p_constant(self, p):
        """ constant : INT_CONST_DEC
                     | FLOAT_CONST        
        """
        p[0] = int(p[1])

        