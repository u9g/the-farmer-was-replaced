import numpy as np, sys
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix
N=32; NEED=int(sys.argv[1]) if len(sys.argv)>1 else 725
idx=lambda x,y,t:(x*N+y)*3+t  # t:0=L,1=H,2=M
nv=N*N*3
rows=[];lb=[];ub=[]
A=lil_matrix((N*N*6+1,nv))
r=0
def cact(x,y):
    return [idx(x,y,t) for t in range(3)]
for x in range(N):
    for y in range(N):
        for v in cact(x,y): A[r,v]=1
        lb.append(0);ub.append(1);r+=1
        for (dx,dy,t) in ((-1,0,0),(0,-1,0),(1,0,1),(0,1,1)):
            X,Y=x+dx,y+dy
            if 0<=X<N and 0<=Y<N:
                A[r,idx(x,y,t)]=1
                for v in cact(X,Y): A[r,v]+=1
                lb.append(0);ub.append(1);r+=1
for x in range(N):
    for y in range(N):
        for v in cact(x,y): A[r,v]=1
lb.append(NEED);ub.append(N*N);r+=1
A=A[:r]
c=np.zeros(nv)
for x in range(N):
    for y in range(N): c[idx(x,y,2)]=1
res=milp(c,constraints=LinearConstraint(A.tocsr(),lb,ub),integrality=np.ones(nv),bounds=Bounds(0,1),options={"time_limit":120,"disp":False})
print(res.status,res.message,"min M cells for",NEED,"=",res.fun)
xv=np.round(res.x).astype(int)
for y in range(N-1,-1,-1):
    row=""
    for x in range(N):
        t=[xv[idx(x,y,k)] for k in range(3)]
        row+="LHM"[t.index(1)] if 1 in t else "."
    print(row)
