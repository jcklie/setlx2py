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
from setlx2py.setlx_semcheck import *

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

    def p_unary_expression_4(self, p):
        """ unary_expression : quantor
                             | term
        """
        p[0] = p[1]

    def p_power_1(self, p):
        """ power : primary """
        p[0] = p[1]

    def p_power_2(self, p):
        """ power : primary POW power """
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
    ##  Enclosures
    ##

    def p_enclosure(self, p):
        """ enclosure : set_range
                      | set_display
                      | set_comprehension
                      | list_range
                      | list_display
                      | list_comprehension   
                      | parenth_form
        """
        p[0] = p[1]

    def p_parenth_form(self, p):
        """ parenth_form : LPAREN expression RPAREN """
        p[0] = p[2]

    ##
    ## Comprehension
    ##

    def p_comprehension_condition_1(self, p):
        """ comprehension_condition : PIPE expression """
        p[0] = p[2]

    def p_comprehension_condition_2(self, p):
        """ comprehension_condition : epsilon """
        p[0] = None
        
    # Set comprehension

    def p_set_comprehension(self, p):
        """ set_comprehension : LBRACE expression COLON \
                                iterator_chain comprehension_condition RBRACE
        """
        p[0] = Comprehension('set', p[2], p[4], p[5], p[2].coord)

    # List comprehension

    def p_list_comprehension(self, p):
        """ list_comprehension : LBRACKET expression COLON \
                                 iterator_chain comprehension_condition RBRACKET
        """
        p[0] = Comprehension('list', p[2], p[4], p[5], p[2].coord)

    ##
    ## Range
    ##

    # Set range

    def p_set_range_1(self, p):
        """ set_range : LBRACE expression RANGE expression RBRACE """
        p[0] = Range('set', p[2], p[4], None)

    def p_set_range_2(self, p):
        """ set_range : LBRACE expression \
                        COMMA expression RANGE expression RBRACE
        """
        p[0] = Range('set', p[2], p[6], p[4])

    # List Range
    
    def p_list_range_1(self, p):
       """ list_range : LBRACKET expression RANGE expression RBRACKET """
       p[0] = Range('list', p[2], p[4], None)

    def p_list_range_2(self, p):
        """ list_range : LBRACKET expression \
                         COMMA expression RANGE expression RBRACKET """
        p[0] = Range('list', p[2], p[6], p[4])

    ##
    ## Displays
    ##

    # Set Display

    def p_set_display_1(self, p):
        """ set_display : LBRACE expression RBRACE """
        p[0] = Set([p[2]], p[2].coord)

    def p_set_display_2(self, p):
        """ set_display : LBRACE expression COMMA argument_list RBRACE """
        lst = p[4].arguments
        expr = p[2]
        lst.insert(0, expr)
        p[0] = Set(lst, expr.coord)

    def p_set_display_3(self, p):
        """ set_display : LBRACE RBRACE """
        p[0] = Set([])

    def p_set_display_4(self, p):
        """ set_display : LBRACE expression PIPE expression RBRACE  """
        p[0] = Pattern(p[2], p[4], p[2].coord)

    # List Display

    def p_list_display_1(self, p):
        """ list_display : LBRACKET expression RBRACKET """
        p[0] = List([p[2]], p[2].coord)

    def p_list_display_2(self, p):
        """ list_display : LBRACKET expression COMMA argument_list RBRACKET """
        lst = p[4].arguments
        expr = p[2]
        lst.insert(0, expr)
        p[0] = List(lst, expr.coord)

    def p_list_display_3(self, p):
        """ list_display : LBRACKET RBRACKET """
        p[0] = List([])
        
    def p_list_display_4(self, p):
        """ list_display : LBRACKET expression PIPE expression RBRACKET """
        p[0] = Pattern(p[2], p[4], p[2].coord)
        
    ##
    ## Lambda Definitions
    ##

    def p_lambda_definition(self, p):
        """ lambda_definition : lambda_parameters LAMBDADEF expression """
        p[0] = Lambda(p[1], p[3], p[1].coord)

    def p_lambda_parameters_1(self, p):
        """ lambda_parameters : identifier """
        param = p[1]
        p[0] = ParamList([param], p[1].coord)

    def p_lambda_parameters_2(self, p):
        """ lambda_parameters : list_display """
        lst = p[1].items
        params = ParamList(lst, p[1].coord)
        check_lambda(params)
        p[0] = params

    ##
    ## Assignment Statement
    ##

    # TODO : recursive assignment
    def p_assignment_statement(self, p):
        """ assignment_statement : target ASSIGN expression """
        p[0] = Assignment(p[2], p[1], p[3],  p[3].coord)

    def p_target(self, p):
        """ target : expression """
        ast = p[1]
        check_target(ast)
        p[0] = p[1]
        
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
        """ term : TERM LPAREN argument_list RPAREN """
        p[0] = Term(p[1], p[3], p[3].coord)

    def p_term_2(self, p):
        """ term : TERM LPAREN RPAREN """
        lst = ArgumentList([])
        p[0] = Term(p[1], lst)

    ##
    ## Procedures
    ##
        
    def p_procedure_1(self, p):
        """ procedure : PROCEDURE LPAREN parameter_list RPAREN \
                        LBRACE block RBRACE
        """
        p[0] = Procedure(p[3], p[6], p[6].coord)

    def p_procedure_2(self, p):
        """ procedure : CPROCEDURE LPAREN parameter_list RPAREN \
                        LBRACE block RBRACE
        """
        p[0] = CachedProcedure(p[3], p[6], p[6].coord)

    def p_parameter_list_1(self, p):
        """ parameter_list : params """
        p[0] = p[1]

    def p_parameter_list_2(self, p):
        """ parameter_list : epsilon """
        p[0] = ParamList([])

    def p_params(self, p):
        """ params : procedure_param
                   | params COMMA procedure_param
        """
        if len(p) == 2: # single parameter
            p[0] = ParamList([p[1]], p[1].coord)
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
        """ iterator : comparison """
        ast = p[1]
        check_iterator(ast)
        p[0] = Iterator(ast.left, ast.right, ast.coord)

    def p_iterator_chain_1(self, p):
        """ iterator_chain : iterator """
        p[0] = p[1]

    def p_iterator_chain_2(self, p):
        """ iterator_chain : iterator_chain COMMA iterator """
        if not isinstance(p[1], IteratorChain):
            p[1] = IteratorChain([p[1]], p[1].coord)
        p[1].iterators.append(p[3])
        p[0] = p[1]

    ####
    ##
    ## Compound statement
    ##
    ####
        
    def p_compound_statement(self, p):
        """ compound_statement : if_statement
                               | switch_statement
                               | match_statement
                               | scan_statement
                               | while_loop
                               | do_while_loop
                               | for_loop
                               | class
                               | try_statement
                               | check_statement
                               
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
    ## Match
    ##

    def p_match_statement(self, p):
        """ match_statement : MATCH LPAREN expression RPAREN \
                              LBRACE match_list default_case RBRACE 
        """
        if not isinstance(p[6], CaseList):
            p[6] = CaseList([p[6]], p[3].coord)

        p[0] = Match(p[3], p[6], p[7], p[3].coord)

    def p_match_list_1(self, p):
        """ match_list : matchee  """
        p[0] = p[1]
    
    def p_match_list_2(self, p):
        """ match_list : match_list matchee """
        if not isinstance(p[1], CaseList):
            p[1] = CaseList([p[1]], p[1].coord)
        p[1].cases.append(p[2])
        p[0] = p[1]

    def p_matche(self, p):
        """ matchee : match_case
                    | regex_branch
        """
        p[0] = p[1]

    def p_match_case(self, p):
        """ match_case : CASE expression_list case_condition COLON block """
        p[0] = MatchCase(p[2], p[3], p[5], p[2].coord)

    # Regex case

    def p_regex_branch(self, p):
        """ regex_branch : REGEX expression as case_condition COLON block """
        p[0] = Regex(p[2], p[3], p[4], p[6], p[2].coord)

    def p_as_1(self, p):
        """ as : AS expression """
        p[0] = As(p[2], p[2].coord)

    def p_as_2(self, p):
        """ as : epsilon """
        p[0] = None

    def p_case_condition_1(self, p):
        """ case_condition : PIPE expression """
        p[0] = p[2]

    def p_case_condition_2(self, p):
        """ case_condition : epsilon """
        p[0] = None

    ##
    ## Scan
    ##

    def p_scan_statement(self, p):
        """ scan_statement : SCAN LPAREN expression RPAREN using \
                             LBRACE regex_list default_case RBRACE
        """
        if not isinstance(p[7], CaseList):
            p[7] = CaseList([p[7]], p[7].coord)

        p[0] = Scan(p[3], p[5], p[7], p[8], p[3].coord)

    def p_using_1(self, p):
        """ using : USING identifier """
        p[0] = As(p[2], p[2].coord)

    def p_using_2(self, p):
        """ using : epsilon """
        

    def p_regex_list_1(self, p):
        """ regex_list : regex_branch  """
        p[0] = p[1]
    
    def p_regex_list_2(self, p):
        """ regex_list : regex_list regex_branch """
        if not isinstance(p[1], CaseList):
            p[1] = CaseList([p[1]], p[1].coord)
        p[1].cases.append(p[2])
        p[0] = p[1]

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

    def p_for_loop(self, p):
        """ for_loop : FOR LPAREN iterator_chain  RPAREN LBRACE block RBRACE """
        p[0] = For(p[3], p[6], p[3].coord)

    ##
    ## Class
    ##

    def p_class(self, p):
        """ class : CLASS identifier LPAREN parameter_list RPAREN \
                    LBRACE block static_block RBRACE
        """
        p[0] = Class(p[2], p[4], p[7],p[8], p[2].coord)

    def p_static_block_1(self, p):
        """ static_block : STATIC LBRACE block RBRACE """
        p[0] = p[3]

    def p_static_block_2(self, p):
        """ static_block : epsilon """
        p[0] = Block([])

    ##
    ## Try/Catch
    ##

    def p_try_statement(self, p):
        """ try_statement : TRY LBRACE block RBRACE catches """
        p[0] = Try(p[3], p[5], p[3].coord)

    def p_catches_1(self, p):
        """ catches : catch_clause """
        p[0] = Catches([p[1]], p[1].coord)
        
    def p_catches_2(self, p):
        """ catches : catches catch_clause """
        p[1].clauses.append(p[2].clauses)
        p[0] = p[1]

    def p_catch_clause(self, p):
        """ catch_clause : catch_type LPAREN identifier RPAREN \
                           LBRACE block RBRACE
        """
       
        p[0] = CatchClause(p[1], p[3], p[6], p[3].coord)

    def p_catch_type(self, p):
        """ catch_type : CATCH
                       | CATCH_USR
                       | CATCH_LNG
        """
        p[0] = p[1]

    ##
    ## Backtrack
    ##

    def p_check_statement(self, p):
        """ check_statement : CHECK LBRACE block RBRACE """
        p[0] = Check(p[3], p[3].coord)