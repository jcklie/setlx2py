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

def test_operators_boolean():
    assert_token_types('<==>', ['EQUIVALENT'])
    assert_token_types('<!=>', ['ANTIVALENT'])            

def test_constants_integer():
    assert_token_types('1337', ['INTEGER'])
    assert_token_types('0', ['INTEGER'])

def test_constants_double():

    # More digits - More digits
    assert_token_types('1337.42', ['DOUBLE'])
        
    # Singe digit - Single digit
    assert_token_types('0.0', ['DOUBLE'])
    
    # Zero Digit - More digits
    assert_token_types('.42', ['DOUBLE'])    

    # Zero Digit . Single digit 
    assert_token_types('.1', ['DOUBLE'])

def test_constants_bool():
    assert_token_types('true', ['TRUE'])
    assert_token_types('false', ['FALSE'])