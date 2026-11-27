# econ_16: one drone, fixed per-state layouts walked as closed routes (a route may repeat cells,
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
		[C, B, G],
		[B, C, B],
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
LACK = {'A': (B, -1), 'B': (B, -1), 'C': (T, -1), 'D': (P, P), 'E': (P, P)}
WATER_ON = {T: 1, C: 1}
M_EST = 1.5
PEND_M = 1.7
WAIT = 1.0
LATE = 1.5
WET_LO = 0.1
SUN_N = 12
PW_TARGET = 24
OPEN_NB = {'D': 6, 'E': 4}
DBG = False
OPEN_WKEEP = 99
PRE_STEPS = {'D': 0, 'E': 0}

N = [3]
NEED = [0, 0, 0]
CY = [1]
ENT = {}
YLD = {}
GRO = {}
RT = []
PV = []
PEND = [0, 0]
SF = {}
LAY = []
STK = ['A']
LACKW = [B]
LACKH = [-1]
HCNT = {}
GOT = [False]
WKEEP = [0]


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
	return num_items(Items.Hay) >= NEED[0] and num_items(Items.Wood) >= NEED[1] and num_items(Items.Carrot) >= NEED[2]


def clear(ci):
	# the plant on ci is gone: drop its pending yield
	v = PV[ci]
	if v > 0:
		PEND[0] -= v
	elif v < 0:
		PEND[1] += v
	PV[ci] = 0


def cut(ci):
	harvest()
	GOT[0] = True
	clear(ci)


def put(ci, r, want):
	# plant want (role r) here; returns True if planted
	if not plant(want):
		return False
	g = GRO[r]
	if r in WATER_ON and get_water() < WET_LO and num_items(Items.Water) > WKEEP[0]:
		use_item(Items.Water)
	if get_water() > 0.15:
		g = g / 2
	RT[ci] = get_time() + g
	if r == C:
		PV[ci] = -CY[0]
		PEND[1] += CY[0]
	elif r == T or r == B:
		PV[ci] = YLD[r]
		PEND[0] += YLD[r]
	return True


def crop(ci, r, want, e, hn):
	# cut the ripe plant here (waiting a moment if this cell's own crop is about to ripen), replant
	if e != None and e != Entities.Grass:
		if not can_harvest():
			if e != want:
				return
			dt = RT[ci] - get_time()
			if dt < WAIT and dt > -LATE:
				lim = get_time() + WAIT + LATE
				while not can_harvest() and get_time() < lim:
					pass
			if not can_harvest():
				return
		cut(ci)
		if ci in SF:
			SF.pop(ci)
	elif e == Entities.Grass and hn and can_harvest():
		harvest()
		GOT[0] = True
	if r == C and get_ground_type() != Grounds.Soil:
		till()
	put(ci, r, want)


def work(ci, r):
	hv = num_items(Items.Hay)
	wd = num_items(Items.Wood)
	rc = NEED[2] - num_items(Items.Carrot) - PEND[1] * PEND_M
	if rc < 0:
		rc = 0
	hn = NEED[0] - hv + rc / M_EST > 0
	wn = NEED[1] - wd - PEND[0] * PEND_M + rc / M_EST > 0
	e = get_entity_type()
	if r == K:
		if e == Entities.Bush:
			if wn and can_harvest():
				cut(ci)
				put(ci, K, Entities.Bush)
			return
		if e == None or e == Entities.Grass:
			if e == Entities.Grass and hn and can_harvest():
				harvest()
				GOT[0] = True
			put(ci, K, Entities.Bush)
			return
		r = B
	if r == T or r == B:
		if not wn:
			r = C
	if r == C:
		if rc <= 0:
			if wn:
				r = T
			else:
				r = G
		elif wd < CY[0]:
			r = LACKW[0]
		elif hv < CY[0]:
			r = LACKH[0]
	if r == G:
		if e == Entities.Grass:
			if hn and can_harvest():
				harvest()
				GOT[0] = True
			return
		if e != None:
			if not can_harvest():
				return
			cut(ci)
			if ci in SF:
				SF.pop(ci)
		if get_ground_type() == Grounds.Soil:
			till()
		return
	if r == P:
		if e == Entities.Grass:
			if hn and can_harvest():
				harvest()
				GOT[0] = True
			till()
		elif e == None:
			if get_ground_type() != Grounds.Soil:
				till()
		elif can_harvest():
			cut(ci)
			if ci in SF:
				SF.pop(ci)
		return
	if r == S or r < 0:
		return
	crop(ci, r, ENT[r], e, hn)


def go(tx, ty):
	n = N[0]
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
	n = N[0]
	cis = []
	ds = []
	for q in p:
		cis.append(q[1] * n + q[0])
		ds.append(q[2])
	return [cis, ds, p[0][0], p[0][1], 0]


