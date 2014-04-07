#------------------------------------------------------------------------------
# setlx2py: setlx_list.py
#
# Home of the SetlxList, a 1-indexed list
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

class SetlxList(list):
    """
    Since python lists are zero-indexed, and SetlX
    is one-indexed, it has to be converted somewhere
    """
        
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
        """ Setlx slices include the upper limit, whereas Python does not
            Be sure to return SetlxList
        """
        sliced =  list.__getslice__(self, self._zerobased(i or 1),
                                    self._zerobased(j + 1))
        return SetlxList(sliced)

    def __setslice__(self, i, j, value):
        list.__setslice__(self, self._zerobased(i or 1),
                          self._zerobased(j), value)

    def index(self, value, start=1, stop=-1):
        return list.index(self, value, self._zerobased(start),
                          self._zerobased(stop)) + 1

    def pop(self, i):
        return list.pop(self, self._zerobased(i))

    def __add__(self, other):
        concat = list.__add__(self, other)
        return SetlxList(concat)
