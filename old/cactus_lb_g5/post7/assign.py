# model round-B chunk assignment: extract per seed per drone (tail_end, pos, G) and per chunk (start, fp, done)
import sys,re,statistics as st,json,pickle
entry=sys.argv[1]; out=sys.argv[2]; files=sys.argv[3:]
L=open(entry).read().split('\n'); cache={}
TA=200/6075
def owner(ln):
    if ln in cache: return cache[ln]
    l=L[ln-1]; lev=len(l)-len(l.lstrip('\t'))
    r='?'
    for i in range(ln-2,-1,-1):
        m=re.match(r'(\t*)def (w\d+)\(\):',L[i])
        if m and len(m.group(1))<lev: r=m.group(2); break
    cache[ln]=r; return r
# pre-travel ranges per w
defs=[]
for i,l in enumerate(L):
    m=re.match(r'(\t*)def (w\d+)\(\):',l)
    if m: defs.append((i,m.group(2),len(m.group(1))))
PT={}
for (i,n,ind) in defs:
    body=ind+1; j=i+1; e=None; w=None
    while j<len(L):
        l=L[j]
        if l.strip()=='' : j+=1; continue
        li=len(l)-len(l.lstrip('\t'))
        if li<body: break
        if li==body and l.strip()=='e = tl + 0.9345' and e is None: e=j+1
        if li==body and l.strip()=='while num_items(Items.Cactus) <= 0:' and w is None: w=j+1
        j+=1
    if e is None: e=w-8
    PT[n]=(e,w)
DIR=[(0,1),(1,0),(0,-1),(-1,0)]
S=[]
for f in files:
    ev=[l.rstrip('\n').split('\t') for l in open(f)]
    ev=[p for p in ev if p[0]=='E']
    hv=[]
    for p in ev:
        if p[3]=='harvest':
            t=float(p[1])
            if not hv or t-hv[-1]>0.5: hv.append(t)
    hA,hB=hv[0],hv[-1]
    nm={};alive={}
    lastact={};prevB={};usedB={};lastplantB={};lastplantA={};tail={};pos={};sig={};fp={};fpos={};bend={};bown={}
    for p in ev:
        t=float(p[1]);d=int(p[2]);k=p[3];ln=int(p[8].split(':')[1]);x,y=int(p[4]),int(p[5])
        if k=='end':
            alive[d]=False; continue
        if k in('till','plant') and t<hA and not alive.get(d):
            nm[d]=owner(ln); alive[d]=True
        if not alive.get(d): continue
        n=nm[d]; e,w=PT[n]
        if t<hA+0.5 and d not in sig:
            if e<=ln<=w+1 and d not in tail:
                tail[d]=lastact[d]+TA if d in lastact else t; pos[d]=(x,y)
            if k=='plant' and t<hA: lastplantA[d]=t
            if k=='use' or (k=='harvest' and abs(t-hA)<1e-9): sig[d]=t
        if k in ('move','swap','plant','till','use','harvest'): lastact[d]=t
        if t>=hA and t<hB:
            if k=='plant' and d not in fp: fp[d]=t; fpos[d]=(x,y); bown[d]=owner(ln)
            if k in ('move','swap','plant','use') : bend[d]=t+TA
            if k=='plant': prevB[d]=lastplantB.get(d,t); lastplantB[d]=t
            if k=='use': usedB[d]=True
    rec={'hA':hA,'hB':hB,'dr':{},'ch':{}}
    for d,n in nm.items():
        G=lastplantA[d]+TA+0.9676
        rec['dr'][n]={'tail':tail[d],'pos':pos[d],'G':G,'sig':sig[d]}
        k=bown[d]
        lp=None
        rec['ch'][k]={'start':fpos[d],'fp':fp[d],'done':max(bend[d],(prevB[d] if usedB.get(d) else lastplantB[d])+TA+0.9676),'drone':n,'lp':(prevB[d] if usedB.get(d) else lastplantB[d]),'wend':bend[d]}
    S.append(rec)
pickle.dump(S,open(out,'wb'))
# validate model on current assignment
def tdist(a,b):
    dx=abs(a[0]-b[0]); dy=abs(a[1]-b[1]); return min(dx,32-dx)+min(dy,32-dy)
def arrival(dr,dist):
    e=dr['G']-0.0331
    t=dr['tail']; n1=0
    while n1<dist and t<e: t+=TA; n1+=1
    s=max(dr['G'],t)
    return s+TA+(dist-n1)*TA
errs=[]
for rec in S:
    for k,c in rec['ch'].items():
        dr=rec['dr'][c['drone']]
        d=tdist(dr['pos'],c['start'])
        pf=max(arrival(dr,d),rec['hA']+0.0005)
        errs.append(pf-c['fp'])
print('fp model err mean %.4f sd %.4f max %.4f min %.4f'%(st.mean(errs),st.pstdev(errs),max(errs),min(errs)))
