# Launch-path compute shave (deployment corner).
# Every `def` costs 1 tick, and the module-level helper defs run on the main drone before its
# first spawn, so they delay every drone's launch. The helpers only round B uses (pk_*, own,
# hlp, xcasw, fsSW_E, found by scanning each drone's code up to its first-harvest wait) move into
# one module-level function `ldefs()` that defines them as globals (`global NAME` + `def NAME`);
# each drone calls `ldefs()` just before it waits for the first harvest (idle time; the harvester
# w19 calls it after its harvesting loop). w0's body also runs at module level (no `def w0`).
# First spawn: 21 -> 11 ticks. Apply after any other edits to these helpers.
# usage: python lazydefs2.py IN.py OUT.py
import re, sys
src, dst = sys.argv[1], sys.argv[2]
L = open(src).read().split('\n')
i0 = next(i for i, l in enumerate(L) if l.startswith('def w0():'))


def ind(l):
    return len(l) - len(l.lstrip('\t'))


tops = {}
i = 0
while i < i0:
    m = re.match(r'def (\w+)\(', L[i])
    if m:
        j = i + 1
        while j < i0 and (L[j] == '' or L[j].startswith('\t')):
            j += 1
        while L[j - 1] == '':
            j -= 1
        tops[m.group(1)] = (i, j)
        i = j
    else:
        i += 1
H = list(tops)
blocks = []
for i in range(i0, len(L)):
    m = re.match(r'(\t*)def (w\d+)\(\):$', L[i])
    if m:
        blocks.append((i, len(m.group(1)), m.group(2)))
usedA = set()
waitat = {}
for (i, lev, name) in blocks:
    j = i + 1
    own_lines = []
    while j < len(L) and (L[j].strip() == '' or ind(L[j]) > lev):
        l = L[j]
        if re.match(r'\t*def w\d+\(\):$', l):
            lv = ind(l)
            j += 1
            while j < len(L) and (L[j].strip() == '' or ind(L[j]) > lv):
                j += 1
            continue
        own_lines.append(j)
        j += 1
    waits = [k for k in own_lines if L[k] == '\t' * (lev + 1) + 'while num_items(Items.Cactus) <= 0:']
    assert waits, name
    k = waits[0]
    for x in own_lines:
        if x >= k:
            break
        for h in H:
            if re.search(r'\b%s\b' % h, L[x]):
                usedA.add(h)
    if L[k + 1].strip().startswith('if (get_time() // WDT)'):
        k = waits[1]
    waitat[k] = lev + 1
# helpers referenced by round-A helpers stay too
ch = True
while ch:
    ch = False
    for h in list(usedA):
        a, b = tops[h]
        for g in H:
            if g not in usedA and any(re.search(r'\b%s\b' % g, l) for l in L[a + 1:b]):
                usedA.add(g)
                ch = True
MOVE = [h for h in H if h not in usedA]
print('moved into ldefs():', MOVE, file=sys.stderr)
dead = set()
for n in MOVE:
    dead.update(range(*tops[n]))
ld = ['def ldefs():'] + ['\tglobal %s' % n for n in MOVE]
for n in MOVE:
    a, b = tops[n]
    ld += [('\t' + x) if x else '' for x in L[a:b] if x != '']
out = []
for x, l in enumerate(L):
    if x == i0:
        out += ld + ['', '']
    if x in dead:
        continue
    if x in waitat:
        out.append('\t' * waitat[x] + 'ldefs()')
    out.append(l)
s = re.sub(r'\n\n\n\n+', '\n\n\n', '\n'.join(out))
o = s.split('\n')
a = next(i for i, l in enumerate(o) if l.startswith('def w0():'))
b = max(i for i, l in enumerate(o) if l == 'w0()')
o = o[:a] + [l[1:] if l.startswith('\t') else l for l in o[a + 1:b]] + o[b + 1:]
open(dst, 'w', newline='\n').write('\n'.join(o))
