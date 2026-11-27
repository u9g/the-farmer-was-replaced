# layout_2: a fixed layout per field size, demand-aware harvesting on one torus walk.
# Cells: G grass (harvest only when hay is still needed), B bush / T tree (wood), C carrot.

LAYOUTS = {
	3: ['CCC', 'BBB', 'GGG'],
	4: ['BCBC', 'CGCG', 'BCBC', 'CGCG'],
	6: ['TCGTCG', 'CGTCGT', 'GTCGTC', 'TCGTCG', 'CGTCGT', 'GTCGTC'],
}
LAYOUTS_T = {
	4: ['TCTC', 'CTCT', 'TCTC', 'CTCT'],
}
MEST = 2.0

DBG = True


def run_farm(need):
	n = get_world_size()
	L = LAYOUTS[n]
	if num_unlocked(Unlocks.Trees) > 0 and n in LAYOUTS_T:
		L = LAYOUTS_T[n]
	if num_unlocked(Unlocks.Trees) == 0:
		rows = []
		for r in L:
			s = ''
			for ch in r:
				if ch == 'T':
					s = s + 'B'
				else:
					s = s + ch
			rows.append(s)
		L = rows
	typ = {}
	for y in range(n):
		for x in range(n):
			typ[(x, y)] = L[n - 1 - y][x]
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
	k = 0
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
		t = typ[(get_pos_x(), get_pos_y())]
		e = get_entity_type()
		if t == 'G':
			if needh:
				if e == Entities.Grass:
					if can_harvest():
						harvest()
				elif e == None or can_harvest():
					harvest()
					if get_ground_type() == Grounds.Soil:
						till()
		elif t == 'B' or t == 'T':
			ent = Entities.Bush
			if t == 'T':
				ent = Entities.Tree
			if e == ent:
				if needw and can_harvest():
					harvest()
					plant(ent)
			else:
				if e == Entities.Grass and can_harvest() and needh:
					harvest()
				plant(ent)
		else:
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
				if left > 0 and w >= ccost and h >= ccost:
					if e == Entities.Grass and can_harvest():
						harvest()
					till()
					if plant(Entities.Carrot):
						pendc += cy
		k += 1
		if DBG and k % (n * n) == 0:
			quick_print(get_time(), w, h, c, pendc)
		if k % n == 0:
			move(East)
		else:
			move(North)
