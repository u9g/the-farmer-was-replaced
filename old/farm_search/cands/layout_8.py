# layout_8: 6x6 farms laid out on diagonals, a drone that always steps East or North to the more
# valuable neighbour, and one early burst of sunflower power.
#
# Layout: the crop of cell (x, y) follows its diagonal (x - y) % 6. East is diagonal + 1, North
# diagonal - 1, so the drone moving East/North walks across two neighbouring diagonals at will.
# A crop on a two-cell-wide band has most cells within companion reach holding other crops
# (each plant's random companion is one cell within distance 3 that must hold one given other
# crop; x5 yield when it does).
# Power: ten sunflowers on cells marked S (carrot soil); once ripe the one with most petals is cut
# (8 power with ten standing), replanted, and the next most-petalled ripe one cut, SUN_CUTS times
# in all; then the S cells go back to carrots. Power doubles the drone's speed.

LAYS = {
	'D': 'CCGTGT',
	'E': 'GGCTCT',
}
# cells (x, y) that hold the sunflowers for the power burst
SUNS = {
	'D': [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (1, 0), (2, 1), (3, 2), (4, 3)],
	'E': [(2, 0), (3, 1), (4, 2), (5, 3), (0, 4), (1, 5), (4, 0), (5, 1), (0, 2), (1, 3)],
}
SUN_CUTS = {'D': 2, 'E': 3}
GROW = {'G': 0.5, 'C': 6.0, 'T': 7.0, 'S': 7.0}
RF = 1.05
RETRY = 0.6
MEST = 1.9
CYL_F = 1.2
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
	n = 6
	N = 36
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
	cc = lc
	cyl = lc * CYL_F
	dg = LAYS[st]
	ty = []
	sd = []
	ne = []
	nn = []
	for i in range(N):
		x = i // 6
		y = i % 6
		ty.append(dg[(x - y) % 6])
		sd.append((x, y) in SUNS[st])
		ne.append(((x + 1) % 6) * 6 + y)
		nn.append(x * 6 + (y + 1) % 6)
	# what each cell holds: G grass, C carrot, T tree, S sunflower, E empty soil
	pl = []
	rt = []
	for i in range(N):
		pl.append('G')
		rt.append(0)
	cuts = 0
	sunp = {}
	pendc = 0
	vt = {'G': 0, 'C': 0, 'T': 0, 'S': 0, 'E': 0}
	while get_pos_x() != 0:
		move(East)
	while get_pos_y() != 0:
		move(North)
	i = 0
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
		dw = nw + seeds * cc - w
		dh = nh + seeds * cc - h
		now = get_time()
		t = ty[i]
		p = pl[i]
		sun_on = cuts < SUN_CUTS[st] and sd[i] and (len(sunp) > 0 or c >= SUN_START)
		# ---- tend this cell
		if p == 'G':
			if t == 'G':
				if dh > 0 and can_harvest():
					harvest()
					rt[i] = now + 0.5
			elif t == 'T':
				if dh > 0 and can_harvest():
					harvest()
				plant(Entities.Tree)
				pl[i] = 'T'
				rt[i] = now + GROW['T'] * RF
			else:
				if dh > 0 and can_harvest():
					harvest()
					rt[i] = now + 0.5
				if sun_on and c >= 1 and len(sunp) < 10:
					till()
					plant(Entities.Sunflower)
					sunp[i] = measure()
					pl[i] = 'S'
					rt[i] = now + GROW['S'] * RF
				elif left > 0 and w >= cc and h >= cc:
					till()
					plant(Entities.Carrot)
					pendc += cyl
					pl[i] = 'C'
					rt[i] = now + GROW['C'] * RF
		elif p == 'T':
			if dw > 0:
				if can_harvest():
					harvest()
					plant(Entities.Tree)
					rt[i] = now + GROW['T'] * RF
				else:
					rt[i] = now + RETRY
		elif p == 'C' or p == 'E':
			ok = True
			if p == 'C':
				if can_harvest():
					harvest()
					pendc -= cyl
					pl[i] = 'E'
				else:
					ok = False
					rt[i] = now + RETRY
			if ok:
				if sun_on and len(sunp) < 10:
					if num_items(Items.Carrot) >= 1 and plant(Entities.Sunflower):
						sunp[i] = measure()
						pl[i] = 'S'
						rt[i] = now + GROW['S'] * RF
					else:
						rt[i] = now + RETRY
				elif left > 0 and plant(Entities.Carrot):
					pendc += cyl
					pl[i] = 'C'
					rt[i] = now + GROW['C'] * RF
				else:
					rt[i] = now + RETRY
		elif p == 'S':
			if cuts >= SUN_CUTS[st]:
				# the burst is over: back to carrots
				harvest()
				sunp.pop(i)
				pl[i] = 'E'
				if left > 0 and plant(Entities.Carrot):
					pendc += cyl
					pl[i] = 'C'
					rt[i] = now + GROW['C'] * RF
		# ---- the power burst: once ten sunflowers stand and the best is ripe, cut best ones
		if cuts < SUN_CUTS[st] and len(sunp) >= 10:
			while cuts < SUN_CUTS[st]:
				bi = -1
				bp = 0
				for q in sunp:
					if sunp[q] > bp:
						bp = sunp[q]
						bi = q
				if rt[bi] > get_time():
					break
				go(bi // 6, bi % 6)
				while not can_harvest():
					pass
				harvest()
				cuts += 1
				if cuts < SUN_CUTS[st]:
					plant(Entities.Sunflower)
					sunp[bi] = measure()
					rt[bi] = get_time() + GROW['S'] * RF
				else:
					sunp.pop(bi)
					pl[bi] = 'E'
					rt[bi] = 0
			i = get_pos_x() * 6 + get_pos_y()
		# ---- step to the more valuable of the East and North neighbours
		vg = 0
		if dh > 0:
			vg = lg * dh / (nh + 1 + seeds * cc)
		vw = 0
		if dw > 0:
			vw = 5 * lt * dw / (nw + 1 + seeds * cc) / 2
		vc = 0
		if nc > c:
			vc = lc * (nc - c) / (nc + 1) / 2
		vt['G'] = vg
		vt['T'] = vw
		vt['C'] = vc
		vt['E'] = vc * PV
		vt['S'] = vc * PV
		now = get_time()
		a = ne[i]
		b = nn[i]
		va = 0
		vb = 0
		if now >= rt[a]:
			va = vt[pl[a]]
			if pl[a] == 'G' and ty[a] != 'G':
				va = vg + vt[ty[a]] * PV
		if now >= rt[b]:
			vb = vt[pl[b]]
			if pl[b] == 'G' and ty[b] != 'G':
				vb = vg + vt[ty[b]] * PV
		if vb > va or (vb == va and rt[b] < rt[a]):
			move(North)
			i = b
		else:
			move(East)
			i = a


PV = 0.8
SUN_START = 10


def go(tx, ty):
	dx = (tx - get_pos_x()) % 6
	if dx <= 3:
		for _ in range(dx):
			move(East)
	else:
		for _ in range(6 - dx):
			move(West)
	dy = (ty - get_pos_y()) % 6
	if dy <= 3:
		for _ in range(dy):
			move(North)
	else:
		for _ in range(6 - dy):
			move(South)
