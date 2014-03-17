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
        s = unicode(f.read(), errors='replace')
    try:
        parser.parse(s)
    except:
        return False

    return True
        
@with_setup(setup_func, teardown_func)
def test_parsable():
    all_parsable = True
    not_parsable_files = []
    
    for f in os.listdir('tests/fixtures/logic'):
        path = os.path.join('tests/fixtures/logic', f)
        current_parsable = is_parsable(path)

        if not current_parsable:
            all_parsable = False
            not_parsable_files.append(path)

    msg = 'Cannot parse the following files: \n{0}'.format('\n'.join(not_parsable_files))
    assert all_parsable, msg