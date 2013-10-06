from nose.tools import with_setup, eq_

from setlx2py.setlx_lexer import Lexer
from setlx2py.setlx_parser import Parser

######################--   TEST UTIL --######################

global parser

def setup_func():
    global parser
    parser = Parser()

def teardown_func():
    parser = None

######################--   ASSERTS   --######################  


######################--   TESTS     --######################

@with_setup(setup_func, teardown_func)
def test_should_be_creatable():
    assert parser is not None

def test_atomic_value_int():
    node = parser.parse("42;")
    assert node.value == 42

def test_atomic_value_double():
    node = parser.parse("42.0;")
    assert abs(node.value - 42.0) < .001

def test_atomic_value_true():
    node = parser.parse("true;")
    assert node.value

def test_atomic_value_false():
    node = parser.parse("false;")
    assert node.value
