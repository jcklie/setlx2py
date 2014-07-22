#------------------------------------------------------------------------------
# setlx2py: setlx_list.py
#
# Holds helper functions for only internal use
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

import collections
import functools

from setlx2py.builtin.setlx_set import SetlxSet
from setlx2py.builtin.setlx_string import SetlxString
from setlx2py.builtin.setlx_list import SetlxList

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