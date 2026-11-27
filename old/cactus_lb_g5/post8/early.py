# round-B drones skip their growth wait when the main is guaranteed not to harvest before it.
# usage: early.py IN OUT C   (env UNSAFE=1: all drones skip the wait)
import sys,re,os
src,dst,C=sys.argv[1],sys.argv[2],sys.argv[3]
UNSAFE=os.environ.get('UNSAFE')
L=open(src).read().split('\n')
def ind(l): return len(l)-len(l.lstrip('\t'))
defs=[(i,m.group(2),len(m.group(1))) for i,l in enumerate(L) for m in [re.match(r'(\t*)def (w\d+)\(\):',l)] if m]
rep={}  # index -> list of lines replacing it
for (i,n,d) in defs:
    b=d+1; j=i+1; body=[]
    while j<len(L):
        if L[j].strip()=='' : j+=1; continue
        if ind(L[j])<b: break
        if ind(L[j])==b: body.append(j)
        j+=1
    W=[j for j in body if L[j].strip()=='while num_items(Items.Cactus) <= 0:']
    F=[j for j in body if L[j].strip()=='wait_until(tl + 0.9676)'][-1]
    p='\t'*b
    assert F>W[-1]
    if n=='w0':
        assert L[F+1].strip()=='while num_drones() > 1:' and L[F+3].strip()=='harvest()'
        w=W[-1]; assert L[w+1].strip()=='pass'
        rep[w+1]=[L[w+1], p+'hm = get_time()']
        rep[F+3]=[p+'wait_until(hm + %s)'%C, L[F+3]]
        continue
    rep[W[0]]=[p+'hb = 0', L[W[0]]]
    for w in W:
        nl=L[w+1]
        if nl.strip()=='pass': rep[w+1]=[p+'\thb = get_time()']
        else: rep.setdefault(w+1,[nl]); rep[w+1]=[p+'\thb = get_time()']+rep[w+1]
    if UNSAFE: rep[F]=[p+'pass']
    else: rep[F]=[p+'if tl + 0.9676 > hb + %s:'%C, p+'\twait_until(tl + 0.9676)']
out=[]
for i,l in enumerate(L):
    out+= rep.get(i,[l])
open(dst,'w').write('\n'.join(out))
