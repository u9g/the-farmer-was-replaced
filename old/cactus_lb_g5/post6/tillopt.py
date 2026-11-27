import sys,re,json,os,statistics as st
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from parse import parse,D as DIRV
N=32; ACT=200/6075
entry,stats,tills,out=sys.argv[1:5]
MARGIN=float(sys.argv[5]) if len(sys.argv)>5 else 0.3
MAXN=int(sys.argv[6]) if len(sys.argv)>6 else 99
EPS=float(sys.argv[7]) if len(sys.argv)>7 else 1e-5
lines=open(entry).read().split('\n')
pre,W,post=parse(lines)
J=json.load(open(stats)); T=json.load(open(tills))
names=[k for k in J if k[0]!='_']; S=len(J['_H'])
# leaf segment of each drone
pos={}
def go(name,p):
    lm=[]
    for s in W[name][0]:
        if s[0]=='move':
            dx,dy=DIRV[s[1]]; p=((p[0]+dx)%N,(p[1]+dy)%N); lm.append(s[1])
        elif s[0]=='spawn':
            go(s[1],p); lm=[]; hub=p
    hubp=p
    for d in reversed(lm):
        dx,dy=DIRV[d]; hubp=((hubp[0]-dx)%N,(hubp[1]-dy)%N)
    pos[name]=(hubp,p,lm)
go('w0',(0,0))
seg={}
for n,(hub,st_,lm) in pos.items():
    ex=[d for d in lm if d in('East','West')]; ey=[d for d in lm if d in('North','South')]
    sx=(1 if ex and ex[0]=='East' else -1); sy=(1 if ey and ey[0]=='North' else -1)
    assert len(set(ex))<=1 and len(set(ey))<=1
    t0=J[n]['arr']-len(lm)*ACT*201/200
    seg[n]=dict(hub=hub,sx=sx,sy=sy,dx=len(ex),dy=len(ey),t0=t0,ch=[])
own={tuple(map(int,k.split(','))):v for k,v in T.items()}
used=set()
for c in os.environ.get('EXCELLS','').split(';'):
    if c: own.pop(tuple(map(int,c.split(','))),None)
shift={n:0 for n in names}
FULL=os.environ.get('FULL')
if FULL:
    F=json.load(open(FULL))
    mA=[max(F[n]['A'][s] for n in names) for s in range(S)]
    BW=float(os.environ.get('BW','1'))
def obj(sh):
    if not FULL:
        return st.mean(max(J[n]['D'][s]-sh[n]*ACT for n in names) for s in range(S))
    tot=0
    for s in range(S):
        hA=F['_hA'][s]; hA2=hA+max(F[n]['A'][s]-sh[n]*ACT for n in names)-mA[s]
        e=0; 
        for n in names:
            r=F[n]['ready'][s]
            d=max(hA2,r-sh[n]*ACT)-max(hA,r)
            e=max(e,F[n]['bend'][s]+d)
        tot+= (hA2-hA)*(1-BW)+e*BW
    return tot/S
cur=obj(shift)
print('base obj',cur)
EXCL=set(os.environ.get('EXCL','').split(','))
CAP=float(os.environ.get('CAP','99'))
def cands(k):
    g=seg[k]; out=[]
    if k in EXCL: return out
    if J[k]['done']-(shift[k]-1)*ACT>CAP: return out
    for i in range(g['dx']+1):
        for j in range(g['dy']+1):
            if (i,j)==(0,0) or (i,j)==(g['dx'],g['dy']): continue
            c=((g['hub'][0]+g['sx']*i)%N,(g['hub'][1]+g['sy']*j)%N)
            if c not in own or c in used: continue
            o=own[c]
            if o['own']==k: continue
            if not all((i<=a and j<=b) or (i>=a and j>=b) for (a,b,_) in g['ch']): continue
            nb=sum(1 for (a,b,_) in g['ch'] if a+b<i+j)
            tk=g['t0']+(i+j+nb)*ACT*201/200
            if o['tmin']-tk<MARGIN: continue
            # later chosen cells get delayed by 1: check their margins
            ok=True
            for (a,b,cc) in g['ch']:
                if a+b>i+j:
                    nb2=sum(1 for (a2,b2,_) in g['ch'] if a2+b2<a+b)+1
                    if own[cc]['tmin']-(g['t0']+(a+b+nb2)*ACT*201/200)<MARGIN: ok=False
            if ok: out.append((i,j,c,o['own']))
    return out
n_added=0
while n_added<MAXN:
    best=None
    for k in names:
        for (i,j,c,o) in cands(k):
            shift[k]-=1; shift[o]+=1
            v=obj(shift)
            shift[k]+=1; shift[o]-=1
            if best is None or v<best[0]: best=(v,k,i,j,c,o)
    if best is None or best[0]>cur-EPS: break
    v,k,i,j,c,o=best; cur=v; seg[k]['ch'].append((i,j,c)); used.add(c); shift[k]-=1; shift[o]+=1; n_added+=1
    print('add %s tills %s of %s (t_own %.2f) -> obj %.4f'%(k,c,o,own[c]['tmin'],v))
