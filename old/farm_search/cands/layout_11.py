# layout_11: 6x6 farms laid out on diagonals; the drone steps East (diagonal + 1) or North
# (diagonal - 1). It walks its home band (two neighbouring diagonals) as a staircase and steps
# out to the diagonals beside it only when a cell there (the next one, or the one after it) is
# wanted and, by its planting time, ripe.

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
WAT = {'D': True, 'E': True}
W_LO = 0.15
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
		return (LEFT > 0 and W >= CC and H >= CC) or (DH > 0 and H < HLO)
	if q == 'T':
		return DW > 0 and W < WLO
	if q == 'C':
		return True
	return LEFT > 0 and W >= CC and H >= CC


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
	TY = []
	dd = []
	ne = []
	nn = []
	for i in range(N):
		x = i // 6
		y = i % 6
		# diagonal relative to the home band's lower diagonal
		dd.append((x - y - h0) % 6)
		TY.append(dg[(x - y) % 6])
		ne.append(((x + 1) % 6) * 6 + y)
		nn.append(x * 6 + (y + 1) % 6)
	ty = TY
	# what each cell holds: G grass, C carrot, T tree, E empty soil; when it is (likely) ripe
	PL = []
	RT = []
	for i in range(N):
		PL.append('G')
		RT.append(0)
	pl = PL
	rt = RT
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
					if wat and get_water() < W_LO and num_items(Items.Water) >= 1:
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
					if wat and get_water() < W_LO and num_items(Items.Water) >= 1:
						use_item(Items.Water)
					rt[i] = now + GROW['C'] * RF / (1 + 4 * get_water())
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
			if not go_out and ((d < 2 and MAXOUT >= 2) or (d >= 2 and d <= 3 and d < MAXOUT) or (d > 3 and 7 - d < MAXOUT)):
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
