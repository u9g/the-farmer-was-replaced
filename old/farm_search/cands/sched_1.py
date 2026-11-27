# sched_1: fixed layout per field, torus walk, each cell tended by its role; skip unripe cells.
# roles: G grass (harvest only), C carrot, T tree, B bush

LAY3 = ['CBC', 'BGB', 'CBC']
LAY4B = ['BCBC', 'CGCB', 'BCBC', 'CBCG']
LAY4C = ['TGTG', 'GTGT', 'TGTG', 'GTGT']
LAY6D = ['GCTCGC', 'CGCGCT', 'TCGCGC', 'CGCTCG', 'GCGCGC', 'CTCGCG']
LAY6E = ['GTGCGC', 'CGCGTG', 'GCGTGC', 'TGCGCG', 'GCGCGT', 'CGTGCG']

NEED = {}
ST = [0, 0, 0]  # pending carrots, trees, bushes
FLAG = [True, True, True, True]  # want carrot, want wood (tree/bush), want hay, (unused)
CC = [1]
YC = [1, 5, 1, 1]  # yields: carrot, tree, bush, grass
MC = 1.6
MT = 1.6


def lvl(u):
	n = num_unlocked(u)
	if n <= 1:
		return 1
	return 2 ** (n - 1)


def nd(it):
	if it in NEED:
		return NEED[it]
	return 0


def upd():
	yc = YC[0] * MC
	kc = (nd(Items.Carrot) - num_items(Items.Carrot) - ST[0] * yc) / yc
	if kc < 0:
		kc = 0
	FLAG[0] = kc > 0
	wt = nd(Items.Wood) + kc * CC[0]
	FLAG[1] = num_items(Items.Wood) + ST[1] * YC[1] * MT + ST[2] * YC[2] * MT < wt
	ht = nd(Items.Hay) + kc * CC[0]
	FLAG[2] = num_items(Items.Hay) < ht


def done():
	for it in NEED:
		if num_items(it) < NEED[it]:
			return False
	return True


def tg():
	if FLAG[2] and can_harvest():
		harvest()
		upd()


def tc():
	e = get_entity_type()
	if e == Entities.Carrot:
		if not can_harvest():
			return
		harvest()
		ST[0] -= 1
	elif get_ground_type() != Grounds.Soil:
		if e == Entities.Grass and FLAG[2]:
			harvest()
		till()
	if FLAG[0] and plant(Entities.Carrot):
		ST[0] += 1
	upd()


def tt():
	e = get_entity_type()
	if e == Entities.Tree:
		if not can_harvest():
			return
		harvest()
		ST[1] -= 1
	elif e == Entities.Grass:
		if FLAG[2]:
			harvest()
	if FLAG[1]:
		if plant(Entities.Tree):
			ST[1] += 1
			if get_water() < 0.15 and num_items(Items.Water) >= 1:
				use_item(Items.Water)
	upd()


def tb():
	e = get_entity_type()
	if e == Entities.Bush:
		if not can_harvest():
			return
		harvest()
		ST[2] -= 1
	elif e == Entities.Grass:
		if FLAG[2]:
			harvest()
	if FLAG[1]:
		if plant(Entities.Bush):
			ST[2] += 1
	upd()


def run_farm(need):
	global NEED
	NEED = need
	n = get_world_size()
	if n == 3:
		lay = LAY3
	elif n == 4:
		if num_unlocked(Unlocks.Trees) > 0:
			lay = LAY4C
		else:
			lay = LAY4B
	elif Items.Hay in need:
		lay = LAY6E
	else:
		lay = LAY6D
	CC[0] = lvl(Unlocks.Carrots)
	YC[0] = lvl(Unlocks.Carrots)
	YC[1] = 5 * lvl(Unlocks.Trees)
	YC[2] = lvl(Unlocks.Trees)
	if num_unlocked(Unlocks.Trees) == 0:
		lay2 = []
		for row in lay:
			s = ''
			for ch in row:
				if ch == 'T':
					s += 'B'
				else:
					s += ch
			lay2.append(s)
		lay = lay2
	# route: torus column walk
	fs = []
	ds = []
	x = get_pos_x()
	y = get_pos_y()
	for c in range(n):
		for k in range(n):
			ch = lay[y][x]
			if ch == 'G':
				fs.append(tg)
			elif ch == 'C':
				fs.append(tc)
			elif ch == 'T':
				fs.append(tt)
			else:
				fs.append(tb)
			if k < n - 1:
				ds.append(North)
				y = (y + 1) % n
			else:
				ds.append(East)
				x = (x + 1) % n
	upd()
	L = n * n
	while True:
		for i in range(L):
			f = fs[i]
			f()
			if done():
				return
			move(ds[i])
