import sys,json,retree
from model import parse,arrivals
E='/home/user/the-farmer-was-replaced/cactus_lb_entry.py' if len(sys.argv)<4 else sys.argv[3]
src=open(E).read()
la=json.load(open(sys.argv[1]))
la={k:[(t,tuple(a) if t=='G' else a) for t,a in v] for k,v in la.items()}
L,defs,launch0=parse(E); arr0,P=arrivals(launch0)
for k in la: la[k]=la[k]+[('G',P[k])]
h,f,tl=retree.flatten(src)
ml=retree.from_goto(la)
open(sys.argv[2],'w').write(retree.build(h,f,tl,ml))
L,defs,l2=parse(sys.argv[2]); a2,P2=arrivals(l2)
assert P2==P, 'positions differ'
print('avg arrival',sum(a2.values())/32)
