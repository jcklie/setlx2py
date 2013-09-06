from setlx2py.setlx_lexer import Lexer

lexer = None

######################--   TEST UTIL --######################

def setup_func():
    lexer = Lexer()

def teardown_func():
    lexer = None

######################--   ASSERTS   --######################  

def assert_token_types(self, str, types):
    lexer.input(str)
    assertEqual(token_types(lexer), types)

######################--   TESTS     --######################

@with_setup(setup_func, teardown_func)
def test_should_be_creatable():
    assert lexer is not None

@with_setup(setup_func, teardown_func)
def test_operators_calc():
    assert_token_types('+', ['PLUS'])
    assert_token_types('-', ['MINUS'])
