# layout_3: per-state layout, demand-aware harvesting on one torus walk, sunflower power.
# G grass, B bush, T tree, C carrot, S sunflower.  Rows are listed top (y = n-1) to bottom.

LAY = {
	'A': ['CCC', 'BBB', 'GGG'],
	'B': ['BCBC', 'CGCG', 'BCBC', 'CGCG'],
	'C': ['TBTB', 'BTBT', 'TBTB', 'BTBT'],
	'D': ['TCGCSC', 'CGCTSG', 'GCTCSC', 'CTCGSG', 'TCGCSC', 'CGCTSG'],
	'E': ['TGCGSG', 'GTGCSC', 'CGTGSG', 'GCGTSG', 'TGCGSG', 'GTGCSC'],
}
MEST = 1.9
WLO = 0.2
WATER = {'A': False, 'B': False, 'C': True, 'D': False, 'E': False}
PW_LO = 4
DBG = False


def state():
	n = get_world_size()
	if n == 3:
		return 'A'
	if n == 4:
		if num_unlocked(Unlocks.Trees) > 0:
			return 'C'
		return 'B'
	if num_unlocked(Unlocks.Fertilizer) > 0:
		return 'E'
	return 'D'


def run_farm(need):
	n = get_world_size()
	st = state()
	L = LAY[st]
	use_w = WATER[st]
	# the type of every cell, in the order the torus walk visits them from (0, 0)
	seq = []
	x = 0
	y = 0
	for k in range(n * n):
		seq.append(L[n - 1 - y][x])
		if (k + 1) % n == 0:
			x = (x + 1) % n
		else:
			y = (y + 1) % n
	go(0, 0, n)
	nw = 0
	nh = 0
	nc = 0
	if Items.Wood in need:
		nw = need[Items.Wood]
	if Items.Hay in need:
		nh = need[Items.Hay]
	if Items.Carrot in need:
		nc = need[Items.Carrot]
	lc = 2 ** (num_unlocked(Unlocks.Carrots) - 1)
	ccost = lc
	cy = lc * MEST
	pendc = 0
	sun = {}
	nsun = 0
	for ch in seq:
		if ch == 'S':
			nsun += 1
	k = 0
	N = n * n
	while True:
		w = num_items(Items.Wood)
		h = num_items(Items.Hay)
		c = num_items(Items.Carrot)
		if w >= nw and h >= nh and c >= nc:
			return
		left = nc - c - pendc
		seeds = 0
		if left > 0:
			seeds = (left + cy - 1) // cy
		needw = nw + seeds * ccost > w
		needh = nh + seeds * ccost > h
		t = seq[k % N]
		e = get_entity_type()
		if t == 'G':
			if needh and can_harvest():
				harvest()
		elif t == 'T' or t == 'B':
			ent = Entities.Bush
			if t == 'T':
				ent = Entities.Tree
			if e == ent:
				if needw and can_harvest():
					harvest()
					plant(ent)
					if use_w and get_water() < WLO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
			else:
				if needh and can_harvest():
					harvest()
				plant(ent)
				if use_w and get_water() < WLO and num_items(Items.Water) >= 1:
					use_item(Items.Water)
		elif t == 'C':
			if e == Entities.Carrot:
				if can_harvest():
					harvest()
					pendc -= cy
					if left > 0 and plant(Entities.Carrot):
						pendc += cy
			elif e == None:
				if left > 0 and plant(Entities.Carrot):
					pendc += cy
			else:
				if needh and can_harvest():
					harvest()
				if left > 0 and w >= ccost and h >= ccost:
					till()
					if plant(Entities.Carrot):
						pendc += cy
		elif t == 'S':
			pos = (get_pos_x(), get_pos_y())
			if e == Entities.Sunflower:
				if len(sun) >= 10 and num_items(Items.Power) < PW_LO and can_harvest():
					m = 0
					for q in sun:
						if sun[q] > m:
							m = sun[q]
					if sun[pos] >= m:
						harvest()
						if plant(Entities.Sunflower):
							sun[pos] = measure()
						else:
							sun.pop(pos)
			elif c >= 1 and (left > 20 or nh > h):
				if e != Entities.Carrot and e != None:
					if needh and can_harvest():
						harvest()
					till()
				if plant(Entities.Sunflower):
					sun[pos] = measure()
			elif e == Entities.Grass and needh and can_harvest():
				harvest()
		k += 1
		if DBG and k % N == 0:
			quick_print(get_time(), w, h, c, pendc, num_items(Items.Power))
		if k % n == 0:
			move(East)
		else:
			move(North)


def go(tx, ty, n):
	while get_pos_x() != tx:
		move(East)
	while get_pos_y() != ty:
		move(North)
