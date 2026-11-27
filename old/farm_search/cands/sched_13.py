# sched_13: 3x3/4x4 without trees: a router that picks the next cell by its estimated ready time.
# sched_11: per-state phases and sunflower counts.
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
NSUND = 10
PH6 = [(6, 9999)]
PH6D = [(2, 18), (6, 9999)]
CW = 5.0  # with power on, wait at a carrot planted at least this long ago

NEED = {}
ST = [0, 0, 0]  # pending carrots, trees, bushes
FLAG = [True, True, 0, 0]  # plant carrots, plant wood, carrot plantings to go, wood harvests to go
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
	FLAG[2] = kc
	kc = kc * CC[0]
	w = NC[2] + kc - num_items(Items.Wood) - ST[1] * YC[1] - ST[2] * YC[2]
	FLAG[1] = w > 0
	FLAG[3] = w / YC[2]
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
		if SS[0] < NSUN or (SS[1] >= 10 and SUN[i] < SS[2]):
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


# ---- small farm router (3x3, 4x4 without trees) ---------------------------------------------
LAYR3 = ['XXX', 'XGX', 'XXX']
LAYR4 = ['XXXX', 'XGXX', 'XXXX', 'XXXG']
RXR = 1.0  # X cell: carrot while carrot plantings to go x RXR >= bush harvests to go
RF = 1.0  # a crop is expected ripe at planting + RF x mean growth
LAM = 0.5  # extra cost per second of travel
DMAX = 2
RCHK = 2.0  # an idle X cell is looked at again after this long
IDL = 0.05  # cells ready for longer are preferred
CAND3 = [[(1, 1, [North]), (2, 1, [South]), (3, 1, [East]), (4, 2, [East, North]), (5, 2, [East, South]), (6, 1, [West]), (7, 2, [West, North]), (8, 2, [West, South])], [(0, 1, [South]), (2, 1, [North]), (3, 2, [East, South]), (4, 1, [East]), (5, 2, [East, North]), (6, 2, [West, South]), (7, 1, [West]), (8, 2, [West, North])], [(0, 1, [North]), (1, 1, [South]), (3, 2, [East, North]), (4, 2, [East, South]), (5, 1, [East]), (6, 2, [West, North]), (7, 2, [West, South]), (8, 1, [West])], [(0, 1, [West]), (1, 2, [West, North]), (2, 2, [West, South]), (4, 1, [North]), (5, 1, [South]), (6, 1, [East]), (7, 2, [East, North]), (8, 2, [East, South])], [(0, 2, [West, South]), (1, 1, [West]), (2, 2, [West, North]), (3, 1, [South]), (5, 1, [North]), (6, 2, [East, South]), (7, 1, [East]), (8, 2, [East, North])], [(0, 2, [West, North]), (1, 2, [West, South]), (2, 1, [West]), (3, 1, [North]), (4, 1, [South]), (6, 2, [East, North]), (7, 2, [East, South]), (8, 1, [East])], [(0, 1, [East]), (1, 2, [East, North]), (2, 2, [East, South]), (3, 1, [West]), (4, 2, [West, North]), (5, 2, [West, South]), (7, 1, [North]), (8, 1, [South])], [(0, 2, [East, South]), (1, 1, [East]), (2, 2, [East, North]), (3, 2, [West, South]), (4, 1, [West]), (5, 2, [West, North]), (6, 1, [South]), (8, 1, [North])], [(0, 2, [East, North]), (1, 2, [East, South]), (2, 1, [East]), (3, 2, [West, North]), (4, 2, [West, South]), (5, 1, [West]), (6, 1, [North]), (7, 1, [South])]]
CAND4 = [[(1, 1, [North]), (2, 2, [North, North]), (3, 1, [South]), (4, 1, [East]), (5, 2, [East, North]), (6, 3, [East, North, North]), (7, 2, [East, South]), (8, 2, [East, East]), (9, 3, [East, East, North]), (10, 4, [East, East, North, North]), (11, 3, [East, East, South]), (12, 1, [West]), (13, 2, [West, North]), (14, 3, [West, North, North]), (15, 2, [West, South])], [(0, 1, [South]), (2, 1, [North]), (3, 2, [North, North]), (4, 2, [East, South]), (5, 1, [East]), (6, 2, [East, North]), (7, 3, [East, North, North]), (8, 3, [East, East, South]), (9, 2, [East, East]), (10, 3, [East, East, North]), (11, 4, [East, East, North, North]), (12, 2, [West, South]), (13, 1, [West]), (14, 2, [West, North]), (15, 3, [West, North, North])], [(0, 2, [North, North]), (1, 1, [South]), (3, 1, [North]), (4, 3, [East, North, North]), (5, 2, [East, South]), (6, 1, [East]), (7, 2, [East, North]), (8, 4, [East, East, North, North]), (9, 3, [East, East, South]), (10, 2, [East, East]), (11, 3, [East, East, North]), (12, 3, [West, North, North]), (13, 2, [West, South]), (14, 1, [West]), (15, 2, [West, North])], [(0, 1, [North]), (1, 2, [North, North]), (2, 1, [South]), (4, 2, [East, North]), (5, 3, [East, North, North]), (6, 2, [East, South]), (7, 1, [East]), (8, 3, [East, East, North]), (9, 4, [East, East, North, North]), (10, 3, [East, East, South]), (11, 2, [East, East]), (12, 2, [West, North]), (13, 3, [West, North, North]), (14, 2, [West, South]), (15, 1, [West])], [(0, 1, [West]), (1, 2, [West, North]), (2, 3, [West, North, North]), (3, 2, [West, South]), (5, 1, [North]), (6, 2, [North, North]), (7, 1, [South]), (8, 1, [East]), (9, 2, [East, North]), (10, 3, [East, North, North]), (11, 2, [East, South]), (12, 2, [East, East]), (13, 3, [East, East, North]), (14, 4, [East, East, North, North]), (15, 3, [East, East, South])], [(0, 2, [West, South]), (1, 1, [West]), (2, 2, [West, North]), (3, 3, [West, North, North]), (4, 1, [South]), (6, 1, [North]), (7, 2, [North, North]), (8, 2, [East, South]), (9, 1, [East]), (10, 2, [East, North]), (11, 3, [East, North, North]), (12, 3, [East, East, South]), (13, 2, [East, East]), (14, 3, [East, East, North]), (15, 4, [East, East, North, North])], [(0, 3, [West, North, North]), (1, 2, [West, South]), (2, 1, [West]), (3, 2, [West, North]), (4, 2, [North, North]), (5, 1, [South]), (7, 1, [North]), (8, 3, [East, North, North]), (9, 2, [East, South]), (10, 1, [East]), (11, 2, [East, North]), (12, 4, [East, East, North, North]), (13, 3, [East, East, South]), (14, 2, [East, East]), (15, 3, [East, East, North])], [(0, 2, [West, North]), (1, 3, [West, North, North]), (2, 2, [West, South]), (3, 1, [West]), (4, 1, [North]), (5, 2, [North, North]), (6, 1, [South]), (8, 2, [East, North]), (9, 3, [East, North, North]), (10, 2, [East, South]), (11, 1, [East]), (12, 3, [East, East, North]), (13, 4, [East, East, North, North]), (14, 3, [East, East, South]), (15, 2, [East, East])], [(0, 2, [East, East]), (1, 3, [East, East, North]), (2, 4, [East, East, North, North]), (3, 3, [East, East, South]), (4, 1, [West]), (5, 2, [West, North]), (6, 3, [West, North, North]), (7, 2, [West, South]), (9, 1, [North]), (10, 2, [North, North]), (11, 1, [South]), (12, 1, [East]), (13, 2, [East, North]), (14, 3, [East, North, North]), (15, 2, [East, South])], [(0, 3, [East, East, South]), (1, 2, [East, East]), (2, 3, [East, East, North]), (3, 4, [East, East, North, North]), (4, 2, [West, South]), (5, 1, [West]), (6, 2, [West, North]), (7, 3, [West, North, North]), (8, 1, [South]), (10, 1, [North]), (11, 2, [North, North]), (12, 2, [East, South]), (13, 1, [East]), (14, 2, [East, North]), (15, 3, [East, North, North])], [(0, 4, [East, East, North, North]), (1, 3, [East, East, South]), (2, 2, [East, East]), (3, 3, [East, East, North]), (4, 3, [West, North, North]), (5, 2, [West, South]), (6, 1, [West]), (7, 2, [West, North]), (8, 2, [North, North]), (9, 1, [South]), (11, 1, [North]), (12, 3, [East, North, North]), (13, 2, [East, South]), (14, 1, [East]), (15, 2, [East, North])], [(0, 3, [East, East, North]), (1, 4, [East, East, North, North]), (2, 3, [East, East, South]), (3, 2, [East, East]), (4, 2, [West, North]), (5, 3, [West, North, North]), (6, 2, [West, South]), (7, 1, [West]), (8, 1, [North]), (9, 2, [North, North]), (10, 1, [South]), (12, 2, [East, North]), (13, 3, [East, North, North]), (14, 2, [East, South]), (15, 1, [East])], [(0, 1, [East]), (1, 2, [East, North]), (2, 3, [East, North, North]), (3, 2, [East, South]), (4, 2, [East, East]), (5, 3, [East, East, North]), (6, 4, [East, East, North, North]), (7, 3, [East, East, South]), (8, 1, [West]), (9, 2, [West, North]), (10, 3, [West, North, North]), (11, 2, [West, South]), (13, 1, [North]), (14, 2, [North, North]), (15, 1, [South])], [(0, 2, [East, South]), (1, 1, [East]), (2, 2, [East, North]), (3, 3, [East, North, North]), (4, 3, [East, East, South]), (5, 2, [East, East]), (6, 3, [East, East, North]), (7, 4, [East, East, North, North]), (8, 2, [West, South]), (9, 1, [West]), (10, 2, [West, North]), (11, 3, [West, North, North]), (12, 1, [South]), (14, 1, [North]), (15, 2, [North, North])], [(0, 3, [East, North, North]), (1, 2, [East, South]), (2, 1, [East]), (3, 2, [East, North]), (4, 4, [East, East, North, North]), (5, 3, [East, East, South]), (6, 2, [East, East]), (7, 3, [East, East, North]), (8, 3, [West, North, North]), (9, 2, [West, South]), (10, 1, [West]), (11, 2, [West, North]), (12, 2, [North, North]), (13, 1, [South]), (15, 1, [North])], [(0, 2, [East, North]), (1, 3, [East, North, North]), (2, 2, [East, South]), (3, 1, [East]), (4, 3, [East, East, North]), (5, 4, [East, East, North, North]), (6, 3, [East, East, South]), (7, 2, [East, East]), (8, 2, [West, North]), (9, 3, [West, North, North]), (10, 2, [West, South]), (11, 1, [West]), (12, 1, [North]), (13, 2, [North, North]), (14, 1, [South])]]
INF = 1000000
R = []
KD = []  # what stands on each cell: 0 nothing / grass, 1 carrot, 2 bush
PT = [0]


