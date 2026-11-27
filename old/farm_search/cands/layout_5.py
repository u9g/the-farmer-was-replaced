# layout_5: per-state layout, the drone always moves East or North and picks, each step, the
# neighbour with the more valuable ripe crop (by what is still needed); planting times are kept
# per cell to tell ripeness without looking.
# G grass, B bush, T tree, C carrot.  Rows are listed top (y = n-1) to bottom.

LAY = {
	'A': ['CCC', 'BBB', 'GGG'],
	'B': ['BCBC', 'CGCG', 'BCBC', 'CGCG'],
	'C': ['TBTB', 'BTBT', 'TBTB', 'BTBT'],
	'D': ['GGTCCT'],
	'E': ['GGTCCT'],
}
MEST = 1.9
GROW = {'G': 0.5, 'B': 4.0, 'T': 7.0, 'C': 6.0}
RIPE_F = 1.1
RECHECK = 0.15
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


def layout(st, n):
	L = LAY[st]
	ty = []
	for i in range(n * n):
		x = i % n
		y = i // n
		if len(L) == 1:
			ty.append(L[0][(x - y) % n])
		else:
			ty.append(L[n - 1 - y][x])
	return ty


def run_farm(need):
	n = get_world_size()
	N = n * n
	st = state()
	ty = layout(st, n)
	if num_unlocked(Unlocks.Trees) == 0:
		for i in range(N):
			if ty[i] == 'T':
				ty[i] = 'B'
	ne = []
	nn = []
	for i in range(N):
		x = i % n
		y = i // n
		ne.append((x + 1) % n + n * y)
		nn.append(x + n * ((y + 1) % n))
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
	lt = 2 ** (num_unlocked(Unlocks.Trees) - 1)
	lg = 2 ** (num_unlocked(Unlocks.Grass) - 1)
	ccost = lc
	cy = lc * MEST
	yld = {'G': lg * MEST, 'B': lt * MEST, 'T': 5 * lt * MEST, 'C': lc * MEST}
	pendc = 0
	# when each cell's crop is expected ripe (grass is ripe at the start)
	rt = []
	for i in range(N):
		rt.append(0)
	i = get_pos_x() + n * get_pos_y()
	val = {'G': 0, 'B': 0, 'T': 0, 'C': 0}
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
		dw = nw + seeds * ccost - w
		dh = nh + seeds * ccost - h
		needw = dw > 0
		needh = dh > 0
		t = ty[i]
		e = get_entity_type()
		now = get_time()
		if t == 'G':
			if e == Entities.Grass:
				if needh and can_harvest():
					harvest()
					rt[i] = now + 0.5
			elif e == None or can_harvest():
				if e != None:
					harvest()
				if get_ground_type() == Grounds.Soil:
					till()
				rt[i] = now + 0.5
		elif t == 'C':
			if e == Entities.Carrot:
				if can_harvest():
					harvest()
					pendc -= cy
					rt[i] = 1000000
					if left > 0 and plant(Entities.Carrot):
						pendc += cy
						rt[i] = now + GROW['C'] * RIPE_F
			elif e == None:
				if left > 0 and plant(Entities.Carrot):
					pendc += cy
					rt[i] = now + GROW['C'] * RIPE_F
			elif e == Entities.Grass or can_harvest():
				if needh and can_harvest():
					harvest()
				if left > 0 and w >= ccost and h >= ccost:
					till()
					if plant(Entities.Carrot):
						pendc += cy
						rt[i] = now + GROW['C'] * RIPE_F
		else:
			ent = Entities.Bush
			if t == 'T':
				ent = Entities.Tree
			if e == ent:
				if needw and can_harvest():
					harvest()
					plant(ent)
					rt[i] = now + GROW[t] * RIPE_F
			elif e == Entities.Grass or e == None or can_harvest():
				if e != None and needh and can_harvest():
					harvest()
				plant(ent)
				rt[i] = now + GROW[t] * RIPE_F
		if rt[i] <= now:
			# nothing done here (unripe, or nothing to plant): look again a little later
			rt[i] = now + GROW[t] * RECHECK
		# value of each crop type now (what is still short, per unit of need)
		vg = 0
		if needh:
			vg = dh / (nh + 1 + seeds * ccost)
		vw = 0
		if needw:
			vw = dw / (nw + 1 + seeds * ccost)
		vc = 0
		if nc > c:
			vc = (nc - c) / (nc + 1)
		val['G'] = vg * yld['G']
		val['T'] = vw * yld['T'] / 2
		val['B'] = vw * yld['B'] / 2
		val['C'] = vc * yld['C'] / 2
		now = get_time()
		a = ne[i]
		b = nn[i]
		va = 0
		vb = 0
		if now >= rt[a]:
			va = val[ty[a]]
		if now >= rt[b]:
			vb = val[ty[b]]
		if vb > va or (vb == va and rt[b] < rt[a]):
			move(North)
			i = b
		else:
			move(East)
			i = a
