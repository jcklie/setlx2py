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
        self.parser = yacc.yacc(module=self, start='file_input')

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

    def p_file_input(self, p):
        """ file_input : statement_list """
        p[0] = FileAST([]) if p[1] is None else FileAST(p[1])

    def p_epsilon(self, p):
        """ epsilon : """
        p[0] = None

    ##
    ## Statements
    ##

    def p_statement_list_1(self, p):
        """ statement_list : statement  """
        p[0] = p[1]

    def p_statement_list_2(self, p):
        """ statement_list : statement_list statement  """
        if p[2] is not None:
            p[1].extend(p[2])
        p[0] = p[1]

    def p_statement(self, p):
        """ statement : simple_statement SEMICOLON
                      | compound_statement
        """
        p[0] = [p[1]]

    ####
    ##
    ## Simple statements
    ##
    ####
        
    def p_simple_statement(self, p):
        """ simple_statement : expression_statement
                             | assert_statement
                             | assignment_statement
                             | augmented_assign_statement
                             | backtrack_statement        
                             | break_statement
                             | continue_statement
                             | exit_statement
                             | return_statement
                             | quantor
                             | term
        """
        p[0] = p[1]

    def p_expression_statement(self, p):
        """ expression_statement : expression """
        p[0] = p[1]

    def p_backtrack_statement(self, p):
        """ backtrack_statement : BACKTRACK """
        p[0] = Backtrack()

    def p_break_statement(self, p):
        """ break_statement : BREAK """
        p[0] = Break()

    def p_continue_statement(self, p):
        """ continue_statement : CONTINUE """
        p[0] = Continue()

    def p_exit_statement(self, p):
        """ exit_statement : EXIT """
        p[0] = Exit()

    def p_return_statement_1(self, p):
        """ return_statement : RETURN """
        p[0] = Return(None)

    def p_return_statement_2(self, p):
        """ return_statement : RETURN expression """
        p[0] = Return(p[2], p[2].coord)
    
    ##
    ## Expressions
    ##

    def p_expression_list_1(self, p):
        """ expression_list : expression  """
        p[0] = p[1]

    def p_expression_list_2(self, p):
        """ expression_list : expression_list COMMA expression """
        if not isinstance(p[1], ExprList):
            p[1] = ExprList([p[1]], p[1].coord)
        p[1].exprs.append(p[3])
        p[0] = p[1]
        

    def p_expression_1(self, p):
        """ expression : implication
                       | lambda_definition
        """
        p[0] = p[1]

    def p_expression_2(self, p):
        """ expression : implication EQUIVALENT implication
                       | implication ANTIVALENT implication
        """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)


    # Implication
        
    def p_implication_1(self, p):
        """ implication : disjunction """
        p[0] = p[1]

    def p_implication_2(self, p):
        """ implication : disjunction IMPLICATES disjunction """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    # Disjunction

    def p_disjunction_1(self, p):
        """ disjunction : conjunction  """
        p[0] = p[1]

    def p_disjunction_2(self, p):
        """ disjunction : disjunction OR conjunction """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    # Conjunction

    def p_conjunction_1(self, p):
        """ conjunction : comparison """
        p[0] = p[1]

    def p_conjunction_2(self, p):
        """ conjunction : conjunction AND comparison """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    # Comparison

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

    # Sum

    def p_sum_1(self, p):
        """ sum : product """
        p[0] = p[1]

    def p_sum_2(self, p):
        """ sum : sum PLUS product 
                | sum MINUS product
        """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    # Product
                
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

    # Reduce
        
    def p_reduce_1(self, p):
        """ reduce : unary_expression """
        p[0] = p[1]

    def p_reduce_2(self, p):
        """ reduce : reduce SUM unary_expression
                   | reduce PRODUCT unary_expression
        """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    # Unary expression
        
    def p_unary_expression_1(self, p):
        """ unary_expression : power """
        p[0] = p[1]

    def p_unary_expression_2(self, p):
        """ unary_expression : SUM     unary_expression
                             | PRODUCT unary_expression
                             | HASH    unary_expression
                             | MINUS   unary_expression
                             | AT      unary_expression
        """
        p[0] = UnaryOp(p[1], p[2], p[2].coord)

    def p_unary_expression_3(self, p):
        """ unary_expression : BANG unary_expression """
        p[0] = UnaryOp('not', p[2], p[2].coord)

    def p_power_1(self, p):
        """ power : primary """
        p[0] = p[1]

    def p_power_2(self, p):
        """ power : primary POW unary_expression """
        p[0] = BinaryOp(p[2], p[1], p[3], p[1].coord)

    ## Primary
        
    def p_primary_1(self, p):
        """ primary  : atom
                     | attributeref
                     | subscription
                     | slicing
                     | procedure
                     | call
        """
        p[0] = p[1]

    def p_primary_2(self, p):
        """ primary : primary BANG """
        p[0] = UnaryOp('fac', p[1], p[1].coord)

    # Atom

    def p_atom(self, p):
        """ atom : identifier
                 | literal
                 | enclosure
        """
        p[0] = p[1]

    def p_variable(self, p):
        """ identifier : IDENTIFIER 
                       | UNUSED
        """
        p[0] = Identifier(p[1])

    # Attribute Ref

    def p_attributeref(self, p):
        """ attributeref : primary DOT identifier """
        p[0] = AttributeRef(p[1], p[3], p[1].coord)

    # Subscription

    def p_subscription(self, p):
        """ subscription : primary LBRACKET expression RBRACKET """
        p[0] = Subscription(p[1], p[3], p[1].coord)

    # Slicing

    def p_slicing(self, p):
        """ slicing : primary LBRACKET lower_bound RANGE upper_bound RBRACKET """
        p[0] = Slice(p[1], p[3], p[5])

    def p_lower_bound(self, p):
        """ lower_bound : expression
                        | epsilon
        """
        p[0] = p[1]

    def p_upper_bound(self, p):
        """ upper_bound : expression
                        | epsilon
        """
        p[0] = p[1]

    ##
    ## Literals
    ##

    def p_literal(self, p):
        """ literal : stringliteral
                    | integer
                    | floatnumber
                    | boolean
        """
        p[0] = p[1]

    # String constants

    def p_string_literal_1(self, p):
        """ stringliteral : STRING """
        p[0] = Constant('string', str(p[1]))

    def p_string_literal_2(self, p):
        """ stringliteral : LITERAL """
        p[0] = Constant('literal', str(p[1]))

    # Numerical constants

    def p_integer(self, p):
        """ integer  : INTEGER """
        p[0] = Constant('int', int(p[1]))

    def p_floatnumber(self, p):
        """ floatnumber : DOUBLE """
        p[0] = Constant('double', float(p[1]))

    def p_boolean_1(self, p):
        """ boolean : TRUE """
        p[0] = Constant('bool', True)

    def p_boolean_2(self, p):
        """ boolean : FALSE """
        p[0] = Constant('bool', False)

    ##
    ## Lambda Definitions
    ##

    def p_lambda_definition(self, p):
        """ lambda_definition : lambda_parameters LAMBDADEF expression """
        p[0] = Lambda(p[1], p[3], p[1].coord)

    def p_lambda_parameters(self, p):
        """ lambda_parameters : identifier
                              | LT parameter_list GT
        """
        if len(p) == 2:
            param = Param(p[1].name)
            p[0] = ParamList([param], p[1].coord)
        else:
            p[0] = p[2]
        

    ##
    ## Assignment Statement
    ##

    # TODO : recursive assignment
    def p_assignment_statement(self, p):
        """ assignment_statement : target_list ASSIGN expression """
        p[0] = Assignment(p[2], p[1], p[3],  p[3].coord)
        
    def p_target_list_1(self, p):
        """ target_list : target """
        p[0] = p[1]

    def p_target_list_2(self, p):
        """ target_list : target_list COMMA target """
        if not isinstance(p[1], TargetList):
             p[1] = TargetList([p[1]], p[1].coord)
        p[1].targets.append(p[3])
        p[0] = p[1]

    def p_target_1(self, p):
        """ target : identifier
                   | attributeref
                   | subscription        
        """
        p[0] = p[1]

    def p_target_2(self, p):
        """ target : LBRACKET target_list RBRACKET """
        p[0] = p[2]
        
        
    ##
    ## Augmented Assignment Statement
    ##

    def p_augmented_assign_statement(self, p):
        """ augmented_assign_statement : augtarget augop expression """
        p[0] = Assignment(p[2], p[1], p[3],  p[3].coord)
        
    def p_augtarget(self, p):
        """ augtarget : identifier
                      | attributeref
                      | subscription
        """
        p[0] = p[1]

    def p_augop(self, p):
        """ augop :  PLUS_EQUAL  
                  |  MINUS_EQUAL   
                  |  TIMES_EQUAL   
                  |  DIVIDE_EQUAL  
                  |  IDIVIDE_EQUAL 
                  |  MOD_EQUAL
        """
        p[0] = p[1]

    ##
    ## Assert
    ##

    def p_assert_statement(self, p):
        """ assert_statement : ASSERT LPAREN expression COMMA expression RPAREN """
        p[0] = Assert(p[3], p[5], p[3].coord)

    ##
    ## Term
    ##

    def p_term(self, p):
        """ term : TERM LPAREN term_arguments RPAREN """
        p[0] = Term(p[1], p[3], p[3].coord)

    def p_term_arguments(self, p):
        """ term_arguments : expression_list
                           | epsilon
        """
        p[0] = p[1] if p[1] is not None else ExprList([])

    ##
    ## Procedures
    ##
        
    def p_procedure_1(self, p):
        """ procedure : PROCEDURE LPAREN parameter_list RPAREN \
                        LBRACE block RBRACE
        """
        p[0] = Procedure(p[3], p[6], p[3].coord)

    def p_procedure_2(self, p):
        """ procedure : CPROCEDURE LPAREN parameter_list RPAREN \
                        LBRACE block RBRACE
        """
        p[0] = CachedProcedure(p[3], p[6], p[3].coord)

    def p_parameter_list(self, p):
        """ parameter_list : procedure_param
                           | parameter_list COMMA procedure_param
                           | epsilon
        """
        if len(p) == 2:
            if p[1] is None: p[0] = ParamList([])
            else: p[0] = ParamList([p[1]], p[1].coord)
        else:
            p[1].params.append(p[3])
            p[0] = p[1]

    def p_procedure_param(self, p):
        """ procedure_param : identifier """
        p[0] = Param(p[1].name, p[1].coord)

    ##
    ## Call
    ##

    def p_call(self, p):
        """ call : primary LPAREN argument_list RPAREN
                 | primary LPAREN RPAREN
        """
        argumentlist = p[3] if len(p) == 5 else ArgumentList([])
        p[0] = Call(p[1], argumentlist, p[1].coord)

    def p_argument_list(self, p):
        """ argument_list : expression
                          | argument_list COMMA expression
        """

        if len(p) == 2: # single expr
            p[0] = ArgumentList([p[1]], p[1].coord)
        else:
            p[1].arguments.append(p[3])
            p[0] = p[1]

    ##
    ## Quantor
    ##
    
    def p_quantor_1(self, p):
        """ quantor : FORALL LPAREN iterator_chain PIPE expression RPAREN """
        p[0] = Quantor('all', p[3], p[5], p[3].coord)

    def p_quantor_2(self, p):
        """ quantor : EXISTS LPAREN iterator_chain PIPE expression RPAREN """
        p[0] = Quantor('any', p[3], p[5], p[3].coord)

    ##
    ## Iterator
    ##

    def p_iterator(self, p):
        """ iterator : target IN expression """
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
    ##  Enclosures
    ##

    def p_enclosure(self, p):
        """ enclosure : parenth_form """
        p[0] = p[1]

    def p_parenth_form(self, p):
        """ parenth_form : LPAREN expression RPAREN """
        p[0] = p[2]


    ####
    ##
    ## Compound statement
    ##
    ####
        
    def p_compound_statement(self, p):
        """ compound_statement : if_statement
                               | switch_statement
                               | while_loop
                               | do_while_loop
        """
        p[0] = p[1]
        
    def p_block(self, p):
        """ block : statement_list
                  | epsilon
        """
        if p[1] is None:
            p[0] = Block([])
        else:
            p[0] = Block(p[1])
      
    ##
    ## If Statements
    ##

    def p_if_statement_1(self, p):
        """ if_statement : IF LPAREN expression RPAREN LBRACE block RBRACE """
        p[0] = If(p[3], p[6], None, p[3].coord)

    def p_if_statement_2(self, p):
        """ if_statement : IF LPAREN expression RPAREN \
                           LBRACE block RBRACE \
                           ELSE LBRACE block RBRACE """
        p[0] = If(p[3], p[6], p[10], p[3].coord)
        
    def p_if_statement_3(self, p):
        """ if_statement : IF LPAREN expression RPAREN \
                           LBRACE block RBRACE \
                           ELSE if_statement  """
        p[0] = If(p[3], p[6], p[9], p[3].coord)
        
    ##
    ## Switch Statement
    ##

    def p_switch_statement(self, p):
        """ switch_statement : SWITCH LBRACE case_statements default_case RBRACE """
        p[0] = Switch(p[3], p[4], p[3].coord)

    def p_case_statements(self, p):
        """ case_statements : case_list
                            | epsilon
        """
        if p[1] is None:
            p[0] = CaseList([])
        else:
            p[0] = CaseList(p[1])

    def p_case_list_1(self, p):
        """ case_list : case_statement  """
        p[0] = [p[1]]

    def p_case_list_2(self, p):
        """ case_list : case_list case_statement  """
        if p[2] is not None:
            p[1].append(p[2])
        p[0] = p[1]

    def p_case_statement(self, p):
         """ case_statement : CASE expression COLON block """
         p[0] = Case(p[2], p[4], p[2].coord)

    def p_default_case_1(self, p):
        """ default_case : DEFAULT COLON block """
        p[0] = Default(p[3], p[3].coord)

    def p_default_case_2(self, p):
        """ default_case : epsilon """
        p[0] = None
        
    ##
    ## Loops
    ##

    def p_while_loop(self, p):
        """ while_loop : WHILE LPAREN expression RPAREN LBRACE block RBRACE """
        p[0] = While(p[3], p[6], p[3].coord)

    def p_do_while_loop(self, p):
        """ do_while_loop : DO LBRACE block RBRACE \
                            WHILE LPAREN expression RPAREN SEMICOLON
        """
        p[0] = DoWhile(p[7], p[3], p[3].coord)

#    def p_for_loop(self, p):
#        """ for_loop : FOR LPAREN iterator_chain  RPAREN LBRACE block RBRACE """
#        p[0] = For(p[3], p[6], p[3].coord)

        
    # ##
    # ## Values
    # ##

    # def p_unused(self, p):
    #     """ unused : UNUSED """
    #     p[0] = Variable('unused', 'unused')
        
    # def p_value_1(self, p):
    #     """ value : atomic_value """
    #     p[0] = p[1]


    # def p_value_4(self, p):
    #     """ value : unused """
    #     p[0] = p[1]

    # ## Atomic Value
        

