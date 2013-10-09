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
        """ init_expr : expr SEMICOLON """
        p[0] = p[1]

    ##
    ## Expressions
    ##

    def p_expr_1(self, p):
        """ expr : implication """
        p[0] = p[1]

    def p_expr_2(self, p):
        """ expr : implication EQUIVALENT implication
                 | implication ANTIVALENT implication
        """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)
        
    def p_implication_1(self, p):
        """ implication : disjunction """
        p[0] = p[1]

    def p_implication_2(self, p):
        """ implication : disjunction IMPLICATES disjunction """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    def p_disjunction_1(self, p):
        """ disjunction : conjunction  """
        p[0] = p[1]

    def p_disjunction_2(self, p):
        """ disjunction : conjunction OR disjunction """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)        

    def p_conjunction_1(self, p):
        """ conjunction : comparison """
        p[0] = p[1]

    def p_conjunction_2(self, p):
        """ conjunction : comparison AND comparison """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    def p_comparison_1(self, p):
        """ comparison : sum """
        p[0] = p[1]

    def p_comparison_2(self, p):
        """ comparison : sum EQ sum
                       | sum NEQ sum
                       | sum LT sum
                       | sum LE sum
                       | sum GT sum
                       | sum GE sum
                       | sum IN sum
                       | sum NOTIN sum
        """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    def p_sum_1(self, p):
        """ sum : product """
        p[0] = p[1]

    def p_sum_2(self, p):
        """ sum : product PLUS  product
                | product MINUS product
        """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)
        
    def p_product_1(self, p):
        """ product : reduce """
        p[0] = p[1]

    def p_product_2(self, p):
        """ product : reduce TIMES     reduce
                    | reduce DIVIDE    reduce
                    | reduce IDIVIDE   reduce
                    | reduce MOD       reduce
                    | reduce CARTESIAN reduce
        """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)
        
    def p_reduce_1(self, p):
        """ reduce : prefix_operation """
        p[0] = p[1]

    def p_reduce_2(self, p):
        """ reduce : prefix_operation SUM prefix_operation
                   | prefix_operation PRODUCT prefix_operation
        """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)
        
    def p_prefix_operation_1(self, p):
        """ prefix_operation : factor """
        p[0] = p[1]

    def p_prefix_operation_2(self, p):
        """ prefix_operation : SUM     prefix_operation
                             | PRODUCT prefix_operation
                             | HASH    prefix_operation
                             | MINUS   prefix_operation
                             | AT      prefix_operation
        """
        p[0] = UnaryOp(p[1], p[2], p[2].coord)
        
    def p_factor_1(self, p):
        """ factor  : value """
        p[0] = p[1]
        
    def p_value_1(self, p):
        """ value : atomic_value """
        p[0] = p[1]

    def p_value_2(self, p):
        """ value : STRING """
        p[0] = Constant('string', str(p[1]))

    def p_value_3(self, p):
        """ value : LITERAL """
        p[0] = Constant('literal', str(p[1]))

    def p_value_4(self, p):
        """ value : UNUSED """
        p[0] = Constant('unused', 'unused')
        
    def p_atomic_value_1(self, p):
        """ atomic_value  : INTEGER """
        p[0] = Constant('int', int(p[1]))

    def p_atomic_value_2(self, p):
        """ atomic_value : DOUBLE """
        p[0] = Constant('double', float(p[1]))

    def p_atomic_value_3(self, p):
        """ atomic_value : TRUE """
        p[0] = Constant('bool', True)

    def p_atomic_value_4(self, p):
        """ atomic_value : FALSE """
        p[0] = Constant('bool', False)