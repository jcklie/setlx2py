#------------------------------------------------------------------------------
# setlx2py: setlx_list.py
#
# Home of the SetlxList, a 1-indexed list
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

import math
import collections
import functools
import operator
import random
import sys
import itertools as it

from setlx2py.builtin.setlx_set import SetlxSet
from setlx2py.builtin.setlx_string import SetlxString
from setlx2py.builtin.setlx_list import SetlxList

# Functions and Operators on Sets and Lists

def stlx_arb(m):
    """7. The function arb(s) picks an arbitrary element from the sequence s. The argument s
    can either be a set, a list, or a string. """
    return random.sample(m, 1)[0]

def stlx_from(m):
    """11. The function from(s) picks an arbitrary element from the sequence s. The argument
    s can either be a set, a list, or a string. This element is removed from s and returned. This
    function returns the same element as the function arb discussed previously.    
    """
    n = stlx_arb(m)
    m.remove(n)
    return n

def stlx_powerset(s):
    """17. If s is a set, the expression pow(s) computes the power set of s. The power set of s is 
    defined as the set of all subsets of s."""
    lst = list(s)
    return SetlxSet(it.chain.from_iterable(it.combinations(lst, r) for r in range(len(lst)+1)))

# Mathematical Functions

stlx_sin = math.sin
stlx_cos = math.cos
stlx_tan = math.tan
stlx_asin = math.asin
stlx_acos = math.acos
stlx_atan = math.atan

#==========================================

def stlx_pow(a,b=None):
    if b is None:
        return stlx_powerset(a)
    elif isinstance(a, SetlxSet) and b == 2:
        return stlx_cartesian(a,a)
    elif isinstance(b, SetlxSet) and a == 2:
        return stlx_powerset(b)
    else:
        return a ** b

def stlx_print(*args):
    s = ''.join(str(arg) for arg in args) + '\n'
    sys.stdout.write(s)

def stlx_range(*args):
    """
    [a..z]
    [a,b..z]
    """
    
    if not len(args) in [2,3]:
        raise Exception("stlx_range needs two or three arguments!")

    if len(args) == 2:
        a, z = args
        s = 1
        comp = operator.le
    else:
        a, b, z = args
        s = b - a
        comp = operator.le if a < b else operator.ge
        
    n = a
    while comp(n, z):
        yield n
        n += s

stlx_len = len
stlx_sum = sum
stlx_zip = zip
stlx_char = chr
stlx_is_string = lambda x : isinstance(x, basestring)

# Math
# ----

stlx_factorial = math.factorial

# Logic
# -----

def stlx_implies(p,q):
    return not(p) or q

def stlx_equivalent(p,q):
    return p == q

def stlx_antivalent(p,q):
    return not stlx_equivalent(p,q)

# Sets
# ----

def stlx_cartesian(*args):
    return SetlxSet(it.product(*args))



def stlx_product(factors):
    return functools.reduce(operator.mul, factors, 1)





# Misc
# ----

def stlx_abort(s):
    raise Exception(s)

# Matching
# --------

Pattern = collections.namedtuple('Pattern', ['headcount', 'has_tail'])

def _empty(x):
    return len(x) == 0

def stlx_matches(pattern, variables):
    """ A pattern matches when there are at least
    len(var) bindable elements in it.
    """
    if pattern.headcount == 0 and not _empty(variables):
        return False
    elif pattern.has_tail:
        return len(variables) >= pattern.headcount
    else:
        return len(variables) == pattern.headcount

class Bumper(object):

    def __add__(self, other):
        return other

    def __radd__(self, other):
        return other

    def __len__(self):
        return 0

    def __eq__(self, other):
        return isinstance(other, Bumper)

    def __repr__(self):
        return '<om>'

def stlx_bind(pattern, matchee):
    """
    Args:
        pattern (Pattern): The pattern which is bound to
        matche (SetlxList) : Data to bind to a pattern
    """

    assert isinstance(matchee, (SetlxString, SetlxList)), type(matchee)
    
    binding = []

    length = pattern.headcount

    # We use 1-Indexed counting here
    for i in range(1, length + 1):
        binding.append(matchee[i])

    if pattern.has_tail:
        last = matchee[length+1:]
        if last:
            binding.append(last)
        else:
            binding.append(Bumper())

    return binding

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
    