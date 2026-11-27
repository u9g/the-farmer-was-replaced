# min/mean till time per cell across traces, and its line + owner
import sys,re,json
entry=sys.argv[1]; out=sys.argv[2]; files=sys.argv[3:]
lines=open(entry).read().split('\n'); cache={}
def owner(ln):
    if ln in cache: return cache[ln]
    l=lines[ln-1]; lev=len(l)-len(l.lstrip('\t'))
    for i in range(ln-2,-1,-1):
        m=re.match(r'(\t*)def (w\d+)\(\):',lines[i])
        if m and len(m.group(1))<lev: cache[ln]=m.group(2); return m.group(2)
C={}
X=set()
for f in files:
    tl={}
    for l in open(f):
        p=l.split('\t')
        if p[0]!='E': continue
        if p[3]=='harvest': break
        if p[3]=='till': tl.setdefault((p[4],p[5]),p[2])
        if p[3]=='plant' and (p[4],p[5]) in tl and tl[(p[4],p[5])]!=p[2]: X.add(p[4]+','+p[5])
for f in files:
    for l in open(f):
        p=l.split('\t')
        if p[0]!='E': continue
        if p[3]=='harvest': break
        if p[3]=='till':
            k=p[4]+','+p[5]; t=float(p[1]); ln=int(p[8].split(':')[1])
            if k in C:
                assert C[k]['ln']==ln
                C[k]['tmin']=min(C[k]['tmin'],t)
            else: C[k]=dict(tmin=t,ln=ln,own=owner(ln))
[C.pop(k) for k in X if k in C]
json.dump(C,open(out,'w'))
print(len(C))