def rplant(c):
	# plant on an X cell (soil): carrot or bush, whichever is shorter; returns the ready time
	upd()
	if FLAG[0] and (FLAG[2] * RXR >= FLAG[3] or not FLAG[1]) and num_items(Items.Wood) >= CC[0] and num_items(Items.Hay) >= CC[0]:
		if plant(Entities.Carrot):
			ST[0] += 1
			KD[c] = 1
			upd()
			return get_time() + 6 * RF
	if FLAG[1]:
		if plant(Entities.Bush):
			ST[2] += 1
			KD[c] = 2
			upd()
			return get_time() + 4 * RF
	KD[c] = 0
	return get_time() + RCHK


def rtend(c, g):
	# returns True if something was harvested
	r = False
	if g:
		if num_items(Items.Hay) < HT[0]:
			while not can_harvest():
				pass
			harvest()
			R[c] = get_time() + 0.5
			return True
		R[c] = get_time() + 3
		return False
	k = KD[c]
	if k == 1 or k == 2:
		while not can_harvest():
			pass
		harvest()
		if k == 1:
			ST[0] -= 1
		else:
			ST[2] -= 1
		r = True
	elif get_ground_type() != Grounds.Soil:
		if get_entity_type() == Entities.Grass and num_items(Items.Hay) < HT[0]:
			harvest()
			r = True
		till()
	R[c] = rplant(c)
	return r


