#------------------------------------------------------------------------------
# setlx2py: setlx_list.py
#
# Predefined functions of SetlX
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

import math
import functools
import operator
import random
import sys
import itertools as it
import collections

from setlx2py.builtin.setlx_set import SetlxSet
from setlx2py.builtin.setlx_string import SetlxString
from setlx2py.builtin.setlx_list import SetlxList

# Functions and Operators on Sets and Lists
# =========================================

#7
def stlx_arb(m):
    """The function arb(s) picks an arbitrary element from the sequence s. The argument s
    can either be a set, a list, or a string. """
    return random.sample(m, 1)[0]

#8
def stlx_collect(m):
    d = collections.defaultdict(int)
    for x in m: 
        d[x] += 1
    return SetlxSet( [ SetlxList( [k, c]) for k, c in d.iteritems()])

#9
def stlx_first(s):
    return next(iter(s))

#10
def stlx_last(s):
    return s[-1]

#11
def stlx_from(m):
    """The function from(s) picks an arbitrary element from the sequence s. The argument
    s can either be a set, a list, or a string. This element is removed from s and returned. This
    function returns the same element as the function arb discussed previously.    
    """
    n = stlx_arb(m)
    m.remove(n)
    return n

#14
def stlx_domain(s):
    """"""
    lst = [x for x, unused in s]
    return SetlxSet(lst)

#17
def stlx_powerset(s):
    """If s is a set, the expression pow(s) computes the power set of s. The power set of s is 
    defined as the set of all subsets of s."""

    def powerset_generator(i):
        for subset in it.chain.from_iterable(it.combinations(i, r) for r in range(len(i)+1)):
            yield set(subset)
            
    return SetlxSet(SetlxSet(z) for z in powerset_generator(s))

#18
def stlx_range(s):
    """ If r is a binary relation, then the equality
        range(r) = { y :[x,y] in R }
        holds.
    """
    lst = [y for unused, y in s]
    return SetlxSet(lst)

# Mathematical Functions
# =========================================

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

def stlx_lst_from_range(*args):
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


    

def is_builtin_function(name):
    return name in [ 'print', 'from', 'arb', 'pow', 'char', 'isString', 'abort', 'cos', 'powerset', 'domain', 'range' ]
    