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
        self.parser = yacc.yacc(module=self, start='init_block_or_epsilon')

    def parse(self, text):
        return self.parser.parse(input=text, lexer=self.lexer)

    def p_error(self, t):
        if t is None:
            raise SyntaxError("unexpected token", self.lexer, None)
        else:
            msg = "unexpected token: '{}' - Line: {} - Pos: {}" \
            .format(t.value, t.lineno, t.lexpos)
            raise SyntaxError(msg, self.lexer, t.value, t.lineno, t.lexpos)

    ##
    ## Precedence and associativity of operators
    ##
    precedence = (
    )

    ##
    ## Grammar productions
    ## Implementation of the BNF defined in Pure.g of setlx interpreter 
    ##

    def p_init_block_or_epsilon(self, p):
        """ init_block_or_epsilon : init_block
                                  | epsilon
        """
        p[0] = FileAST([]) if p[1] is None else FileAST(p[1])

    def p_init_block_1(self, p):
        """ init_block : statement  """
        p[0] = p[1]

    def p_init_block_2(self, p):
        """ init_block : init_block statement """
        if p[2] is not None:
            p[1].extend(p[2])
        p[0] = p[1]

    def p_statement_1(self, p):
        """ statement : if_statement
                      | jump_statement SEMICOLON
                      | assert_statement SEMICOLON
                      | assignment_direct SEMICOLON
                      | assignment_other  SEMICOLON
                      | expr SEMICOLON 
        """
        p[0] = [p[1]]

    ##
    ## Block
    ##

    def p_block(self, p):
        """ block : stmt_list
                  | epsilon
        """
        if p[1] is None:
            p[0] = Block([])
        else:
            p[0] = Block(p[1])

    def p_stmt_list_1(self, p):
        """ stmt_list : statement  """
        p[0] = p[1]

    def p_stmt_list_2(self, p):
        """ stmt_list : stmt_list statement  """
        if p[2] is not None:
            p[1].extend(p[2])
        p[0] = p[1]

    ##
    ## Misc
    ##

    # Variable

    def p_variable(self, p):
        """ variable : IDENTIFIER """
        p[0] = Variable(p[1])

    ## Condition

    def p_condition(self, p):
        """ condition : expr """
        p[0] = p[1]

    ##
    ## If Statements
    ##

    def p_if_statement_1(self, p):
        """ if_statement : IF LPAREN condition RPAREN LBRACE block RBRACE """
        p[0] = If(p[3], p[6], None, p[3].coord)

    def p_if_statement_2(self, p):
        """ if_statement : IF LPAREN condition RPAREN \
                           LBRACE block RBRACE \
                           ELSE LBRACE block RBRACE """
        p[0] = If(p[3], p[6], p[10], p[3].coord)
        

    ## 
    ## Jump Statements
    ##

    def p_jump_statement_1(self, p):
        """ jump_statement : BACKTRACK """
        p[0] = Backtrack()

    def p_jump_statement_2(self, p):
        """ jump_statement : BREAK """
        p[0] = Break()

    def p_jump_statement_3(self, p):
        """ jump_statement : CONTINUE """
        p[0] = Continue()

    def p_jump_statement_4(self, p):
        """ jump_statement : EXIT """
        p[0] = Exit()

    def p_jump_statement_5(self, p):
        """ jump_statement : RETURN """
        p[0] = Return(None)

    def p_jump_statement_6(self, p):
        """ jump_statement : RETURN expr """
        p[0] = Return(p[2], p[2].coord)

    
    ##
    ## Assert
    ##

    def p_assert_statement(self, p):
        """ assert_statement : ASSERT LPAREN condition COMMA expr RPAREN """
        p[0] = Assert(p[3], p[5], p[3].coord)

    ##
    ## Assignment
    ##

    ## Assignment Direct
    def p_assignment_direct_1(self, p):
        """ assignment_direct : assignable ASSIGN expr """
        p[0] = Assignment(p[2], p[1], p[3],  p[1].coord)

    ## Assignment Other
    def p_assignment_other(self, p):
        """ assignment_other : assignable PLUS_EQUAL    expr
                             | assignable MINUS_EQUAL   expr
                             | assignable TIMES_EQUAL   expr
                             | assignable DIVIDE_EQUAL  expr
                             | assignable IDIVIDE_EQUAL expr
                             | assignable MOD_EQUAL     expr
        """
        p[0] = Assignment(p[2], p[1], p[3], p[1].coord)
        
    ## Assignable

    def p_assignable_1(self, p):
        """ assignable : variable
                       | unused
        """
        p[0] = p[1]

    def p_assignable_2(self, p):
        """ assignable : assignable DOT variable """
        p[0] = MemberAccess(p[1], p[3], p[1].coord)

    def p_assignable_3(self, p):
        """ assignable : assignable LBRACKET expr RBRACKET """
        p[0] = ArrayRef(p[1], p[3], p[1].coord)

    def p_assignable_4(self, p):
        """ assignable : LBRACKET explicit_assign_list RBRACKET
        """
        p[0] = p[2]

    def p_explicit_assign_list_1(self, p):
        """ explicit_assign_list : assignable """
        p[0] = p[1]

    def p_explicit_assign_list_2(self, p):
        """ explicit_assign_list : explicit_assign_list COMMA assignable """
        if not isinstance(p[1], AssignmentList):
            p[1] = AssignmentList([p[1]], p[1].coord)
        p[1].assignments.append(p[3])
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

    def p_expr_list_1(self, p):
        """ expr_list : expr  """
        p[0] = p[1]

    def p_expr_list_2(self, p):
        """ expr_list : expr_list COMMA expr """
        if not isinstance(p[1], ExprList):
            p[1] = ExprList([p[1]], p[1].coord)
        p[1].exprs.append(p[3])
        p[0] = p[1]

    ## Implication
        
    def p_implication_1(self, p):
        """ implication : disjunction """
        p[0] = p[1]

    def p_implication_2(self, p):
        """ implication : disjunction IMPLICATES disjunction """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    ## Disjunction

    def p_disjunction_1(self, p):
        """ disjunction : conjunction  """
        p[0] = p[1]

    def p_disjunction_2(self, p):
        """ disjunction : disjunction OR conjunction """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    ## Conjunction

    def p_conjunction_1(self, p):
        """ conjunction : comparison """
        p[0] = p[1]

    def p_conjunction_2(self, p):
        """ conjunction : conjunction AND comparison """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    ## Comparison

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

    ## Sum

    def p_sum_1(self, p):
        """ sum : product """
        p[0] = p[1]

    def p_sum_2(self, p):
        """ sum : sum PLUS product 
                | sum MINUS product
        """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    ## Product
                
    def p_product_1(self, p):
        """ product : reduce """
        p[0] = p[1]

    def p_product_2(self, p):
        """ product : product TIMES     reduce
                    | product DIVIDE    reduce
                    | product IDIVIDE   reduce
                    | product MOD       reduce
                    | product CARTESIAN reduce
        """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    ## Reduce
        
    def p_reduce_1(self, p):
        """ reduce : prefix_operation """
        p[0] = p[1]

    def p_reduce_2(self, p):
        """ reduce : reduce SUM prefix_operation
                   | reduce PRODUCT prefix_operation
        """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    ## Prefix Operation
        
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

    def p_prefix_operation_3(self, p):
        """ prefix_operation : factor POW prefix_operation """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    ## Factor
        
    def p_factor_1(self, p):
        """ factor  : value """
        p[0] = p[1]

    def p_factor_2(self, p):
        """ factor : BANG factor """
        p[0] = UnaryOp('not', p[2], p[2].coord)

    def p_factor_3(self, p):
        """ factor : value BANG """
        p[0] = UnaryOp('fac', p[1], p[1].coord)

    def p_factor_4(self, p):
        """ factor : TERM LPAREN term_arguments RPAREN """
        p[0] = Term(p[1], p[3], p[3].coord)

    ## Quantor

    def p_factor_5(self, p):
        """ factor : FORALL LPAREN iterator_chain PIPE condition RPAREN """
        p[0] = Quantor('all', p[3], p[5], p[3].coord)

    def p_factor_6(self, p):
        """ factor : EXISTS LPAREN iterator_chain PIPE condition RPAREN """
        p[0] = Quantor('any', p[3], p[5], p[3].coord)

    def p_factor_7(self, p):
        """ factor : LPAREN expr RPAREN """
        p[0] = p[2]

    def p_factor_8(self, p):
        """ factor : variable """
        p[0] = p[1]

    ##
    ## Term
    ##

    def p_term_arguments(self, p):
        """ term_arguments : expr_list
                           | epsilon
        """
        p[0] = p[1] if p[1] is not None else ExprList([])

    ##
    ## Iterator
    ##

    def p_iterator(self, p):
        """ iterator : assignable IN expr """
        p[0] = Iterator(p[1], p[3], p[1].coord)

    def p_iterator_chain_1(self, p):
        """ iterator_chain : iterator """
        p[0] = p[1]

    def p_iterator_chain_2(self, p):
        """ iterator_chain : iterator_chain COMMA iterator """
        if not isinstance(p[1], IteratorChain):
            p[1] = IteratorChain([p[1]], p[1].coord)
        p[1].iterators.append(p[3])
        p[0] = p[1]

    ##
    ## Values
    ##

    def p_unused(self, p):
        """ unused : UNUSED """
        p[0] = Variable('unused', 'unused')
        
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
        """ value : unused """
        p[0] = p[1]

    ## Atomic Value
        
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

    def p_epsilon(self, p):
        """ epsilon : """
        p[0] = None