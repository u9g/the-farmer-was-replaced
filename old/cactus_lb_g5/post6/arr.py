import sys,glob,statistics as st
from collections import defaultdict
A=defaultdict(list);D=defaultdict(list);L=defaultdict(int);H=[];LA=defaultdict(list)
for f in sys.argv[1:]:
    arr={};done={};hv=None;spl={}
    for line in open(f):
        p=line.rstrip('\n').split('\t')
        if p[0]!='E':continue
        t=float(p[1]);d=int(p[2]);k=p[3]
        if k=='harvest' and hv is None: hv=t
        if hv is not None: continue
        if k in('till','plant') and d not in arr: arr[d]=t
        if k=='use' and d not in done: done[d]=t
    H.append(hv)
    m=max(done.values()); 
    for d in arr:
        A[d].append(arr[d]); D[d].append(done.get(d,float('nan')))
    L[max(done,key=done.get)]+=1
print('harvestA mean',st.mean(H))
print('drone arr  arr_sd  done  done_sd rest latest')
for d in sorted(A):
    print(d, round(st.mean(A[d]),3), round(st.pstdev(A[d]),3), round(st.mean(D[d]),3), round(st.pstdev(D[d]),3), round(st.mean(D[d])-st.mean(A[d]),3), L[d])
print('mean arr', st.mean(st.mean(v) for v in A.values()))
