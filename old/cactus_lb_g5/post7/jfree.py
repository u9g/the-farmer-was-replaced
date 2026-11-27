"""Free exits for junction-settle blocks that end mid-tail: instead of walking back to a fixed cell
and then on to the next work, go straight from the cell the settle ended on.

    python jfree.py IN.py OUT.py
"""
import re, sys
src, dst = sys.argv[1], sys.argv[2]
L = open(src).read().split('\n')
DV = {'North': (0, 1), 'South': (0, -1), 'East': (1, 0), 'West': (-1, 0)}
def ind(l): return len(l) - len(l.lstrip('\t'))
def path(dx, dy, first):
    xs = ['East'] * dx if dx > 0 else ['West'] * (-dx)
    ys = ['North'] * dy if dy > 0 else ['South'] * (-dy)
    return (ys + xs) if first in ('North', 'South') else (xs + ys)
rep = {}
nsaved = 0
for i, l in enumerate(L):
    if not re.match(r'\s*wk = \[', l): continue
    lev = ind(l)
    j = i
    while not L[j].strip().startswith('while qi < qn:'): j += 1
    k = j + 1
    while ind(L[k]) > lev or L[k].strip() == '': k += 1
    if L[k].strip().startswith('c = cur'): continue
    retmap = {}; t = k; order = []
    while True:
        s = L[t].strip()
        m = re.match(r'(?:el)?if cur == (\d+):$', s)
        if not m or ind(L[t]) != lev: break
        b = int(m.group(1)); mv = []; u = t + 1
        while u < len(L) and ind(L[u]) == lev + 1 and re.match(r'move\((\w+)\)$', L[u].strip()):
            mv.append(L[u].strip()[5:-1]); u += 1
        assert ind(L[u]) <= lev, (u, L[u])
        retmap[b] = mv; order.append(b); t = u
    if not retmap: continue
    fs = t
    fol = []
    while ind(L[t]) == lev and re.match(r'move\((\w+)\)$', L[t].strip()):
        fol.append(L[t].strip()[5:-1]); t += 1
    if not fol: continue
    fx = sum(DV[m][0] for m in fol); fy = sum(DV[m][1] for m in fol)
    tab = '\t' * lev
    out = []
    first = True
    sav = []
    for b in order:
        dx = sum(DV[m][0] for m in retmap[b]) + fx; dy = sum(DV[m][1] for m in retmap[b]) + fy
        p = path(dx, dy, fol[0])
        sav.append(len(retmap[b]) + len(fol) - len(p))
        out.append(tab + ('if' if first else 'elif') + ' cur == %d:' % b); first = False
        out += [tab + '\tmove(%s)' % d for d in p] or [tab + '\tpass']
    out.append(tab + 'else:')
    fp = path(fx, fy, fol[0])
    out += [tab + '\tmove(%s)' % d for d in fp]
    sav.append(len(fol) - len(fp))
    if max(sav) == 0: continue
    nsaved += 1
    print('block at %d: savings per cur %s' % (i + 1, dict(zip(order + ['ret'], sav))))
    rep[k] = out
    for x in range(k + 1, t): rep[x] = []
res = []
for x, l in enumerate(L):
    if x in rep: res += rep[x]
    else: res.append(l)
open(dst, 'w').write('\n'.join(res))
print('blocks changed', nsaved)
