# econ_2: per-state phased layouts, serpentine passes, demand-driven roles with fallbacks,
# minimal sunflower power (10+ sunflowers, cut only the max when power is low), water on plants.

G = 0
T = 1
C = 2
S = 3
B = 4

# phases: list of (passes, layout rows); the last phase repeats
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
		(1, [
			[S, T, G, T, G, T],
			[S, G, T, G, T, G],
			[S, T, G, T, G, T],
			[S, G, T, G, T, G],
			[S, T, G, T, G, T],
			[S, S, S, S, S, G],
		]),
		(99999, [
			[S, C, T, C, G, C],
			[S, G, C, G, C, G],
			[S, C, G, C, T, C],
			[S, G, C, G, C, G],
			[S, C, T, C, G, C],
			[S, S, S, S, S, G],
		]),
	],
	'E': [
		(1, [
			[S, T, G, T, G, T],
			[S, G, T, G, T, G],
			[S, T, G, T, G, T],
			[S, G, T, G, T, G],
			[S, T, G, T, G, T],
			[S, S, S, S, S, G],
		]),
		(99999, [
			[S, C, G, T, G, C],
			[S, G, C, G, C, G],
			[S, T, G, C, G, T],
			[S, G, C, G, C, G],
			[S, C, G, T, G, C],
			[S, S, S, S, S, G],
		]),
	],
}
M_EST = 1.5
PW_LO = 3
WATER_ON = [T, C, S]
WET_LO = 0.1
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
	sun = num_unlocked(Unlocks.Sunflowers) > 0
	ty = 5 * lv(Unlocks.Trees)
	by = lv(Unlocks.Trees)
	cy = lv(Unlocks.Carrots)
	ent = {T: Entities.Tree, B: Entities.Bush, C: Entities.Carrot, S: Entities.Sunflower}
	yld = {T: ty, B: by, C: cy, S: 0}
	if not trees:
		ent[T] = Entities.Bush
		yld[T] = by
	phases = CFG[state_key(need)]
	ph = 0
	left = phases[0][0]
	lay = phases[0][1]
	sf = {}
	pc = 0
	pw = 0
	x = 0
	y = 0
	dy = 1
	cells = n * n
	k = 0
	while True:
		r = lay[y][x]
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
		pos = (x, y)
		if r == S:
			if not sun:
				r = G
			elif e == Entities.Sunflower:
				if num_items(Items.Power) < PW_LO and len(sf) >= 10 and can_harvest():
					m = 0
					for q in sf:
						if sf[q] > m:
							m = sf[q]
					if sf[pos] >= m:
						harvest()
						sf.pop(pos)
						e = None
			elif e != None and e != Entities.Grass:
				if can_harvest():
					harvest()
					if e == Entities.Carrot:
						pc -= cy
					else:
						pw -= yld[T]
					e = None
			if r == S and e != Entities.Sunflower and e != None and e != Entities.Grass:
				r = -1
			if r == S and e != Entities.Sunflower and ca >= 1:
				if e == Entities.Grass and hreq > 0 and can_harvest():
					harvest()
				if get_ground_type() != Grounds.Soil:
					till()
				if plant(Entities.Sunflower):
					sf[pos] = measure()
					if get_water() < WET_LO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
		elif r == G:
			if e == Entities.Grass:
				if hreq > 0 and can_harvest():
					harvest()
			elif e != None and e != Entities.Sunflower:
				if can_harvest():
					harvest()
					if e == Entities.Carrot:
						pc -= cy
					else:
						pw -= yld[T]
			if get_ground_type() == Grounds.Soil and get_entity_type() == None:
				till()
		elif r != -1:
			want = ent[r]
			if e == want or (e != None and e != Entities.Grass):
				if e == Entities.Sunflower:
					want = None
				elif can_harvest():
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
					if r == C:
						pc += cy
					else:
						pw += yld[r]
					if get_water() < WET_LO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
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
