"""Round-A first-harvest tweaks (text pass on cactus_lb_entry.py).

HPOLL=1: the w19 harvester checks for the 32nd signal before each of its post-signal
         pre-travel moves (harvest there if it stands on a cactus), not only after them.
STAG="w16:1,w23:2": growth-bound drones that end in the same tick wait that many extra
         ticks, so the last of them sees the others' water and harvests itself.
"""
import os, re, sys

src, dst = sys.argv[1], sys.argv[2]
T = open(src).read()
L = T.split('\n')

def find_def(name):
    for i, l in enumerate(L):
        if re.match(r'\s*def %s\(\):' % name, l):
            return i
    raise KeyError(name)

def own_lines(name):
    i = find_def(name)
    ind = len(L[i]) - len(L[i].lstrip('\t'))
    j = i + 1; out = []; skip = None
    while j < len(L) and (L[j].strip() == '' or len(L[j]) - len(L[j].lstrip('\t')) > ind):
        li = len(L[j]) - len(L[j].lstrip('\t'))
        if skip is not None and (L[j].strip() == '' or li > skip):
            j += 1; continue
        skip = None
        if L[j].lstrip().startswith('def '):
            skip = li
        else:
            out.append(j)
        j += 1
    return out

if os.environ.get('HPOLL', '1') == '1':
    ls = own_lines('w19')
    # first 'for q in P:' after the harvester's signal
    k = next(j for j in ls if L[j].strip() == 'for q in P:' and 'NSIG + 1' in L[j + 4])
    ind = L[k][:len(L[k]) - len(L[k].lstrip('\t'))]
    assert L[k + 2].strip() == 'move(d)'
    L[k + 2] = '\n'.join([
        ind + '\t\tif num_items(Items.Cactus) <= 0:',
        ind + '\t\t\tif (get_time() // WDT) - num_items(Items.Water) >= NSIG + 1:',
        ind + '\t\t\t\tif get_entity_type() == Entities.Cactus:',
        ind + '\t\t\t\t\tharvest()',
        ind + '\t\tmove(d)'])
    print('HPOLL at line', k + 1)

stag = os.environ.get('STAG', 'w16:1,w23:2')
TICK = 1 / 6075.0
for item in filter(None, stag.split(',')):
    nm, n = item.split(':')
    ls = own_lines(nm)
    k = next(j for j in ls if L[j].strip() == 'wait_until(tl + 0.9676)' and 'NSIG' in L[j + 1])
    L[k] = L[k].replace('0.9676', '%.5f' % (0.9676 + int(n) * TICK))
    print('STAG', nm, 'line', k + 1, L[k].strip())

open(dst, 'w').write('\n'.join(L))
