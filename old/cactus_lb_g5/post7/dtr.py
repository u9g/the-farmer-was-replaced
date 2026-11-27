"""Replace runs of consecutive unconditional moves (same indentation, nothing in between) that are
longer than their net displacement by a shortest path (same first direction first).

    python dtr.py IN.py OUT.py
"""
import re, sys
L = open(sys.argv[1]).read().split('\n')
DV = {'North': (0, 1), 'South': (0, -1), 'East': (1, 0), 'West': (-1, 0)}
MV = re.compile(r'(\s*)move\((North|South|East|West)\)$')
def ind(l): return len(l) - len(l.lstrip('\t'))
out = []; i = 0; n = 0; saved = 0
while i < len(L):
    m = MV.match(L[i])
    if not m: out.append(L[i]); i += 1; continue
    j = i; mv = []
    while j < len(L) and ind(L[j]) == ind(L[i]) and MV.match(L[j]):
        mv.append(MV.match(L[j]).group(2)); j += 1
    dx = sum(DV[d][0] for d in mv); dy = sum(DV[d][1] for d in mv)
    if abs(dx) >= 16 or abs(dy) >= 16:
        out += L[i:j]; i = j; continue
    if len(mv) > abs(dx) + abs(dy):
        xs = ['East'] * dx if dx > 0 else ['West'] * (-dx)
        ys = ['North'] * dy if dy > 0 else ['South'] * (-dy)
        p = (ys + xs) if mv[0] in ('North', 'South') else (xs + ys)
        if not p:
            # an empty block body would be a syntax error: keep a no-op only if needed
            p = []
        out += [m.group(1) + 'move(%s)' % d for d in p]
        n += 1; saved += len(mv) - len(p)
        print('line %d: %s -> %s' % (i + 1, ''.join(d[0] for d in mv), ''.join(d[0] for d in p)))
    else:
        out += L[i:j]
    i = j
open(sys.argv[2], 'w').write('\n'.join(out))
print('runs', n, 'moves saved', saved)
