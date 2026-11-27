# econ_4: generic full-field serpentine farm with per-state phased layouts, demand-driven
# roles with fallbacks, short waits at crops about to ripen, water on fresh plants.

G = 0
T = 1
C = 2
S = 3
B = 4

CFG = {
	'A': [
		(99999, [
			[C, B, G],
			[B, C, B],
			[C, B, C],
		]),
	],
	'B': [
		(99999, [
			[B, C, B, C],
			[C, B, G, B],
			[B, C, B, C],
			[G, B, C, B],
		]),
	],
	'C': [
		(99999, [
			[T, B, T, B],
			[B, T, B, T],
			[T, B, T, B],
			[B, T, B, T],
		]),
	],
	'D': [
		(99999, [
			[C, G, C, T, C, G],
			[T, C, G, C, G, C],
			[C, G, C, G, C, T],
			[G, C, T, C, G, C],
			[C, G, C, G, C, G],
			[G, C, G, C, T, C],
		]),
	],
	'E': [
		(99999, [
			[C, G, T, G, T, G],
			[G, T, G, C, G, T],
			[T, G, C, G, T, G],
			[G, T, G, T, G, C],
			[T, G, C, G, T, G],
			[G, C, G, T, G, T],
		]),
	],
}
M_EST = 1.5
WAIT = 1.0
WET_LO = 0.1
GROW = {}
DBG = False


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


def run_farm(need):
	n = get_world_size()
	nh = 0
	nw = 0
	nc = 0
	if Items.Hay in need:
		nh = need[Items.Hay]
	if Items.Wood in need:
		nw = need[Items.Wood]
	if Items.Carrot in need:
		nc = need[Items.Carrot]
	trees = num_unlocked(Unlocks.Trees) > 0
	ty = 5 * lv(Unlocks.Trees)
	by = lv(Unlocks.Trees)
	cy = lv(Unlocks.Carrots)
	ent = {T: Entities.Tree, B: Entities.Bush, C: Entities.Carrot, S: Entities.Sunflower}
	yld = {T: ty, B: by, C: cy, S: 0}
	gro = {T: 7.0, B: 4.0, C: 6.0, S: 7.0}
	if not trees:
		ent[T] = Entities.Bush
		yld[T] = by
		gro[T] = 4.0
	phases = CFG[state_key(need)]
	ph = 0
	left = phases[0][0]
	lay = phases[0][1]
	rt = []
	for i in range(n * n):
		rt.append(0)
	pc = 0
	pw = 0
	x = 0
	y = 0
	dy = 1
	k = 0
	cells = n * n
	while True:
		r = lay[y][x]
		ci = y * n + x
		hv = num_items(Items.Hay)
		wd = num_items(Items.Wood)
		ca = num_items(Items.Carrot)
		rc = nc - ca - pc * M_EST
		plantings = 0
		if rc > 0:
			plantings = rc / (cy * M_EST)
		hreq = nh + plantings * cy - hv
		wreq = nw + plantings * cy - wd - pw * M_EST
		if r == T or r == B:
			if wreq <= 0:
				r = C
		if r == C:
			if rc <= 0 or wd < cy or hv < cy:
				r = G
		e = get_entity_type()
		if r == G:
			if e == Entities.Grass:
				if hreq > 0 and can_harvest():
					harvest()
			elif e != None:
				if can_harvest():
					harvest()
					if e == Entities.Carrot:
						pc -= cy
					else:
						pw -= ty
				if get_ground_type() == Grounds.Soil and get_entity_type() == None:
					till()
			elif get_ground_type() == Grounds.Soil:
				till()
		else:
			want = ent[r]
			if e != None and e != Entities.Grass:
				if e == want and rt[ci] - get_time() < WAIT:
					while not can_harvest():
						pass
				if can_harvest():
					harvest()
					if e == Entities.Carrot:
						pc -= cy
					else:
						pw -= yld[T]
					e = None
				else:
					want = None
			if want != None:
				if e == Entities.Grass and hreq > 0 and can_harvest():
					harvest()
				if r == C and get_ground_type() != Grounds.Soil:
					till()
				if plant(want):
					g = gro[r]
					if get_water() < WET_LO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
					if get_water() > 0.15:
						g = g / 2
					rt[ci] = get_time() + g
					if r == C:
						pc += cy
					else:
						pw += yld[r]
		if num_items(Items.Hay) >= nh and num_items(Items.Wood) >= nw and num_items(Items.Carrot) >= nc:
			return
		k += 1
		if k >= cells:
			k = 0
			left -= 1
			if left <= 0 and ph < len(phases) - 1:
				ph += 1
				left = phases[ph][0]
				lay = phases[ph][1]
			if DBG:
				quick_print(get_time(), num_items(Items.Hay), num_items(Items.Wood), num_items(Items.Carrot), num_items(Items.Power), pc, pw)
		if (dy == 1 and y == n - 1) or (dy == -1 and y == 0):
			move(East)
			x = (x + 1) % n
			dy = -dy
		elif dy == 1:
			move(North)
			y += 1
		else:
			move(South)
			y -= 1
