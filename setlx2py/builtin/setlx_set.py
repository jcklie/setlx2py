#------------------------------------------------------------------------------
# setlx2py: setlx_list.py
#
# Home of the SetlxSet
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

import blist

class SetlxSet(blist.sortedset):

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

        for _ in range(max(l1,l2)):
            try:
                x = it1.next()
                y = it2.next()
                if x != y:
                    return x < y
            except StopIteration:
                return l1 < l2
                    
        return False

    def __getitem__(self, key):
        """ Sets of pairs, e.g. { [1,2], [3, 4] } act like maps """
        if isinstance(key, slice):
            return blist.sortedset.__getitem__(self, key)
        else:
            if self._has_duplicate_keys(): return None
            for x, y in self:
                if x == key:
                    return y   

    def __repr__(self):
        data = sorted(self)

        s = ', '.join(repr(i) for i in data)
        
        s = s.replace('(', '{')
        s = s.replace(')', '}')
        s = s.replace(',}', '}')
        return '{' + s + '}'    
    
    def _has_duplicate_keys(self):
        """ Returns True if self is map and iterable contains 
        duplicate entries at first position of tuple
        """        
        return len({x for x, _ in self}) != len(self)
