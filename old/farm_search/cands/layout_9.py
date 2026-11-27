# layout_9: 6x6 farms laid out on diagonals; the drone steps East (diagonal + 1) or North
# (diagonal - 1) by simple per-state rules, so it walks the carrot (or grass) band as a staircase
# and steps out to a side diagonal only when that crop is wanted and (by its planting time) ripe.

LAYS = {
	'D': 'CCGGGT',
	'E': 'GGCTCT',
}
GROW = {'G': 0.5, 'C': 6.0, 'T': 7.0, 'S': 7.0}
RF = 1.1
RETRY = 0.5
CYL_F = 1.2
HAY_LO = 48
WOOD_LO = 48
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
	dg = LAYS[st]
	ty = []
	dd = []
	ne = []
	nn = []
	for i in range(N):
		x = i // 6
		y = i % 6
		dd.append((x - y) % 6)
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
				rt[i] = now + GROW['T'] * RF
			else:
				if dh > 0 and can_harvest():
					harvest()
					rt[i] = now + 0.5
				if left > 0 and w >= cc and h >= cc:
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
				if left > 0 and plant(Entities.Carrot):
					pendc += cyl
					pl[i] = 'C'
					rt[i] = now + GROW['C'] * RF
				else:
					rt[i] = now + RETRY
		# ---- next step
		d = dd[i]
		now = get_time()
		a = ne[i]
		b = nn[i]
		go_e = True
		if st == 'D':
			# carrots on 0, 1; grass on 2 (and 3, 4); trees on 5
			if d == 0:
				# out to the tree (diagonal 5) if wood is short and it is ripe or unplanted
				go_e = not (w < WOOD_LO and dw > 0 and now >= rt[b])
			elif d == 1:
				go_e = h < HAY_LO and dh > 0 and now >= rt[a]
			elif d == 2:
				go_e = False
			elif d == 5:
				go_e = True
			else:
				go_e = False
		else:
			# grass on 0, 1; carrots 2, 4; trees 3, 5
			if d == 0:
				go_e = not (dw > 0 and now >= rt[b])
			elif d == 1:
				go_e = nc > c and now >= rt[a]
			elif d == 2:
				go_e = False
			elif d == 5:
				go_e = True
			else:
				go_e = False
		if go_e:
			move(East)
			i = a
		else:
			move(North)
			i = b
