# reassign round-B chunks between drones in the nested entry.
# usage: reassign.py IN OUT "chunk=drone,chunk=drone,..."   (drone wX runs the round-B code of chunk)
import sys,re
src,out,spec=sys.argv[1],sys.argv[2],sys.argv[3]
L=open(src).read().split('\n')
START={'w0': (2, 4), 'w1': (13, 2), 'w10': (1, 24), 'w11': (6, 21), 'w12': (15, 14), 'w13': (23, 5), 'w14': (0, 1), 'w15': (25, 10), 'w16': (17, 19), 'w17': (9, 28), 'w18': (4, 29), 'w19': (12, 19), 'w2': (5, 12), 'w20': (21, 12), 'w21': (30, 9), 'w22': (29, 2), 'w23': (23, 18), 'w24': (15, 25), 'w25': (14, 30), 'w26': (25, 19), 'w27': (27, 25), 'w28': (18, 29), 'w29': (29, 27), 'w3': (6, 7), 'w30': (25, 24), 'w31': (31, 30), 'w4': (2, 17), 'w5': (29, 17), 'w6': (11, 9), 'w7': (20, 1), 'w8': (17, 6), 'w9': (9, 15)}
DV={'North':(0,1),'East':(1,0),'South':(0,-1),'West':(-1,0)}
def ind(l): return len(l)-len(l.lstrip('\t'))
defs={}
for i,l in enumerate(L):
    m=re.match(r'(\t*)def (w\d+)\(\):',l)
    if m: defs[m.group(2)]=(i,len(m.group(1)))
def body_lines(n):
    i,d=defs[n]; b=d+1; res=[]; j=i+1
    while j<len(L):
        l=L[j]
        if l.strip()=='': j+=1; continue
        if ind(l)<b: break
        if ind(l)==b: res.append(j)
        j+=1
    return b,res
info={}
for n in defs:
    b,bl=body_lines(n)
    E=[j for j in bl if L[j].strip()=='e = tl + 0.9345']
    W=[j for j in bl if L[j].strip()=='while num_items(Items.Cactus) <= 0:']
    F=[j for j in bl if L[j].strip()=='wait_until(tl + 0.9676)']
    if not W: continue
    W=W[0]; F=F[-1]
    sw=[j for j in bl if L[j].strip()=='wait_until(tl + 0.9676)' and j<W][-1]
    if E:
        e=E[0]; c0 = e-1 if L[e-1].strip()=='c = cur' else e
    else:
        e=None; c0=sw
    info[n]=dict(b=b,ptstart=c0,e=e,sw=sw,W=W,F=F)
def branches(n):
    I=info[n]
    if I['e'] is None: return {None:[]}
    seg=L[I['ptstart']:I['sw']]
    br={}; cur=None; b=I['b']
    for l in seg:
        s=l.strip()
        m=re.match(r'(?:el)?if c == (\d+):',s)
        if m and ind(l)==b: cur=int(m.group(1)); br[cur]=[]; continue
        m=re.match(r'move\((\w+)\)',s)
        if m: br.setdefault(cur,[]).append(m.group(1))
    return br
def endpos(n):
    S=START[n]; res={}
    for c,mv in branches(n).items():
        x,y=S
        for d in mv: x-=DV[d][0]; y-=DV[d][1]
        res[c]=(x%32,y%32)
    return res
def path(a,b,order):
    dx=(b[0]-a[0])%32; dy=(b[1]-a[1])%32
    xs=['East']*dx if dx<=16 else ['West']*(32-dx)
    ys=['North']*dy if dy<=16 else ['South']*(32-dy)
    return xs+ys if order=='xy' else ys+xs
def nested(mv,t):
    # the ptw2 style nested block for a move list, at indent t
    if not mv: return []
    out=[]
    def rec(i,t):
        out.append('\t'*t+'if get_time() < e:')
        out.append('\t'*(t+1)+'move(%s)'%mv[i])
        if i+1<len(mv): rec(i+1,t+1)
        out.append('\t'*t+'else:')
        out.append('\t'*(t+1)+'P.append((%s,))'%', '.join(mv[i:]))
    rec(0,t)
    return out
def mkpt(n,target,order):
    I=info[n]; b=I['b']; ep=endpos(n)
    o=[]
    keys=list(ep)
    if keys==[None]:
        o.append('\t'*b+'e = tl + 0.9345'); o.append('\t'*b+'P = []')
        o+=nested(path(ep[None],target,order),b)
    else:
        o.append('\t'*b+'c = cur'); o.append('\t'*b+'e = tl + 0.9345'); o.append('\t'*b+'P = []')
        for i,c in enumerate(sorted(keys)):
            mv=path(ep[c],target,order)
            o.append('\t'*b+('if' if i==0 else 'elif')+' c == %d:'%c)
            nb=nested(mv,b+1)
            o+= nb if nb else ['\t'*(b+1)+'pass']
    return o
asg=dict(kv.split('=') for kv in spec.split(',')) if spec else {}
order=sys.argv[4] if len(sys.argv)>4 else 'xy'
# blocks to replace, process from bottom to top
rep=[]
for chunk,drone in asg.items():
    I=info[drone]; J=info[chunk]
    blk=L[J['W']:J['F']+1]
    sh=I['b']-J['b']
    nb=[('\t'*sh+l if sh>=0 else l[-sh:]) if l.strip() else l for l in blk]
    for l in nb:
        assert not re.match(r'\s*def w\d+',l) and 'spawn_drone(w' not in l, l
    rep.append((I['W'],I['F']+1,nb))
    newpt=mkpt(drone,START[chunk],order)
    rep.append((I['ptstart'],I['sw'],newpt))
    if I['e'] is None:
        rep[-1]=(I['sw'],I['sw'],newpt)
msgs=[(drone,chunk,{c:len(path(p,START[chunk],order)) for c,p in endpos(drone).items()},{c:len(m) for c,m in branches(drone).items()},endpos(drone)) for chunk,drone in asg.items()]
rep.sort(key=lambda r:-r[0])
for a,b,nb in rep:
    L[a:b]=nb
open(out,'w').write('\n'.join(L))
for m in msgs: print(*m,file=sys.stderr)
