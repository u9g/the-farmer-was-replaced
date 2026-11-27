# layout_4: per-state layouts (a boot layout for the first laps, then the main one), demand-aware
# harvesting on one torus walk, optional sunflower power.
# G grass, B bush, T tree, C carrot, S sunflower.  Rows are listed top (y = n-1) to bottom.

CFG = {
	'A': (['CCC', 'BBB', 'GGG'], ['BBB', 'BBB', 'GGG'], 1),
	'B': (['BCBC', 'CGCG', 'BCBC', 'CGCG'], ['BGBG', 'GBGB', 'BGBG', 'GBGB'], 1),
	'C': (['TBTB', 'BTBT', 'TBTB', 'BTBT'], ['TBTB', 'BTBT', 'TBTB', 'BTBT'], 0),
	'D': (['CGCGCG', 'TCGCGC', 'CTCTCG', 'GCGCTC', 'CCCGCT', 'GCTCCC'], ['TGTGTG', 'GTGTGT', 'TGTGTG', 'GTGTGT', 'TGTGTG', 'GTGTGT'], 1),
	'E': (['TGCGSG', 'GTGCSC', 'CGTGSG', 'GCGTSG', 'TGCGSG', 'GTGCSC'], ['TGCGSG', 'GTGCSC', 'CGTGSG', 'GCGTSG', 'TGCGSG', 'GTGCSC'], 0),
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


def walk_seq(L, n):
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
	return seq


def run_farm(need):
	n = get_world_size()
	st = state()
	cfg = CFG[st]
	main = walk_seq(cfg[0], n)
	boot = walk_seq(cfg[1], n)
	nboot = cfg[2]
	use_w = WATER[st]
	while get_pos_x() != 0:
		move(East)
	while get_pos_y() != 0:
		move(North)
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
	k = 0
	N = n * n
	seq = boot
	if nboot == 0:
		seq = main
	ENT = {'G': Entities.Grass, 'B': Entities.Bush, 'T': Entities.Tree, 'C': Entities.Carrot, 'S': Entities.Sunflower}
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
		i = k % N
		if k == nboot * N:
			seq = main
		t = seq[i]
		want = ENT[t]
		e = get_entity_type()
		if e == want:
			if t == 'G':
				if needh and can_harvest():
					harvest()
			elif t == 'C':
				if can_harvest():
					harvest()
					pendc -= cy
					if left > 0 and plant(Entities.Carrot):
						pendc += cy
			elif t == 'S':
				if len(sun) >= 10 and num_items(Items.Power) < PW_LO and can_harvest():
					pos = (get_pos_x(), get_pos_y())
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
			else:
				if needw and can_harvest():
					harvest()
					plant(want)
					if use_w and get_water() < WLO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
		else:
			# the cell holds something else (or nothing): make it the wanted type
			ok = True
			if e != None:
				if e == Entities.Grass:
					if needh and can_harvest():
						harvest()
				elif can_harvest():
					if e == Entities.Carrot:
						pendc -= cy
					harvest()
				else:
					ok = False
			if ok:
				if t == 'G':
					if get_ground_type() == Grounds.Soil:
						till()
				elif t == 'C':
					if left > 0 and w >= ccost and h >= ccost:
						if get_ground_type() != Grounds.Soil:
							till()
						if plant(Entities.Carrot):
							pendc += cy
				elif t == 'S':
					if c >= 1 and (left > 20 or nh > h):
						if get_ground_type() != Grounds.Soil:
							till()
						if plant(Entities.Sunflower):
							sun[(get_pos_x(), get_pos_y())] = measure()
				else:
					plant(want)
					if use_w and get_water() < WLO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
		k += 1
		if DBG and k % N == 0:
			quick_print(get_time(), w, h, c, pendc, num_items(Items.Power))
		if k % n == 0:
			move(East)
		else:
			move(North)
