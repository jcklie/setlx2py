from nose.tools import with_setup, eq_

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

######################--   TESTS     --######################

def test_should_be_creatable():
    lexer = Lexer()
    assert lexer is not None

def test_operators_calc():
    assert_token_types('+', ['PLUS'])
    assert_token_types('-', ['MINUS'])
    assert_token_types('\\', ['DIVIDE'])
    assert_token_types('*', ['TIMES'])

def test_constants_int_dec():
    assert_token_types('1337', ['INT_CONST_DEC'])
    assert_token_types('-1337', ['INT_CONST_DEC'])
    assert_token_types('+1337', ['INT_CONST_DEC'])

