# econ_32: one drone, fixed per-state layouts walked as closed routes (a route may repeat cells,
# e.g. laps of a grass ring between passes over the crop rows). Each cell has a role; a role falls
# back to another when its item is no longer needed or its seed is short. Pending yields are
# tracked per cell, so the farm stops planting what is already covered.
# 6x6 states with sunflowers: a scripted opening gets 12 sunflowers up fast (bushes -> carrots ->
# sunflowers in columns 0-1, the highest-petal ones watered) and cuts the highest ones while 10+
# stand (8 power each = 240 actions at double speed), then the whole field farms.

G = 0
T = 1
C = 2
S = 3
B = 4
P = 5
K = 6

LAYOUT = {
	'A': [
		[C, B, B],
		[B, G, B],
		[C, B, C],
	],
	'B': [
		[B, C, B, C],
		[C, B, G, B],
		[B, C, B, C],
		[G, B, C, B],
	],
	'C': [
		[T, G, T, G],
		[G, T, G, T],
		[T, G, T, G],
		[G, T, G, T],
	],
	# rows are y = 0..5, columns x = 0..5
	'D': [
		[C, T, C, G, C, G],
		[G, C, G, C, T, C],
		[C, G, C, G, C, T],
		[G, C, T, C, G, C],
		[C, G, C, T, C, G],
		[T, C, G, C, G, C],
	],
	'E': [
		[G, G, G, G, G, G],
		[T, C, K, T, C, K],
		[K, T, C, K, T, C],
		[C, K, T, C, K, T],
		[T, C, K, T, C, K],
		[K, T, C, K, T, C],
	],
}
# the main block (columns 2-5) while the sunflowers are set up in columns 0-1
LAYOUT_OPEN = {
	'D': [
		[S, S, C, T, C, T],
		[S, S, T, C, T, C],
		[S, S, C, T, C, T],
		[S, S, T, C, T, C],
		[S, S, C, T, C, T],
		[S, S, T, C, T, C],
	],
	'E': [
		[G, G, G, G, G, G],
		[T, C, K, T, C, K],
		[K, T, C, K, T, C],
		[S, S, S, S, S, S],
		[S, S, S, S, S, S],
		[K, T, C, K, T, C],
	],
}
# laps of the row-0 grass ring per pass over the other rows (states not listed: plain serpentine)
RING = {'E': 6}
# sunflower block: rows y, y+1 (states not listed: columns 0-1)
SUN_ROWS = {'E': 3}
# what a carrot cell does when wood / hay is short
LACK = {'A': (B, G), 'B': (B, -1), 'C': (T, -1), 'D': (P, P), 'E': (P, P)}
WATER_ON = {T: 1, C: 1}
M_EST = 1.5
PEND_M = 1.7
WAIT = 1.0
LATE = 1.5
WET_LO = 0.1
SUN_N = 12
# a sunflower with this many petals gets water as soon as it is planted
SUN_WP = 14
PW_TARGET = 24
OPEN_NB = {'D': 6, 'E': 4}
# the sunflower block's cells (in block order) at the start: bushes feed the first carrots,
# trees stand until the sunflowers go in (their wood seeds the farm), -1: till for later
OPEN_PAT = {'D': [B, B, B, B, B, B, -1, T, -1, T, -1, T], 'E': [B, B, B, B, B, -1, -1, -1, -1, -1, -1, -1]}
DBG = False
OPEN_WKEEP = 99
PRE_STEPS = {'D': 0, 'E': 0}

NN = 3
NH = 0
NW = 0
NC = 0
CYV = 1
PDW = 0
PDC = 0
GOTF = False
WKV = 0
LKW = 4
LKH = -1
SKEY = 'A'
SUNST = False
WATC = True
WATR = [False, True, True, False, False, False, False, False]
ENT = {}
YLD = {}
GRO = {}
RT = []
PV = []
SF = {}
LAY = []
HCNT = {}


def lv(u):
	k = num_unlocked(u)
	if k <= 1:
		return 1
	return 2 ** (k - 1)


