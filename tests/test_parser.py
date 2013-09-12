from nose.tools import with_setup, eq_

from setlx2py.setlx_lexer import Lexer
from setlx2py.setlx_parser import Parser

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


