import sys,statistics as st,re
from collections import defaultdict
entry=sys.argv[1]; files=sys.argv[2:]
lines=open(entry).read().split('\n'); cache={}
def owner(ln):
    if ln in cache: return cache[ln]
    l=lines[ln-1]; lev=len(l)-len(l.lstrip('\t'))
    for i in range(ln-2,-1,-1):
        m=re.match(r'(\t*)def (w\d+)\(\):',lines[i])
        if m and len(m.group(1))<lev: cache[ln]=m.group(2); return m.group(2)
F=defaultdict(list);E=defaultdict(list);LB=defaultdict(int);DA=defaultdict(list)
for f in files:
    hv=[];fp={};last={};nm={};ua={}
    ev=[l.rstrip('\n').split('\t') for l in open(f)]
    for p in ev:
        if p[0]=='E' and p[3]=='harvest':
            t=float(p[1])
            if not hv or t-hv[-1]>0.5: hv.append(t)
    h1,h2=hv[0],hv[1]
    for p in ev:
        if p[0]!='E':continue
        t=float(p[1]);d=int(p[2]);k=p[3]
        if k in('till','plant') and d not in nm: nm[d]=owner(int(p[8].split(':')[1]))
        if k=='use' and t<h1 and d not in ua: ua[d]=t
        if t>h1 and t<h2:
            if k=='plant' and d not in fp: fp[d]=t
            if k not in('measure','items','time'): last[d]=t
    for d in fp:
        if d not in nm: continue
        F[nm[d]].append(fp[d]-h1); E[nm[d]].append(last[d]-h1)
        DA[nm[d]].append(h1-ua[d])
    lb=max((d for d in last if d in nm),key=lambda d:last[d]); LB[nm[lb]]+=1
print('name  B-first-plant(after hA)  B-end  slackA(hA-useA) latestB')
for n in sorted(F,key=lambda n:-st.mean(E[n])):
    print(n, '%.3f %.3f  %.3f %d'%(st.mean(F[n]),st.mean(E[n]),st.mean(DA[n]),LB[n]))