def state_key(need):
	n = get_world_size()
	if n <= 3:
		return 'A'
	if n == 4:
		if num_unlocked(Unlocks.Trees) > 0:
			return 'C'
		return 'B'
	if Items.Hay in need:
		return 'E'
	return 'D'


def done():
	return num_items(Items.Hay) >= NH and num_items(Items.Wood) >= NW and num_items(Items.Carrot) >= NC


def clear(ci):
	global PDW
	global PDC
	# the plant on ci is gone: drop its pending yield
	v = PV[ci]
	if v > 0:
		PDW -= v
	elif v < 0:
		PDC += v
	PV[ci] = 0


def cut(ci):
	global GOTF
	harvest()
	GOTF = True
	clear(ci)


def put(ci, r, want):
	global PDW
	global PDC
	# plant want (role r) here; returns True if planted
	if not plant(want):
		return False
	g = GRO[r]
	if WATR[r] and num_items(Items.Water) > WKV and get_water() < WET_LO:
		use_item(Items.Water)
		g = g / 2
	elif WATR[r] and get_water() > 0.15:
		g = g / 2
	RT[ci] = get_time() + g
	if r == C:
		PV[ci] = -CYV
		PDC += CYV
	elif r == T or r == B:
		v = YLD[r]
		PV[ci] = v
		PDW += v
	return True


def ripe(ci):
	# can_harvest(), waiting a moment if this cell's crop is about to ripen
	if can_harvest():
		return True
	dt = RT[ci] - get_time()
	if dt < WAIT and dt > -LATE:
		lim = get_time() + WAIT + LATE
		while not can_harvest() and get_time() < lim:
			pass
		return can_harvest()
	return False


def work(ci, r):
	global GOTF
	e = get_entity_type()
	if r == G:
		if e == Entities.Grass:
			if can_harvest():
				rc = NC - num_items(Items.Carrot) - PDC * PEND_M
				if rc < 0:
					rc = 0
				if NH - num_items(Items.Hay) + rc / M_EST > 0:
					harvest()
					GOTF = True
			return
		if e != None:
			if not can_harvest():
				return
			cut(ci)
			if SUNST and ci in SF:
				SF.pop(ci)
		if get_ground_type() == Grounds.Soil:
			till()
		return
	hv = num_items(Items.Hay)
	wd = num_items(Items.Wood)
	rc = NC - num_items(Items.Carrot) - PDC * PEND_M
	if rc < 0:
		rc = 0
	wn = NW - wd - PDW * PEND_M + rc / M_EST > 0
	if r == K:
		if e == Entities.Bush:
			if wn and can_harvest():
				cut(ci)
				put(ci, K, Entities.Bush)
			return
		if e == None or e == Entities.Grass:
			if e == Entities.Grass and can_harvest() and NH - hv + rc / M_EST > 0:
				harvest()
				GOTF = True
			put(ci, K, Entities.Bush)
			return
		r = B
	elif r == T or r == B:
		if not wn:
			r = C
	if r == C:
		if rc <= 0:
			if wn:
				r = T
			else:
				r = G
		elif wd < CYV:
			r = LKW
		elif hv < CYV:
			r = LKH
		if r == G:
			work(ci, G)
			return
	if r == P:
		if e == Entities.Grass:
			if NH - hv + rc / M_EST > 0 and can_harvest():
				harvest()
				GOTF = True
			till()
		elif e == None:
			if get_ground_type() != Grounds.Soil:
				till()
		elif can_harvest():
			cut(ci)
			if SUNST and ci in SF:
				SF.pop(ci)
		return
	if r == S or r < 0:
		return
	want = ENT[r]
	if e != None and e != Entities.Grass:
		if e == want:
			if not ripe(ci):
				return
		elif not can_harvest():
			return
		cut(ci)
		if SUNST and ci in SF:
			SF.pop(ci)
	elif e == Entities.Grass and NH - hv + rc / M_EST > 0 and can_harvest():
		harvest()
		GOTF = True
	if r == C and get_ground_type() != Grounds.Soil:
		till()
	put(ci, r, want)


