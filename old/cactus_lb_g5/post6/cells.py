# per chunk: till cells with time and line; per drone: launch path cells (before first till) with times
import sys,re,json
entry=sys.argv[1]; f=sys.argv[2]
lines=open(entry).read().split('\n'); cache={}
def owner(ln):
    if ln in cache: return cache[ln]
    l=lines[ln-1]; lev=len(l)-len(l.lstrip('\t'))
    for i in range(ln-2,-1,-1):
        m=re.match(r'(\t*)def (w\d+)\(\):',lines[i])
        if m and len(m.group(1))<lev: cache[ln]=m.group(2); return m.group(2)
till={};path={};nm={};started=set()
for l in open(f):
    p=l.rstrip('\n').split('\t')
    if p[0]!='E':continue
    if p[3]=='harvest': break
    d=int(p[2]); t=float(p[1]); x,y=int(p[4]),int(p[5]); ln=int(p[8].split(':')[1])
    if p[3]=='till':
        if d not in nm: nm[d]=owner(ln)
        till.setdefault(nm[d],[]).append((t,x,y,ln))
    elif p[3]=='move' and d not in nm:
        path.setdefault(d,[]).append((t,x,y))  # position before move
out={'till':till,'path':{}}
for d in path:
    if d in nm: out['path'][nm[d]]=path[d]
json.dump(out,open(sys.argv[3],'w'))
