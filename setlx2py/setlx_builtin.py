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

import itertools as it

# Custom classes
# ==============

class Set(frozenset):

    def __init__(self, iterable):
        super(Set, self).__init__(iterable)

    def __add__(self, other):
        return self.union(other)
        
    def __mul__(self, other):
        return self.intersection(other)

    def __mod__(self, other):
        return self.symmetric_difference(other)

    def _tuple_it(self, l):
        return tuple(map(self._tuple_it, l)) if isinstance(l, (list, tuple)) else l

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
    return reduce(operator.mul, factors, 1)

builtin = {
    # Classes
    'Set'       : Set,
    # Functions
    'factorial' : math.factorial,
    'product'   : product,
    'implies'   : implies,
    'equivalent': equivalent,
    'antivalent': antivalent,
    'pow'       : custom_pow,
    'cartesian' : cartesian,
}
    




