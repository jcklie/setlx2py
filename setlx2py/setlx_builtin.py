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

class Set(blist.sortedset):

    def __add__(self, other):
        return self.union(other)
        
    def __mul__(self, other):
        return self.intersection(other)

    def __mod__(self, other):
        return self.symmetric_difference(other)

    def __lt__(self, other):
        l1 = len(self)
        l2 = len(other)

        it1 = iter(self)
        it2 = iter(other)

        for i in range(max(l1,l2)):
            try:
                x = it1.next()
                y = it2.next()
                if x != y:
                    return x < y
            except StopIteration:
                return l1 < l2
                    
        return False

    def __getitem__(self, val):
        return super(Set, self).__getitem__(val)
        

    def __repr__(self):
        data = sorted(self)

        s = ', '.join(repr(i) for i in data)
        
        s = s.replace('(', '{')
        s = s.replace(')', '}')
        s = s.replace(',}', '}')
        return '{' + s + '}'

class SetlxList(list):
    """
    Since python lists are zero-indexed, and SetlX
    is one-indexed, it has to be converted somewhere
    """
        
    """One-based version of list."""

    def _zerobased(self, i):
        if type(i) is slice:
            return slice(self._zerobased(i.start),
                         self._zerobased(i.stop), i.step)
        else:
            if i is None or i < 0:
                return i
            elif not i:
                raise IndexError("element 0 does not exist in 1-based list")
            return i - 1

    def __getitem__(self, i):
        return list.__getitem__(self, self._zerobased(i))
    def __setitem__(self, i, value):
        list.__setitem__(self, self._zerobased(i), value)

    def __delitem__(self, i):
        list.__delitem__(self, self._zerobased(i))

    def __getslice__(self, i, j):
        """ Setlx slices include the upper limit, whereas Python does not """
        return list.__getslice__(self, self._zerobased(i or 1),
                                 self._zerobased(j + 1))

    def __setslice__(self, i, j, value):
        list.__setslice__(self, self._zerobased(i or 1),
                          self._zerobased(j), value)

    def index(self, value, start=1, stop=-1):
        return list.index(self, value, self._zerobased(start),
                          self._zerobased(stop)) + 1

    def pop(self, i):
        return list.pop(self, self._zerobased(i))

class SetlxString(str):

    def _zerobased(self, i):
        if type(i) is slice:
            return slice(self._zerobased(i.start),
                         self._zerobased(i.stop), i.step)
        else:
            if i is None or i < 0:
                return i
            elif not i:
                raise IndexError("element 0 does not exist in 1-based string")
            return i - 1

    def __getitem__(self, i):
        n = str.__getitem__(self, self._zerobased(i))
        return SetlxString(n)

    def __setitem__(self, i, value):
        str.__setitem__(self, self._zerobased(i), value)
        
    def __delitem__(self, i):
        str.__delitem__(self, self._zerobased(i))

    def __getslice__(self, i, j):
        """ Setlx slices include the upper limit, whereas Python does not """
        n = str.__getslice__(self, self._zerobased(i or 1), self._zerobased(j + 1))
        return SetlxString(n)

    def __setslice__(self, i, j, value):
        str.__setslice__(self, self._zerobased(i or 1),
                         self._zerobased(j), value)

    def index(self, value, start=1, stop=-1):
        return str.index(self, value, self._zerobased(start),
                         self._zerobased(stop)) + 1

    def pop(self, i):
        return str.pop(self, self._zerobased(i))

    def index(self, value, start=1, stop=-1):
        return str.index(self, value, self._zerobased(start),
                         self._zerobased(stop)) + 1

    def __add__(self, other):
        s = other if isinstance(other, basestring) else str(other)
        return "{0}{1}".format(self, s)

    def __radd__(self, other):
        s = other if isinstance(other, basestring) else str(other)
        return "{0}{1}".format(s, self)

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

def stlx_pow(a,b):
    if isinstance(a, Set) and b == 2:
        return stlx_cartesian(a,a)
    elif isinstance(b, Set) and a == 2:
        return stlx_powerset(b)
    else:
        return a ** b

def stlx_print(*args):
    s = ''.join(str(arg) for arg in args) + '\n'
    sys.stdout.write(s)

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

def stlx_cartesian(a,b):
    return Set(element for element in it.product(a, b))

def stlx_powerset(s):
    lst = list(s)
    return Set(it.chain.from_iterable(it.combinations(lst, r)
                                      for r in range(len(lst)+1)))

def stlx_product(factors):
    return functools.reduce(operator.mul, factors, 1)

def stlx_arb(m):
    return random.sample(m, 1)[0]

def stlx_from(m):
    n = stlx_arb(m)
    altered_m = m - Set([n])
    return altered_m, n

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

    assert isinstance(matchee, (SetlxString, SetlxList))
    
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




