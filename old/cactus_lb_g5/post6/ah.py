import sys,re
src=open(sys.argv[1]).read().split('\n'); out=[]
H=0
for i,l in enumerate(src):
    out.append(l)
    if l.strip()=='use_item(Items.Water)':
        t=l[:len(l)-len(l.lstrip('\t'))]
        out.append(t+'if (get_time() // WDT) - num_items(Items.Water) >= NSIG + 1:')
        out.append(t+'\tif get_entity_type() == Entities.Cactus:')
        out.append(t+'\t\tharvest()')
for i,l in enumerate(out):
    if l.strip()=='while (get_time() // WDT) - num_items(Items.Water) < NSIG + 1:':
        assert out[i+1].strip()=='pass' and out[i+2].strip()=='harvest()'
        t=out[i+2][:len(out[i+2])-len(out[i+2].lstrip('\t'))]
        out[i+2]=t+'if num_items(Items.Cactus) <= 0:'
        out.insert(i+3,t+'\tharvest()')
        H+=1
assert H==1
open(sys.argv[2],'w').write('\n'.join(out))
