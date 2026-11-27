# layout_10: 6x6 farms laid out on diagonals; the drone steps East (diagonal + 1) or North
# (diagonal - 1). It walks its home band (two neighbouring diagonals) as a staircase and steps
# out to the diagonals beside it only when the cell there is wanted and (by its planting time)
# ripe, going further out while the next cell is wanted too.

LAYS = {
	# carrots on 0, 1 (home); grass 2, 3, 4; trees 5
	'D': ('CCGGGT', 0),
	# grass on 0, 1 (home); carrots 2, 4; trees 3, 5
	'E': ('GGCTCT', 0),
}
GROW = {'G': 0.5, 'C': 6.0, 'T': 7.0, 'S': 7.0}
RF = 1.1
RETRY = 0.5
CYL_F = 1.2
LO = {'D': (48, 48), 'E': (100000, 100000)}
MAXOUT = 2
WAT = {'D': 'C', 'E': 'C'}
W_LO = 0.15
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
	cc = lc
	cyl = lc * CYL_F
	dg = LAYS[st][0]
	h0 = LAYS[st][1]
	hay_lo = LO[st][0]
	wood_lo = LO[st][1]
	wat = WAT[st]
	ty = []
	dd = []
	ne = []
	nn = []
	for i in range(N):
		x = i // 6
		y = i % 6
		# diagonal relative to the home band's lower diagonal
		dd.append((x - y - h0) % 6)
		ty.append(dg[(x - y) % 6])
		ne.append(((x + 1) % 6) * 6 + y)
		nn.append(x * 6 + (y + 1) % 6)
	# what each cell holds: G grass, C carrot, T tree, E empty soil; when it is (likely) ripe
	pl = []
	rt = []
	for i in range(N):
		pl.append('G')
		rt.append(0)
	pendc = 0
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
				rt[i] = now + GROW['T'] * RF / (1 + 4 * get_water())
			else:
				if dh > 0 and can_harvest():
					harvest()
				rt[i] = now + RETRY
				if left > 0 and w >= cc and h >= cc:
					till()
					plant(Entities.Carrot)
					pendc += cyl
					pl[i] = 'C'
					if wat == 'C' and get_water() < W_LO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
					rt[i] = now + GROW['C'] * RF / (1 + 4 * get_water())
		elif p == 'T':
			if dw > 0:
				if can_harvest():
					harvest()
					plant(Entities.Tree)
					rt[i] = now + GROW['T'] * RF / (1 + 4 * get_water())
				else:
					rt[i] = now + RETRY
		else:
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
				rt[i] = now + RETRY
				if left > 0 and plant(Entities.Carrot):
					pendc += cyl
					pl[i] = 'C'
					if wat == 'C' and get_water() < W_LO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
					rt[i] = now + GROW['C'] * RF / (1 + 4 * get_water())
		# ---- next step: East is diagonal + 1, North diagonal - 1
		d = dd[i]
		now = get_time()
		a = ne[i]
		b = nn[i]
		if d == 0:
			o = b
		elif d == 1:
			o = a
		elif d <= 3:
			# above the band (2, 3): further out is East
			o = a
		else:
			o = b
		# is the cell `o` (one step further from home, or out of it) wanted now?
		want = False
		if d < 2 or (d <= 3 and d - 1 < MAXOUT) or (d > 3 and 6 - d < MAXOUT):
			if now >= rt[o]:
				q = pl[o]
				if q == 'G':
					u = ty[o]
					if u == 'G':
						want = dh > 0 and h < hay_lo
					elif u == 'T':
						want = dw > 0
					else:
						want = (left > 0 and w >= cc and h >= cc) or (dh > 0 and h < hay_lo)
				elif q == 'T':
					want = dw > 0 and w < wood_lo
				elif q == 'C':
					want = True
				else:
					want = left > 0 and w >= cc and h >= cc
		if d == 0:
			go_e = not want
		elif d == 1:
			go_e = want
		elif d <= 3:
			go_e = want
		else:
			go_e = not want
		if go_e:
			move(East)
			i = a
		else:
			move(North)
			i = b
