# econ_5: generic per-cell worker on fixed per-state layouts walked as closed cycles, with a
# scripted sunflower opening on the 6x6 states (12 sunflowers in columns 0-1, the highest-petal
# ones watered and cut while 10+ stand: 8 power each), after which columns 0-1 farm too.

G = 0
T = 1
C = 2
S = 3
B = 4
P = 5

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
		[T, B, T, B],
		[B, T, B, T],
		[T, B, T, B],
		[B, T, B, T],
	],
	# rows are y = 0..5, columns x = 0..5; columns 0-1 are the sunflower block
	'D': [
		[S, S, C, T, C, G],
		[S, S, G, C, G, C],
		[S, S, C, G, C, T],
		[S, S, T, C, G, C],
		[S, S, C, G, C, G],
		[S, S, G, C, T, C],
	],
	'E': [
		[S, S, T, G, T, G],
		[S, S, G, C, G, T],
		[S, S, C, G, T, G],
		[S, S, G, T, G, C],
		[S, S, T, G, C, G],
		[S, S, G, C, G, T],
	],
}
# what a sunflower cell becomes once the power is in
SUN_AFTER = {'D': C, 'E': G}
M_EST = 1.5
WAIT = 1.0
WET_LO = 0.1
PW_TARGET = 24
SUN_N = 12
DBG = False
BUSH_T = 9999
WATER_ON = {T: 1, C: 1}

NH = 0
NW = 0
NC = 0
CY = 1
TY = 5
ENT = {}
YLD = {}
GRO = {}
RT = []
PC = [0]
PW = [0]
SF = {}
LAY = []
SUNR = [S]
WOODR = [T]
LACKW = [T]
LACKH = [-1]
LACK = {'A': (B, -1), 'B': (B, -1), 'C': (T, -1), 'D': (G, G), 'E': (G, G)}


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


def sf_max():
	m = 0
	for q in SF:
		if SF[q] > m:
			m = SF[q]
	return m


def plant_here(r, ci, want):
	if plant(want):
		g = GRO[r]
		if r in WATER_ON and get_water() < WET_LO and num_items(Items.Water) >= 1:
			use_item(Items.Water)
		if get_water() > 0.15:
			g = g / 2
		RT[ci] = get_time() + g
		if r == C:
			PC[0] += CY
		elif r != S:
			PW[0] += YLD[r]
		return True
	return False


def cut(e):
	harvest()
	if e == Entities.Carrot:
		PC[0] -= CY
	elif e == Entities.Tree:
		PW[0] -= TY
	elif e == Entities.Bush:
		PW[0] -= YLD[B]


def work(x, y, r):
	n = get_world_size()
	ci = y * n + x
	if r == S:
		r = SUNR[0]
	hv = num_items(Items.Hay)
	wd = num_items(Items.Wood)
	ca = num_items(Items.Carrot)
	rc = NC - ca - PC[0] * M_EST
	plantings = 0
	if rc > 0:
		plantings = rc / (CY * M_EST)
	hreq = NH + plantings * CY - hv
	wreq = NW + plantings * CY - wd - PW[0] * M_EST
	if r == B and get_time() > BUSH_T:
		r = G
	if r == T or r == B:
		if wreq <= 0:
			r = C
	if r == C:
		if rc <= 0:
			if wreq > 0:
				r = WOODR[0]
			else:
				r = G
		elif wd < CY:
			r = LACKW[0]
		elif hv < CY:
			r = LACKH[0]
		if r == G:
			r = P
	e = get_entity_type()
	if r == -1:
		return
	if r == S:
		pos = (x, y)
		if e == Entities.Sunflower:
			return
		if e != None and e != Entities.Grass:
			if not can_harvest():
				return
			cut(e)
			e = None
		if ca >= 1:
			if e == Entities.Grass and hreq > 0 and can_harvest():
				harvest()
			if get_ground_type() != Grounds.Soil:
				till()
			if plant(Entities.Sunflower):
				SF[pos] = measure()
				RT[ci] = get_time() + 7
		return
	if r == P:
		if e == Entities.Grass:
			if hreq > 0 and can_harvest():
				harvest()
			till()
		elif e == None:
			if get_ground_type() != Grounds.Soil:
				till()
		elif can_harvest():
			cut(e)
			if (x, y) in SF:
				SF.pop((x, y))
		return
	if r == G:
		if e == Entities.Grass:
			if hreq > 0 and can_harvest():
				harvest()
		elif e != None:
			if can_harvest():
				cut(e)
				if (x, y) in SF:
					SF.pop((x, y))
			if get_ground_type() == Grounds.Soil and get_entity_type() == None:
				till()
		elif get_ground_type() == Grounds.Soil:
			till()
		return
	want = ENT[r]
	if e != None and e != Entities.Grass:
		if e == want and RT[ci] - get_time() < WAIT:
			while not can_harvest():
				pass
		if not can_harvest():
			return
		cut(e)
		if (x, y) in SF:
			SF.pop((x, y))
		e = None
	if e == Entities.Grass and hreq > 0 and can_harvest():
		harvest()
	if r == C and get_ground_type() != Grounds.Soil:
		till()
	plant_here(r, ci, want)


def go(tx, ty):
	n = get_world_size()
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


def walk(path, k):
	# run k cells of the closed walk path from wherever we are on it; returns True when done
	i = 0
	m = len(path)
	while i < m:
		q = path[i]
		if q[0] == get_pos_x() and q[1] == get_pos_y():
			break
		i += 1
	if i >= m:
		go(path[0][0], path[0][1])
		i = 0
	for _ in range(k):
		q = path[i]
		work(q[0], q[1], LAY[q[1]][q[0]])
		if done():
			return True
		move(q[2])
		i = (i + 1) % m
	return False


