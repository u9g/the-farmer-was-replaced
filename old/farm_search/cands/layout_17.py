# layout_17: 3x3 farm (state A) walked row by row: the three rows are all next to each other on
# the torus, so after each row (three cells, three moves) the drone picks the row with the most
# ripe, still-needed crops by their planting times (or waits for the first to ripen).
# Other states: layout_16.

ROWS_A = ['CCB', 'BCG', 'BCB']
GA = {'G': 0.5, 'B': 4.0, 'C': 6.0}
RFA = 1.0
VA = {'G': 1, 'B': 3, 'C': 3, 'P': 2}
MESTA = 1.4


def run_A(need):
	n = 3
	nw = 0
	nc = 0
	nh = 0
	if Items.Wood in need:
		nw = need[Items.Wood]
	if Items.Carrot in need:
		nc = need[Items.Carrot]
	if Items.Hay in need:
		nh = need[Items.Hay]
	ty = []
	for i in range(9):
		ty.append(ROWS_A[2 - i % 3][i // 3])
	# rt: when the crop on the cell is (likely) ripe; pl: what stands there
	rt = []
	pl = []
	for i in range(9):
		rt.append(0)
		pl.append('G')
	pendc = 0
	while get_pos_x() != 0:
		move(East)
	while get_pos_y() != 0:
		move(North)
	while True:
		y = get_pos_y()
		# ---- the row: three cells
		for s in range(3):
			w = num_items(Items.Wood)
			h = num_items(Items.Hay)
			c = num_items(Items.Carrot)
			if w >= nw and h >= nh and c >= nc:
				return
			left = nc - c - pendc
			seeds = 0
			if left > 0:
				seeds = (left + MESTA - 1) // MESTA
			needw = nw + seeds > w
			needh = nh + seeds > h
			i = get_pos_x() * 3 + y
			t = ty[i]
			p = pl[i]
			now = get_time()
			if now >= rt[i]:
				if t == 'G':
					if needh and can_harvest():
						harvest()
					rt[i] = now + 0.5
				elif t == 'B':
					if p == 'B':
						if can_harvest():
							if needw:
								harvest()
								plant(Entities.Bush)
								rt[i] = get_time() + GA['B'] * RFA
							else:
								rt[i] = now + 1
						else:
							rt[i] = now + 0.25
					else:
						if needh and can_harvest():
							harvest()
						plant(Entities.Bush)
						pl[i] = 'B'
						rt[i] = get_time() + GA['B'] * RFA
				else:
					ok = True
					if p == 'C':
						if can_harvest():
							harvest()
							pendc -= MESTA
							pl[i] = 'E'
						else:
							ok = False
							rt[i] = now + 0.25
					elif p == 'B':
						if can_harvest():
							harvest()
							pl[i] = 'G'
						else:
							ok = False
							rt[i] = now + 0.25
					if ok:
						rt[i] = now + 0.5
						if left > 0 and num_items(Items.Wood) >= 1 and num_items(Items.Hay) >= 1:
							if pl[i] == 'G':
								if needh and can_harvest():
									harvest()
								till()
							plant(Entities.Carrot)
							pendc += MESTA
							pl[i] = 'C'
							rt[i] = get_time() + GA['C'] * RFA
						elif pl[i] == 'G' and num_items(Items.Wood) < 1:
							# no wood for a carrot yet: a bush meanwhile
							if needh and can_harvest():
								harvest()
							plant(Entities.Bush)
							pl[i] = 'B'
							rt[i] = get_time() + GA['B'] * RFA
			if s < 2:
				move(East)
		# ---- next row
		now = get_time()
		w = num_items(Items.Wood)
		h = num_items(Items.Hay)
		c = num_items(Items.Carrot)
		vb = 0
		if w < nw + nc - c:
			vb = VA['B']
		vc = 0
		if c < nc:
			vc = VA['C']
		vg = 0
		if h < nh + nc - c:
			vg = VA['G']
		val = {'G': vg, 'B': vb, 'C': vc, 'E': vc, 'P': 0}
		best = -1
		bv = 0
		soon = now + 1.1
		sr = 0
		for r in range(3):
			v = 0
			# the row is entered at the column the drone stands on, then walked East
			for k in range(3):
				j = k * 3 + r
				q = pl[j]
				if q == 'G' and ty[j] != 'G':
					q = 'P'
				vq = val[q]
				if q == 'P':
					vq = 2
				if vq > 0:
					if rt[j] <= now + 0.5:
						v += vq
					elif rt[j] < soon:
						soon = rt[j]
						sr = r
			if r == y:
				v -= 1
			if v > bv:
				bv = v
				best = r
		if best < 0:
			best = sr
			# nothing ripe: wait for the first crop that ripens
			while get_time() < soon - 0.6:
				pass
		dy = (best - y) % 3
		if dy == 1:
			move(North)
		elif dy == 2:
			move(South)
		else:
			move(East)


# layout_16 (layout_15 + small farms wait at a crop that is nearly ripe):
# layout_15: the best layout per state so far, in one file.
# 3x3 and 4x4 farms (states A, B, C): a fixed crop per cell on one torus walk (layout_4's engine)
# with the layouts found by searching all / sampled arrangements in the simulator.
# 6x6 farms (D, E): diagonal bands and an early sunflower power burst (layout_14's engine).

# layout_13: 6x6 farms laid out on diagonals, a drone that steps East (diagonal + 1) or North
# (diagonal - 1), and one early burst of sunflower power.
#
# The crop of cell (x, y) follows its diagonal (x - y) % 6. The drone walks its home band (two
# neighbouring diagonals) as a staircase, E N E N ..., and steps out to the diagonals beside it
# only when the cell there (or the one after it) is wanted and, by its planting time, ripe.
# A crop on a two-wide band has most cells within companion reach holding other crops.
# Power: once carrots allow, ten sunflowers go on the band of diagonals SUN_D, SUN_D + 1 (which
# holds nothing else until then); when they are ripe the one with most petals is cut (8 power
# with ten standing) and replanted, and the next best ripe one cut, SUN_CUTS times; then that
# band gets its own crops. Power doubles the drone's speed.

LAYS = {
	# carrots on 0, 1 (home); grass 2, 3, 4; trees 5
	'D': ('CCGGGT', 0),
	# grass on 0, 1 (home); carrots 2, 4; trees 3, 5
	'E': ('GGCTCT', 0),
}
SUN_D = {'D': 3, 'E': 3}
SUN_CUTS = {'D': 2, 'E': 3}
SUN_MIN_C = 12
GROW = {'G': 0.5, 'B': 4.0, 'C': 6.0, 'T': 7.0, 'S': 7.0}
BOOT_B = {'D': 4, 'E': 6}
INIT_RT = {'D': [0, 0, 0, 0, 0, 0], 'E': [0, 0, 0, 0, 0, 2.5]}
RF = 1.1
RETRY = 0.5
CYL_F = 1.2
LO = {'D': (48, 48), 'E': (100000, 100000)}
MAXOUT = 2
LOOK2 = {'D': False, 'E': True}
WAT = {'D': True, 'E': True}
W_LO = 0.15
PW_LO = 2
DBG = False

TY = []
PL = []
RT = []
DH = 0
DW = 0
LEFT = 0
W = 0
H = 0
CC = 1
HLO = 0
WLO = 0
NOW = 0
SST = [0]
BOOTB = [0]


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


def want(o):
	# is cell o worth a visit now?
	if NOW < RT[o]:
		return False
	q = PL[o]
	if q == 'G':
		u = TY[o]
		if u == 'G':
			return DH > 0 and H < HLO
		if u == 'T':
			return DW > 0
		return (LEFT > 0 and W >= CC and H >= CC) or (BOOTB[0] > 0 and W < CC)
	if q == 'T':
		return DW > 0 and W < WLO
	if q == 'B':
		return True
	if q == 'C':
		return True
	if q == 'S':
		return SST[0] == 2
	return LEFT > 0 and W >= CC and H >= CC


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


def run6(need):
	global TY
	global PL
	global RT
	global DH
	global DW
	global LEFT
	global W
	global H
	global CC
	global HLO
	global WLO
	global NOW
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
	CC = lc
	cc = lc
	cyl = lc * CYL_F
	dg = LAYS[st][0]
	h0 = LAYS[st][1]
	HLO = LO[st][0]
	WLO = LO[st][1]
	wat = WAT[st] and num_unlocked(Unlocks.Watering) > 0
	look2 = LOOK2[st]
	boot_b = BOOT_B[st]
	BOOTB[0] = boot_b
	sun_d = SUN_D[st]
	scuts = SUN_CUTS[st]
	if num_unlocked(Unlocks.Sunflowers) == 0:
		scuts = 0
	TY = []
	dd = []
	ne = []
	nn = []
	PL = []
	RT = []
	for i in range(N):
		x = i // 6
		y = i % 6
		# diagonal relative to the home band's lower diagonal
		dd.append((x - y - h0) % 6)
		TY.append(dg[(x - y) % 6])
		ne.append(((x + 1) % 6) * 6 + y)
		nn.append(x * 6 + (y + 1) % 6)
		# what each cell holds: G grass, C carrot, T tree, E empty soil, S sunflower (or kept
		# free for one); and when it is (likely) ripe
		k = (x - y - sun_d) % 6
		if scuts > 0 and k < 2:
			PL.append('S')
			RT.append(1000000)
		else:
			PL.append('G')
			RT.append(INIT_RT[st][(x - y) % 6])
	ty = TY
	pl = PL
	rt = RT
	pendc = 0
	# sunflower state: 0 not planted, 1 planted (waiting / cutting), 2 done
	sst = 0
	SST[0] = 0
	if scuts == 0:
		sst = 2
		SST[0] = 2
	sunp = {}
	smax = -1
	cuts = 0
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
					if wat and get_water() < W_LO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
					rt[i] = now + GROW['C'] * RF / (1 + 4 * get_water())
				elif boot_b > 0 and w < cc:
					boot_b -= 1
					BOOTB[0] = boot_b
					plant(Entities.Bush)
					pl[i] = 'B'
					rt[i] = now + GROW['B'] * RF
		elif p == 'B':
			if can_harvest():
				harvest()
				pl[i] = 'G'
				rt[i] = 0
				if left > 0 and num_items(Items.Wood) >= cc and num_items(Items.Hay) >= cc:
					till()
					plant(Entities.Carrot)
					pendc += cyl
					pl[i] = 'C'
					if wat and get_water() < W_LO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
					rt[i] = now + GROW['C'] * RF / (1 + 4 * get_water())
			else:
				rt[i] = now + RETRY
		elif p == 'T':
			if dw > 0:
				if can_harvest():
					harvest()
					plant(Entities.Tree)
					rt[i] = now + GROW['T'] * RF / (1 + 4 * get_water())
				else:
					rt[i] = now + RETRY
		elif p == 'S':
			if sst == 2:
				# the burst is over: this cell gets its own crop
				if get_entity_type() != None:
					harvest()
				if t == 'G':
					till()
					pl[i] = 'G'
					rt[i] = now + 0.5
				elif t == 'T':
					plant(Entities.Tree)
					pl[i] = 'T'
					rt[i] = now + GROW['T'] * RF / (1 + 4 * get_water())
				else:
					pl[i] = 'E'
					rt[i] = 0
					if left > 0 and plant(Entities.Carrot):
						pendc += cyl
						pl[i] = 'C'
						rt[i] = now + GROW['C'] * RF / (1 + 4 * get_water())
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
					if wat and get_water() < W_LO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
					rt[i] = now + GROW['C'] * RF / (1 + 4 * get_water())
		# ---- sunflowers: plant the band once there are carrots for it, then the burst
		if sst == 0 and num_items(Items.Carrot) >= SUN_MIN_C:
			x0 = get_pos_x()
			y0 = get_pos_y()
			# the band's lower diagonal cell in this row
			go((y0 + sun_d) % 6, y0)
			ev = True
			for k in range(12):
				j = get_pos_x() * 6 + get_pos_y()
				if len(sunp) < 10:
					if get_entity_type() == Entities.Grass and h < HLO and can_harvest():
						harvest()
					till()
					if plant(Entities.Sunflower):
						sunp[j] = measure()
						rt[j] = get_time() + GROW['S'] * RF / (1 + 4 * get_water())
				if k < 11:
					if ev:
						move(East)
					else:
						move(North)
					ev = not ev
			sst = 1
			bp = 0
			for q in sunp:
				if sunp[q] > bp or (sunp[q] == bp and rt[q] < rt[smax]):
					bp = sunp[q]
					smax = q
			i = get_pos_x() * 6 + get_pos_y()
		elif sst == 1 and get_time() >= rt[smax] and (cuts == 0 or num_items(Items.Power) < PW_LO):
			while cuts < scuts:
				go(smax // 6, smax % 6)
				while not can_harvest():
					pass
				harvest()
				cuts += 1
				if cuts < scuts:
					plant(Entities.Sunflower)
					sunp[smax] = measure()
					rt[smax] = get_time() + GROW['S'] * RF / (1 + 4 * get_water())
				else:
					sunp.pop(smax)
					pl[smax] = 'E'
					rt[smax] = 0
					sst = 2
					SST[0] = 2
					for q in sunp:
						rt[q] = 0
					break
				bp = 0
				for q in sunp:
					if sunp[q] > bp or (sunp[q] == bp and rt[q] < rt[smax]):
						bp = sunp[q]
						smax = q
				if rt[smax] > get_time():
					break
			i = get_pos_x() * 6 + get_pos_y()
		# ---- next step: East is diagonal + 1, North diagonal - 1
		d = dd[i]
		NOW = get_time()
		DH = dh
		DW = dw
		LEFT = left
		W = num_items(Items.Wood)
		H = num_items(Items.Hay)
		a = ne[i]
		b = nn[i]
		# o: the cell one step further from home; o2: the one after it
		if d == 0:
			o = b
			o2 = nn[b]
			out = True
		elif d == 1:
			o = a
			o2 = ne[a]
			out = True
		elif d <= 3:
			o = a
			o2 = ne[a]
			out = d - 1 < MAXOUT
		else:
			o = b
			o2 = nn[b]
			out = 6 - d < MAXOUT
		go_out = False
		if out:
			go_out = want(o)
			if look2 and not go_out and ((d < 2 and MAXOUT >= 2) or (d >= 2 and d <= 3 and d < MAXOUT) or (d > 3 and 7 - d < MAXOUT)):
				go_out = want(o2)
		if d == 0 or d > 3:
			go_e = not go_out
		else:
			go_e = go_out
		if go_e:
			move(East)
			i = a
		else:
			move(North)
			i = b


# ---- small farms ----

# wait at an unripe crop once WAIT_F of its mean growth time has passed
WAIT_F = {'A': 99, 'B': 0.9, 'C': 99}
WG = [1]

CFG = {
	'A': (['CCB', 'BCG', 'BCB'], ['BBB', 'BBG', 'BBB'], 1),
	'B': (['BBCC', 'GBGC', 'CBBB', 'CBCC'], ['BBBB', 'GBGB', 'BBBB', 'BBBB'], 1),
	'C': (['TGTG', 'GTGT', 'TGTG', 'GTGT'], ['TGTG', 'GTGT', 'TGTG', 'GTGT'], 0),
}
MEST = 1.9
WAT_LO = 0.2
WATER = {'A': False, 'B': False, 'C': True, 'D': False, 'E': False}
SPW_LO = 4
DBG = False


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


def run_small(need):
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
	wf = WAIT_F[st]
	pt = []
	for q in range(N):
		pt.append(-1000)
	gm = {'B': 4.0, 'T': 7.0, 'C': 6.0}
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
				if not can_harvest() and get_time() - pt[i] > wf * gm['C'] / (1 + 4 * WG[0] * get_water()):
					while not can_harvest():
						pass
				if can_harvest():
					harvest()
					pendc -= cy
					if left > 0 and plant(Entities.Carrot):
						pendc += cy
						pt[i] = get_time()
			elif t == 'S':
				if len(sun) >= 10 and num_items(Items.Power) < SPW_LO and can_harvest():
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
				if needw and not can_harvest() and get_time() - pt[i] > wf * gm[t] / (1 + 4 * WG[0] * get_water()):
					while not can_harvest():
						pass
				if needw and can_harvest():
					harvest()
					plant(want)
					pt[i] = get_time()
					if use_w and get_water() < WAT_LO and num_items(Items.Water) >= 1:
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
							pt[i] = get_time()
				elif t == 'S':
					if c >= 1 and (left > 20 or nh > h):
						if get_ground_type() != Grounds.Soil:
							till()
						if plant(Entities.Sunflower):
							sun[(get_pos_x(), get_pos_y())] = measure()
				else:
					plant(want)
					pt[i] = get_time()
					if use_w and get_water() < WAT_LO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
		k += 1
		if DBG and k % N == 0:
			quick_print(get_time(), w, h, c, pendc, num_items(Items.Power))
		if k % n == 0:
			move(East)
		else:
			move(North)


def run_farm(need):
	if get_world_size() == 3:
		run_A(need)
	elif get_world_size() <= 4:
		run_small(need)
	else:
		run6(need)
