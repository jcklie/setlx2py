
from setlx2py.builtin.setlx_functions import *
from setlx2py.builtin.setlx_internals import *
from setlx2py.builtin.setlx_set import SetlxSet
from setlx2py.builtin.setlx_list import SetlxList
from setlx2py.builtin.setlx_string import SetlxString

def findPath(x, y, r):
    p = SetlxSet([SetlxList([x])])
    while True:
        oldP = p
        p = p + (pathProduct(p, r))
        found = SetlxSet([l for l in p if ((l[stlx_len(l)]) == y)])
        if found != SetlxSet([]):
            return stlx_arb(found)

        if p == oldP:
            return



def pathProduct(p, q):
    return SetlxSet([add(x, y) for x in p for y in q if (((x[stlx_len(x)]) == (y[1])) and (not (cyclic(add(x, y)))))])

def cyclic(p):
    return (stlx_len((SetlxSet([x for x in p] )))) < (stlx_len(p))

def add(p, q):
    return p + (q[2:])

def printPath(path, all):
    for i in SetlxList(stlx_lst_from_range(1,(stlx_len(path)))):
        left = path[i]
        right = all - left
        if ((stlx_len(left)) == 9) or ((stlx_len(right)) == 9):
            stlx_print(left - SetlxSet([SetlxString('Boot')]), 18 * SetlxString(' '), right - SetlxSet([SetlxString('Boot')]))
            stlx_print(SetlxString(''))
        else:
            stlx_print(left - SetlxSet([SetlxString('Boot')]), 20 * SetlxString(' '), right - SetlxSet([SetlxString('Boot')]))
            stlx_print(SetlxString(''))

        if i == (stlx_len(path)):
            break

        if SetlxString('Boot') in left:
            m = (left - (path[i + 1])) - SetlxSet([SetlxString('Boot')])
            stlx_print(SetlxString('                                >>>> '), m, SetlxString(' >>>> '))
        else:
            m = (right - (all - (path[i + 1]))) - SetlxSet([SetlxString('Boot')])
            stlx_print(SetlxString('                                <<<< '), m, SetlxString(' <<<< '))

        stlx_print(SetlxString(''))


all = SetlxSet([SetlxString('Polizist'),SetlxString('Verbrecher'),SetlxString('Mutter'),SetlxString('Vater'),SetlxString('Anton'),SetlxString('Bruno'),SetlxString('Cindy'),SetlxString('Doris'),SetlxString('Boot')])
verboten = lambda s: (verbotenSide(s)) or (verbotenSide(all - s))
def verbotenSide(s):
    boys = SetlxSet([SetlxString('Anton'),SetlxString('Bruno')])
    girls = SetlxSet([SetlxString('Cindy'),SetlxString('Doris')])
    return ((((SetlxString('Verbrecher') in s) and ((stlx_len(s)) > 1)) and (not (SetlxString('Polizist') in s))) or ((((boys * s) != SetlxSet([])) and (SetlxString('Mutter') in s)) and (not (SetlxString('Vater') in s)))) or ((((girls * s) != SetlxSet([])) and (SetlxString('Vater') in s)) and (not (SetlxString('Mutter') in s)))

p = SetlxSet([s for s in stlx_pow(2,all) if (not (verboten(s)))])
def bootOK(b):
    canRow = SetlxSet([SetlxString('Mutter'),SetlxString('Vater'),SetlxString('Polizist')])
    return ((SetlxString('Boot') in b) and ((stlx_len(b)) <= 3)) and ((canRow * b) != SetlxSet([]))

r1 = SetlxSet([SetlxList([s,s - b]) for s in p for b in stlx_pow(2,s) if ((bootOK(b)) and (not (verboten(s - b))))])
r2 = SetlxSet([SetlxList([x,y]) for [y,x] in r1] )
r = r1 + r2
start = all
goal = SetlxSet([])
path = findPath(start, goal, r)
printPath(path, all)
stlx_print(stlx_len(path))
