# usage: bend.py IN OUT [steps]  steps: f=floor before poll, q=w13 deadline, h=hlp/own tail
import sys
src, dst = sys.argv[1], sys.argv[2]
steps = sys.argv[3] if len(sys.argv) > 3 else 'fqh'
s = open(src).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new)
if 'f' in steps:
    rep("\twait_until(tl + 0.9676)\n\twhile num_drones() > 1:\n\t\tpass\n\twait_until(hm + 2.6)\n\tharvest()\n",
        "\twait_until(tl + 0.9676)\n\twait_until(hm + 2.6)\n\twhile num_drones() > 1:\n\t\tpass\n\tharvest()\n")
if 'h' in steps:
    rep("""	while j <= e:
		FS[j]()
		if j < e:
			for d in MS[j]:
				move(d)
		j += 1


def own(""", """	while j < e:
		FS[j]()
		for d in MS[j]:
			move(d)
		j += 1
	FS[e]()


def own(""")
    rep("""		FS[j]()
		if j < e:
			for d in MS[j]:
				move(d)
		j += 1
""", """		FS[j]()
		for d in MS[j]:
			move(d)
		j += 1
	FS[e]()
""")
    rep("\twhile j <= e:\n\t\tif e - j >= 2 and", "\twhile j < e:\n\t\tif e - j >= 2 and")
if 'q' in steps:
    L = s.split('\n')
    # w13: round-A unconditional 4-water on the cell its last round-B pk pushes a cactus onto
    i = L.index('\t\tdef w13():') if '\t\tdef w13():' in L else [k for k, l in enumerate(L) if l.strip() == 'def w13():'][0]
    k = i
    while L[k].strip() != 'use_item(Items.Water, 4)': k += 1
    L[k] = L[k].replace('use_item(Items.Water, 4)', 'wA = use_item(Items.Water, 4)')
    while not (L[k].strip() == 'pk_East_North_None_0_0()' and L[k+1].strip() == 'tl = get_time()' and L[k+2].strip() == 'if use_item(Items.Water, 4):'):
        k += 1
    ind = L[k][:len(L[k]) - len(L[k].lstrip('\t'))]
    L[k] = ind + 'tq = pkq()'
    assert L[k+3].strip() == 'tl = get_time() - 0.0988'
    L[k+3] += '\n' + ind + '\tif wA:\n' + ind + '\t\ttl = tq'
    j = L.index('def pk_East_North_West_0_1():')
    L[j:j] = ['def pkq():', '\tglobal PD', '\tplant(Entities.Cactus)', '\tt = get_time() - 0.0658', '\tif PD:', '\t\tt = get_time()',
              '\t\tswap(East)', '\t\tplant(Entities.Cactus)', '\t\tPD = False', '\tswap(North)', '\tplant(Entities.Cactus)', '\treturn t', '', '']
    s = '\n'.join(L)
open(dst, 'w').write(s)