def small_farm(lay):
	n = get_world_size()
	N = n * n
	tm = 200 / (400 * 1.5 ** num_unlocked(Unlocks.Speed))
	isg = []
	for c in range(N):
		isg.append(lay[c % n][c // n] == 'G')
		R.append(0)
		KD.append(0)
	cand = CAND3
	if n == 4:
		cand = CAND4
	tl = []
	tc2 = []
	for k in range(5):
		tl.append(k * tm)
		tc2.append(k * tm * LAM)
	upd()
	cur = get_pos_x() * n + get_pos_y()
	while True:
		if rtend(cur, isg[cur]) and done():
			return
		now = get_time()
		best = None
		bc = R[cur] - now
		for q in cand[cur]:
			t = R[q[0]] - now
			d = q[1]
			if t < tl[d]:
				t = tl[d] + t * IDL
			t += tc2[d]
			if t < bc:
				bc = t
				best = q
		if best != None:
			for d in best[2]:
				move(d)
			cur = best[0]
		else:
			t = R[cur]
			while get_time() < t:
				pass


def run_farm(need):
	global NEED
	NEED = need
	n = get_world_size()
	ph = PH6
	global NSUN
	nsun = NSUN
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
		ph = PH6D
		nsun = NSUND
	NSUN = nsun
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
	if n < 6 and not tr:
		if n == 3:
			small_farm(LAYR3)
		else:
			small_farm(LAYR4)
		return
	RT.append(0)
	for c in range(n * n):
		RT.append(0)
	upd()
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
