#------------------------------------------------------------------------------
# setlx2py: test_parsable
#
# Unit tests for the Parser class in setlx_parser.py
# Beware: Only the fact whether example code can 
#         be parsed is tested here!
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

import os

from nose.tools import eq_, with_setup, nottest

from setlx2py.setlx_parser import Parser

try:
    unicode('foo', errors='replace')
except NameError:
    def unicode(s, **kwargs): return s

##
## Test housekeeping
##

parser = Parser()

def setup_func():
    global parser
    parser = Parser()
    
def teardown_func():
    parser = None

def is_parsable(path):
    with open(path, 'r') as f:
        try:
            s = unicode(f.read(), errors='replace')
        except Exception as e:
            print(path)
            raise 

    try:
        parser.parse(s)
        return True        
    except SyntaxError as e:
        return False

def assert_parsable(folder):
    all_parsable = True
    not_parsable_files = []
    folder = os.path.abspath(folder)

    entries = [os.path.join(folder,f) for f in os.listdir(folder)]
    files = [f for f in entries if os.path.isfile(f)]
    
    for f in files:
        current_parsable = is_parsable(f)

        if not current_parsable:
            all_parsable = False
            not_parsable_files.append(f)

    msg = 'Cannot parse the following files: \n{0}'.format('\n'.join(not_parsable_files))
    assert all_parsable, msg

@with_setup(setup_func, teardown_func)
def test_parsable_logic():
    assert_parsable('tests/fixtures/logic') 

@with_setup(setup_func, teardown_func)
def test_parsable_logic_solutions():
    assert_parsable('tests/fixtures/logic/solutions')     