def sun_open(main):
	# a few bushes for the first carrots, then 12 sunflowers in columns 0-1
	n = get_world_size()
	go(0, 0)
	for y in range(n):
		plant(Entities.Bush)
		RT[y * n] = get_time() + 4
		move(North)
	move(East)
	for y in range(n):
		if can_harvest():
			harvest()
		till()
		move(North)
	move(West)
	for y in range(n):
		if get_entity_type() == Entities.Bush:
			if RT[y * n] - get_time() < 2:
				while not can_harvest():
					pass
			if can_harvest():
				harvest()
		till()
		move(North)
	# carrots in column 0
	k = 0
	for y in range(n):
		if num_items(Items.Wood) >= CY and num_items(Items.Hay) >= CY and k * CY * 1 < SUN_N:
			if plant(Entities.Carrot):
				k += 1
				RT[y * n] = get_time() + 6
				if num_items(Items.Water) >= 1:
					use_item(Items.Water)
					RT[y * n] = get_time() + 3
		move(North)
	if DBG:
		quick_print("carrots planted", get_time(), k)
	# work the main block while they grow
	t_ready = 0
	for y in range(n):
		if RT[y * n] > t_ready:
			t_ready = RT[y * n]
	while get_time() < t_ready - 2:
		walk(main, 4)
	# harvest the carrots, plant sunflowers on columns 0-1
	go(0, 0)
	for y in range(n):
		e = get_entity_type()
		if e == Entities.Carrot:
			while not can_harvest():
				pass
			harvest()
		move(North)
	if DBG:
		quick_print("carrots cut", get_time(), num_items(Items.Carrot))
	plant_sun_block()
	if DBG:
		quick_print("sun planted", get_time(), len(SF), num_items(Items.Water))


def plant_sun_block():
	n = get_world_size()
	go(0, 0)
	for c in range(2):
		for y in range(n):
			yy = y
			if c == 1:
				yy = n - 1 - y
			pos = (get_pos_x(), get_pos_y())
			e = get_entity_type()
			if e != Entities.Sunflower and len(SF) < SUN_N and num_items(Items.Carrot) >= 1:
				if e != None:
					harvest()
				if get_ground_type() != Grounds.Soil:
					till()
				if plant(Entities.Sunflower):
					SF[pos] = measure()
					RT[pos[1] * n + pos[0]] = get_time() + 7
			if y < n - 1:
				if c == 0:
					move(North)
				else:
					move(South)
		if c == 0:
			move(East)
	# water the highest ones
	order = []
	for q in SF:
		order.append(q)
	w = num_items(Items.Water)
	while w >= 1 and len(order) > 0:
		bi = 0
		for j in range(len(order)):
			if SF[order[j]] > SF[order[bi]]:
				bi = j
		q = order.pop(bi)
		go(q[0], q[1])
		use_item(Items.Water)
		RT[q[1] * n + q[0]] = get_time() + 3.5
		w -= 1


def sun_boost(main):
	# cut the highest-petal sunflower while 10+ stand and power is under target
	n = get_world_size()
	while len(SF) >= 10 and num_items(Items.Power) < PW_TARGET:
		m = sf_max()
		best = None
		bt = 0
		for q in SF:
			if SF[q] == m:
				t = RT[q[1] * n + q[0]]
				if best == None or t < bt:
					best = q
					bt = t
		while get_time() < bt - 1.5:
			if walk(main, 3):
				return
		go(best[0], best[1])
		while not can_harvest():
			pass
		harvest()
		SF.pop(best)


def run_farm(need):
	global NH
	global NW
	global NC
	global CY
	global TY
	global ENT
	global YLD
	global GRO
	global RT
	global LAY
	n = get_world_size()
	if Items.Hay in need:
		NH = need[Items.Hay]
	if Items.Wood in need:
		NW = need[Items.Wood]
	if Items.Carrot in need:
		NC = need[Items.Carrot]
	trees = num_unlocked(Unlocks.Trees) > 0
	TY = 5 * lv(Unlocks.Trees)
	by = lv(Unlocks.Trees)
	CY = lv(Unlocks.Carrots)
	ENT = {T: Entities.Tree, B: Entities.Bush, C: Entities.Carrot, S: Entities.Sunflower}
	YLD = {T: TY, B: by, C: CY, S: 0}
	GRO = {T: 7.0, B: 4.0, C: 6.0, S: 7.0}
	if not trees:
		ENT[T] = Entities.Bush
		YLD[T] = by
		GRO[T] = 4.0
	key = state_key(need)
	LAY = LAYOUT[key]
	LACKW[0] = LACK[key][0]
	LACKH[0] = LACK[key][1]
	RT = []
	for i in range(n * n):
		RT.append(0)
	full = serp(0, n, n)
	if num_unlocked(Unlocks.Sunflowers) > 0 and n >= 6:
		main = serp(2, n - 2, n)
		sun_open(main)
		sun_boost(main)
		SUNR[0] = SUN_AFTER[key]
		if DBG:
			quick_print("boosted", get_time(), num_items(Items.Power))
	else:
		SUNR[0] = G
	go(0, 0)
	while True:
		if walk(full, n * n):
			return
		if DBG:
			quick_print(get_time(), num_items(Items.Hay), num_items(Items.Wood), num_items(Items.Carrot), num_items(Items.Power), PC[0], PW[0])
