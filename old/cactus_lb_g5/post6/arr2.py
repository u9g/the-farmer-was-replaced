import os
# per-chunk arrival/done stats mapped to w names: outputs json
import sys,statistics as st,json,re
from collections import defaultdict
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
entry=sys.argv[1]; files=sys.argv[3:]
lines=open(entry).read().split('\n')
cache={}
def owner(ln):
    if ln in cache: return cache[ln]
    l=lines[ln-1]; lev=len(l)-len(l.lstrip('\t'))
    for i in range(ln-2,-1,-1):
        m=re.match(r'(\t*)def (w\d+)\(\):',lines[i])
        if m and len(m.group(1))<lev: cache[ln]=m.group(2); return m.group(2)
A=defaultdict(list);D=defaultdict(list);L=defaultdict(int);H=[]
for f in files:
    arr={};done={};hv=None;nm={}
    for line in open(f):
        p=line.rstrip('\n').split('\t')
        if p[0]!='E':continue
        t=float(p[1]);d=int(p[2]);k=p[3]
        if k=='harvest' and hv is None:
            hv=t
            if d not in done: done[d]=t
        if hv is not None: continue
        if k in('till','plant') and d not in arr: arr[d]=t; nm[d]=owner(int(p[8].split(':')[1]))
        if k=='use' and d not in done: done[d]=t
    H.append(hv)
    for d in arr: A[nm[d]].append(arr[d]); D[nm[d]].append(done[d])
    L[nm[max(done,key=done.get)]]+=1
out={n:dict(arr=st.mean(A[n]),done=st.mean(D[n]),sd=st.pstdev(D[n]),late=L[n],D=D[n],A=A[n]) for n in A}
out['_H']=H
print('harvestA',st.mean(H),'meanarr',st.mean(v['arr'] for k,v in out.items() if k[0]!='_'))
for n in sorted([k for k in out if k[0]!='_'],key=lambda n:-out[n]['done']): print(n,{k:round(v,3) for k,v in out[n].items() if k not in 'DA'})
json.dump(out,open(sys.argv[2],'w'))
