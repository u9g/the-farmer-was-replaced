"""Dynamic water on the last round-B plant: a drone whose last plant comes late (get_time() > X,
absolute run time: hb is 0 for drones that arrive after the first harvest, so it is no reference)
waters it (4 water; on the empty cell before planting where the plant before is two actions back,
on the cactus after planting where it follows a swap) and counts its growth wait from the plant before.
Sites that already water or fertilize are left alone.
usage: dynwat.py IN OUT X [N]   (N = water per use, default 4)"""
import sys
src, dst, X = sys.argv[1], sys.argv[2], sys.argv[3]
N = sys.argv[4] if len(sys.argv) > 4 else '4'
L = open(src).read().split('\n')
hbs = [i for i, l in enumerate(L) if l.strip() == 'hb = 0']
edits = []  # (line index of tl, kind)
for h in hbs:
    j = h
    while 'tl = get_time()' not in L[j]:
        j += 1
    nxt = L[j + 1].strip()
    if nxt.startswith('if use_item') or nxt.startswith('if tw'):
        continue
    p1, p2, p3 = L[j - 1].strip(), L[j - 2].strip(), L[j - 3].strip()
    ind = L[j][:len(L[j]) - len(L[j].lstrip())]
    if p1 == 'plant(Entities.Cactus)' and p2.startswith('move(') and (p3 == 'plant(Entities.Cactus)' or (p3.startswith('pk_') and ('_None_1_0' in p3 or '_None_0_0' in p3))):
        edits.append((j, 'M', ind))
    elif p1 == 'plant(Entities.Cactus)' and p2.startswith('swap(') and p3 == 'plant(Entities.Cactus)':
        edits.append((j, 'P', ind))
    elif p1.startswith('pk_') and p1.endswith('_None_1_0()') or p1.startswith('pk_') and '_None_0_0' in p1:
        edits.append((j, 'P', ind))
    else:
        print('skip', j + 1, p3, '|', p2, '|', p1, file=sys.stderr)
for j, kind, ind in sorted(edits, reverse=True):
    if kind == 'M':
        # water the empty cell before the last plant
        new = [ind + 'tw = 0',
               ind + 'if get_time() > %s:' % X,
               ind + '\tif use_item(Items.Water, %s):' % N,
               ind + '\t\ttw = 1',
               ind + 'plant(Entities.Cactus)',
               ind + 'tl = get_time()',
               ind + 'if tw:',
               ind + '\ttl = tl - 0.0988']
        L[j - 1:j + 1] = new
    else:
        new = [ind + 'tl = get_time()',
               ind + 'if tl > %s:' % X,
               ind + '\tif use_item(Items.Water, %s):' % N,
               ind + '\t\ttl = get_time() - 0.0988']
        L[j:j + 1] = new
print(len(edits), 'sites', file=sys.stderr)
open(dst, 'w').write('\n'.join(L))