def walk(rt, k):
	# k steps along route rt from its saved place; returns True when the need is met
	cis = rt[0]
	ds = rt[1]
	m = len(cis)
	i = rt[4]
	n = N[0]
	ci = cis[i]
	if get_pos_x() != ci % n or get_pos_y() != ci // n:
		go(ci % n, ci // n)
	lay = LAY
	for _ in range(k):
		ci = cis[i]
		GOT[0] = False
		work(ci, lay[ci])
		if GOT[0] and done():
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
	n = N[0]
	p = []
	if STK[0] in SUN_ROWS:
		ya = SUN_ROWS[STK[0]]
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
	n = N[0]
	blk = sblock()
	nb = OPEN_NB[STK[0]]
	for j in range(nb):
		q = blk[j]
		go(q[0], q[1])
		put(q[1] * n + q[0], B, Entities.Bush)
	for j in range(nb, len(blk)):
		q = blk[j]
		go(q[0], q[1])
		if can_harvest():
			harvest()
		till()
	k = 0
	kk = (SUN_N + CY[0] - 1) // CY[0]
	for j in range(nb):
		q = blk[j]
		go(q[0], q[1])
		ci = q[1] * n + q[0]
		if RT[ci] - get_time() < 2:
			while not can_harvest():
				pass
		if can_harvest():
			cut(ci)
		if get_ground_type() != Grounds.Soil:
			till()
		if k < kk and num_items(Items.Wood) >= CY[0] and num_items(Items.Hay) >= CY[0]:
			if put(ci, C, Entities.Carrot):
				k += 1
	if DBG:
		quick_print("carrots planted", get_time(), k)
	t_ready = 0
	for j in range(nb):
		q = blk[j]
		ci = q[1] * n + q[0]
		if RT[ci] > t_ready:
			t_ready = RT[ci]
	while get_time() < t_ready - 2:
		walk(main, 4)
	for j in range(nb):
		q = blk[j]
		ci = q[1] * n + q[0]
		go(q[0], q[1])
		if get_entity_type() == Entities.Carrot:
			while not can_harvest():
				pass
			cut(ci)
	if DBG:
		quick_print("carrots cut", get_time(), num_items(Items.Carrot))
	for j in range(len(blk) - 1, -1, -1):
		q = blk[j]
		go(q[0], q[1])
		ci = q[1] * n + q[0]
		e = get_entity_type()
		if e != Entities.Sunflower and len(SF) < SUN_N and num_items(Items.Carrot) >= 1:
			if e != None:
				harvest()
				clear(ci)
			if get_ground_type() != Grounds.Soil:
				till()
			if plant(Entities.Sunflower):
				SF[ci] = measure()
				RT[ci] = get_time() + 7
	water_suns()
	if DBG:
		quick_print("sun planted", get_time(), len(SF), num_items(Items.Water))


def water_suns():
	# water the highest unwatered sunflowers while water is in stock
	n = N[0]
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
	n = N[0]
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
	global LAY
	global RT
	global PV
	global ENT
	global YLD
	global GRO
	n = get_world_size()
	N[0] = n
	if Items.Hay in need:
		NEED[0] = need[Items.Hay]
	if Items.Wood in need:
		NEED[1] = need[Items.Wood]
	if Items.Carrot in need:
		NEED[2] = need[Items.Carrot]
	trees = num_unlocked(Unlocks.Trees) > 0
	ty = 5 * lv(Unlocks.Trees)
	by = lv(Unlocks.Trees)
	CY[0] = lv(Unlocks.Carrots)
	ENT = {T: Entities.Tree, B: Entities.Bush, C: Entities.Carrot}
	YLD = {T: ty, B: by, K: by}
	GRO = {T: 7.0, B: 4.0, C: 6.0, K: 4.0}
	if not trees:
		ENT[T] = Entities.Bush
		YLD[T] = by
		GRO[T] = 4.0
	key = state_key(need)
	STK[0] = key
	LACKW[0] = LACK[key][0]
	LACKH[0] = LACK[key][1]
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
	if num_unlocked(Unlocks.Sunflowers) > 0 and key in LAYOUT_OPEN:
		if key in SUN_ROWS:
			main = full
		else:
			main = mkroute(serp(2, n - 2, n))
		LAY = flat(LAYOUT_OPEN[key])
		WKEEP[0] = OPEN_WKEEP
		if PRE_STEPS[key] > 0:
			walk(main, PRE_STEPS[key])
		sun_open(main)
		sun_boost(main)
		WKEEP[0] = 0
		if DBG:
			quick_print("boosted", get_time(), num_items(Items.Power), num_items(Items.Hay), num_items(Items.Wood), num_items(Items.Carrot), PEND)
	LAY = flat(LAYOUT[key])
	ring = None
	if key in RING:
		ring = mkroute(ring_path(n, 1)[0:n])
		ring[1][n - 1] = East
	while True:
		if ring != None and num_items(Items.Wood) >= NEED[1] and num_items(Items.Carrot) >= NEED[2]:
			if walk(ring, n):
				return
			continue
		if walk(full, len(full[0])):
			return
		if DBG:
			quick_print(get_time(), num_items(Items.Hay), num_items(Items.Wood), num_items(Items.Carrot), num_items(Items.Power), PEND)
