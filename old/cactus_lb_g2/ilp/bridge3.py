# Window ILP: redesign a bottom-edge junction between band A (a,a+1) and band B (a+3,a+4)
import numpy as np, sys
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix
N=32
import os
NOMM=os.environ.get("NOMM")=="1"
a=int(sys.argv[1]); X0,X1,H=int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]); LAM=float(sys.argv[5]); MAXM=int(sys.argv[6]) if len(sys.argv)>6 else 99
walls=set(range(a-1,63,3))|set(range(a-1,-1,-3))
def base(x,y):  # standard pattern cell?
    if not(0<=x<N and 0<=y<N): return None
    s=x+y
    if s in walls: return None
    return 'L' if (s-a)%3==0 else 'H'
win=[(x,y) for x in range(X0,X1+1) for y in range(H) if 0<=x<N and a-1<=x+y<=a+5]
wi={c:i for i,c in enumerate(win)}
def inwin(c): return c in wi
def fixed(c): return None if inwin(c) else base(*c)
nW=len(win)
tv=lambda i,t:i*3+t
# boundary fixed region cells adjacent to window
bnd=[]
for (x,y) in win:
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
        m=(x+dx,y+dy)
        if not inwin(m) and fixed(m) and m not in bnd: bnd.append(m)
bnd_all=list(bnd)
bnd=[c for c in bnd if (c[0]+c[1]) in (a,a+1,a+3,a+4)]
nodes=win+bnd; ni={c:i for i,c in enumerate(nodes)}
arcs=[]
for c in nodes:
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
        m=(c[0]+dx,c[1]+dy)
        if m in ni and (inwin(c) or inwin(m)): arcs.append((ni[c],ni[m]))
band=lambda c:(c[0]+c[1]-a+3)//3
for i,c in enumerate(bnd):
    for j,m in enumerate(bnd):
        if i!=j and band(c)==band(m): arcs.append((ni[c],ni[m]))
nv=nW*3+len(arcs)
fv=lambda k:nW*3+k
A=lil_matrix((20000,nv)); lb=[];ub=[]; r=[0]
def row(d,l,u):
    for k,v in d.items(): A[r[0],k]=A[r[0],k]+v
    lb.append(l);ub.append(u);r[0]+=1
def cact(c):  # returns (dict of var coeffs, const)
    if inwin(c): return ({tv(wi[c],t):1 for t in range(3)},0)
    return ({},1 if fixed(c) else 0)
def typ(c,t):  # indicator of type t at c
    if inwin(c): return ({tv(wi[c],t):1},0)
    f=fixed(c)
    return ({},1 if f=="LHM"[t] else 0)
for c in win:
    i=wi[c]; x,y=c
    row({tv(i,0):1,tv(i,1):1,tv(i,2):1},0,1)
    for dx,dy,t in ((-1,0,0),(0,-1,0),(1,0,1),(0,1,1)):  # L: W,S empty ; H: N,E empty
        m=(x+dx,y+dy)
        d,k=cact(m); d=dict(d); d[tv(i,t)]=d.get(tv(i,t),0)+1
        row(d,-np.inf,1-k)
    for dx,dy in (() if NOMM else ((1,0),(0,1),(-1,0),(0,-1))):  # no M-M
        m=(x+dx,y+dy)
        d,k=typ(m,2); d=dict(d); d[tv(i,2)]=d.get(tv(i,2),0)+1
        row(d,-np.inf,1-k)
# fixed cells adjacent to window must keep their type validity: fixed L's lower nbrs empty, fixed H's upper empty; fixed cells are L/H (pure) so:
for c in bnd_all:
    x,y=c; f=fixed(c)
    for dx,dy,need in ((-1,0,'L'),(0,-1,'L'),(1,0,'H'),(0,1,'H')):
        m=(x+dx,y+dy)
        if inwin(m) and f==need:
            d,k=cact(m); row(d,-np.inf,0)
# connectivity: flow from root (first bnd cell of band A) to all region nodes
BIG=len(nodes)
root=0
# pick root: a boundary cell with s in {a,a+1}
for c in bnd:
    if (c[0]+c[1]) in (a,a+1): root=ni[c]; break
for k,(u,v) in enumerate(arcs):
    for z in (u,v):
        c=nodes[z]
        if inwin(c):
            d={fv(k):1}; 
            for t in range(3): d[tv(wi[c],t)]=-BIG
            row(d,-np.inf,0)
inn={i:[] for i in range(len(nodes))}; out={i:[] for i in range(len(nodes))}
for k,(u,v) in enumerate(arcs): out[u].append(k); inn[v].append(k)
for i,c in enumerate(nodes):
    if i==root: continue
    d={}
    for k in inn[i]: d[fv(k)]=d.get(fv(k),0)+1
    for k in out[i]: d[fv(k)]=d.get(fv(k),0)-1
    if inwin(c):
        for t in range(3): d[tv(wi[c],t)]=-1
        row(d,0,0)
    else:
        row(d,1,1)
row({tv(wi[c],2):1 for c in win},0,MAXM)
A=A[:r[0]]
cvec=np.zeros(nv)
for c in win:
    i=wi[c]
    cvec[tv(i,0)]=-1; cvec[tv(i,1)]=-1; cvec[tv(i,2)]=-1+LAM
integ=np.zeros(nv); integ[:nW*3]=1
ubv=np.ones(nv); ubv[nW*3:]=BIG
res=milp(cvec,constraints=LinearConstraint(A.tocsr(),lb,ub),integrality=integ,bounds=Bounds(0,ubv),options={"time_limit":120})
print(res.status,res.message)
if res.x is None: sys.exit()
xv=np.round(res.x[:nW*3]).astype(int)
cnt=0;M=0;base_cnt=sum(1 for c in win if base(*c))
lay={}
for c in win:
    t=[xv[tv(wi[c],k)] for k in range(3)]
    if 1 in t: lay[c]="LHM"[t.index(1)]; cnt+=1; M+=t[2]
print("window cells",cnt,"(standard",base_cnt,") M",M)
for y in range(H+1,-1,-1):
    print("".join((lay.get((x,y),'.') if inwin((x,y)) else (fixed((x,y)) or ' ').lower()) for x in range(X0-2,X1+3)))
