# remove wafter watering from given round-B owners: unwater.py IN OUT w19,...
import sys,re
L=open(sys.argv[1]).read().split('\n'); names=sys.argv[3].split(',')
def owner(i):
    lev=len(L[i])-len(L[i].lstrip('\t'))
    for j in range(i-1,-1,-1):
        m=re.match(r'(\t*)def (w\d+)\(\):',L[j])
        if m and len(m.group(1))<lev: return m.group(2)
dele=[]
for i,l in enumerate(L):
    if l.strip()=='if use_item(Items.Water, 4):' and L[i-1].strip()=='tl = get_time()' and L[i+1].strip()=='tl = get_time() - 0.0988' and owner(i) in names:
        dele+= [i,i+1]; names.remove(owner(i))
assert not names,names
open(sys.argv[2],'w').write('\n'.join(l for i,l in enumerate(L) if i not in dele))