def go(tx, ty):
	n = NN
	h = n // 2
	dx = (tx - get_pos_x()) % n
	if dx > 0:
		if dx <= h:
			for _ in range(dx):
				move(East)
		else:
			for _ in range(n - dx):
				move(West)
	dy = (ty - get_pos_y()) % n
	if dy > 0:
		if dy <= h:
			for _ in range(dy):
				move(North)
		else:
			for _ in range(n - dy):
				move(South)


def serp(x0, w, n):
	# closed walk over columns x0..x0+w-1 (all rows); returns [(x, y, dir)]
	p = []
	if w == n:
		x = 0
		y = 0
		for i in range(n * n):
			if i % n == n - 1:
				p.append((x, y, East))
				x = (x + 1) % n
			else:
				p.append((x, y, North))
				y = (y + 1) % n
		return p
	for y in range(n - 1):
		p.append((x0, y, North))
	p.append((x0, n - 1, East))
	for c in range(1, w):
		xx = x0 + c
		if c % 2 == 1:
			for y in range(n - 1, 1, -1):
				p.append((xx, y, South))
			if c == w - 1:
				p.append((xx, 1, South))
			else:
				p.append((xx, 1, East))
		else:
			for y in range(1, n - 1):
				p.append((xx, y, North))
			p.append((xx, n - 1, East))
	for c in range(w - 1, 0, -1):
		p.append((x0 + c, 0, West))
	return p


def ring_path(n, laps):
	# laps of row 0 (east), then a serpentine over rows 1..n-1 back to row 0
	p = []
	for l in range(laps):
		for x in range(n):
			p.append((x, 0, East))
	p[len(p) - 1] = (n - 1, 0, North)
	x = n - 1
	for y in range(1, n):
		for j in range(n - 1):
			if y % 2 == 1:
				p.append((x, y, West))
				x -= 1
			else:
				p.append((x, y, East))
				x += 1
		p.append((x, y, North))
	return p


def mkroute(p):
	# [(x, y, dir)] -> [ci list, dir list, x, y of the start]
	n = NN
	cis = []
	ds = []
	for q in p:
		cis.append(q[1] * n + q[0])
		ds.append(q[2])
	return [cis, ds, p[0][0], p[0][1], 0]


def wc(ci):
	# fast path for a carrot cell holding a carrot or nothing; anything else goes to work()
	global GOTF
	global PDC
	e = get_entity_type()
	if e == Entities.Carrot:
		if not ripe(ci):
			return
		harvest()
		GOTF = True
		PDC -= CYV
		PV[ci] = 0
	elif e != None:
		work(ci, C)
		return
	if NC - num_items(Items.Carrot) - PDC * PEND_M > 0 and num_items(Items.Wood) >= CYV and num_items(Items.Hay) >= CYV:
		if plant(Entities.Carrot):
			g = 6.0
			if WATC and num_items(Items.Water) > WKV and get_water() < WET_LO:
				use_item(Items.Water)
				g = 3.0
			RT[ci] = get_time() + g
			PV[ci] = -CYV
			PDC += CYV
			return
	work(ci, C)


def wt(ci, r):
	# fast path for a tree / bush cell holding its own plant
	global GOTF
	global PDW
	e = get_entity_type()
	want = ENT[r]
	if e != want:
		work(ci, r)
		return
	if not ripe(ci):
		return
	harvest()
	GOTF = True
	PDW -= PV[ci]
	PV[ci] = 0
	rc = NC - num_items(Items.Carrot) - PDC * PEND_M
	if rc < 0:
		rc = 0
	if NW - num_items(Items.Wood) - PDW * PEND_M + rc / M_EST > 0:
		put(ci, r, want)
	else:
		work(ci, r)


