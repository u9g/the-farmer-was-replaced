# layout_14 (layout_13 + boot bushes, tunable ripeness for the first trees):
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
BOOT_B = {'D': 0, 'E': 6}
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


def run_farm(need):
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
