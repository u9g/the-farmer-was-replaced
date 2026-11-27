# sched_3: fixed layout per field, torus walk, each cell tended by its role; skip unripe cells.
# roles: G grass (harvest only), C carrot, T tree, B bush, S sunflower (power: only the max is cut)

LAY3 = ['CBC', 'BGB', 'CBC']
LAY4B = ['BCBC', 'CGCB', 'BCBC', 'CBCG']
LAY4C = ['TGTG', 'GTGT', 'TGTG', 'GTGT']
LAY6D = ['SCTCSC', 'CSCSCT', 'TCSCGC', 'CGCTCS', 'SCGCSC', 'CTCSCS']
LAY6E = ['GTGCGC', 'CGCGTG', 'GCGTGC', 'TGCGCG', 'GCGCGT', 'CGTGCG']
PW_LO = 12
MC = 1.6
MT = 1.6
WLO = 0.15

NEED = {}
ST = [0, 0, 0]  # pending carrots, trees, bushes
FLAG = [True, True]  # want carrot, want wood
HT = [0]
CC = [1]
YC = [1, 5, 1, 1]  # yields: carrot, tree, bush, grass
NC = [0, 0, 0, 0]
SP = []
SM = [0, 0]  # max petals, sunflowers standing


def lvl(u):
	n = num_unlocked(u)
	if n <= 1:
		return 1
	return 2 ** (n - 1)


def upd():
	kc = NC[0] - num_items(Items.Carrot) * NC[1] - ST[0]
	if kc < 0:
		kc = 0
	FLAG[0] = kc > 0
	kc = kc * CC[0]
	FLAG[1] = num_items(Items.Wood) + ST[1] * YC[1] + ST[2] * YC[2] < NC[2] + kc
	HT[0] = NC[3] + kc


def done():
	for it in NEED:
		if num_items(it) < NEED[it]:
			return False
	return True


def tg(i):
	if num_items(Items.Hay) < HT[0] and can_harvest():
		harvest()
		return True
	return False


def tc(i):
	e = get_entity_type()
	r = False
	if e == Entities.Carrot:
		if not can_harvest():
			return False
		harvest()
		ST[0] -= 1
		r = True
	elif get_ground_type() != Grounds.Soil:
		if e == Entities.Grass and num_items(Items.Hay) < HT[0]:
			harvest()
			r = True
		till()
	if FLAG[0] and plant(Entities.Carrot):
		ST[0] += 1
	upd()
	return r


def tt(i):
	e = get_entity_type()
	r = False
	if e == Entities.Tree:
		if not can_harvest():
			return False
		harvest()
		ST[1] -= 1
		r = True
	elif e == Entities.Grass:
		if num_items(Items.Hay) < HT[0]:
			harvest()
			r = True
	if FLAG[1]:
		if plant(Entities.Tree):
			ST[1] += 1
			if get_water() < WLO and num_items(Items.Water) >= 1:
				use_item(Items.Water)
	upd()
	return r


def tb(i):
	e = get_entity_type()
	r = False
	if e == Entities.Bush:
		if not can_harvest():
			return False
		harvest()
		ST[2] -= 1
		r = True
	elif e == Entities.Grass:
		if num_items(Items.Hay) < HT[0]:
			harvest()
			r = True
	if FLAG[1]:
		if plant(Entities.Bush):
			ST[2] += 1
	upd()
	return r


def smax():
	m = 0
	for p in SP:
		if p > m:
			m = p
	SM[0] = m


def ts(i):
	p = SP[i]
	if p == 0:
		if num_items(Items.Carrot) < 1:
			return False
		r = False
		if get_ground_type() != Grounds.Soil:
			if get_entity_type() == Entities.Grass and num_items(Items.Hay) < HT[0]:
				harvest()
				r = True
			till()
		if plant(Entities.Sunflower):
			SP[i] = measure()
			SM[1] += 1
			smax()
			upd()
		return r
	if p == SM[0] and SM[1] >= 10 and num_items(Items.Power) < PW_LO and can_harvest():
		harvest()
		if plant(Entities.Sunflower):
			SP[i] = measure()
		else:
			SP[i] = 0
			SM[1] -= 1
		smax()
		upd()
	return False


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
	YC[1] = 5 * lvl(Unlocks.Trees) * MT
	YC[2] = lvl(Unlocks.Trees) * MT
	NC[1] = 1 / (YC[0] * MC)
	if Items.Carrot in need:
		NC[0] = need[Items.Carrot] * NC[1]
	if Items.Wood in need:
		NC[2] = need[Items.Wood]
	if Items.Hay in need:
		NC[3] = need[Items.Hay]
	sun = num_unlocked(Unlocks.Sunflowers) > 0
	tr = num_unlocked(Unlocks.Trees) > 0
	# route: torus column walk
	fs = []
	ds = []
	x = get_pos_x()
	y = get_pos_y()
	for c in range(n):
		for k in range(n):
			ch = lay[y][x]
			if ch == 'T' and not tr:
				ch = 'B'
			if ch == 'S' and not sun:
				ch = 'C'
			SP.append(0)
			if ch == 'G':
				fs.append(tg)
			elif ch == 'C':
				fs.append(tc)
			elif ch == 'T':
				fs.append(tt)
			elif ch == 'S':
				fs.append(ts)
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
			if f(i) and done():
				return
			move(ds[i])
