"""Round A: water the last-planted cell of chosen chunks before planting it, and count the growth
wait from the plant before it (the watered cactus grows in 0.2 s and, even if a fix swaps it onto a
dry cell right away, is grown before the earlier one).

    WL=w19,w15,w25 python wlast.py IN.py OUT.py

Every pre-watering is unconditional (4 water) and all happen long before the first round-A signal,
so the signal count NSIG (water used) goes up by 4 per chunk.
"""
import os, re, sys

src, dst = sys.argv[1], sys.argv[2]
L = open(src).read().split('\n')
names = [x for x in os.environ.get('WL', 'w19,w15,w25').split(',') if x]
UNITS = int(os.environ.get('WU', '4'))

def own_lines(name):
    i = next(i for i, l in enumerate(L) if re.match(r'\s*def %s\(\):' % name, l))
    ind = len(L[i]) - len(L[i].lstrip('\t'))
    j = i + 1; out = []; skip = None
    while j < len(L) and (L[j].strip() == '' or len(L[j]) - len(L[j].lstrip('\t')) > ind):
        li = len(L[j]) - len(L[j].lstrip('\t'))
        if skip is not None and (L[j].strip() == '' or li > skip):
            j += 1; continue
        skip = None
        if L[j].lstrip().startswith('def '): skip = li
        else: out.append(j)
        j += 1
    return out

ins = {}   # line index -> list of lines to insert before
rep = {}   # line index -> replacement (None = delete)
for nm in names:
    ow = own_lines(nm)
    k = next(x for x in ow if L[x].strip() == 'tl = get_time()')
    pos = ow.index(k)
    plants = [x for x in ow[:pos] if L[x].strip() == 'plant(Entities.Cactus)']
    p1, p2 = plants[-1], plants[-2]
    ind1 = L[p1][:len(L[p1]) - len(L[p1].lstrip('\t'))]
    ind2 = L[p2][:len(L[p2]) - len(L[p2].lstrip('\t'))]
    assert ind1 == ind2 == L[k][:len(ind1)]
    # between p2 and p1 there must be no other plant; record what is there
    between = [L[x].strip() for x in ow if p2 < x < p1]
    print(nm, 'between plants:', between, '| after:', [L[x].strip() for x in ow[pos:pos + 3]])
    ins.setdefault(p2 + 1, []).append(ind2 + 'tl = get_time()')
    ins.setdefault(p1, []).append(ind1 + 'use_item(Items.Water, %d)' % UNITS)
    rep[k] = None
out = []
for i, l in enumerate(L):
    if i in ins: out += ins[i]
    if i in rep:
        if rep[i] is not None: out.append(rep[i])
        continue
    out.append(l)
T = '\n'.join(out)
n0 = re.search(r'^NSIG = (\d+)$', T, re.M)
T = re.sub(r'^NSIG = \d+$', 'NSIG = %d' % (int(n0.group(1)) + UNITS * len(names)), T, count=1, flags=re.M)
open(dst, 'w').write(T)
print('NSIG', int(n0.group(1)) + UNITS * len(names))
