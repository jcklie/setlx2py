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

import itertools as it

# Custom classes
# ==============

class Set(frozenset):

    def __init__(self, iterable):
        super(Set, self).__init__()

    def __add__(self, other):
        return self.union(other)
        
    def __mul__(self, other):
        return self.intersection(other)

    def __mod__(self, other):
        return self.symmetric_difference(other)

    def _tuple_it(self, l):
        return tuple(map(self._tuple_it, l)) if isinstance(l, (list, tuple)) else l

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

# Builtin Functions
# =================

# Change builtin functions
# ------------------------

def custom_pow(a,b):
    if isinstance(a, Set) and b == 2:
        return cartesian(a,a)
    elif isinstance(b, Set) and a == 2:
        return powerset(b)
    else:
        return a ** b        

# Logic
# -----

def implies(p,q):
    return not(p) or q

def equivalent(p,q):
    return p == q

def antivalent(p,q):
    return not equivalent(p,q)

# Sets
# ----

def cartesian(a,b):
    return Set(element for element in it.product(a, b))

def powerset(s):
    lst = list(s)
    return Set(it.chain.from_iterable(it.combinations(lst, r) for r in range(len(lst)+1)))

def product(factors):
    return functools.reduce(operator.mul, factors, 1)

# Matching
# --------

class Pattern(collections.namedtuple('Pattern', ['head', 'tail'])):
    def __new__(cls, head, tail=None):
        return super(Pattern, cls).__new__(cls, head, tail)

def _empty(x):
    return len(x) == 0

def matches(pattern, variables):
    """ A pattern matches when there are at least
    len(var) bindable elements in it.
    """
    if _empty(pattern.head) and not _empty(variables): return False
    return len(variables) >= len(pattern.head)

def bind(pattern, matchee='_matchee'):
    front = ', '.join(pattern.head)
    back = ''
    for i in range(len(pattern.head)):
        back += '{0}[{1}], '.format(matchee, i) # e.g. _matchee[0]

    if pattern.tail:
        front += ', ' + pattern.tail
        back += '{0}[{1}:]'.format(matchee, i+1)
    return front + ' = ' + back
    
builtin = {
    # Classes
    'Set'       : Set,
    'Pattern'   : Pattern,
    'memoized'  : memoized,
    # Functions
    'factorial' : math.factorial,
    'product'   : product,
    'implies'   : implies,
    'equivalent': equivalent,
    'antivalent': antivalent,
    'pow'       : custom_pow,
    'cartesian' : cartesian,
    'matches'   : matches
}
    




