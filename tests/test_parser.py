from nose.tools import with_setup, eq_

from setlx2py.setlx_lexer import Lexer
from setlx2py.setlx_parser import Parser

######################--   TEST UTIL --######################

def create_parser():
    parser = Parser()
    return parser 

######################--   ASSERTS   --######################  


######################--   TESTS     --######################

def test_should_be_creatable():
    parser= Parser()
    assert parser is not None

def test_expressions_simple():
    t1 = """1 + 1"""

