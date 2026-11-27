# layout_12: small farms (3x3, 4x4): a fixed crop per cell, planting times kept per cell, and a
# drone that steps to a neighbour (any of four) holding a ripe crop that is still needed; when no
# neighbour has one it heads for the crop that ripens first and waits there.

LAYS = {
	'A': ['CCC', 'BBB', 'GGG'],
	'B': ['BCBC', 'CGCG', 'BCBC', 'CGCG'],
	'C': ['TBTB', 'BTBT', 'TBTB', 'BTBT'],
}
GROW = {'G': 0.5, 'B': 4.0, 'C': 6.0, 'T': 7.0}
RF = 1.0
CYL_F = 1.2
PRI = {'G': 1, 'B': 3, 'T': 3, 'C': 3, 'P': 2}
WATER_T = 0.2
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
	st = state()
	n = get_world_size()
	N = n * n
	L = LAYS[st]
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
	cc = lc
	cyl = lc * CYL_F
	wat = num_unlocked(Unlocks.Watering) > 0
	ty = []
	nb = []
	for i in range(N):
		x = i // n
		y = i % n
		ty.append(L[n - 1 - y][x])
		nb.append([(((x + 1) % n) * n + y, East), (x * n + (y + 1) % n, North), (((x - 1) % n) * n + y, West), (x * n + (y - 1) % n, South)])
	ent = {'G': Entities.Grass, 'B': Entities.Bush, 'T': Entities.Tree, 'C': Entities.Carrot}
	# rt: when the cell's crop is (likely) ripe; grass cells start ripe, others want planting
	rt = []
	for i in range(N):
		rt.append(0)
	pendc = 0
	i = get_pos_x() * n + get_pos_y()
	while True:
		w = num_items(Items.Wood)
		h = num_items(Items.Hay)
		c = num_items(Items.Carrot)
		if w >= nw and h >= nh and c >= nc:
			return
		left = nc - c - pendc
		seeds = 0
		if left > 0:
			seeds = (left + cyl - 1) // cyl
		need_w = nw + seeds * cc > w
		need_h = nh + seeds * cc > h
		need_c = nc > c
		t = ty[i]
		e = get_entity_type()
		now = get_time()
		# ---- tend
		if t == 'G':
			if e == Entities.Grass:
				if need_h and can_harvest():
					harvest()
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
					pendc -= cyl
					e = None
				else:
					rt[i] = now + 0.3
			if e != Entities.Carrot:
				if e == Entities.Grass and need_h and can_harvest():
					harvest()
				if left > 0 and num_items(Items.Wood) >= cc and num_items(Items.Hay) >= cc:
					if get_ground_type() != Grounds.Soil:
						till()
					plant(Entities.Carrot)
					pendc += cyl
					if wat and get_water() < WATER_T and num_items(Items.Water) >= 1:
						use_item(Items.Water)
					rt[i] = now + GROW['C'] * RF / (1 + 4 * get_water())
				else:
					rt[i] = now + 1
		else:
			me = ent[t]
			if e == me:
				if can_harvest():
					if need_w:
						harvest()
						plant(me)
						if wat and get_water() < WATER_T and num_items(Items.Water) >= 1:
							use_item(Items.Water)
						rt[i] = now + GROW[t] * RF / (1 + 4 * get_water())
					else:
						rt[i] = now + 1
				else:
					rt[i] = now + 0.3
			else:
				if e == Entities.Grass and need_h and can_harvest():
					harvest()
				plant(me)
				if wat and get_water() < WATER_T and num_items(Items.Water) >= 1:
					use_item(Items.Water)
				rt[i] = now + GROW[t] * RF / (1 + 4 * get_water())
		# ---- next: the best ripe neighbour, else head for what ripens first
		now = get_time()
		pg = 0
		if need_h:
			pg = PRI['G']
		pw = 0
		if need_w:
			pw = PRI['B']
		pc = 0
		if need_c or left > 0:
			pc = PRI['C']
		pv = {'G': pg, 'B': pw, 'T': pw, 'C': pc}
		bj = -1
		bv = 0
		bd = None
		for q in nb[i]:
			j = q[0]
			if rt[j] <= now:
				v = pv[ty[j]]
				if v > bv:
					bv = v
					bj = j
					bd = q[1]
		if bj >= 0:
			move(bd)
			i = bj
			continue
		# nothing ripe next door: the useful cell that ripens first
		bj = -1
		bt = 1000000
		for j in range(N):
			if j != i and pv[ty[j]] > 0 and rt[j] < bt:
				bt = rt[j]
				bj = j
		if bj < 0:
			bj = nb[i][0][0]
		go(bj // n, bj % n, n)
		i = bj
		if rt[bj] > get_time() and ty[bj] != 'G':
			t0 = rt[bj]
			while get_time() < t0:
				pass


def go(tx, ty, n):
	dx = (tx - get_pos_x()) % n
	if dx <= n // 2:
		for _ in range(dx):
			move(East)
	else:
		for _ in range(n - dx):
			move(West)
	dy = (ty - get_pos_y()) % n
	if dy <= n // 2:
		for _ in range(dy):
			move(North)
	else:
		for _ in range(n - dy):
			move(South)