def walk(rt, k):
	global GOTF
	# k steps along route rt from its saved place; returns True when the need is met
	cis = rt[0]
	ds = rt[1]
	m = len(cis)
	i = rt[4]
	n = NN
	ci = cis[i]
	if get_pos_x() != ci % n or get_pos_y() != ci // n:
		go(ci % n, ci // n)
	lay = LAY
	for _ in range(k):
		ci = cis[i]
		GOTF = False
		r = lay[ci]
		if r == C:
			wc(ci)
		elif r == T or r == B:
			wt(ci, r)
		else:
			work(ci, r)
		if GOTF and done():
			rt[4] = i
			return True
		move(ds[i])
		i += 1
		if i >= m:
			i = 0
	rt[4] = i
	return False


def flat(rows):
	f = []
	for row in rows:
		for v in row:
			f.append(v)
	return f


def sblock():
	# the 12 sunflower cells as a walk (consecutive cells adjacent)
	n = NN
	p = []
	if SKEY in SUN_ROWS:
		ya = SUN_ROWS[SKEY]
		for x in range(n):
			p.append((x, ya))
		for x in range(n - 1, -1, -1):
			p.append((x, ya + 1))
	else:
		for y in range(n):
			p.append((0, y))
		for y in range(n - 1, -1, -1):
			p.append((1, y))
	return p


def sun_open(main):
	# bushes for the first carrots (planted where the bushes stood), then sunflowers on the block
	n = NN
	blk = sblock()
	pat = OPEN_PAT[SKEY]
	for j in range(len(blk)):
		q = blk[j]
		go(q[0], q[1])
		ci = q[1] * n + q[0]
		if pat[j] == B:
			put(ci, B, Entities.Bush)
		elif pat[j] == T:
			if can_harvest():
				harvest()
			put(ci, T, Entities.Tree)
		else:
			if can_harvest():
				harvest()
			till()
	k = 0
	kk = (SUN_N + CYV - 1) // CYV
	for j in range(len(blk)):
		if pat[j] != B:
			continue
		q = blk[j]
		go(q[0], q[1])
		ci = q[1] * n + q[0]
		if RT[ci] - get_time() < 2:
			while not can_harvest():
				pass
		if can_harvest():
			cut(ci)
		if get_ground_type() != Grounds.Soil:
			clear(ci)
			till()
		if k < kk and num_items(Items.Wood) >= CYV and num_items(Items.Hay) >= CYV:
			if put(ci, C, Entities.Carrot):
				k += 1
	if DBG:
		quick_print("carrots planted", get_time(), k)
	t_ready = 0
	for j in range(len(blk)):
		q = blk[j]
		ci = q[1] * n + q[0]
		if RT[ci] > t_ready:
			t_ready = RT[ci]
	while get_time() < t_ready - 2:
		walk(main, 4)
	for j in range(len(blk)):
		q = blk[j]
		go(q[0], q[1])
		ci = q[1] * n + q[0]
		e = get_entity_type()
		if e == Entities.Carrot:
			while not can_harvest():
				pass
			cut(ci)
			e = None
		if e != Entities.Sunflower and len(SF) < SUN_N and num_items(Items.Carrot) >= 1:
			if e != None:
				if e == Entities.Tree and not can_harvest():
					while not can_harvest() and RT[ci] - get_time() < 1.5:
						pass
				harvest()
				clear(ci)
			if get_ground_type() != Grounds.Soil:
				till()
			if plant(Entities.Sunflower):
				v = measure()
				SF[ci] = v
				RT[ci] = get_time() + 7
				if v >= SUN_WP and num_items(Items.Water) >= 1:
					use_item(Items.Water)
					RT[ci] = get_time() + 3.5
	water_suns()
	if DBG:
		quick_print("sun planted", get_time(), len(SF), num_items(Items.Water))


def water_suns():
	# water the highest unwatered sunflowers while water is in stock
	n = NN
	while num_items(Items.Water) >= 1:
		best = -1
		bv = -1
		for q in SF:
			if SF[q] > bv and RT[q] - get_time() > 4:
				bv = SF[q]
				best = q
		if best < 0:
			return
		go(best % n, best // n)
		use_item(Items.Water)
		RT[best] = get_time() + 3.5


def sf_max():
	m = 0
	for q in SF:
		if SF[q] > m:
			m = SF[q]
	return m


def sun_boost(main):
	# cut the highest-petal sunflower while 10+ stand and power is under target
	n = NN
	while len(SF) >= 10 and num_items(Items.Power) < PW_TARGET:
		m = sf_max()
		best = -1
		bt = 0
		for q in SF:
			if SF[q] == m:
				t = RT[q]
				if best < 0 or t < bt:
					best = q
					bt = t
		while get_time() < bt - 1.5:
			if num_items(Items.Water) >= 1 and bt - get_time() > 4:
				water_suns()
				bt = RT[best]
			if walk(main, 3):
				return
		go(best % n, best // n)
		while not can_harvest():
			pass
		harvest()
		SF.pop(best)


def run_farm(need):
	global NN
	global NH
	global NW
	global NC
	global CYV
	global PDW
	global PDC
	global WKV
	global LKW
	global LKH
	global SKEY
	global SUNST
	global LAY
	global RT
	global PV
	global ENT
	global YLD
	global GRO
	n = get_world_size()
	NN = n
	if Items.Hay in need:
		NH = need[Items.Hay]
	if Items.Wood in need:
		NW = need[Items.Wood]
	if Items.Carrot in need:
		NC = need[Items.Carrot]
	trees = num_unlocked(Unlocks.Trees) > 0
	ty = 5 * lv(Unlocks.Trees)
	by = lv(Unlocks.Trees)
	CYV = lv(Unlocks.Carrots)
	ENT = {T: Entities.Tree, B: Entities.Bush, C: Entities.Carrot}
	YLD = {T: ty, B: by, K: by}
	GRO = {T: 7.0, B: 4.0, C: 6.0, K: 4.0}
	if not trees:
		ENT[T] = Entities.Bush
		YLD[T] = by
		GRO[T] = 4.0
	key = state_key(need)
	SKEY = key
	LKW = LACK[key][0]
	LKH = LACK[key][1]
	RT = []
	PV = []
	for i in range(n * n):
		RT.append(0)
		PV.append(0)
	if key in RING:
		full = mkroute(ring_path(n, RING[key]))
		full[4] = RING[key] * n
	else:
		full = mkroute(serp(0, n, n))
	SUNST = num_unlocked(Unlocks.Sunflowers) > 0 and key in LAYOUT_OPEN
	if SUNST:
		if key in SUN_ROWS:
			main = full
		else:
			main = mkroute(serp(2, n - 2, n))
		LAY = flat(LAYOUT_OPEN[key])
		WKV = OPEN_WKEEP
		if PRE_STEPS[key] > 0:
			walk(main, PRE_STEPS[key])
		sun_open(main)
		sun_boost(main)
		WKV = 0
		if DBG:
			quick_print("boosted", get_time(), num_items(Items.Power), num_items(Items.Hay), num_items(Items.Wood), num_items(Items.Carrot), PDW, PDC)
	LAY = flat(LAYOUT[key])
	ring = None
	if key in RING:
		ring = mkroute(ring_path(n, 1)[0:n])
		ring[1][n - 1] = East
	last = -1
	while True:
		tot = min(num_items(Items.Hay), NH) + min(num_items(Items.Wood), NW) + min(num_items(Items.Carrot), NC)
		if tot <= last:
			# nothing came in for a whole pass: forget the pending yields
			PDW = 0
			PDC = 0
			for i in range(n * n):
				PV[i] = 0
		last = tot
		if ring != None and num_items(Items.Wood) >= NW and num_items(Items.Carrot) >= NC:
			if walk(ring, n):
				return
			continue
		if walk(full, len(full[0])):
			return
		if DBG:
			quick_print(get_time(), num_items(Items.Hay), num_items(Items.Wood), num_items(Items.Carrot), num_items(Items.Power), PDW, PDC)
