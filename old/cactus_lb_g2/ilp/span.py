import numpy as np, sys
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix
N=int(sys.argv[1]); SPAN=int(sys.argv[2])
cells=[(x,y) for x in range(N) for y in range(N)]; ci={c:i for i,c in enumerate(cells)}; NC=len(cells)
tv=lambda i,t:i*3+t
arcs=[(ci[c],ci[(c[0]+dx,c[1]+dy)]) for c in cells for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)) if (c[0]+dx,c[1]+dy) in ci]
nv=NC*3+len(arcs); fv=lambda k:NC*3+k
A=lil_matrix((NC*20+len(arcs)*2,nv)); lb=[];ub=[]; r=[0]
def row(d,l,u):
    for k,v in d.items(): A[r[0],k]+=v
    lb.append(l);ub.append(u);r[0]+=1
for i,(x,y) in enumerate(cells):
    row({tv(i,t):1 for t in range(3)},0,1)
    for dx,dy,t in ((-1,0,0),(0,-1,0),(1,0,1),(0,1,1)):
        m=(x+dx,y+dy)
        if m in ci:
            d={tv(ci[m],k):1 for k in range(3)}; d[tv(i,t)]=d.get(tv(i,t),0)+1; row(d,0,1)
    for dx,dy in ((1,0),(0,1)):
        m=(x+dx,y+dy)
        if m in ci: row({tv(i,2):1,tv(ci[m],2):1},0,1)
root=ci[(0,0)]
row({tv(root,t):1 for t in range(3)},1,1)
B=NC
for k,(u,v) in enumerate(arcs):
    for z in (u,v):
        d={fv(k):1}
        for t in range(3): d[tv(z,t)]=-B
        row(d,-np.inf,0)
inn={i:[] for i in range(NC)}; out={i:[] for i in range(NC)}
for k,(u,v) in enumerate(arcs): out[u].append(k); inn[v].append(k)
for i in range(NC):
    if i==root: continue
    d={}
    for k in inn[i]: d[fv(k)]=d.get(fv(k),0)+1
    for k in out[i]: d[fv(k)]=d.get(fv(k),0)-1
    for t in range(3): d[tv(i,t)]=-1
    row(d,0,0)
# require some cell at diagonal >= SPAN
row({tv(ci[c],t):1 for c in cells if c[0]+c[1]>=SPAN for t in range(3)},1,np.inf)
A=A[:r[0]]
c=np.zeros(nv)
integ=np.zeros(nv); integ[:NC*3]=1
ubv=np.ones(nv); ubv[NC*3:]=B
res=milp(c,constraints=LinearConstraint(A.tocsr(),lb,ub),integrality=integ,bounds=Bounds(0,ubv),options={"time_limit":60})
print(N,SPAN,res.status,res.message)
if res.x is not None:
    xv=np.round(res.x[:NC*3]).astype(int)
    for y in range(N-1,-1,-1):
        print("".join(("LHM"[[xv[tv(ci[(x,y)],k)] for k in range(3)].index(1)] if sum(xv[tv(ci[(x,y)],k)] for k in range(3)) else ".") for x in range(N)))
