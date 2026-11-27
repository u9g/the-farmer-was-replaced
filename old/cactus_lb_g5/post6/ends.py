import os
import sys,re,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from tree import td,plan_tree
entry=sys.argv[1]; f=sys.argv[2]
lines=open(entry).read().split('\n'); cache={}
def owner(ln):
    if ln in cache: return cache[ln]
    l=lines[ln-1]; lev=len(l)-len(l.lstrip('\t'))
    for i in range(ln-2,-1,-1):
        m=re.match(r'(\t*)def (w\d+)\(\):',lines[i])
        if m and len(m.group(1))<lev: cache[ln]=m.group(2); return m.group(2)
first={};lastp={};nm={};hv=None;cnt={}
for l in open(f):
    p=l.rstrip('\n').split('\t')
    if p[0]!='E':continue
    if p[3]=='harvest': break
    d=int(p[2])
    if p[3]=='till':
        if d not in nm: nm[d]=owner(int(p[8].split(':')[1])); first[d]=(int(p[4]),int(p[5]))
        lastp[d]=(int(p[4]),int(p[5])); cnt[d]=cnt.get(d,0)+1
S={};E={}
for d in nm: S[nm[d]]=first[d]; E[nm[d]]=lastp[d]
o=(0,0)
print('sum dist starts',sum(td(o,S[n]) for n in S),'nearer',sum(min(td(o,S[n]),td(o,E[n])) for n in S))
print('cells',sum(cnt.values()))
J=json.load(open(sys.argv[3]))
ACT=201/6075
order=sorted(S,key=lambda x:int(x[1:]))
for nm_,SS in (('cur',S),('near',{n:(S[n] if td(o,S[n])<=td(o,E[n]) else E[n]) for n in S})):
    R={n:0 for n in order}
    plan,arr,pred=plan_tree(order,SS,R,1.0)
    print(nm_,'mean arr (actions, sum obj tau=1 approx)',sum(arr.values())/32*ACT)
