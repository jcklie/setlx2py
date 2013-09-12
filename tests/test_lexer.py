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
    assert_token_types('-1337', ['MINUS', 'INT_CONST_DEC'])
    assert_token_types('+1337', ['PLUS', 'INT_CONST_DEC'])
    assert_token_types('0', ['INT_CONST_DEC'])

def test_constants_frac_dect():

    # More digits - More digits
    assert_token_types('1337.42', ['FLOAT_CONST'])
    assert_token_types('-1337.42', ['MINUS', 'FLOAT_CONST'])
    assert_token_types('+1337.42', ['PLUS', 'FLOAT_CONST'])

    # Singe digit - Single digit
    assert_token_types('0.0', ['FLOAT_CONST'])
    assert_token_types('-4.2', ['MINUS', 'FLOAT_CONST'])
    assert_token_types('+3.6', ['PLUS', 'FLOAT_CONST'])

    # Zero Digit - More digits
    assert_token_types('.42', ['FLOAT_CONST'])    
    assert_token_types('+.42', ['PLUS', 'FLOAT_CONST'])
    assert_token_types('-.42', ['MINUS', 'FLOAT_CONST'])

    # Zero Digit . Single digit 
    assert_token_types('.1', ['FLOAT_CONST'])
    assert_token_types('-.1', ['MINUS', 'FLOAT_CONST'])
    assert_token_types('+.1', ['PLUS', 'FLOAT_CONST'])
