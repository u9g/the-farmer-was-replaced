import sys,math,json
from functools import lru_cache
sys.setrecursionlimit(10000)
N=32
def td(a,b):
    dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]); return min(dx,N-dx)+min(dy,N-dy)
def pmoves(a,b):
    out=[]
    dx=(b[0]-a[0])%N
    if dx<=N-dx: out+=['East']*dx
    else: out+=['West']*(N-dx)
    dy=(b[1]-a[1])%N
    if dy<=N-dy: out+=['North']*dy
    else: out+=['South']*(N-dy)
    return out
def plan_tree(order,S,R,tau,hanan=False,origin=(0,0)):
    """order: list of chunk names; S name->pos; R name->rest (actions). returns plan dict and predicted arrivals"""
    st=[S[n] for n in order]; rs=[R[n] for n in order]; n=len(order)
    ref=max(rs)
    @lru_cache(None)
    def cands(i,j):
        c={st[k] for k in range(i,j)}
        if hanan:
            xs={st[k][0] for k in range(i,j)}; ys={st[k][1] for k in range(i,j)}
            if j-i<=hanan: c|={(x,y) for x in xs for y in ys}
        return tuple(c)
    @lru_cache(None)
    def h(i,j,p):
        if j-i==1:
            return (math.exp((td(p,st[i])+rs[i]-ref)/tau),None)
        best=None
        for q in set(cands(i,j))|{p}:
            dq=td(p,q); f=math.exp((dq+1)/tau)
            for m in range(i+1,j):
                v=f*(h(i,m,q)[0]+h(m,j,q)[0])
                if best is None or v<best[0]: best=(v,(q,m))
        return best
    plan={nm:[] for nm in order}; arr={}
    def walk(i,j,p,t):
        if j-i==1:
            plan[order[i]]+= [('move',d) for d in pmoves(p,st[i])]
            arr[order[i]]=t+td(p,st[i]); return
        q,m=h(i,j,p)[1]
        plan[order[i]]+=[('move',d) for d in pmoves(p,q)]+[('spawn',order[m])]
        t2=t+td(p,q)+1
        walk(m,j,q,t2); walk(i,m,q,t2)
    walk(0,n,origin,0)
    return plan,arr,tau*math.log(h(0,n,origin)[0])+ref
