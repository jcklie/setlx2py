from nose.tools import with_setup, eq_, nottest

from setlx2py.setlx_lexer import Lexer

##
## Test housekeeping
##

def create_lexer():
    lexer = Lexer()
    lexer.build()
    return lexer

def token_list(lexer): 
    return list(iter(lexer.token, None))

def token_types(lexer):
    return [i.type for i in token_list(lexer)]

##
## Custom asserts
##

def assert_token_types(text, expected_types):
    lexer = create_lexer()
    lexer.input(text)
    actual_tokens = token_types(lexer)
    eq_(expected_types, actual_tokens, "{} != {}".format(expected_types, actual_tokens))

def assert_token_type(text, expected_type):
    assert_token_types(text, [expected_type])

##
## Tests
##

def test_should_be_creatable():
    lexer = Lexer()
    assert lexer is not None

def test_operators_sum():
    assert_token_types('+', ['PLUS'])
    assert_token_types('-', ['MINUS'])

def test_operators_product():
    assert_token_types('/', ['DIVIDE'])
    assert_token_types('*', ['TIMES'])
    assert_token_types('\\', ['IDIVIDE'])
    assert_token_types('%', ['MOD'])
    assert_token_types('><', ['CARTESIAN'])
    assert_token_types('**', ['POW'])

def test_operators_prefix():
    assert_token_types('@', ['AT'])
    assert_token_types('#', ['HASH'])
    assert_token_types('!', ['BANG'])

def test_operators_reduce():
    assert_token_types('+/', ['SUM'])
    assert_token_types('*/', ['PRODUCT'])

def test_operators_boolean():
    assert_token_types('<==>', ['EQUIVALENT'])
    assert_token_types('<!=>', ['ANTIVALENT'])
    assert_token_types('=>', ['IMPLICATES'])
    assert_token_types('||', ['OR'])
    assert_token_types('&&', ['AND'])
    assert_token_types('==', ['EQ'])
    assert_token_types('!=', ['NEQ'])
    assert_token_types('<', ['LT'])
    assert_token_types('<=', ['LE'])
    assert_token_types('>', ['GT'])
    assert_token_types('>=', ['GE'])

def test_keywords():
    assert_token_type('in', 'IN')
    assert_token_type('notin', 'NOTIN')
    assert_token_type('forall', 'FORALL')
    assert_token_type('exists', 'EXISTS')
    assert_token_type('break', 'BREAK')
    assert_token_type('continue', 'CONTINUE')
    assert_token_type('exit', 'EXIT')
    assert_token_type('return', 'RETURN')
    assert_token_type('if', 'IF')
    assert_token_type('else', 'ELSE')
    assert_token_type('match', 'MATCH')
    assert_token_type('regex', 'REGEX')
    assert_token_type('as', 'AS')
    assert_token_type('scan', 'SCAN')
    assert_token_type('using', 'USING')

def test_keywords_class():
    assert_token_type('class', 'CLASS')
    assert_token_type('static', 'STATIC')

def test_keywords_switch():
    assert_token_type('switch', 'SWITCH')
    assert_token_type('case', 'CASE')
    assert_token_type('default', 'DEFAULT')

def test_keywords_loops():
    assert_token_type('while', 'WHILE')
    assert_token_type('do', 'DO')
    assert_token_type('for', 'FOR')

def test_keywords_backtrack():
    assert_token_type('backtrack', 'BACKTRACK')
    assert_token_type('check', 'CHECK')

def test_keywords_procedures():
    assert_token_type('procedure', 'PROCEDURE')
    assert_token_type('cachedProcedure', 'CPROCEDURE')

def test_constants_integer():
    assert_token_type('1337', 'INTEGER')
    assert_token_type('0', 'INTEGER')

def test_constants_double():

    # More digits - More digits
    assert_token_type('1337.42', 'DOUBLE')
        
    # Single digit - Single digit
    assert_token_type('0.0', 'DOUBLE')
    assert_token_type('.2', 'DOUBLE')    

def test_constants_double_exponential():
    assert_token_type('1.23E+02', 'DOUBLE')
    assert_token_type('1.23E-04', 'DOUBLE')
    assert_token_type('.5e2', 'DOUBLE')
    
    # Zero Digit - More digits
#    assert_token_types('.42', ['DOUBLE'])    

    # Zero Digit . Single digit 
#    assert_token_types('.1', ['DOUBLE'])

def test_constants_bool():
    assert_token_types('true', ['TRUE'])
    assert_token_types('false', ['FALSE'])

def test_identifier():
    assert_token_types('q0', ['IDENTIFIER'])
    assert_token_types('a', ['IDENTIFIER'])
    assert_token_types('a_', ['IDENTIFIER'])
    assert_token_types('a13234', ['IDENTIFIER'])
    assert_token_types('z42a_____', ['IDENTIFIER'])

def test_term():
    assert_token_type('F', 'TERM')
    assert_token_type('FabcXYZ', 'TERM')
    assert_token_type('Hugo_', 'TERM')
    assert_token_type('^sum', 'TERM')

def test_strings():
    assert_token_types('"FOOBAR"', ['STRING'])
    assert_token_types('"\n4214"', ['STRING'])

def test_literal():
    assert_token_types("'FOOBAR'", ['LITERAL'])
    assert_token_types("'\n4214'", ['LITERAL'])

def test_unused():
    assert_token_types("_", ['UNUSED'])

def test_delimiter():
    assert_token_type(';', 'SEMICOLON')
    assert_token_type(',', 'COMMA')
    assert_token_type(':', 'COLON')
    assert_token_type('.', 'DOT')
    assert_token_type('..', 'RANGE')
    assert_token_types('()', ['LPAREN', 'RPAREN'])
    assert_token_types('[]', ['LBRACKET', 'RBRACKET'])
    assert_token_types('{}', ['LBRACE', 'RBRACE'])

def test_assign():
    assert_token_type(':=',  'ASSIGN')
    assert_token_type('+=',  'PLUS_EQUAL')
    assert_token_type('-=',  'MINUS_EQUAL')
    assert_token_type('*=',  'TIMES_EQUAL')
    assert_token_type('/=',  'DIVIDE_EQUAL')
    assert_token_type('\\=', 'IDIVIDE_EQUAL')
    assert_token_type('%=',  'MOD_EQUAL')
    assert_token_type('|->', 'LAMBDADEF')

def test_try_catch():
    assert_token_type('try', 'TRY')
    assert_token_type('catch', 'CATCH')
    assert_token_type('catchUsr', 'CATCH_USR')
    assert_token_type('catchLng', 'CATCH_LNG')

##
## More complex examples
##

def test_case_statements():
    assert_token_types("case grade == 'A' : return 'Excellent';",
                       ['CASE', 'IDENTIFIER', 'EQ', 'LITERAL', 'COLON',
                        'RETURN', 'LITERAL', 'SEMICOLON'])
def test_range():
    assert_token_types("[1..10]", ['LBRACKET', 'INTEGER', 'RANGE',
                                   'INTEGER', 'RBRACKET'])

##
## Test escape stuffs
##

def test_escape_doublequote():
    s = r'''"The formula \""'''
    assert_token_types(s, ['STRING'])

def test_escape_singleuote():
    s = r"""'The formula \''"""
    assert_token_types(s, ['LITERAL'])

