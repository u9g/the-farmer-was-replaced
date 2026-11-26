import random, functools
from lay import *
def sz(d): return d+1 if d<=31 else 63-d
def dp_walls(k):
    @functools.lru_cache(None)
    def f(last,k):
        if 62-last<=2: return (0,())
        if 62-last==3 and k>=1: return (0,())
        best=(10**9,())
        for gap,c in ((3,0),(4,1)):
            nx=last+gap
            if c>k or nx>62: continue
            v,w=f(nx,k-c)
            if sz(nx)+v<best[0]: best=(sz(nx)+v,(nx,)+w)
        return best
    best=(10**9,())
    for st in (0,1,2,3):
        kk=k-(1 if st==3 else 0)
        if kk<0: continue
        v,w=f(st,kk)
        if sz(st)+v<best[0]: best=(sz(st)+v,(st,)+w)
    return list(best[1])
