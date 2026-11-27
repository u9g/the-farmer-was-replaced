# sched_10: sched_9 with a narrower route first on 6x6 (PH6: (columns, until time)).
# sched_9: sched_7, and while power is on, wait at a carrot that is due soon.
# sched_7: layouts with flexible support cells, torus walk, skip unripe cells; on 6x6 with
# sunflowers, a one-off sunflower burst: the first NSUN freed carrot cells get sunflowers, the
# highest-petal one is cut while 10 or more stand (8 power each), then the rest are cut and the
# cells go back to carrots.
# roles: G grass, C carrot (or sunflower during the burst), T tree-or-grass, B bush-or-grass

LAY3 = ['CBC', 'BGB', 'CBC']
LAY4B = ['BCBC', 'CGCB', 'BCBC', 'CBCG']
LAY4C = ['TGTG', 'GTGT', 'TGTG', 'GTGT']
LAY6D = ['TCTCTC', 'CTCTCT', 'TCTCTC', 'CTCTCT', 'TCTCTC', 'CTCTCT']
LAY6E = ['GTGCGC', 'CGCGTG', 'GCGTGC', 'TGCGCG', 'GCGCGT', 'CGTGCG']
MC = 1.8  # expected carrot multiplier, for planning seeds
MCP = 1.3  # pending carrots counted at this multiplier when deciding to plant more
MT = 1.7
WLO = 0.15
NSUN = 13
PH6 = [(2, 12), (4, 30), (6, 9999)]
CW = 5.0  # with power on, wait at a carrot planted at least this long ago

NEED = {}
ST = [0, 0, 0]  # pending carrots, trees, bushes
FLAG = [True, True]  # plant carrots, plant wood
HT = [0]
CC = [1]
YC = [1, 5, 1]  # yields: carrot, tree (x MT), bush (x MT)
NC = [0, 0, 0, 0]
RT = []
SUN = {}  # route index -> petals of the sunflower standing there
SS = [0, 0, 0]  # sunflowers planted so far, standing now, max petals


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


def done():
	for it in NEED:
		if num_items(it) < NEED[it]:
			return False
	return True


def smax():
	m = 0
	for k in SUN:
		if SUN[k] > m:
			m = SUN[k]
	SS[2] = m


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
			if get_time() < RT[i] or num_items(Items.Power) == 0:
				return False
			while not can_harvest():
				pass
		harvest()
		ST[0] -= 1
		r = True
	elif e == Entities.Sunflower:
		if not can_harvest():
			return False
		if SS[1] >= 10 and SUN[i] < SS[2]:
			return False
		harvest()
		SUN.pop(i)
		SS[1] -= 1
		smax()
	elif get_ground_type() != Grounds.Soil:
		if e == Entities.Grass and num_items(Items.Hay) < HT[0]:
			harvest()
			r = True
		till()
	if SS[0] < NSUN and num_items(Items.Carrot) >= 1:
		if plant(Entities.Sunflower):
			SUN[i] = measure()
			SS[0] += 1
			SS[1] += 1
			smax()
			upd()
			return r
	if FLAG[0] and plant(Entities.Carrot):
		ST[0] += 1
		RT[i] = get_time() + CW
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
		upd()
	elif e == Entities.Grass:
		if num_items(Items.Hay) < HT[0] and can_harvest():
			harvest()
			r = True
	if FLAG[1]:
		if plant(Entities.Bush):
			ST[2] += 1
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
	if num_unlocked(Unlocks.Sunflowers) == 0:
		SS[0] = NSUN
	CC[0] = lvl(Unlocks.Carrots)
	YC[0] = lvl(Unlocks.Carrots)
	YC[1] = 5 * lvl(Unlocks.Trees) * MT
	YC[2] = lvl(Unlocks.Trees) * MT
	NC[1] = YC[0] * MCP
	if Items.Carrot in need:
		NC[0] = need[Items.Carrot]
	if SS[0] < NSUN:
		NC[0] += NSUN
	if Items.Wood in need:
		NC[2] = need[Items.Wood]
	if Items.Hay in need:
		NC[3] = need[Items.Hay]
	tr = num_unlocked(Unlocks.Trees) > 0
	RT.append(0)
	for c in range(n * n):
		RT.append(0)
	upd()
	ph = PH6
	if n != 6:
		ph = [(n, 9999)]
	for p in ph:
		r = route(n, p[0], lay, tr)
		fs = r[0]
		ds = r[1]
		cs = r[2]
		L = len(fs)
		until = p[1]
		while get_time() < until:
			for i in range(L):
				f = fs[i]
				if f(cs[i]) and done():
					return
				move(ds[i])


def route(n, K, lay, tr):
	# K == n: torus column walk (every cell once, n * n moves); K < n (even): a snake over
	# columns 0..K-1, then east along row 0 back to column 0
	fs = []
	ds = []
	cs = []
	x = 0
	y = 0
	if K == n:
		for c in range(n):
			for k in range(n):
				cs.append(x * n + y)
				if k < n - 1:
					ds.append(North)
					y = (y + 1) % n
				else:
					ds.append(East)
					x = (x + 1) % n
	else:
		for c in range(K):
			for k in range(n):
				cs.append(x * n + y)
				if k < n - 1:
					if c % 2 == 0:
						ds.append(North)
						y += 1
					else:
						ds.append(South)
						y -= 1
				else:
					ds.append(East)
					x += 1
		while x < n:
			cs.append(x * n + y)
			ds.append(East)
			x += 1
	for c in cs:
		ch = lay[c % n][c // n]
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
	return (fs, ds, cs)
