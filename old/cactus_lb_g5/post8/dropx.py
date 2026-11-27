"""dropx.py IN OUT W XCAS : delete the line XCAS that follows W's first `tl = get_time()`"""
import sys, re
src,dst,W,X=sys.argv[1:5]
L=open(src).read().split('\n')
stk=[]; own=[]
for i,ln in enumerate(L):
    if ln.strip():
        ind=len(ln)-len(ln.lstrip('\t'))
        while stk and stk[-1][0]>=ind: stk.pop()
        m=re.match(r'\s*def (\w+)\(',ln)
        if m: stk.append((ind,m.group(1)))
    if stk and stk[-1][1]==W: own.append(i)
t=[i for i in own if L[i].strip()=='tl = get_time()'][0]
assert L[t+1].strip()==X, L[t+1]
del L[t+1]
open(dst,'w').write('\n'.join(L))
