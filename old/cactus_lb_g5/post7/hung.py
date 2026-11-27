import pickle,sys,statistics as st
import numpy as np
from scipy.optimize import linear_sum_assignment
S=[]
for f in sys.argv[1].split(','): S+=pickle.load(open(f,'rb'))
FIX=sys.argv[2].split(',')
TA=200/6075
def tdist(a,b):
    dx=abs(a[0]-b[0]); dy=abs(a[1]-b[1]); return min(dx,32-dx)+min(dy,32-dy)
def arrival(dr,dist):
    e=dr['G']-0.0331
    t=dr['tail']; n1=0
    while n1<dist and t<e: t+=TA; n1+=1
    s=max(dr['G'],t)
    return s+TA+(dist-n1)*TA
chunks=sorted(S[0]['ch'],key=lambda k:int(k[1:]))
base={k:S[0]['ch'][k]['drone'] for k in chunks}
drones=chunks
LAT={(d,k):np.array([max(0,arrival(r['dr'][d],tdist(r['dr'][d]['pos'],r['ch'][k]['start']))-r['hA']) for r in S]) for d in drones for k in chunks}
# criticality: fraction of seeds where chunk done within W of the max
def crit(W):
    c={}
    for k in chunks:
        n=0
        for r in S:
            m=max(r['ch'][j]['done'] for j in chunks)
            if r['ch'][k]['done']>=m-W: n+=1
        c[k]=n/len(S)
    return c
def solve(cost):
    C=np.array([[cost(d,k) for k in chunks] for d in drones])
    for f in FIX:
        if not f: continue
        i=drones.index(f)
        for j in range(len(chunks)):
            if j!=i: C[i,j]+=100
    r,c=linear_sum_assignment(C)
    a={chunks[j]:drones[i] for i,j in zip(r,c)}
    return a
for name,cost in [('sum',lambda d,k:LAT[d,k].mean()),('sq',lambda d,k:(LAT[d,k]**2).mean()),
                  ('crit05',lambda d,k,c=crit(0.05):LAT[d,k].mean()*(0.2+c[k])),('crit10',lambda d,k,c=crit(0.10):LAT[d,k].mean()*(0.2+c[k]))]:
    a=solve(cost)
    print(name,'late %.3f'%sum(LAT[a[k],k].mean() for k in chunks),','.join('%s=%s'%(k,a[k]) for k in chunks if a[k]!=base[k]))