# phase 2: excursions from the start cell (out L cells in one direction, back), tilling a subset
EXC=int(os.environ.get('EXC','0')); EXL=int(os.environ.get('EXL','4'))
for k in seg: seg[k]['exc']=None
DV4={'East':(1,0),'West':(-1,0),'North':(0,1),'South':(0,-1)}
while EXC:
    best=None
    for k in names:
        g=seg[k]
        if g['exc'] is not None or k in EXCL: continue
        s0=((g['hub'][0]+g['sx']*g['dx'])%N,(g['hub'][1]+g['sy']*g['dy'])%N)
        ta=g['t0']+(g['dx']+g['dy']+len(g['ch']))*ACT*201/200
        for dn,(ux,uy) in DV4.items():
            for L_ in range(1,EXL+1):
                cells=[((s0[0]+ux*i)%N,(s0[1]+uy*i)%N) for i in range(1,L_+1)]
                pick=[]; nt=0
                for i,c in enumerate(cells):
                    if c in own and c not in used and own[c]['own']!=k:
                        tk=ta+(i+1+nt)*ACT*201/200
                        if own[c]['tmin']-tk>=MARGIN: pick.append(c); nt+=1
                if not pick or own.get(cells[-1]) is None or cells[-1] not in pick: continue
                cost=2*L_+len(pick)
                sh=dict(shift); sh[k]-=cost
                for c in pick: sh[own[c]['own']]+=1
                # all own-chunk margins for k's earlier tills unaffected; k's chunk shifts by cost
                v=obj(sh)
                if best is None or v<best[0]: best=(v,k,dn,L_,pick,sh)
    if best is None or best[0]>cur-EPS: break
    v,k,dn,L_,pick,sh=best; cur=v; shift=sh; seg[k]['exc']=(dn,L_,pick); used.update(pick)
    print('exc %s %s x%d tills %s -> obj %.4f'%(k,dn,L_,[(c,own[c]['own']) for c in pick],v))
# emit: modify lines
L=list(lines)
dirn={(1,0):'East',(-1,0):'West',(0,1):'North',(0,-1):'South'}
def leafblock(k):
    i=next(i for i,l in enumerate(L) if re.match(r'\t*def %s\(\):$'%k,l))
    lev=len(L[i])-len(L[i].lstrip('\t'))
    j=i+1; last=None
    while True:
        l=L[j]; s=l.strip(); li=len(l)-len(l.lstrip('\t'))
        if li==lev+1 and re.match(r'def w\d+\(\):$',s):
            j+=1
            while L[j].strip()=='' or len(L[j])-len(L[j].lstrip('\t'))>lev+1: j+=1
            continue
        if li==lev+1 and s.startswith('spawn_drone(w'): j+=1; last=j; continue
        if li==lev+1 and re.match(r'move\(\w+\)$',s): j+=1; continue
        break
    b=last if last is not None else i+1
    return b,j,lev+1
R={}
for k,g in seg.items():
    if not g['ch'] and not g['exc']: continue
    b,e,lv=leafblock(k)
    old=[L[x].strip() for x in range(b,e)]
    assert len(old)==g['dx']+g['dy'] and all(o.startswith('move(') for o in old),(k,old)
    new=[]; ci=cj=0
    for (a,bb,c) in sorted(g['ch'],key=lambda t:t[0]+t[1]):
        new+=['move(%s)'%dirn[(g['sx'],0)]]*(a-ci)+['move(%s)'%dirn[(0,g['sy'])]]*(bb-cj)+['till()']; ci,cj=a,bb
    new+=['move(%s)'%dirn[(g['sx'],0)]]*(g['dx']-ci)+['move(%s)'%dirn[(0,g['sy'])]]*(g['dy']-cj)
    if g['exc']:
        dn,L_,pick=g['exc']; ux,uy=DV4[dn]; back={'East':'West','West':'East','North':'South','South':'North'}[dn]
        s0=((g['hub'][0]+g['sx']*g['dx'])%N,(g['hub'][1]+g['sy']*g['dy'])%N)
        for i in range(1,L_+1):
            new.append('move(%s)'%dn)
            if ((s0[0]+ux*i)%N,(s0[1]+uy*i)%N) in pick: new.append('till()')
        new+=['move(%s)'%back]*L_
    R[b]=['\t'*lv+x for x in new]
    for x in range(b+1,e): R[x]=[]
for c in used:
    ln=own[c]['ln']-1
    assert L[ln].strip()=='till()',L[ln]
    R[ln]=[]
outl=[]
for x,l in enumerate(L):
    outl+= R[x] if x in R else [l]
open(out,'w').write('\n'.join(outl))
print('tills moved',len(used),'pred obj',cur)
