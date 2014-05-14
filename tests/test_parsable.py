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

from __future__ import unicode_literals

import os

from nose.tools import eq_, with_setup, nottest

from setlx2py.setlx_parser import Parser

##
## Test housekeeping
##

parser = Parser(yacc_optimize=False)

def is_parsable(path):
    with open(path, 'r') as f:
        try:
            s = f.read()
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

    msg =  'Parsed [{0}/{1}]\n'.format(len(files) - len(not_parsable_files),
                                       len(files))

    s = '\n'.join(not_parsable_files)
    msg += 'Cannot parse the following files: \n{0}'.format(s)
    
    assert all_parsable, msg

def test_parsable_logic():
    assert_parsable('tests/fixtures/logic') 

def test_parsable_logic_solutions():
    assert_parsable('tests/fixtures/logic/')     