"""What the N latest drones of each round did after their growth wait ended (the only tail
work the harvest waits for), by function, kind and line.
    python3 hol_tail.py ENTRY.py N TRACES..."""
import sys, re, collections, statistics as st
entry=sys.argv[1]; src=open(entry).read().split('\n')
func_of={}; stack=[]
for i,l in enumerate(src,1):
    s=l.lstrip('\t'); ind=len(l)-len(s)
    if s.strip():
        while stack and ind<=stack[-1][0]: stack.pop()
        m=re.match(r'def (\w+)',s)
        if m: stack.append((ind,m.group(1)))
    func_of[i]=stack[-1][1] if stack else '<top>'
ACT=200/6075.0; GROW=0.9676; TOP=int(sys.argv[2]); files=sys.argv[3:]
B=collections.defaultdict(float); L=collections.defaultdict(float); n=0
for fn in files:
    ev=[]
    for l in open(fn):
        p=l.rstrip('\n').split('\t')
        if p[0]=='E': ev.append((float(p[1]),int(p[2]),p[3],int(p[7]),int(p[8].split(':')[1]) if ':' in p[8] else 0,p[9] if len(p)>9 else ''))
    hv=[e[0] for e in ev if e[2]=='harvest' and e[5] and float(e[5])>1e6]
    for r,(lo,hi) in enumerate(((0,hv[0]),(hv[0],hv[1]))):
        la,lp={},{}
        for e in ev:
            if not (lo<=e[0]<hi and e[3]==200): continue
            if e[2]=='plant': lp[e[1]]=max(lp.get(e[1],0),e[0]+ACT)
            if e[2]!='end' and (r==1 and e[2]!='harvest' or r==0 and e[2] in ('use','harvest')):
                la[e[1]]=max(la.get(e[1],0),e[0]+ACT)
        fin={d:max(la[d],lp[d]+GROW) for d in la if d in lp}
        for h in sorted(fin,key=fin.get,reverse=True)[:TOP]:
            g=lp[h]+GROW
            if la[h]<=g: continue
            es=[e for e in ev if e[1]==h and lo<=e[0]<la[h]]
            for i,e in enumerate(es):
                nt=es[i+1][0] if i+1<len(es) else la[h]
                a,b=max(e[0],g),nt
                if b<=a: continue
                f=func_of.get(e[4],'?'); f='w*' if re.fullmatch(r'w\d+',f) else f
                k=e[2] if e[3]==200 else 'read/wait'
                B[(r,f,k)]+=b-a; L[(r,e[4])]+=b-a
    n+=1
for r in (0,1):
    print(f'round {"AB"[r]}: time past growth on the {TOP} latest drones (ms per run, summed over them)')
    for (rr,f,k),v in sorted(B.items(),key=lambda x:-x[1]):
        if rr==r and v/n*1000>=3: print(f'   {f:22} {k:10} {v/n*1000:6.1f}')
    for (rr,ln),v in sorted(L.items(),key=lambda x:-x[1])[:12]:
        if rr==r: print(f'      line {ln:6} {func_of.get(ln):10} {v/n*1000:5.1f}  {src[ln-1].strip()[:60]}')
