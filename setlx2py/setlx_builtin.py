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




class memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    '''
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)

    
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




