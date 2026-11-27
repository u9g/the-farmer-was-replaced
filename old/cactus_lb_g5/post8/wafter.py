# water (U units) the last round-B cell after planting it; count growth wait from the plant before.
# usage: wafter.py IN OUT w12,w19,...   env U=4
import sys,re,os
src,dst,names=sys.argv[1],sys.argv[2],sys.argv[3].split(',')
U=os.environ.get('U','4')
L=open(src).read().split('\n')
def owner(i):
    l=L[i]; lev=len(l)-len(l.lstrip('\t'))
    for j in range(i-1,-1,-1):
        m=re.match(r'(\t*)def (w\d+)\(\):',L[j])
        if m and len(m.group(1))<lev: return m.group(2)
ins=[]
for w in [i for i,l in enumerate(L) if l.strip()=='while num_items(Items.Cactus) <= 0:']:
    o=owner(w)
    if o not in names: continue
    ind=len(L[w])-len(L[w].lstrip('\t'))
    j=w+1
    while not (L[j].strip()=='tl = get_time()' and len(L[j])-len(L[j].lstrip('\t'))==ind): j+=1
    if j in [x for x,_ in ins]: continue
    assert 'Fertilizer' not in L[j+1] and 'tw' not in L[j+1], (o,L[j+1])
    p='\t'*ind
    ins.append((j,[p+'if use_item(Items.Water, %s):'%U, p+'\ttl = get_time() - 0.0988']))
    names.remove(o)
assert not names, names
for j,b in sorted(ins,reverse=True): L[j+1:j+1]=b
open(dst,'w').write('\n'.join(L))
