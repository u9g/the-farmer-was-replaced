# undo early.py
import sys,re
L=open(sys.argv[1]).read().split('\n'); out=[]; i=0
while i<len(L):
    l=L[i]; s=l.strip(); p=l[:len(l)-len(l.lstrip('\t'))]
    if s=='hb = 0' or s=='hm = get_time()' or re.match(r'wait_until\(hm \+ [\d.]+\)$',s): i+=1; continue
    if s=='hb = get_time()':
        nxt=L[i+1] if i+1<len(L) else ''
        if len(nxt)-len(nxt.lstrip('\t'))==len(p) and nxt.strip(): i+=1; continue  # prepended
        out.append(p+'pass'); i+=1; continue
    m=re.match(r'if tl \+ 0\.9676 > hb \+ [\d.]+:$',s)
    if m:
        assert L[i+1].strip()=='wait_until(tl + 0.9676)'
        out.append(p+'wait_until(tl + 0.9676)'); i+=2; continue
    out.append(l); i+=1
open(sys.argv[2],'w').write('\n'.join(out))
