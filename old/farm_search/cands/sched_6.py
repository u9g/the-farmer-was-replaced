# sched_6: sched_5 plus waiting at an unripe crop that is due soon (planting times tracked).
# roles: G grass (harvest while hay is short, several cuts in a row if very short),
# C carrot, T tree (grass while wood is not short), B bush (likewise)

LAY3 = ['CBC', 'BGB', 'CBC']
LAY4B = ['BCBC', 'CGCB', 'BCBC', 'CBCG']
LAY4C = ['TGTG', 'GTGT', 'TGTG', 'GTGT']
LAY6D = ['TCTCTC', 'CTCTCT', 'TCTCTC', 'CTCTCT', 'TCTCTC', 'CTCTCT']
LAY6E = ['GTGCGC', 'CGCGTG', 'GCGTGC', 'TGCGCG', 'GCGCGT', 'CGTGCG']
MC = 1.8  # expected carrot multiplier, for planning seeds
MCP = 1.3  # pending carrots counted at this multiplier when deciding to plant more
MT = 1.7
MG = 1.8
WLO = 0.15
WAITW = 1.0  # wait at a crop whose earliest ripening is less than this many seconds away
GK = 4  # most cuts in a row on a grass cell
GX = 3.0  # keep cutting while the hay shortfall is above this many cuts

NEED = {}
ST = [0, 0, 0]  # pending carrots, trees, bushes
FLAG = [True, True]  # plant carrots, plant wood
HT = [0, 0]  # hay target, hay level above which one cut is enough
CC = [1]
YC = [1, 5, 1, 1]  # yields: carrot, tree (x MT), bush (x MT)
NC = [0, 0, 0, 0]
RT = []


def lvl(u):
	n = num_unlocked(u)
	if n <= 1:
		return 1
	return 2 ** (n - 1)


def upd():
	r = NC[0] - num_items(Items.Carrot)
	FLAG[0] = r > ST[0] * NC[1]
	kc = r / (YC[0] * MC) - ST[0]
	if kc < 0:
		kc = 0
	kc = kc * CC[0]
	FLAG[1] = NC[2] + kc > num_items(Items.Wood) + ST[1] * YC[1] + ST[2] * YC[2]
	HT[0] = NC[3] + kc
	HT[1] = HT[0] - YC[3]


def done():
	for it in NEED:
		if num_items(it) < NEED[it]:
			return False
	return True


def tg(i):
	if num_items(Items.Hay) >= HT[0]:
		return False
	if not can_harvest():
		return False
	harvest()
	k = 1
	while k < GK and num_items(Items.Hay) < HT[1]:
		while not can_harvest():
			pass
		harvest()
		k += 1
	return True


def tc(i):
	e = get_entity_type()
	r = False
	if e == Entities.Carrot:
		if not can_harvest():
			if get_time() < RT[i]:
				return False
			while not can_harvest():
				pass
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
		RT[i] = get_time() + 4.8 - WAITW
	upd()
	return r


def tt(i):
	e = get_entity_type()
	r = False
	if e == Entities.Tree:
		if not can_harvest():
			if get_time() < RT[i]:
				return False
			while not can_harvest():
				pass
		harvest()
		ST[1] -= 1
		r = True
		upd()
	elif e == Entities.Grass:
		if num_items(Items.Hay) < HT[0] and can_harvest():
			harvest()
			r = True
	if FLAG[1]:
		if plant(Entities.Tree):
			ST[1] += 1
			if get_water() < WLO and num_items(Items.Water) >= 1:
				use_item(Items.Water)
			RT[i] = get_time() + 5.6 / (1 + 4 * get_water()) - WAITW
			upd()
	return r


def tb(i):
	e = get_entity_type()
	r = False
	if e == Entities.Bush:
		if not can_harvest():
			if get_time() < RT[i]:
				return False
			while not can_harvest():
				pass
		harvest()
		ST[2] -= 1
		r = True
		upd()
	elif e == Entities.Grass:
		if num_items(Items.Hay) < HT[0] and can_harvest():
			harvest()
			r = True
	if FLAG[1]:
		if plant(Entities.Bush):
			ST[2] += 1
			RT[i] = get_time() + 3.2 - WAITW
			upd()
	return r


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
	YC[3] = lvl(Unlocks.Grass) * MG * GX
	NC[1] = YC[0] * MCP
	if Items.Carrot in need:
		NC[0] = need[Items.Carrot]
	if Items.Wood in need:
		NC[2] = need[Items.Wood]
	if Items.Hay in need:
		NC[3] = need[Items.Hay]
	tr = num_unlocked(Unlocks.Trees) > 0
	# route: torus column walk
	fs = []
	ds = []
	x = get_pos_x()
	y = get_pos_y()
	for c in range(n):
		for k in range(n):
			ch = lay[y][x]
			RT.append(0)
			if ch == 'T' and not tr:
				ch = 'B'
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
			if f(i) and done():
				return
			move(ds[i])
