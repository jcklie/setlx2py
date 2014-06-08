#------------------------------------------------------------------------------
# setlx2py: setlx_builtin.py
#
# Builtin functions and other dependencies for setlx
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

import math
import collections
import operator
import functools
import sys
import random
import itertools as it
import blist

# Custom classes
# ==============





    
builtin = [
    # Classes
    'Set',

    'Pattern'  ,
    'memoized',
    
    # Functions
    'factorial',
    'product',   
    
    'implies',
    'equivalent',
    'antivalent',
    'arb',
    'pop_random',
    'powerset',
    'pow',
    'cartesian',
    
    'matches',
    'bind',

    'print',

    'is_string',

    'zip',
    'char',
]

def generate_builtin_import():
    s = 'from setlx2py.setlx_builtin import '
    for k, v in builtin.items():
        s += '{0} as {1}, '.format(v, k if isinstance(k, basestring) else k.func_name)
    return s    




