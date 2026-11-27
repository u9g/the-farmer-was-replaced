"""prefix.py IN OUT X:DIR:ROUTINE[:BACK] ...
Right after X's round-A last plant (its first `tl = get_time()`), X steps DIR onto the facing
neighbour's cut middle, settles it with ROUTINE, and steps back.  The neighbour's own later
call there then finds it sorted (middle fixes are permanent in 3-level bands)."""
import sys, re
OPP={"North":"South","South":"North","East":"West","West":"East"}
src, dst = sys.argv[1], sys.argv[2]
L=open(src).read().split('\n')
def owner_lines(w):
    stk=[]; out=[]
    for i,ln in enumerate(L):
        if ln.strip():
            ind=len(ln)-len(ln.lstrip('\t'))
            while stk and stk[-1][0]>=ind: stk.pop()
            m=re.match(r'\s*def (\w+)\(',ln)
            if m: stk.append((ind,m.group(1)))
        if stk and stk[-1][1]==w: out.append(i)
    return out
ins={}
for spec in sys.argv[3:]:
    p=spec.split(':'); X,d,r=p[0],p[1],p[2]
    ls=[i for i in owner_lines(X) if L[i].strip()=='tl = get_time()']
    i=ls[0]
    ind=L[i][:len(L[i])-len(L[i].lstrip('\t'))]
    assert L[i-1].strip()=='plant(Entities.Cactus)', (X, L[i-1])
    ins[i]=[ind+'move(%s)'%d, ind+'%s()'%r, ind+'move(%s)'%OPP[d]]
out=[]
for i,ln in enumerate(L):
    out.append(ln)
    if i in ins: out.extend(ins[i])
open(dst,'w').write('\n'.join(out))
