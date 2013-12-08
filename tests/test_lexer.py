from nose.tools import with_setup, eq_, nottest

from setlx2py.setlx_lexer import Lexer

######################--   TEST UTIL --######################

def create_lexer():
    lexer = Lexer()
    lexer.build()
    return lexer

def token_list(lexer): 
    return list(iter(lexer.token, None))

def token_types(lexer):
    return [i.type for i in token_list(lexer)]

######################--   ASSERTS   --######################  

def assert_token_types(text, expected_types):
    lexer = create_lexer()
    lexer.input(text)
    actual_tokens = token_types(lexer)
    eq_(expected_types, actual_tokens, "{} != {}".format(expected_types, actual_tokens))

def assert_token_type(text, expected_type):
    assert_token_types(text, [expected_type])

######################--   TESTS     --######################

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
    assert_token_type('backtrack', 'BACKTRACK')
    assert_token_type('break', 'BREAK')
    assert_token_type('continue', 'CONTINUE')
    assert_token_type('exit', 'EXIT')
    assert_token_type('return', 'RETURN')
    assert_token_type('if', 'IF')
    assert_token_type('else', 'ELSE')

def test_assert_keyword_loops():
    assert_token_type('while', 'WHILE')
    assert_token_type('do', 'DO')
    assert_token_type('for', 'FOR')

def test_constants_integer():
    assert_token_types('1337', ['INTEGER'])
    assert_token_types('0', ['INTEGER'])

def test_constants_double():

    # More digits - More digits
    assert_token_types('1337.42', ['DOUBLE'])
        
    # Single digit - Single digit
    assert_token_types('0.0', ['DOUBLE'])
    
    # Zero Digit - More digits
    assert_token_types('.42', ['DOUBLE'])    

    # Zero Digit . Single digit 
    assert_token_types('.1', ['DOUBLE'])

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
    assert_token_type('.', 'DOT')
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
    