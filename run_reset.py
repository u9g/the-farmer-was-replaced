# Fastest reset: from a 1x1 farm to unlocking the leaderboard again (1M gold, 2M bone).
# Run with run_reset_lb.py (leaderboard_run(Leaderboards.Fastest_Reset, "run_reset", 256)).
#
# Opening: tight loops for the first unlocks (grass on 1x1, a 1x3 strip, then bushes for wood).
# Early game: one drone on a mixed farm, pass after pass until the next unlock is affordable.
# Every column grows the crops the next few unlocks are shortest of, always two types on the
# two checkerboard colours, since a plant next to the companion it wants gives 5x even before
# polyculture. Megafarm 1 comes before polyculture: weird substance from a checkerboard of
# weird trees, then gold from one maze. Once polyculture is bought, crops grow on one
# checkerboard colour and the other colour holds the companion each crop asks for.
# After that the script works through PLAN: for each unlock it cannot afford yet it runs a round
# for the first item it lacks, using every drone (pumpkin field watered for faster growth, cactus
# on sorted antidiagonal bands, one maze shared by all drones and mapped by drones splitting at its forks, the
# dinosaur snake), with a sunflower round whenever power runs low.

T0 = get_time()


def log(msg):
	quick_print(get_time() - T0, msg)


def width():
	if num_unlocked(Unlocks.Expand) == 1:
		return 1
	return get_world_size()


def lacking(u):
	cost = get_cost(u)
	for item in cost:
		if num_items(item) < cost[item]:
			return item
	return None


def buy(u):
	if lacking(u) == None and unlock(u):
		log(str(u) + " " + str(num_unlocked(u)))
		return True
	return False


def lvl_mult(u):
	n = num_unlocked(u)
	if n <= 1:
		return 1
	return 2 ** (n - 1)


def go(tx, ty):
	n = get_world_size()
	w = width()
	dx = (tx - get_pos_x()) % w
	if dx <= w // 2:
		for _ in range(dx):
			move(East)
	else:
		for _ in range(w - dx):
			move(West)
	dy = (ty - get_pos_y()) % n
	if dy <= n // 2:
		for _ in range(dy):
			move(North)
	else:
		for _ in range(n - dy):
			move(South)


WET_LO = 0.5
WET_N = 3


def wet():
	# top the cell up with water when it has run low and water is in stock
	if get_water() < WET_LO and num_items(Items.Water) >= WET_N:
		use_item(Items.Water, WET_N)


def soil():
	if get_ground_type() != Grounds.Soil:
		till()


def clear_cell():
	# harvest whatever stands here, so something else can be planted
	if get_entity_type() != None:
		harvest()


# ---- running a job on every drone ------------------------------------------------------------

def drones():
	return min(max_drones(), width())


def spawn_node(lo, hi, d, pack):
	# drone lo runs job for drones lo..hi-1: it hands the upper half of its range to a new drone,
	# again and again, so the drones are spawned in a tree (log2(d) spawns before any drone works)
	hs = []
	while hi - lo > 1:
		mid = (lo + hi + 1) // 2
		h = spawn_drone(spawn_node, mid, hi, d, pack)
		if h == None:
			break
		hs.append(h)
		hi = mid
	job = pack[0]
	res = [job(lo, d, pack[1], pack[2])]
	k = len(hs) - 1
	while k >= 0:
		res = res + wait_for(hs[k])
		k -= 1
	return res


def all_drones(job, a, b):
	# job(i, d, a, b) runs on drone i of d; returns the list of results
	return spawn_node(0, drones(), drones(), (job, a, b))


def my_cols(i, d):
	w = width()
	return range(i * w // d, (i + 1) * w // d)


# ---- mixed farm (hay, wood, carrots) -----------------------------------------------------------

NEED = ({}, {})
POLY = False
PEND = {Items.Hay: 0, Items.Wood: 0, Items.Carrot: 0, Items.Weird_Substance: 0}
SUN = {}


def yield_of(e):
	f = 1
	if POLY:
		f = 5 * 2 ** num_unlocked(Unlocks.Polyculture) * 0.6
	if e == Entities.Tree:
		return 5 * lvl_mult(Unlocks.Trees) * f
	if e == Entities.Bush:
		return lvl_mult(Unlocks.Trees) * f
	if e == Entities.Carrot:
		return lvl_mult(Unlocks.Carrots) * f
	return 0


def item_of(e):
	if e == Entities.Carrot:
		return Items.Carrot
	if e == Entities.Grass:
		return Items.Hay
	return Items.Wood


def short(item):
	# NEED = (current unlock's cost, the next few unlocks' cost); the current one comes first
	r = 0
	have = num_items(item) + PEND[item]
	cur = NEED[0]
	if item in cur and cur[item] > have:
		r = 10 + (cur[item] - have) / cur[item]
	look = NEED[1]
	if item in look and look[item] > have:
		r += (look[item] - have) / look[item]
	return r


def choose(even):
	best = Entities.Grass
	bs = short(Items.Hay)
	if num_unlocked(Unlocks.Plant) > 0:
		s = max(short(Items.Wood), short(Items.Weird_Substance))
		if s > bs:
			if num_unlocked(Unlocks.Trees) == 0:
				bs = s
				best = Entities.Bush
			elif even:
				bs = s
				best = Entities.Tree
	if num_unlocked(Unlocks.Carrots) > 0:
		s = short(Items.Carrot)
		if s > bs:
			c = get_cost(Entities.Carrot)
			ok = True
			for it in c:
				if num_items(it) < c[it]:
					ok = False
			if ok:
				best = Entities.Carrot
	return best


def sun_max():
	m = 0
	for k in SUN:
		if SUN[k] > m:
			m = SUN[k]
	return m


def sun_cell():
	# sunflower strip: only the highest-numbered sunflower is cut (8x power)
	pos = (get_pos_x(), get_pos_y())
	e = get_entity_type()
	if e == Entities.Sunflower and pos in SUN:
		if not can_harvest() or SUN[pos] < sun_max() or len(SUN) < 10:
			return
		harvest()
	elif e != None:
		harvest()
	soil()
	if plant(Entities.Sunflower):
		SUN[pos] = measure()
	elif pos in SUN:
		SUN.pop(pos)


def mixed_cell(strip, weird, c):
	if strip and get_pos_x() < 2:
		sun_cell()
		return
	if POLY:
		tend_mixed(c)
	else:
		tend_plain(c)
	# plus shapes centred where (x + 2y) % 5 == 0 tile the field: the west and south arms were
	# just replanted, the north and east arms are cut later in this same pass
	if weird and (get_pos_x() + 2 * get_pos_y()) % 5 == 0:
		if num_items(Items.Weird_Substance) >= 1:
			use_item(Items.Weird_Substance)
		elif num_items(Items.Fertilizer) >= 1:
			use_item(Items.Fertilizer)


def tend_plain(c):
	# no companions yet: cut what is ripe and plant this cell's crop
	e = get_entity_type()
	if e == Entities.Grass:
		if c == Entities.Grass:
			if can_harvest():
				harvest()
			if get_ground_type() == Grounds.Soil:
				till()
			return
		harvest()
	elif e != None:
		if not can_harvest():
			return
		harvest()
	if c == Entities.Grass:
		if get_ground_type() == Grounds.Soil:
			till()
		return
	if c == Entities.Carrot:
		if get_ground_type() != Grounds.Soil:
			till()
	if plant(c):
		PEND[item_of(c)] += yield_of(c)
		if (c == Entities.Tree or c == Entities.Carrot) and get_water() < WT_LO and num_items(Items.Water) >= 1:
			use_item(Items.Water)


WT_LO = 0.12
LPS = None
LP_PW = 40
# polyculture farm: a crop (not a companion cell) planted on soil below WM_LO gets one water
WM_LO = 0.25
# companion checks per planting (a failed check rerolls the plant), fewer while drones own few columns
RR_N = 2
RR_FEW = 1
RR_FEW_D = 4
WANT = {}
REQ = {}
COLS = [0, 0]


def tend_mixed(cdef):
	e = get_entity_type()
	pos = (get_pos_x(), get_pos_y())
	if e != None and e != Entities.Grass and not can_harvest():
		# a growing plant stays, unless a neighbour needs another type here as its companion
		if pos not in WANT or WANT[pos][0] == e:
			return
	if e != None:
		harvest()
	if pos in REQ:
		# this plant's companion claim ends with its harvest
		c = REQ.pop(pos)
		if c in WANT and WANT[c][1] == pos:
			WANT.pop(c)
	if pos in WANT:
		c = WANT[pos][0]
	else:
		c = cdef
	if c == Entities.Grass:
		if get_ground_type() == Grounds.Soil:
			plant(Entities.Grass)
	else:
		if c == Entities.Carrot:
			soil()
		if not plant(c):
			return
		PEND[item_of(c)] += yield_of(c)
		if pos not in WANT and get_water() < WM_LO and num_items(Items.Water) >= 1:
			use_item(Items.Water)
	if POLY and pos not in WANT:
		# claim the companion's cell (a companion planted for another plant claims none: its own
		# claim could make the farm cut a growing crop, and so on down a chain); if it is taken by
		# another type, replant for a new companion
		# (with two drones a wish often falls in the other drone's columns: one reroll, then keep it)
		k = RR_N
		if max_drones() <= RR_FEW_D:
			k = RR_FEW
		for r in range(k):
			comp = get_companion()
			if comp == None:
				return
			cp = comp[1]
			ok = cp[0] >= COLS[0] and cp[0] < COLS[1] and cp != pos
			if ok and PW_C1[0] > 0:
				n = get_world_size()
				tc = cp[0] * n + cp[1]
				if cp[0] % 2 == 1:
					tc = cp[0] * n + n - 1 - cp[1]
				ok = tc >= PW_C0[0] and tc < PW_C1[0]
			if ok:
				if cp not in WANT:
					WANT[cp] = (comp[0], pos)
					REQ[pos] = cp
					return
				# taken: the newest plant holds the cell (for its type)
				WANT[cp] = (comp[0], pos)
				REQ[pos] = cp
				return
			if r == k - 1:
				return
			harvest()
			if c != Entities.Grass or get_ground_type() == Grounds.Soil:
				if not plant(c):
					return


def tend_fm(pos, cdef):
	# tend_mixed for mixed_job's own columns, with the round's yields and reroll count cached
	e = get_entity_type()
	if e != None and e != Entities.Grass and not can_harvest():
		if pos not in WANT or WANT[pos][0] == e:
			return
	if e != None:
		harvest()
	if pos in REQ:
		c = REQ.pop(pos)
		if c in WANT and WANT[c][1] == pos:
			WANT.pop(c)
	c = cdef
	w = pos in WANT
	if w:
		c = WANT[pos][0]
	if c == Entities.Grass:
		if get_ground_type() == Grounds.Soil:
			plant(Entities.Grass)
	else:
		if c == Entities.Carrot:
			if get_ground_type() != Grounds.Soil:
				till()
		if not plant(c):
			return
		PEND[IT[c]] += YLD[c]
		if not w and get_water() < WM_LO and num_items(Items.Water) >= 1:
			use_item(Items.Water)
	if w:
		return
	k = RRK[0]
	for r in range(k):
		comp = get_companion()
		if comp == None:
			return
		cp = comp[1]
		if cp[0] >= COLS[0] and cp[0] < COLS[1] and cp != pos:
			WANT[cp] = (comp[0], pos)
			REQ[pos] = cp
			return
		if r == k - 1:
			return
		harvest()
		if c != Entities.Grass or get_ground_type() == Grounds.Soil:
			if not plant(c):
				return


YLD = {}
RRK = [1]


def mixed_job(i, d, need, flags):
	global NEED
	global POLY
	NEED = need
	POLY = num_unlocked(Unlocks.Polyculture) > 0
	cols = my_cols(i, d)
	COLS[0] = cols[0]
	COLS[1] = cols[0] + len(cols)
	if flags[0]:
		COLS[0] = 2
	strip = flags[0]
	weird = flags[1]
	for k in PEND:
		PEND[k] = 0
	n = get_world_size()
	w = width()
	if w * n == 1:
		goal = 0
		if Items.Hay in NEED[0]:
			goal = NEED[0][Items.Hay]
		if num_items(Items.Hay) >= goal:
			goal = num_items(Items.Hay) + 1
		while num_items(Items.Hay) < goal:
			if can_harvest():
				harvest()
		return 0
	if POLY or d > 1 or strip or weird:
		cl = my_cols(i, d)
		m = len(cl)
		# two or more drones on an unlock's round: pass after pass until it is affordable, checked every
		# column (as one drone does), each drone carrying on from the column it stopped at last round
		lp = d >= 2 and len(NEED) > 2
		fm = POLY and not strip and not weird and PW_C1[0] == 0
		if fm:
			for ct in [Entities.Carrot, Entities.Tree, Entities.Bush, Entities.Grass]:
				YLD[ct] = yield_of(ct)
			RRK[0] = RR_N
			if max_drones() <= RR_FEW_D:
				RRK[0] = RR_FEW
		k = 0
		if lp and len(flags) > 2 and flags[2] != None and len(flags[2]) == d and flags[2][i][1] == POLY:
			k = flags[2][i][0]
		goal = NEED[0]
		if lp:
			goal = NEED[2]
		need_vars()
		j = 0
		if m > 1 and m < w and n % 2 == 0 and HAM:
			return mixed_ham(cl, m, n, k, lp, goal, strip, weird, fm)
		while True:
			if lp and j > 0:
				done = True
				for it in goal:
					if num_items(it) < goal[it]:
						done = False
				if done or (k == 0 and num_items(Items.Power) < LP_PW):
					return (k, POLY)
				if k == 0:
					for it in PEND:
						PEND[it] = 0
			x = cl[k]
			go(x, 0)
			p3 = choose3()
			ce = p3[0]
			co = p3[1]
			if ce == co and not POLY and num_unlocked(Unlocks.Plant) > 0:
				# a mix of crop types lets some plants find their companion (x5 even before polyculture)
				if ce == Entities.Grass and FL[2]:
					ce = Entities.Tree
				elif ce == Entities.Grass:
					co = Entities.Bush
				else:
					co = Entities.Grass
			if x % 2 == 0:
				cs = [ce, co]
			else:
				cs = [co, ce]
			if fm:
				for y in range(n):
					tend_fm((x, y), cs[y % 2])
					move(North)
			else:
				for y in range(n):
					mixed_cell(strip, weird, cs[y % 2])
					move(North)
			k = (k + 1) % m
			j += 1
			if not lp and k == 0:
				return (k, POLY)
	# one drone, no polyculture: pass after pass until the current unlock is affordable;
	# a torus walk (n - 1 steps north per column, then east) visits n * n cells in n * n moves
	small = w * n <= 3
	lt = lvl_mult(Unlocks.Trees)
	lc = lvl_mult(Unlocks.Carrots)
	YC[Entities.Tree] = 5 * lt * 2
	YC[Entities.Bush] = lt * 2
	YC[Entities.Carrot] = lc * 2
	sun_on = SUN_STRIP and w >= 6 and num_unlocked(Unlocks.Sunflowers) > 0
	plant_on = num_unlocked(Unlocks.Plant) > 0
	need_vars()
	# buying needs only the unlock's own cost (seeds for carrots not yet planted are not needed)
	goal = NEED[0]
	if len(NEED) > 2:
		goal = NEED[2]
	# carry on from the column after the one the last round ended on
	x0 = (get_pos_x() + 1) % w
	while True:
		p = None
		for i in range(w):
			x = (x0 + i) % w
			if i > 0:
				# checked every column, so the unlock is bought as soon as it is affordable
				done = True
				for it in goal:
					if num_items(it) < goal[it]:
						done = False
				if done:
					return 0
			px = get_pos_x()
			if px != x:
				if (px + 1) % w == x:
					move(East)
				else:
					go(x, get_pos_y())
			if sun_on and x < SUN_COLS:
				if len(SUN) >= SUN_COLS * n:
					# the strip is full: only its highest flower is ever cut, so walk past the rest
					while len(SUN) >= 10:
						mp = None
						m = 0
						for q in SUN:
							if SUN[q] > m:
								m = SUN[q]
								mp = q
						if mp[0] != x:
							break
						go(x, mp[1])
						if not can_harvest():
							break
						sun_cell()
					continue
				for k in range(n):
					sun_cell()
					if k < n - 1 or w == 1:
						move(North)
				continue
			if p == None or (n != 3 and i % 2 == 0):
				# a 3x3 farm keeps its crop types for the whole pass: rows of one type each
				p = choose3()
			ce = p[0]
			co = p[1]
			if ce == co and plant_on:
				# a mix of crop types lets some plants find their companion (x5 even before polyculture)
				if ce == Entities.Grass and FL[2] and n != 3:
					# hay wanted: grass on the odd cells and trees (not bushes) on the even ones,
					# 5x the wood a cut, and trees already standing when the weird round starts
					ce = Entities.Tree
				elif ce == Entities.Grass:
					co = Entities.Bush
					if FL[2]:
						# trees rather than bushes beside the grass: cut less often, and standing ready
						# for the weird substance round
						ce = Entities.Tree
						co = Entities.Grass
				else:
					co = Entities.Grass
			if x % 2 == 0:
				cs = [ce, co]
			else:
				cs = [co, ce]
			if small:
				for k in range(n):
					tend_wait(cs[get_pos_y() % 2])
					move(North)
			elif n == 3:
				# 3x3: a checkerboard does not fit the torus (column 2 meets column 0), so each row
				# holds one of three types: a plant's companion cell then holds its own type 1 time
				# in 5 instead of about 1 in 2, and 0.27 of the harvests get the x5 instead of 0.19
				cl = [ce, co, third(ce, co)]
				for k in range(2):
					tend_fast(cl[get_pos_y()])
					move(North)
				tend_fast(cl[get_pos_y()])
			elif n % 2 == 0:
				# one function per crop type, called in pairs: fewer ops a cell than tend_fast
				y0 = get_pos_y() % 2
				fa = TF[cs[y0]]
				fb = TF[cs[1 - y0]]
				for k in range(n // 2 - 1):
					fa()
					move(North)
					fb()
					move(North)
				fa()
				move(North)
				fb()
			else:
				for k in range(n - 1):
					tend_fast(cs[get_pos_y() % 2])
					move(North)
				tend_fast(cs[get_pos_y() % 2])
		done = True
		for it in goal:
			if num_items(it) < goal[it]:
				done = False
		if done:
			return 0
		for k in PEND:
			PEND[k] = 0


def mixed_ham(cl, m, n, k, lp, goal, strip, weird, fm):
	# my columns walked as one closed loop (up the first column, then a snake back down the
	# others): every cell once a lap with no steps back west; segment k is cells k*n..k*n+n-1
	c0 = cl[0]
	px = []
	py = []
	for y in range(n):
		px.append(c0)
		py.append(y)
	for r in range(n - 1, -1, -1):
		if (n - 1 - r) % 2 == 0:
			for x in range(c0 + 1, c0 + m):
				px.append(x)
				py.append(r)
		else:
			for x in range(c0 + m - 1, c0, -1):
				px.append(x)
				py.append(r)
	ds = []
	N = m * n
	for t in range(N):
		u = (t + 1) % N
		if px[u] > px[t]:
			ds.append(East)
		elif px[u] < px[t]:
			ds.append(West)
		elif py[u] > py[t]:
			ds.append(North)
		else:
			ds.append(South)
	j = 0
	t = k * n
	go(px[t], py[t])
	while True:
		if lp and j > 0:
			done = True
			for it in goal:
				if num_items(it) < goal[it]:
					done = False
			if done or (k == 0 and num_items(Items.Power) < LP_PW):
				return (k, POLY)
			if k == 0:
				for it in PEND:
					PEND[it] = 0
		p3 = choose3()
		ce = p3[0]
		co = p3[1]
		if ce == co and not POLY and num_unlocked(Unlocks.Plant) > 0:
			if ce == Entities.Grass and FL[2]:
				ce = Entities.Tree
			elif ce == Entities.Grass:
				co = Entities.Bush
			else:
				co = Entities.Grass
		cs = [ce, co]
		if fm:
			for q in range(t, t + n):
				tend_fm((px[q], py[q]), cs[(px[q] + py[q]) % 2])
				move(ds[q])
		else:
			for q in range(t, t + n):
				mixed_cell(strip, weird, cs[(px[q] + py[q]) % 2])
				move(ds[q])
		k = (k + 1) % m
		t = k * n
		j += 1
		if not lp and k == 0:
			return (k, POLY)


HAM = True


def sh(have, c, l):
	r = 0
	if c > have:
		r = 10 + (c - have) / c
	if l > have:
		r += (l - have) / l
	return r


def third(ce, co):
	# the most needed crop type that is neither ce nor co (co if nothing else is needed)
	best = co
	bs = 0
	have = [ce, co]
	if Entities.Grass not in have:
		s = sh(num_items(Items.Hay) + PEND[Items.Hay], NV[0], NV[1])
		if s > bs:
			bs = s
			best = Entities.Grass
	if FL[0] and not (Entities.Bush in have or Entities.Tree in have):
		s = sh(num_items(Items.Wood) + PEND[Items.Wood], NV[2], NV[3])
		if s > bs:
			bs = s
			best = Entities.Bush
			if FL[2] and ce != Entities.Tree:
				best = Entities.Tree
	if FL[3] and Entities.Carrot not in have:
		s = sh(num_items(Items.Carrot) + PEND[Items.Carrot], NV[6], NV[7])
		if s > bs and num_items(Items.Wood) >= FL[4] and num_items(Items.Hay) >= FL[5]:
			best = Entities.Carrot
	return best


def need_vars():
	# what choose3() reads instead of NEED and num_unlocked, set once per round
	global NV
	global FL
	cur = NEED[0]
	look = NEED[1]
	NV = []
	for it in [Items.Hay, Items.Wood, Items.Weird_Substance, Items.Carrot]:
		for d in [cur, look]:
			if it in d:
				NV.append(d[it])
			else:
				NV.append(0)
	c = get_cost(Entities.Carrot)
	FL = [num_unlocked(Unlocks.Plant) > 0, NV[4] > 0 or NV[5] > 0, num_unlocked(Unlocks.Trees) > 0, num_unlocked(Unlocks.Carrots) > 0, c[Items.Wood], c[Items.Hay]]


NV = []
FL = []


def choose3():
	# (choose(True), choose(False)) on the needs and flags need_vars() set
	be = Entities.Grass
	bo = be
	bs = sh(num_items(Items.Hay) + PEND[Items.Hay], NV[0], NV[1])
	so = bs
	if FL[0]:
		s = sh(num_items(Items.Wood) + PEND[Items.Wood], NV[2], NV[3])
		if FL[1]:
			s2 = sh(num_items(Items.Weird_Substance) + PEND[Items.Weird_Substance], NV[4], NV[5])
			if s2 > s:
				s = s2
		if s > bs:
			bs = s
			if FL[2]:
				be = Entities.Tree
			else:
				so = s
				be = Entities.Bush
				bo = be
	if FL[3]:
		s = sh(num_items(Items.Carrot) + PEND[Items.Carrot], NV[6], NV[7])
		if s > bs or s > so:
			if num_items(Items.Wood) >= FL[4] and num_items(Items.Hay) >= FL[5]:
				if s > bs:
					be = Entities.Carrot
				if s > so:
					bo = Entities.Carrot
	return (be, bo)


YC = {Entities.Grass: 0}
IT = {Entities.Carrot: Items.Carrot, Entities.Grass: Items.Hay, Entities.Bush: Items.Wood, Entities.Tree: Items.Wood}


def carrot_ok():
	c = get_cost(Entities.Carrot)
	for it in c:
		if num_items(it) < c[it]:
			return False
	return True


def tend_fast(c):
	# tend_plain with the yields cached for the pass
	e = get_entity_type()
	if e == Entities.Grass:
		if c == Entities.Grass:
			if can_harvest():
				harvest()
			if get_ground_type() == Grounds.Soil:
				till()
			return
		harvest()
	elif e != None:
		if not can_harvest():
			return
		harvest()
	if c == Entities.Grass:
		if get_ground_type() == Grounds.Soil:
			till()
		return
	if c == Entities.Carrot:
		if get_ground_type() != Grounds.Soil:
			till()
	if plant(c):
		PEND[IT[c]] += YC[c]
		if c == Entities.Tree and get_water() < WT_LO and num_items(Items.Water) >= 1:
			# one water at planting ripens the tree within a pass on a small farm, and the
			# soil keeps enough for the next tree as long as it is above WT_LO
			use_item(Items.Water)


def tg():
	e = get_entity_type()
	if e == Entities.Grass:
		if can_harvest():
			harvest()
		return
	if e != None:
		if not can_harvest():
			return
		harvest()
	if get_ground_type() == Grounds.Soil:
		till()


def tt():
	e = get_entity_type()
	if e != None:
		if e != Entities.Grass and not can_harvest():
			return
		harvest()
	if plant(Entities.Tree):
		PEND[Items.Wood] += YC[Entities.Tree]
		if get_water() < WT_LO and num_items(Items.Water) >= 1:
			use_item(Items.Water)


def tb():
	e = get_entity_type()
	if e != None:
		if e != Entities.Grass and not can_harvest():
			return
		harvest()
	if plant(Entities.Bush):
		PEND[Items.Wood] += YC[Entities.Bush]


def tc():
	e = get_entity_type()
	if e != None:
		if e != Entities.Grass and not can_harvest():
			return
		harvest()
	if get_ground_type() != Grounds.Soil:
		till()
	if plant(Entities.Carrot):
		PEND[Items.Carrot] += YC[Entities.Carrot]


TF = {Entities.Grass: tg, Entities.Tree: tt, Entities.Bush: tb, Entities.Carrot: tc}


def tend_wait(c):
	# small farm, growth-bound: wait for the crop here instead of walking past it
	e = get_entity_type()
	if e != None and e != Entities.Grass and e == c:
		while not can_harvest():
			pass
	tend_plain(c)


def mixed_round(need):
	strip = False
	weird = Items.Weird_Substance in need[0] and num_unlocked(Unlocks.Fertilizer) > 0
	global LPS
	LPS = all_drones(mixed_job, need, (strip, weird, LPS))


# ---- polyculture farm ----------------------------------------------------------------------------
# Crops grow on the cells where (x + y) is even, servants on the odd cells. A crop's companion
# wish is claimed when it is planted: an odd cell in the drone's own columns that nobody else has
# claimed for another type. A wish that cannot be claimed is rerolled (cut and replant). Servant
# cells are made into the wished type when the drone passes them, which is always before the crop
# is cut again. Free servant cells stay grass and give hay.

PW_T = []
PW_BY = []
PW_C0 = [0]
PW_C1 = [0]


def pw_item(e):
	if e == Entities.Carrot:
		return Items.Carrot
	if e == Entities.Grass:
		return Items.Hay
	return Items.Wood


def pw_crop(need, have, col):
	# the crop most short of its goal (relative); carrots only while their seeds last a column
	best = Entities.Carrot
	bs = -1
	for e in [Entities.Carrot, Entities.Tree, Entities.Grass]:
		it = pw_item(e)
		if it in need:
			s = (need[it] - have[it]) / need[it]
			if s > bs:
				bs = s
				best = e
	if best == Entities.Carrot:
		seed = get_cost(Entities.Carrot)[Items.Wood] * col
		if have[Items.Wood] < seed:
			return Entities.Tree
		if have[Items.Hay] < seed:
			return Entities.Grass
	return best


def pw_make(e, t):
	# make the entity here type t (t is never None)
	if e == t:
		return
	if t == Entities.Grass:
		if e != None:
			harvest()
		if get_ground_type() == Grounds.Soil:
			plant(Entities.Grass)
		return
	if e != None and e != Entities.Grass:
		harvest()
	if t == Entities.Carrot and get_ground_type() != Grounds.Soil:
		till()
	plant(t)


def pw_cell_crop(c, n, t, rerolls):
	e = get_entity_type()
	if e != None and e != Entities.Grass:
		if not can_harvest():
			return
	if e != None:
		harvest()
	q = PW_BY[c]
	if q >= 0:
		if PW_BY[q] == c:
			PW_T[q] = None
			PW_BY[q] = -1
		PW_BY[c] = -1
	if t == Entities.Carrot and get_ground_type() != Grounds.Soil:
		till()
	if WET_POLY:
		wet()
	if not plant(t):
		return
	for r in range(rerolls + 1):
		comp = get_companion()
		if comp == None:
			return
		px = comp[1][0]
		if px >= PW_C0[0] and px < PW_C1[0]:
			q = px * n + comp[1][1]
			ct = comp[0]
			if (px + comp[1][1]) % 2 == 1:
				w = PW_T[q]
				if w == None or w == ct:
					PW_T[q] = ct
					PW_BY[q] = c
					PW_BY[c] = q
					return
		if r < rerolls:
			harvest()
			if not plant(t):
				return


def pw_cell_servant(c, hay):
	t = PW_T[c]
	e = get_entity_type()
	if t == None:
		if e == Entities.Grass:
			if hay and can_harvest():
				harvest()
		elif e != None:
			if can_harvest():
				harvest()
				if get_ground_type() == Grounds.Soil:
					plant(Entities.Grass)
		elif get_ground_type() == Grounds.Soil:
			plant(Entities.Grass)
		return
	pw_make(e, t)


def mixed_seg(i, d, need, flags):
	# mixed_job for more drones than columns: drone i tends cells i*N//d.. of the whole field's
	# snake path (up column 0, down column 1, ...) and claims companions only inside that stretch
	# (PW_C0[0]..PW_C1[0] as path indices)
	global NEED
	global POLY
	NEED = need
	POLY = True
	for k in PEND:
		PEND[k] = 0
	n = get_world_size()
	w = width()
	N = w * n
	lo = i * N // d
	hi = (i + 1) * N // d
	PW_C0[0] = lo
	PW_C1[0] = hi
	COLS[0] = 0
	COLS[1] = w
	cx = -1
	cs = []
	need_vars()
	todo = range(lo, hi)
	if len(need) > 2:
		# whole passes until the goal is on hand, checked every column
		todo = []
		for k in range(40):
			for t in range(lo, hi):
				todo.append(t)
	for t in todo:
		if t == lo or t % n == 0:
			if len(need) > 2 and num_items(Items.Carrot) >= need[2][Items.Carrot]:
				break
			if t == lo:
				cx = -1
				for k in PEND:
					PEND[k] = 0
		x = t // n
		y = t % n
		if x % 2 == 1:
			y = n - 1 - y
		if x != cx:
			cx = x
			go(x, y)
			p3 = choose3()
			ce = p3[0]
			co = p3[1]
			if x % 2 == 0:
				cs = [ce, co]
			else:
				cs = [co, ce]
		mixed_cell(False, flags[1], cs[y % 2])
		if t < hi - 1 and (t + 1) // n == x:
			if x % 2 == 0:
				move(North)
			else:
				move(South)
	PW_C1[0] = 0
	return 0



# ---- weird substance before cactus ------------------------------------------------------------
# Trees on one checkerboard colour, grass on the other. Plus shapes centred where (x + 2y) % 5 == 0
# tile the field, so one weird substance per centre turns every plant weird once a pass; a weird
# plant gives half its yield as weird substance. Fertilizer starts it off (it only marks its own
# cell).

def wsub_job(i, d, goal, b):
	n = get_world_size()
	if d == 1:
		# one drone: unripe trees are walked past instead of waited for, each ripe tree is made weird
		# just before it is cut, and the grass between them is cut on every pass
		while True:
			for k in range(n):
				e = get_entity_type()
				if (get_pos_x() + get_pos_y()) % 2 == 0:
					if e != Entities.Tree or can_harvest():
						if e == Entities.Tree:
							if num_items(Items.Weird_Substance) >= 1:
								use_item(Items.Weird_Substance)
							elif num_items(Items.Fertilizer) >= 1:
								use_item(Items.Fertilizer)
						if e != None:
							harvest()
						if get_water() < 0.1 and num_items(Items.Water) >= 1:
							use_item(Items.Water)
						plant(Entities.Tree)
				elif get_ground_type() == Grounds.Soil:
					if e != None and can_harvest():
						harvest()
					till()
				elif e != None and can_harvest():
					harvest()
				if num_items(Items.Weird_Substance) >= goal:
					return 0
				if k < n - 1:
					move(North)
			move(East)
	cols = my_cols(i, d)
	while num_items(Items.Weird_Substance) < goal:
		for x in cols:
			if num_items(Items.Weird_Substance) >= goal:
				return 0
			go(x, get_pos_y())
			if get_pos_y() == 0:
				ys = range(n)
				dy = North
			else:
				ys = range(n - 1, -1, -1)
				dy = South
			k = 0
			for y in ys:
				e = get_entity_type()
				if (x + y) % 2 == 0:
					if e == Entities.Tree and not can_harvest():
						pass
					elif e == Entities.Tree:
						# made weird just before it is cut (it and its four grass neighbours flip): every ripe
						# tree yields weird substance in the same pass, from the first pass on
						if num_items(Items.Weird_Substance) >= 1:
							use_item(Items.Weird_Substance)
						elif num_items(Items.Fertilizer) >= 1:
							use_item(Items.Fertilizer)
						harvest()
						if get_water() < 0.25 and num_items(Items.Water) >= 1:
							use_item(Items.Water)
						plant(Entities.Tree)
					else:
						if e != None:
							harvest()
						if get_water() < 0.25 and num_items(Items.Water) >= 1:
							use_item(Items.Water)
						plant(Entities.Tree)
				elif get_ground_type() == Grounds.Soil:
					# back to grassland, so grass stands here and regrows by itself
					if e != None and can_harvest():
						harvest()
					till()
				elif e != None and e != Entities.Grass:
					if can_harvest():
						harvest()
				k += 1
				if k < n:
					move(dy)
	return 0


def weird_round(goal):
	all_drones(wsub_job, goal, 0)


# ---- power -------------------------------------------------------------------------------------

def sun_plant_job(i, d, a, b):
	n = get_world_size()
	cells = []
	for x in my_cols(i, d):
		go(x, 0)
		for y in range(n):
			if get_entity_type() != Entities.Sunflower:
				clear_cell()
				soil()
				plant(Entities.Sunflower)
			v = measure()
			sun_water(v)
			cells.append((x, y, v))
			move(North)
	return cells


# soil water a sunflower gets at planting, by petal count: the flowers cut first wait for growth
# (7 s dry, 1 / (1 + 4 * water) of that when wet); later levels have grown by their turn anyway
SUN_WT = {15: 0.7, 14: 0.45, 13: 0.2, 12: 0.05, 11: 0.01}


def bd_settle(k, a, f, b, dfr, LO, UP, MX, path, wf):
	# insert cell k: fix it against the cells already in place. Planting forwards (dfr False) those
	# are the indices up to k; on the walk back (dfr True) the indices from k to b - 1 and those
	# before f. A mixed cell's neighbours all lie in its own stretch (cuts are between pure cells).
	# A swap moves a pure cell's value the safe way; a mixed cell can be broken on one side only
	# (the side it moved towards), so it goes back on the work list for that side.
	# 0: lower, 1: upper, 2: both. wf: the stretch's weird flags (index - a), or None
	work = [(k, 2)]
	cur = k
	while len(work) > 0:
		it = work.pop()
		c = it[0]
		sd = it[1]
		if c != cur:
			if abs(path[cur][0] - path[c][0]) + abs(path[cur][1] - path[c][1]) == 1:
				move(step_dir(path[cur][0], path[cur][1], path[c][0], path[c][1]))
			else:
				go(path[c][0], path[c][1])
			cur = c
		v = measure()
		bd = None
		bq = -1
		bv = 0
		bl = False
		if sd != 1:
			for e in LO[c]:
				q = e[1]
				if (dfr and ((q >= k and q < b) or q < f)) or (not dfr and q <= k):
					w = measure(e[0])
					if w - v > bv:
						bv = w - v
						bd = e[0]
						bq = q
						bl = True
		if sd != 0:
			for e in UP[c]:
				q = e[1]
				if (dfr and ((q >= k and q < b) or q < f)) or (not dfr and q <= k):
					w = measure(e[0])
					if v - w > bv:
						bv = v - w
						bd = e[0]
						bq = q
						bl = False
		if bd != None:
			swap(bd)
			if wf != None:
				t = wf[c - a]
				wf[c - a] = wf[bq - a]
				wf[bq - a] = t
			# swapped with a lower neighbour: this cell got bigger (check its uppers), the
			# neighbour smaller (check its lowers); the other way round for an upper one
			if bl:
				if MX[bq]:
					work.append((bq, 0))
				if MX[c]:
					work.append((c, 1))
			else:
				if MX[bq]:
					work.append((bq, 1))
				if MX[c]:
					work.append((c, 0))
	if cur != k:
		go(path[k][0], path[k][1])


def sun_cut_job(i, d, lists, v):
	for c in lists[i]:
		go(c[0], c[1])
		while not can_harvest():
			pass
		harvest()
	return 0


SUN_PER = 1


def power_round():
	n = width() * get_world_size()
	if max_drones() == 1:
		if n >= 12:
			power_mini()
		return
	if num_items(Items.Carrot) < n:
		return
	if SUN_NEW:
		power_round2(n)
		return
	d = drones()
	cells = all_drones(sun_plant_job, 0, 0)
	for v in range(15, 6, -1):
		if SUN_TARGET > 0 and num_items(Items.Power) >= SUN_TARGET:
			break
		# this petal count's cells, in field order, shared out evenly in runs of neighbours
		cv = []
		for cl in cells:
			for c in cl:
				if c[2] == v:
					cv.append(c)
		m = len(cv)
		if m == 0:
			continue
		k = min(d, (m + SUN_PER - 1) // SUN_PER)
		lists = []
		for j in range(k):
			lists.append(cv[j * m // k:(j + 1) * m // k])
		spawn_node(0, k, k, (sun_cut_job, lists, v))


SUN_STRIP = False
SUN_COLS = 2

SUN_WET = 1.0
SUN_WN = 4
SUN_WRES = 0
# the last power round (nothing else needs water after it): water by petal count, see sun_water
SUN_GRADED = True
SUN_WSAFE = 1.06
# the snake's neighbour tables are built during a power round's wait for its flowers
SUN_DINO = True
SUN_MARGIN = 1.04
SUN_SLACK = 0
SUN_GROW = 0.05
SUN_NEW = True
SUN_BLK = 16
# a sunflower's petals are drawn anew at every planting: in the last power round (carrots to
# spare) one planted with fewer than SUN_MINP is cut at once (not grown: nothing lost but its
# seed) and planted again, so the round has fewer petal levels and fewer passes of its drones.
# Earlier rounds do not: the extra plantings cost them what the passes save.
SUN_MINP = 7
# carrots a round leaves alone when it plants again
SUN_SEEDS = 100


def sun_dist(x0, y0, x1, y1, w, n):
	dx = (x1 - x0) % w
	if dx > w - dx:
		dx = w - dx
	dy = (y1 - y0) % n
	if dy > n - dy:
		dy = n - dy
	return dx + dy


def sun_plant2(i, d, wet, b):
	# plant my columns, water them when stock allows, then plan my cuts level by level from the
	# main drone's end cell (where every cut drone is spawned)
	n = get_world_size()
	w = width()
	by = []
	for v in range(16):
		by.append([])
	ready = 0
	minp = 0
	if num_unlocked(Unlocks.Mazes) >= 4:
		minp = SUN_MINP
	# rd[v]: when the last flower with v petals is grown; a level's cuts wait only for its own flowers
	rd = []
	for v in range(16):
		rd.append(0)
	# my cells: whole columns, or with more drones than columns a stretch of the whole field's
	# snake path (up column 0, down column 1, ...)
	N = w * n
	lo = i * N // d
	hi = (i + 1) * N // d
	if d <= w:
		cs = my_cols(i, d)
		lo = cs[0] * n
		hi = lo + len(cs) * n
	if b > 0 and hi > lo + b:
		# a part round: only the first b cells
		hi = lo + b
	cl = []
	if SUN_BLK > 0 and d >= SUN_BLK and w == n:
		# square-ish blocks: my level-by-level cuts stay close together
		gy = 1
		while (gy + 1) * (gy + 1) <= d:
			gy += 1
		while d % gy != 0:
			gy -= 1
		gx = d // gy
		bx = i % gx
		bj = i // gx
		y0 = bj * n // gy
		y1 = (bj + 1) * n // gy
		for x in range(bx * w // gx, (bx + 1) * w // gx):
			if (x - bx * w // gx) % 2 == 0:
				for y in range(y0, y1):
					cl.append((x, y))
			else:
				for y in range(y1 - 1, y0 - 1, -1):
					cl.append((x, y))
		if b > 0 and len(cl) > b:
			cl = cl[:b]
	else:
		for c in range(lo, hi):
			x = c // n
			y = c % n
			if d > w and x % 2 == 1:
				y = n - 1 - y
			cl.append((x, y))
	ci = len(cl)
	for xy in cl:
		x = xy[0]
		y = xy[1]
		go(x, y)
		ci -= 1
		if get_entity_type() != Entities.Sunflower:
			clear_cell()
			soil()
			plant(Entities.Sunflower)
			m = measure()
			while m != None and m < minp and num_items(Items.Carrot) > SUN_SEEDS:
				harvest()
				plant(Entities.Sunflower)
				m = measure()
		m = measure()
		# two drones, too little water to wet them all (wet[0] == 2): the last-planted high-petal
		# flowers, which set when the cuts can start, get one water each
		if wet[0] == 2 and m != None and ci < 17 and m >= 11 and get_water() < 0.2 and num_items(Items.Water) >= 1:
			use_item(Items.Water, 1)
		if m != None and wet[m] > 0:
			if wet[0] > 0:
				# by petal count: up to the level this flower's turn in the cutting order needs
				k = (wet[m] * 0.25 - get_water() + 0.24) // 0.25
			else:
				k = min(wet[m], (SUN_WET - get_water()) // 0.25)
			if k >= 1 and num_items(Items.Water) >= k:
				use_item(Items.Water, k)
		t = get_time() + 8.4 / (1 + 3.8 * get_water())
		if t > ready:
			ready = t
		if m != None:
			by[m].append((x, y))
			if t > rd[m]:
				rd[m] = t
	# the main drone's end cell, where every cut drone is spawned
	c = 1 * N // d
	if d <= w:
		c = (my_cols(0, d)[-1] + 1) * n
	if b > 0 and c > b:
		c = b
	c -= 1
	cx = c // n
	cy = c % n
	if d > w and cx % 2 == 1:
		cy = n - 1 - cy
	if SUN_BLK > 0 and d >= SUN_BLK and w == n:
		# drone 0's block ends where its snake ends
		gy = 1
		while (gy + 1) * (gy + 1) <= d:
			gy += 1
		while d % gy != 0:
			gy -= 1
		gx = d // gy
		y1 = n // gy
		x1 = w // gx
		cx = x1 - 1
		cy = y1 - 1
		if (x1 - 1) % 2 == 1:
			cy = 0
		if b > 0 and b < x1 * y1:
			k = b - 1
			cx = k // y1
			cy = k % y1
			if cx % 2 == 1:
				cy = y1 - 1 - cy
	plan = []
	for v in range(15, 6, -1):
		left = by[v]
		route = []
		walk = 0
		work = 0
		while len(left) > 0:
			bj = 0
			bd = 999
			for j in range(len(left)):
				c = left[j]
				dd = sun_dist(cx, cy, c[0], c[1], w, n)
				if dd < bd:
					bd = dd
					bj = j
			c = left.pop(bj)
			if len(route) == 0:
				walk = bd
			else:
				work += bd
			work += 1
			route.append(c)
			cx = c[0]
			cy = c[1]
		plan.append((route, walk, work))
	return (plan, ready, rd)


def sun_cut2(i, d, a):
	plans = a[0]
	T = a[1]
	plan = plans[i]
	mz = a[3]
	for li in range(a[2]):
		route = plan[li][0]
		until = T[li]
		for k in range(len(route)):
			c = route[k]
			go(c[0], c[1])
			if k == 0:
				while get_time() < until:
					pass
			if mz == None:
				while not can_harvest():
					pass
				harvest()
			else:
				# the maze may already be up if this flower was slow: never harvest a hedge
				e = get_entity_type()
				while e == Entities.Sunflower and not can_harvest():
					e = get_entity_type()
				if e == Entities.Sunflower:
					harvest()
	if mz != None:
		# straight on to my start in the maze that follows
		mz_life(mz[0][i], mz[1], mz[2], mz[3], mz[4], mz[5])


def sun_water(nf, fl, lv):
	# waters (0.25 each) a flower gets at planting, by petal count (entry 0 marks the list), for
	# nf flowers (fl a drone) on lv petal levels and the water in stock. The flowers are cut from
	# 15 petals down, a pass of the drones per level, and a dry one takes up to 8.4 s to grow: a
	# level that is watered is cut while the dry ones still grow. So the 15s get the most and
	# every level after them enough to be grown when its turn comes (a turn taken as short as it
	# can be, so no level is ever late), and the richest such plan the stock covers is taken.
	# With less than a water a flower the top levels get one each.
	act = 200 / (400 * 1.5 ** num_unlocked(Unlocks.Speed))
	if num_items(Items.Power) > 0:
		act = act / 2
	step = act * (fl * 2 / lv + 3)
	have = (num_items(Items.Water) - SUN_WRES) * lv / nf
	us = None
	for u in [1, 2, 3, 4]:
		g = 8.4 / (1 + 0.95 * u)
		vs = [u]
		cost = u
		for j in range(1, lv):
			need = (8.4 / (g + j * step) - 1.08) / 0.95
			k = 1
			while k < need and k < u:
				k += 1
			vs.append(k)
			cost += k
		if cost < lv * u:
			# uneven: the stock must also cover more flowers than usual on the watered levels
			cost = cost * SUN_WSAFE
		if cost > have:
			if u == 1:
				us = vs
				for j in range(lv):
					if us[j] > have:
						us[j] = 0
					have -= us[j]
			break
		us = vs
	wl = [1]
	for v in range(1, 16):
		wl.append(0)
	for j in range(lv):
		wl[15 - j] = us[j]
	return wl


def power_round2(n):
	d = drones()
	if width() > 1:
		d = min(max_drones(), width() * get_world_size())
	b = 0
	nf = n
	if SUN_TARGET > 0 and SUN_PART:
		# plant only what the target needs: 8 power a cut, the drones' own use meanwhile, and the
		# last 9 flowers (cut once fewer than 10 are left) give almost nothing
		k = (SUN_TARGET - num_items(Items.Power) + d * SUN_PDR) // (8 * lvl_mult(Unlocks.Sunflowers)) + 12
		b = k // d + 1
		nf = min(n, b * d)
	if (num_unlocked(Unlocks.Dinosaurs) > 0 or num_unlocked(Unlocks.Mazes) >= 4) and SUN_GRADED:
		wet = sun_water(nf, nf / d, 16 - max(SUN_MINP, 7))
	else:
		k = min(SUN_WN, (num_items(Items.Water) - SUN_WRES) // n)
		wet = [0]
		for v in range(1, 16):
			wet.append(k)
		if k == 0 and d == 2:
			wet[0] = 2
	res = spawn_node(0, d, d, (sun_plant2, wet, b))
	if SUN_DINO and SUN_TARGET == 0 and num_unlocked(Unlocks.Dinosaurs) > 0 and SN != get_world_size():
		# the snake's neighbour tables, built by every drone while the sunflowers grow
		dino_setup()
	d = len(res)
	act = 200 / (400 * 1.5 ** num_unlocked(Unlocks.Speed))
	if num_items(Items.Power) > 0:
		act = act / 2
	act = act * SUN_MARGIN
	plans = []
	ready = 0
	for r in res:
		plans.append(r[0])
		if r[1] > ready:
			ready = r[1]
	L = 9
	if SUN_TARGET > 0:
		gain = num_items(Items.Power) - d * 0.5 * (ready - get_time() + 3)
		per = 8 * lvl_mult(Unlocks.Sunflowers)
		L = 0
		while L < 9 and gain < SUN_TARGET:
			for i in range(d):
				gain += per * len(plans[i][L][0])
			L += 1
	rl = []
	for v in range(16):
		rl.append(0)
	for r in res:
		for v in range(16):
			if r[2][v] > rl[v]:
				rl[v] = r[2][v]
	T = [rl[15] + SUN_GROW]
	now = get_time() + 6 * act
	ts = []
	for i in range(d):
		ts.append(now)
	for li in range(L):
		if rl[15 - li] + SUN_GROW > T[li]:
			T[li] = rl[15 - li] + SUN_GROW
		tv = T[li]
		f = tv
		some = False
		for i in range(d):
			c = plans[i][li]
			if len(c[0]) == 0:
				continue
			some = True
			ti = ts[i] + c[1] * act
			if ti < tv:
				ti = tv
			ti = ti + c[2] * act
			ts[i] = ti
			if ti > f:
				f = ti
		if some:
			T.append(f + SUN_SLACK * act)
		else:
			# a level nobody has a flower in takes no time
			T.append(tv)
	mz = None
	if SUN_MZ != None and d == len(SUN_MZ[2]) and d == MZ_GXS * MZ_GXS:
		# the cut drones go on to the maze: each takes the start of the block its last cut is in
		# (or a free one), and the maze is made once the last of them can be on its start
		global SUN_MZ_DONE
		SUN_MZ_DONE = True
		n2 = get_world_size()
		st = SUN_MZ[2]
		w = width()
		last = []
		for i in range(d):
			c = (0, 0)
			for li in range(L):
				r = plans[i][li][0]
				if len(r) > 0:
					c = r[-1]
			last.append(c)
		gx = MZ_GXS
		gy = d // gx
		asg = []
		for i in range(d):
			asg.append(-1)
		used = {}
		for i in range(d):
			j = (last[i][0] * gx // n2) + (last[i][1] * gy // n2) * gx
			if j < d and not (j in used):
				asg[i] = j
				used[j] = True
		j = 0
		for i in range(d):
			if asg[i] < 0:
				while j in used:
					j += 1
				asg[i] = j
				used[j] = True
		# the main drone (cut drone 0) makes the maze, as in maze_round
		for i in range(d):
			if asg[i] == 0:
				asg[i] = asg[0]
				asg[0] = 0
		start_at = 0
		act0 = 200 / (400 * 1.5 ** num_unlocked(Unlocks.Speed)) / 2
		for i in range(d):
			x = st[asg[i]]
			t = ts[i] + act0 * (sun_dist(last[i][0], last[i][1], x % n2, x // n2, w, n2) + MZ_SUNW)
			if t > start_at:
				start_at = t
		mz = (asg, SUN_MZ[0], SUN_MZ[1], st, start_at, SUN_MZ[3])
	fan(sun_cut2, 0, d, d, (plans, T, L, mz))





MZ_TPF = 0.21
SUN_PAD = 150
SUN_TARGET = 0
SUN_PART = True
SUN_PDR = 12
PW_LATE = 100
PW_MARGIN = 0.9


def power_need(need):
	# before a maze: enough power for all of it, the round cut short once the stock covers it
	global SUN_TARGET
	if num_unlocked(Unlocks.Sunflowers) == 0 or width() < 6 or (SUN_STRIP and drones() == 1):
		return
	if num_items(Items.Power) < need:
		SUN_TARGET = need
		power_round()
		SUN_TARGET = 0


def power_mini():
	# one drone on a small farm: every cell a sunflower, then the highest cut while at least 10
	# stand (8x power each); the rest are left for the next farm pass
	n = get_world_size()
	w = width()
	sf = {}
	for i in range(w):
		for k in range(n):
			e = get_entity_type()
			pos = (get_pos_x(), get_pos_y())
			if e == Entities.Sunflower:
				sf[pos] = measure()
			else:
				if e != None:
					harvest()
				soil()
				if plant(Entities.Sunflower):
					sf[pos] = measure()
			if k < n - 1:
				move(North)
		move(North)
		move(East)
	while len(sf) >= PM_MIN:
		mp = None
		m = 0
		for q in sf:
			if sf[q] > m:
				m = sf[q]
				mp = q
		go(mp[0], mp[1])
		if not can_harvest() and num_items(Items.Water) >= 1:
			use_item(Items.Water)
		while not can_harvest():
			pass
		harvest()
		sf.pop(mp)


PM_LO = 10
PM_MIN = 10


def power_check():
	if num_unlocked(Unlocks.Sunflowers) > 0 and drones() == 1 and width() * get_world_size() >= 12:
		if num_items(Items.Power) < PM_LO:
			power_mini()
		return
	if num_unlocked(Unlocks.Sunflowers) == 0 or width() < 6 or (SUN_STRIP and drones() == 1):
		return
	lim = 50 * drones()
	if drones() <= 2:
		lim = 20 * drones()
	if num_unlocked(Unlocks.Dinosaurs) >= 1 or num_unlocked(Unlocks.Mazes) >= 4:
		# only the Mazes 4 cactus, snakes (one drone and its helpers) and the last maze are left:
		# that maze's own power check makes just what it needs, in a part round merged into the
		# maze (~4 s), which is far cheaper than a whole-field round here (~9 s)
		lim = PW_LATE
	if num_items(Items.Power) < lim:
		power_round()


# ---- pumpkins ----------------------------------------------------------------------------------
# Entry points: pumpkin_round() (one whole-field pumpkin, harvested), pumpkin_until(goal).
# Helpers shared with the cactus section: fan, snake, step_dir.

def fan(job, lo, hi, d, a):
	# job(i, d, a) on drones lo..hi-1: each drone hands the upper half of its range to a new drone,
	# so the last one starts after log2(d) spawns instead of d - 1
	hs = []
	left = []
	while hi - lo > 1:
		mid = (lo + hi + 1) // 2
		h = spawn_drone(fan, job, mid, hi, d, a)
		if h == None:
			left.append((mid, hi))
		else:
			hs.append(h)
		hi = mid
	job(lo, d, a)
	for r in left:
		fan(job, r[0], r[1], d, a)
	for h in hs:
		wait_for(h)




def snake(i, d):
	# path through drone i's columns: up the first, down the next, ...
	n = get_world_size()
	if d > n:
		# more drones than columns: drone i takes cells i*N//d.. of the whole field's path
		px = []
		py = []
		N = n * n
		for t in range(i * N // d, (i + 1) * N // d):
			x = t // n
			px.append(x)
			if x % 2 == 0:
				py.append(t % n)
			else:
				py.append(n - 1 - t % n)
		return (px, py)
	px = []
	py = []
	up = True
	for x in my_cols(i, d):
		for k in range(n):
			px.append(x)
			if up:
				py.append(k)
			else:
				py.append(n - 1 - k)
		up = not up
	return (px, py)


def step_dir(x0, y0, x1, y1):
	if x1 > x0:
		return East
	if x1 < x0:
		return West
	if y1 > y0:
		return North
	return South


# One pumpkin over the whole field. Every drone plants its columns, then walks over just the cells
# of its columns that have not grown yet, replanting the dead ones, and is done once all of them
# have grown (a grown pumpkin cannot die any more). Once column
# 0: measure() there equals measure(North), which wraps round to (0, 0), only once one pumpkin
# spans the whole height, so it harvests the moment the field has merged.
# Water: a cell below PK_WLO gets one water whenever there is any. Water stays in the soil (it
# loses about 1% a second), so it is spread thin over many cells rather than poured on a few.

PK_WLO = 0.2
PK_FA = 2
PK_RES = 6000
PK_ALL = True
PK_PERS = True
PK_PERS_MIN = 4
PK_PERS_C = 1.4


def pk_wet():
	if get_water() < PK_WLO and num_items(Items.Water) >= 1:
		use_item(Items.Water)


def pk_wet2():
	# a replanted cell is likely to be among the last to grow: water it more
	w = get_water()
	s = num_items(Items.Water)
	if w < 0.5 and s >= 1:
		use_item(Items.Water, min(s, 3 - w // 0.25))


def pk_job(i, d, a):
	n = get_world_size()
	p = snake(i, d)
	px = p[0]
	py = p[1]
	L = len(px)
	seed = get_cost(Entities.Pumpkin)[Items.Carrot]
	go(px[0], py[0])
	while get_pos_x() != px[0] or get_pos_y() != py[0]:
		# a maze still stands (its walls stopped a move): cut it down from where this drone is
		e = get_entity_type()
		if e == Entities.Hedge or e == Entities.Treasure:
			harvest()
		go(px[0], py[0])
	while True:
		pk_pass(px, py, L, seed, i, n, a)
		if a <= 1:
			return 0
		a -= 1
		if i == 0:
			# the field is one pumpkin once (0, n - 1) and (0, 0) (north of it, round the edge) match
			go(0, n - 1)
			while not (can_harvest() and measure() == measure(North)):
				pass
			harvest()
		else:
			while get_entity_type() == Entities.Pumpkin:
				pass
		# the next round walks the path the other way, from where this drone is
		rx = []
		ry = []
		for t in range(L):
			rx.insert(0, px[t])
			ry.insert(0, py[t])
		px = rx
		py = ry
		go(px[0], py[0])


def pk_pass(px, py, L, seed, i, n, a):
	todo = []
	p0 = num_items(Items.Pumpkin)
	for t in range(L):
		e = get_entity_type()
		if e != Entities.Pumpkin:
			if e == Entities.Dead_Pumpkin:
				plant(Entities.Pumpkin)
			else:
				if e != None:
					harvest()
				if num_items(Items.Carrot) < seed:
					return 0
				soil()
				plant(Entities.Pumpkin)
			pk_wet()
			todo.append(t)
		elif not can_harvest():
			todo.append(t)
		if t < L - 1:
			move(step_dir(px[t], py[t], px[t + 1], py[t + 1]))
	# revisit the cells not grown yet, nearest first along the path; replant the dead ones
	at = L - 1
	while len(todo) > 0:
		nt = []
		if at > todo[0]:
			r = []
			for t in todo:
				r.insert(0, t)
			todo = r
		alone = len(todo) == 1
		fert = len(todo) <= PK_FA
		for t in todo:
			go(px[t], py[t])
			at = t
			while True:
				e = get_entity_type()
				if e == Entities.Pumpkin:
					if can_harvest():
						break
					if fert and num_items(Items.Fertilizer) >= 1:
						use_item(Items.Fertilizer)
						continue
					if not alone:
						nt.append(t)
						break
				else:
					if e == None and a > 0 and num_items(Items.Pumpkin) > p0:
						# cut: drone 0 found the field whole (an empty cell is otherwise a planting
						# that failed when another drone took the last carrots first)
						break
					if e != Entities.Dead_Pumpkin and e != None:
						harvest()
					if num_items(Items.Carrot) < seed:
						return 0
					soil()
					plant(Entities.Pumpkin)
					pk_wet2()
					if not alone:
						nt.append(t)
						break
		todo = nt
	return 0


def pumpkin_round(goal):
	# every drone returns once its columns have grown, so the field is one pumpkin by then
	d = drones()
	if PK_ALL and width() > 1:
		d = min(max_drones(), width() * get_world_size())
	n = get_world_size()
	r = 0
	if PK_PERS and d >= PK_PERS_MIN and n >= 6:
		# several rounds with the same drones: drone 0 harvests once the field has merged and
		# the others replant as soon as their cells are cut
		per = n * n * 6 * lvl_mult(Unlocks.Pumpkins)
		r = min((goal - num_items(Items.Pumpkin) + per - 1) // per, num_items(Items.Carrot) // (n * n * get_cost(Entities.Pumpkin)[Items.Carrot] * PK_PERS_C))
	if r >= 2:
		fan(pk_job, 0, d, d, r)
	else:
		fan(pk_job, 0, d, d, 0)
	if get_entity_type() == Entities.Pumpkin:
		harvest()




# ---- cactus ------------------------------------------------------------------------------------
# Entry point: cactus_round(weird). weird=True makes the cactus weird as they are planted (each
# drone tracks its cactus' weird flags through its swaps, see bd_job).
# The field is not sorted whole. Cactus go on 2-wide antidiagonal bands (cells with x + y = s or
# s + 1) separated by an empty diagonal, the bands joined into one snake by a connector cell in
# each empty diagonal, at the field edge. A band cell's band neighbours all lie on the other
# diagonal of its band, so a cell on s is "pure low" (it only has to be no bigger than its
# neighbours) and one on s + 1 "pure high": swapping an out-of-order pair of pure cells moves both
# values the safe way and never breaks another pair, so each edge is fixed once, by one
# compare-and-swap. Only the connectors and the cells next to them are "mixed" (smaller and bigger
# neighbours both), a chain over five diagonals that is settled with a short work list. The harvest
# pops the whole snake: about 45% of the cells (97 on 12x12, 172 on 16x16) for 45% of a full
# field's yield, in a quarter of the time a full sort takes.
# Every drone takes a stretch of the snake: it walks there, plants it forwards fixing each cell
# against the ones before it, then walks back over the last part of the stretch fixing it while
# the cactus grow (the 1 s growth wait is otherwise idle). Where two stretches meet, the earlier
# drone fixes the shared edge once it has planted its last cell. BD_CUTS holds stretches and walk
# backs planned offline for the field sizes and drone counts the run uses (a cost model of
# travel, planting, fixes and connectors, fitted to the simulator, in bd_cuts); any other size cuts the snake
# evenly, away from the connectors, and fixes everything while planting.

BANDS = {}
BD_OFF = 0
BD_GROW = 1.0


def bd_cuts():
	# n * 1000 + drones: (first cell of each stretch, cells fixed on the walk back). A function, so
	# the table costs nothing until the first cactus round
	return {12004: ([0, 24, 44, 72, 97], [9, 14, 5, 5]), 12008: ([0, 10, 20, 37, 53, 65, 73, 87, 97], [5, 4, 7, 5, 10, 2, 5, 5]), 16008: ([0, 20, 43, 66, 88, 112, 134, 159, 172], [8, 13, 15, 10, 8, 8, 8, 7]), 16016: ([0, 10, 19, 33, 46, 53, 69, 82, 97, 110, 126, 139, 146, 153, 159, 166, 172], [8, 3, 8, 11, 1, 14, 8, 13, 8, 14, 8, 5, 1, 4, 1, 1])}


def bd_cells(n, s):
	# the band on diagonals s and s + 1, as a staircase from the top-left end
	r = []
	for i in range(n):
		if 0 <= s + 1 - i and s + 1 - i < n:
			r.append((i, s + 1 - i))
		if 0 <= s - i and s - i < n:
			r.append((i, s - i))
	return r


def bd_path(n, o):
	# the snake: bands on s = o - 3, o, o + 3, ..., every other one walked backwards, each joined
	# to the next by a connector on s + 2 (dropping up to two cells at the band ends to reach it)
	path = []
	j = 0
	ps = 0
	s = o - 3
	while s <= 2 * n - 2:
		b = bd_cells(n, s)
		if len(b) > 0:
			if j % 2 == 1:
				r = []
				for k in range(len(b) - 1, -1, -1):
					r.append(b[k])
				b = r
			if len(path) == 0:
				path = b
			else:
				best = None
				for da in range(3):
					for db in range(3):
						if da < len(path) and db < len(b):
							E = path[len(path) - 1 - da]
							F = b[db]
							if E[0] + E[1] == ps + 1 and F[0] + F[1] == ps + 3:
								for C in [(E[0] + 1, E[1]), (E[0], E[1] + 1)]:
									if C[0] < n and C[1] < n and abs(C[0] - F[0]) + abs(C[1] - F[1]) == 1:
										if best == None or da + db < best[0]:
											best = (da + db, da, db, C)
				if best == None:
					return path
				for _ in range(best[1]):
					path.pop()
				path.append(best[3])
				for k in range(best[2], len(b)):
					path.append(b[k])
			ps = s
			j += 1
		s += 3
	return path


def bd_plan(n, d):
	# (path, F, B, NB, MX, (cuts, walk backs), SP, LW, SQ, LO, UP), built once per size
	key = n * 1000 + d
	if key in BANDS:
		return BANDS[key]
	path = bd_path(n, BD_OFF)
	L = len(path)
	idx = {}
	for k in range(L):
		idx[path[k]] = k
	F = [None]
	B = [None]
	NB = []
	MX = []
	for k in range(L):
		x = path[k][0]
		y = path[k][1]
		if k < L - 1:
			F.append(step_dir(x, y, path[k + 1][0], path[k + 1][1]))
			B.append(step_dir(path[k + 1][0], path[k + 1][1], x, y))
		# neighbours: (dir, index, is_lower)
		nb = []
		lo = 0
		up = 0
		if (x, y - 1) in idx:
			nb.append((South, idx[(x, y - 1)], True))
			lo += 1
		if (x - 1, y) in idx:
			nb.append((West, idx[(x - 1, y)], True))
			lo += 1
		if (x, y + 1) in idx:
			nb.append((North, idx[(x, y + 1)], False))
			up += 1
		if (x + 1, y) in idx:
			nb.append((East, idx[(x + 1, y)], False))
			up += 1
		NB.append(nb)
		MX.append(lo > 0 and up > 0)
	cuts = bd_cuts()
	if key in cuts:
		cut = cuts[key]
	else:
		# even stretches, cut away from mixed cells and their neighbours, nothing deferred
		near = []
		for k in range(L):
			near.append(MX[k])
		for k in range(L):
			if MX[k]:
				for e in NB[k]:
					near[e[1]] = True
		cs = [0]
		cm = []
		for i in range(1, d):
			t = i * L // d
			k = t
			while k < L - 1 and (near[k] or near[k - 1]):
				k += 1
			k2 = t
			while k2 > 1 and (near[k2] or near[k2 - 1]):
				k2 -= 1
			if t - k2 < k - t and not (near[k2] or near[k2 - 1]):
				k = k2
			if k <= cs[len(cs) - 1]:
				k = cs[len(cs) - 1] + 1
			cs.append(k)
			cm.append(0)
		cs.append(L)
		cm.append(0)
		cut = (cs, cm)
	# SP / SQ: a pure cell whose only neighbour fixed before it is the previous cell (planting
	# forwards) / the next cell (walking back), neither mixed: one compare-and-swap with it.
	# LW: is cell k + 1 an upper neighbour of cell k? LO / UP: lower / upper neighbours (dir, index)
	SP = []
	SQ = []
	LW = []
	LO = []
	UP = []
	for k in range(L):
		ear = []
		lat = []
		lo = []
		up = []
		lw = False
		for e in NB[k]:
			if e[1] < k:
				ear.append(e)
			else:
				lat.append(e)
			if e[2]:
				lo.append((e[0], e[1]))
			else:
				up.append((e[0], e[1]))
			if e[1] == k + 1:
				lw = not e[2]
		sp = None
		if not MX[k] and len(ear) == 1 and ear[0][1] == k - 1 and not MX[k - 1]:
			sp = (ear[0][0], ear[0][2])
		sq = None
		if not MX[k] and len(lat) == 1 and lat[0][1] == k + 1 and not MX[k + 1]:
			sq = (lat[0][0], lat[0][2])
		SP.append(sp)
		SQ.append(sq)
		LW.append(lw)
		LO.append(lo)
		UP.append(up)
	plan = (path, F, B, NB, MX, cut, SP, LW, SQ, LO, UP)
	BANDS[key] = plan
	return plan


def cactus3_job(i, d, a):
	# Band layout: the antidiagonals x + y = 3 mod 4 stay empty but for one connector cell each
	# (at a field edge), so the field is a chain of 3-wide bands. In a band the low and high
	# diagonals only touch the middle one: fixing a middle cell (swap with its largest lower or
	# smallest upper neighbour until it fits) only ever improves the other cells, so one pass over
	# the middles sorts a band. Each connector, with the cells either side of it along the edge,
	# is a short chain (one cell beside it is left empty for that), sorted by one drone.
	# The tables come from cactus_round.
	n = get_world_size()
	CN = CJ_S[0]
	DR = CJ_S[1]
	JC = CJ_S[2]
	px = []
	py = []
	for g in range(CJ_S[3][i], CJ_S[3][i + 1]):
		x = g // n
		y = g % n
		if x % 2 == 1:
			y = n - 1 - y
		if CJ_S[4][i]:
			px.insert(0, x)
			py.insert(0, y)
		else:
			px.append(x)
			py.append(y)
	L = len(px)
	wd = a[0]
	R = a[1]
	w0 = num_items(Items.Weird_Substance)
	k1 = 0
	while not (((px[k1] + py[k1]) % 4 != 3 and not (px[k1], py[k1]) in DR) or (px[k1], py[k1]) in CN):
		k1 += 1
	# sunflowers on my path's empty cells (a few ballast ones with fewer than 12 petals that
	# stay, so 10 always stand)
	sfi = {}
	if a[2]:
		for k in range(L):
			x = px[k]
			y = py[k]
			if not (((x + y) % 4 != 3 and not (x, y) in DR) or (x, y) in CN):
				sfi[k] = (x + 4 * y) % 6 == 0
	for r in range(R):
		if r > 0:
			# the harvest pops my cell
			while get_entity_type() == Entities.Cactus:
				pass
		act = 0
		if len(sfi) > 0:
			p = (a[3] + r) % 7
			if p == 0:
				if a[4] - a[3] - r - 1 >= 2 + 4:
					act = 1
			elif p > 2:
				act = 2
				lv = 15 - (p - 2 - 1)
		go(px[0], py[0])
		tl = get_time()
		for k in range(L):
			x = px[k]
			y = py[k]
			if ((x + y) % 4 != 3 and not (x, y) in DR) or (x, y) in CN:
				if get_entity_type() != Entities.Cactus:
					clear_cell()
					soil()
					plant(Entities.Cactus)
					tl = get_time()
			elif get_entity_type() != None:
				if wd or not k in sfi or get_entity_type() != Entities.Sunflower:
					harvest()
			if k < L - 1:
				move(step_dir(x, y, px[k + 1], py[k + 1]))
		# back along the path: fix the middles
		k = L - 1
		while k >= 0:
			x = px[k]
			y = py[k]
			if act > 0 and k in sfi:
				if act == 1:
					if get_entity_type() == None and num_items(Items.Carrot) > 2000:
						soil()
						plant(Entities.Sunflower)
						if sfi[k]:
							while measure() >= 12:
								harvest()
								plant(Entities.Sunflower)
						else:
							while measure() < 12:
								harvest()
								plant(Entities.Sunflower)
				elif get_entity_type() == Entities.Sunflower and measure() >= lv and can_harvest():
					harvest()
			if (x + y) % 4 == 1 and not (x, y) in JC and not (x, y) in DR:
				f = (x < n - 1 and not (x + 1, y) in DR, y < n - 1 and not (x, y + 1) in DR, x > 0 and not (x - 1, y) in DR, y > 0 and not (x, y - 1) in DR)
				while True:
					h = measure()
					e = h
					if f[0]:
						e = measure(East)
						while e == None:
							e = measure(East)
					nn = h
					if f[1]:
						nn = measure(North)
						while nn == None:
							nn = measure(North)
					w = h
					if f[2]:
						w = measure(West)
						while w == None:
							w = measure(West)
					s = h
					if f[3]:
						s = measure(South)
						while s == None:
							s = measure(South)
					if w > s:
						if w > h:
							swap(West)
							continue
					elif s > h:
						swap(South)
						continue
					if e < nn:
						if e < h:
							swap(East)
							continue
					elif nn < h:
						swap(North)
						continue
					break
			if wd and (x + 2 * y) % 5 == 0 and num_items(Items.Weird_Substance) >= 1 and get_entity_type() == Entities.Cactus:
				# a weird round: weird substance turns this cactus and its neighbours (the centres
				# cover the field once)
				use_item(Items.Weird_Substance)
			if k > 0:
				move(step_dir(px[k], py[k], px[k - 1], py[k - 1]))
			k -= 1
		for ch in CJ_S[5][i]:
			cj_sort(ch)
		tl += 1.0
		while get_time() < tl:
			pass
		if r < R - 1:
			# done: drone 0 harvests once every other drone has used two weird substance (the
			# second use undoes the first's weird cactus), then all go on with the next round
			if i == 0:
				if len(sfi) > 0:
					# a sunflower toggled weird by a drone's signal and cut (4 weird substance)
					# would keep the count up: go on once it has stood still for a while
					c0 = num_items(Items.Weird_Substance)
					t0 = get_time()
					while c0 > w0 - 2 * (d - 1):
						c = num_items(Items.Weird_Substance)
						if c != c0:
							c0 = c
							t0 = get_time()
						elif get_time() > t0 + 2.5 and (c0 - w0 + 2 * (d - 1)) % 4 == 0:
							break
				else:
					while num_items(Items.Weird_Substance) > w0 - 2 * (d - 1):
						pass
				if get_entity_type() != Entities.Cactus:
					go(0, 0)
				harvest()
				w0 = num_items(Items.Weird_Substance)
			else:
				if get_entity_type() != Entities.Cactus:
					go(px[k1], py[k1])
				use_item(Items.Weird_Substance)
				use_item(Items.Weird_Substance)
	return 0


def bd_job(i, d, x):
	# stretch i: walk to its first cell a, plant forwards to b - 1 (fixing the cells before f as
	# they are planted), fix the edge to the next stretch, walk back to f fixing the rest, then
	# wait until the last cactus planted here has grown. x = (plan, weird)
	pl = x[0]
	wd = x[1]
	path = pl[0]
	F = pl[1]
	B = pl[2]
	MX = pl[4]
	SP = pl[6]
	SQ = pl[8]
	LO = pl[9]
	UP = pl[10]
	a = pl[5][0][i]
	b = pl[5][0][i + 1]
	f = b - pl[5][1][i]
	go(path[a][0], path[a][1])
	tl = get_time()
	wf = None
	if wd:
		# weird flags of this stretch's cactus, kept through the swaps (index - a)
		wf = []
		for k in range(a, b):
			wf.append(False)
	for k in range(a, b):
		if k > a:
			move(F[k])
		if get_entity_type() != Entities.Cactus:
			clear_cell()
			soil()
			plant(Entities.Cactus)
			tl = get_time()
		if k > a and k < f:
			sp = SP[k]
			if sp == None:
				bd_settle(k, a, f, b, False, LO, UP, MX, path, wf)
			else:
				v = measure()
				w = measure(sp[0])
				if sp[1]:
					if w > v:
						swap(sp[0])
						if wd:
							t = wf[k - a]
							wf[k - a] = wf[k - a - 1]
							wf[k - a - 1] = t
				elif w < v:
					swap(sp[0])
					if wd:
						t = wf[k - a]
						wf[k - a] = wf[k - a - 1]
						wf[k - a - 1] = t
		if wd and k > a and not wf[k - a - 1]:
			# weird substance turns this cactus and its planted neighbours. Used whenever the
			# cactus before this one is not weird yet: everything behind stays weird, and a
			# cactus left plain here (it was weird, or a swap moved a weird one in) is paired
			# with the next one
			if num_items(Items.Weird_Substance) >= 1:
				use_item(Items.Weird_Substance)
			elif num_items(Items.Fertilizer) >= 1:
				use_item(Items.Fertilizer)
			wf[k - a] = not wf[k - a]
			for e in LO[k]:
				if e[1] >= a and e[1] < k:
					wf[e[1] - a] = not wf[e[1] - a]
			for e in UP[k]:
				if e[1] >= a and e[1] < k:
					wf[e[1] - a] = not wf[e[1] - a]
	if b < len(path):
		# the edge to the next stretch's first cell, planted when its drone arrived
		v = measure()
		dd = F[b]
		w = measure(dd)
		if w != None:
			if pl[7][b - 1]:
				if w < v:
					swap(dd)
			elif w > v:
				swap(dd)
	k = b - 1
	while k >= f:
		sp = SQ[k]
		if sp == None or k == f or k == b - 1:
			bd_settle(k, a, f, b, True, LO, UP, MX, path, wf)
		else:
			v = measure()
			w = measure(sp[0])
			if sp[1]:
				if w > v:
					swap(sp[0])
			elif w < v:
				swap(sp[0])
			# (the flags are not needed after the forward pass: swaps keep the count)
		if k > f:
			move(B[k])
		k -= 1
	t = tl + BD_GROW
	while get_time() < t:
		pass
	return 0


def bd_cells_n():
	# cactus in one round of the 3-wide band layout, for yield estimates (cells squared times the
	# cactus multiplier): the field less the empty diagonals, plus a connector in each and less
	# the cell left empty beside each connector that is not in a corner
	n = get_world_size()
	c = n * n
	q = 3
	while q <= 2 * n - 2:
		if q <= n - 1:
			c -= q
		else:
			c -= 2 * n - 2 - q
		if q != n - 1:
			c -= 1
		q += 4
	return c


def cj_fix(k, ch, V, wl):
	# make chain cell k (the drone stands on it) fit all its neighbours: swap with the largest
	# lower or smallest upper neighbour out of order until none is; cells a swap changed go on wl
	NB = ch[1][k]
	while True:
		h = measure()
		while h == None:
			h = measure()
		V[k] = h
		for e in NB:
			z = measure(DIRS[e[0]])
			while z == None:
				z = measure(DIRS[e[0]])
			V[e[1]] = z
		ml = -1
		mu = 10
		el = None
		eu = None
		for e in NB:
			z = V[e[1]]
			if e[2]:
				if z > ml:
					ml = z
					el = e
			elif z < mu:
				mu = z
				eu = e
		if ml > h:
			if mu < h and h - mu >= ml - h:
				el = eu
		elif mu < h:
			el = eu
		else:
			break
		swap(DIRS[el[0]])
		V[k] = V[el[1]]
		V[el[1]] = h
		if el[1] < ch[2]:
			wl[el[1]] = True


def cj_sort(ch):
	# one junction chain: every cell fixed in order, then (values kept in V) the nearest cell a
	# swap may have put out of order, until none is
	R = ch[0]
	NB = ch[1]
	m = ch[2]
	V = []
	wl = []
	for _ in R:
		V.append(-1)
	for k in range(m):
		wl.append(False)
	for k in range(m):
		go(R[k][0], R[k][1])
		cj_fix(k, ch, V, wl)
	while True:
		x0 = get_pos_x()
		y0 = get_pos_y()
		best = -1
		bd = 999
		for k in range(m):
			if wl[k]:
				h = V[k]
				bad = False
				for e in NB[k]:
					z = V[e[1]]
					if e[2]:
						if z > h:
							bad = True
					elif z < h:
						bad = True
				if bad:
					dd = abs(R[k][0] - x0) + abs(R[k][1] - y0)
					if dd < bd:
						bd = dd
						best = k
				else:
					wl[k] = False
		if best < 0:
			break
		wl[best] = False
		go(R[best][0], R[best][1])
		cj_fix(best, ch, V, wl)


def cactus_round(weird, R):
	global CJ_N
	global CJ_S
	d = drones()
	n = get_world_size()
	if d <= 4 and n * 1000 + d in bd_cuts():
		if n * 1000 + d == 12004 and not 12004 in BANDS:
			# bd_plan(12, 4) written out (saves 3 s of compute)
			BANDS[12004] = ([(0,1),(0,0),(1,0),(2,0),(3,0),(3,1),(2,1),(2,2),(1,2),(1,3),(0,3),(0,4),(0,5),(0,6),(1,6),(1,5),(2,5),(2,4),(3,4),(3,3),(4,3),(4,2),(5,2),(5,1),(6,1),(6,0),(7,0),(8,0),(9,0),(9,1),(8,1),(8,2),(7,2),(7,3),(6,3),(6,4),(5,4),(5,5),(4,5),(4,6),(3,6),(3,7),(2,7),(2,8),(1,8),(1,9),(0,9),(0,10),(1,10),(1,11),(2,11),(2,10),(3,10),(3,9),(4,9),(4,8),(5,8),(5,7),(6,7),(6,6),(7,6),(7,5),(8,5),(8,4),(9,4),(9,3),(10,3),(10,2),(11,2),(11,3),(11,4),(11,5),(10,5),(10,6),(9,6),(9,7),(8,7),(8,8),(7,8),(7,9),(6,9),(6,10),(5,10),(5,11),(6,11),(7,11),(8,11),(8,10),(9,10),(9,9),(10,9),(10,8),(11,8),(11,9),(11,10),(11,11),(10,11)],[None,South,East,East,East,North,West,North,West,North,West,North,North,North,East,South,East,South,East,South,East,South,East,South,East,South,East,East,East,North,West,North,West,North,West,North,West,North,West,North,West,North,West,North,West,North,West,North,East,North,East,South,East,South,East,South,East,South,East,South,East,South,East,South,East,South,East,South,East,North,North,North,West,North,West,North,West,North,West,North,West,North,West,North,East,East,East,South,East,South,East,South,East,North,North,North,West],[None,North,West,West,West,South,East,South,East,South,East,South,South,South,West,North,West,North,West,North,West,North,West,North,West,North,West,West,West,South,East,South,East,South,East,South,East,South,East,South,East,South,East,South,East,South,East,South,West,South,West,North,West,North,West,North,West,North,West,North,West,North,West,North,West,North,West,North,West,South,South,South,East,South,East,South,East,South,East,South,East,South,East,South,West,West,West,North,West,North,West,North,West,South,South,South,East],[[(South,1,True)],[(North,0,False),(East,2,False)],[(West,1,True),(East,3,False)],[(West,2,True),(North,6,False),(East,4,False)],[(West,3,True),(North,5,False)],[(South,4,True),(West,6,True)],[(South,3,True),(North,7,False),(East,5,False)],[(South,6,True),(West,8,True)],[(North,9,False),(East,7,False)],[(South,8,True),(West,10,True)],[(North,11,False),(East,9,False)],[(South,10,True),(North,12,False)],[(South,11,True),(North,13,False),(East,15,False)],[(South,12,True),(East,14,False)],[(South,15,True),(West,13,True)],[(West,12,True),(North,14,False),(East,16,False)],[(South,17,True),(West,15,True)],[(North,16,False),(East,18,False)],[(South,19,True),(West,17,True)],[(North,18,False),(East,20,False)],[(South,21,True),(West,19,True)],[(North,20,False),(East,22,False)],[(South,23,True),(West,21,True)],[(North,22,False),(East,24,False)],[(South,25,True),(West,23,True)],[(North,24,False),(East,26,False)],[(West,25,True),(East,27,False)],[(West,26,True),(North,30,False),(East,28,False)],[(West,27,True),(North,29,False)],[(South,28,True),(West,30,True)],[(South,27,True),(North,31,False),(East,29,False)],[(South,30,True),(West,32,True)],[(North,33,False),(East,31,False)],[(South,32,True),(West,34,True)],[(North,35,False),(East,33,False)],[(South,34,True),(West,36,True)],[(North,37,False),(East,35,False)],[(South,36,True),(West,38,True)],[(North,39,False),(East,37,False)],[(South,38,True),(West,40,True)],[(North,41,False),(East,39,False)],[(South,40,True),(West,42,True)],[(North,43,False),(East,41,False)],[(South,42,True),(West,44,True)],[(North,45,False),(East,43,False)],[(South,44,True),(West,46,True),(North,48,False)],[(North,47,False),(East,45,False)],[(South,46,True),(East,48,False)],[(South,45,True),(West,47,True),(North,49,False),(East,51,False)],[(South,48,True),(East,50,False)],[(South,51,True),(West,49,True)],[(West,48,True),(North,50,False),(East,52,False)],[(South,53,True),(West,51,True)],[(North,52,False),(East,54,False)],[(South,55,True),(West,53,True)],[(North,54,False),(East,56,False)],[(South,57,True),(West,55,True)],[(North,56,False),(East,58,False)],[(South,59,True),(West,57,True)],[(North,58,False),(East,60,False)],[(South,61,True),(West,59,True)],[(North,60,False),(East,62,False)],[(South,63,True),(West,61,True)],[(North,62,False),(East,64,False)],[(South,65,True),(West,63,True)],[(North,64,False),(East,66,False)],[(South,67,True),(West,65,True),(East,69,False)],[(North,66,False),(East,68,False)],[(West,67,True),(North,69,False)],[(South,68,True),(West,66,True),(North,70,False)],[(South,69,True),(North,71,False)],[(South,70,True),(West,72,True)],[(North,73,False),(East,71,False)],[(South,72,True),(West,74,True)],[(North,75,False),(East,73,False)],[(South,74,True),(West,76,True)],[(North,77,False),(East,75,False)],[(South,76,True),(West,78,True)],[(North,79,False),(East,77,False)],[(South,78,True),(West,80,True)],[(North,81,False),(East,79,False)],[(South,80,True),(West,82,True),(North,84,False)],[(North,83,False),(East,81,False)],[(South,82,True),(East,84,False)],[(South,81,True),(West,83,True),(East,85,False)],[(West,84,True),(East,86,False)],[(South,87,True),(West,85,True)],[(North,86,False),(East,88,False)],[(South,89,True),(West,87,True)],[(North,88,False),(East,90,False)],[(South,91,True),(West,89,True),(East,93,False)],[(North,90,False),(East,92,False)],[(West,91,True),(North,93,False)],[(South,92,True),(West,90,True),(North,94,False)],[(South,93,True),(North,95,False)],[(South,94,True),(West,96,True)],[(East,95,False)]],[False,False,True,True,True,False,True,False,False,False,False,True,True,True,False,True,False,False,False,False,False,False,False,False,False,False,True,True,True,False,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,False,True,True,True,False,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,False,True,True,True,False,False,False,False,False,False,False,False,False,False,True,False,True,True,True,False,False,False,False,True,False,True,True,True,False,False],([0,24,44,72,97],[9,14,5,5]),[None,(North,False),None,None,None,None,None,None,(East,False),(South,True),(East,False),None,None,None,None,None,None,(North,False),(West,True),(North,False),(West,True),(North,False),(West,True),(North,False),(West,True),(North,False),None,None,None,None,None,None,(East,False),(South,True),(East,False),(South,True),(East,False),(South,True),(East,False),(South,True),(East,False),(South,True),(East,False),(South,True),(East,False),None,None,None,None,None,None,None,None,(North,False),(West,True),(North,False),(West,True),(North,False),(West,True),(North,False),(West,True),(North,False),(West,True),(North,False),(West,True),(North,False),None,None,None,None,None,None,(East,False),(South,True),(East,False),(South,True),(East,False),(South,True),(East,False),(South,True),(East,False),None,None,None,None,None,None,(North,False),(West,True),(North,False),None,None,None,None,None,None,(East,False)],[False,True,True,True,True,False,True,False,True,False,True,True,True,True,False,True,False,True,False,True,False,True,False,True,False,True,True,True,True,False,True,False,True,False,True,False,True,False,True,False,True,False,True,False,True,False,True,True,True,True,False,True,False,True,False,True,False,True,False,True,False,True,False,True,False,True,False,True,True,True,True,False,True,False,True,False,True,False,True,False,True,False,True,True,True,True,False,True,False,True,False,True,True,True,True,False,False],[(South,True),None,None,None,None,None,None,(West,True),(North,False),(West,True),None,None,None,None,None,None,(South,True),(East,False),(South,True),(East,False),(South,True),(East,False),(South,True),(East,False),(South,True),None,None,None,None,None,None,(West,True),(North,False),(West,True),(North,False),(West,True),(North,False),(West,True),(North,False),(West,True),(North,False),(West,True),(North,False),(West,True),None,None,None,None,None,None,None,None,(South,True),(East,False),(South,True),(East,False),(South,True),(East,False),(South,True),(East,False),(South,True),(East,False),(South,True),(East,False),(South,True),None,None,None,None,None,None,(West,True),(North,False),(West,True),(North,False),(West,True),(North,False),(West,True),(North,False),(West,True),None,None,None,None,None,None,(South,True),(East,False),(South,True),None,None,None,None,None,None,(West,True),None],[[(South,1)],[],[(West,1)],[(West,2)],[(West,3)],[(South,4),(West,6)],[(South,3)],[(South,6),(West,8)],[],[(South,8),(West,10)],[],[(South,10)],[(South,11)],[(South,12)],[(South,15),(West,13)],[(West,12)],[(South,17),(West,15)],[],[(South,19),(West,17)],[],[(South,21),(West,19)],[],[(South,23),(West,21)],[],[(South,25),(West,23)],[],[(West,25)],[(West,26)],[(West,27)],[(South,28),(West,30)],[(South,27)],[(South,30),(West,32)],[],[(South,32),(West,34)],[],[(South,34),(West,36)],[],[(South,36),(West,38)],[],[(South,38),(West,40)],[],[(South,40),(West,42)],[],[(South,42),(West,44)],[],[(South,44),(West,46)],[],[(South,46)],[(South,45),(West,47)],[(South,48)],[(South,51),(West,49)],[(West,48)],[(South,53),(West,51)],[],[(South,55),(West,53)],[],[(South,57),(West,55)],[],[(South,59),(West,57)],[],[(South,61),(West,59)],[],[(South,63),(West,61)],[],[(South,65),(West,63)],[],[(South,67),(West,65)],[],[(West,67)],[(South,68),(West,66)],[(South,69)],[(South,70),(West,72)],[],[(South,72),(West,74)],[],[(South,74),(West,76)],[],[(South,76),(West,78)],[],[(South,78),(West,80)],[],[(South,80),(West,82)],[],[(South,82)],[(South,81),(West,83)],[(West,84)],[(South,87),(West,85)],[],[(South,89),(West,87)],[],[(South,91),(West,89)],[],[(West,91)],[(South,92),(West,90)],[(South,93)],[(South,94),(West,96)],[]],[[],[(North,0),(East,2)],[(East,3)],[(North,6),(East,4)],[(North,5)],[],[(North,7),(East,5)],[],[(North,9),(East,7)],[],[(North,11),(East,9)],[(North,12)],[(North,13),(East,15)],[(East,14)],[],[(North,14),(East,16)],[],[(North,16),(East,18)],[],[(North,18),(East,20)],[],[(North,20),(East,22)],[],[(North,22),(East,24)],[],[(North,24),(East,26)],[(East,27)],[(North,30),(East,28)],[(North,29)],[],[(North,31),(East,29)],[],[(North,33),(East,31)],[],[(North,35),(East,33)],[],[(North,37),(East,35)],[],[(North,39),(East,37)],[],[(North,41),(East,39)],[],[(North,43),(East,41)],[],[(North,45),(East,43)],[(North,48)],[(North,47),(East,45)],[(East,48)],[(North,49),(East,51)],[(East,50)],[],[(North,50),(East,52)],[],[(North,52),(East,54)],[],[(North,54),(East,56)],[],[(North,56),(East,58)],[],[(North,58),(East,60)],[],[(North,60),(East,62)],[],[(North,62),(East,64)],[],[(North,64),(East,66)],[(East,69)],[(North,66),(East,68)],[(North,69)],[(North,70)],[(North,71)],[],[(North,73),(East,71)],[],[(North,75),(East,73)],[],[(North,77),(East,75)],[],[(North,79),(East,77)],[],[(North,81),(East,79)],[(North,84)],[(North,83),(East,81)],[(East,84)],[(East,85)],[(East,86)],[],[(North,86),(East,88)],[],[(North,88),(East,90)],[(East,93)],[(North,90),(East,92)],[(North,93)],[(North,94)],[(North,95)],[],[(East,95)]])
		pl = bd_plan(n, d)
		if R == 0:
			return
		for r in range(R):
			fan(bd_job, 0, d, d, (pl, weird))
			if get_entity_type() != Entities.Cactus:
				go(pl[0][0][0], pl[0][0][1])
			harvest()
		return
	if CJ_N != n * 100 + d and n * 100 + d == 1616:
		# the 16x16 layout for 16 drones as worked out below, written out (saves 2.5 s of compute)
		CJ_N = 1616
		CJ_S = ({(0,3):True,(7,0):True,(0,11):True,(15,0):True,(4,15):True,(15,8):True,(12,15):True},{(1,3):True,(7,1):True,(1,11):True,(4,14):True,(14,8):True,(12,14):True},{(0,1):True,(0,2):True,(0,3):True,(0,4):True,(1,4):True,(0,5):True,(5,0):True,(6,0):True,(7,0):True,(8,0):True,(8,1):True,(9,0):True,(0,9):True,(0,10):True,(0,11):True,(0,12):True,(1,12):True,(0,13):True,(13,0):True,(14,0):True,(15,0):True,(15,1):True,(15,2):True,(3,14):True,(2,15):True,(3,15):True,(4,15):True,(5,15):True,(6,15):True,(14,7):True,(15,6):True,(15,7):True,(15,8):True,(15,9):True,(15,10):True,(11,14):True,(10,15):True,(11,15):True,(12,15):True,(13,15):True,(14,15):True},[0,10,18,41,62,85,90,98,120,141,162,183,203,225,237,247,256],[False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,False],[[([(0,1),(0,2),(0,3),(0,4),(1,4),(0,5),(1,1),(0,0),(1,5),(2,4),(0,6)],[[(0,1,False),(1,6,False),(2,7,True)],[(0,2,False),(2,0,True)],[(0,3,False),(2,1,True)],[(0,5,False),(1,4,False),(2,2,True)],[(0,8,False),(1,9,False),(3,3,True)],[(0,10,False),(1,8,False),(2,3,True)]],6)],[([(0,9),(0,10),(0,11),(0,12),(1,12),(0,13),(1,9),(0,8),(1,13),(2,12),(0,14)],[[(0,1,False),(1,6,False),(2,7,True)],[(0,2,False),(2,0,True)],[(0,3,False),(2,1,True)],[(0,5,False),(1,4,False),(2,2,True)],[(0,8,False),(1,9,False),(3,3,True)],[(0,10,False),(1,8,False),(2,3,True)]],6)],[],[],[],[([(5,0),(6,0),(7,0),(8,0),(8,1),(9,0),(5,1),(4,0),(8,2),(9,1),(10,0)],[[(0,6,False),(1,1,False),(3,7,True)],[(1,2,False),(3,0,True)],[(1,3,False),(3,1,True)],[(0,4,False),(1,5,False),(3,2,True)],[(0,8,False),(1,9,False),(2,3,True)],[(0,9,False),(1,10,False),(3,3,True)]],6)],[([(6,15),(5,15),(4,15),(3,15),(2,15),(3,14),(7,15),(6,14),(2,14),(1,15),(3,13)],[[(1,6,False),(2,7,True),(3,1,True)],[(1,0,False),(3,2,True)],[(1,1,False),(3,3,True)],[(1,2,False),(2,5,True),(3,4,True)],[(1,3,False),(2,8,True),(3,9,True)],[(0,3,False),(2,10,True),(3,8,True)]],6)],[],[],[],[],[],[],[([(13,0),(14,0),(15,0),(15,1),(15,2),(13,1),(12,0),(15,3),(14,2)],[[(0,5,False),(1,1,False),(3,6,True)],[(1,2,False),(3,0,True)],[(0,3,False),(3,1,True)],[(0,4,False),(2,2,True)],[(0,7,False),(2,3,True),(3,8,True)]],5)],[([(14,15),(13,15),(12,15),(11,15),(10,15),(11,14),(15,15),(14,14),(10,14),(9,15),(11,13)],[[(1,6,False),(2,7,True),(3,1,True)],[(1,0,False),(3,2,True)],[(1,1,False),(3,3,True)],[(1,2,False),(2,5,True),(3,4,True)],[(1,3,False),(2,8,True),(3,9,True)],[(0,3,False),(2,10,True),(3,8,True)]],6)],[([(14,7),(15,6),(15,7),(15,8),(15,9),(15,10),(14,6),(13,7),(15,5),(15,11),(14,10)],[[(1,2,False),(2,6,True),(3,7,True)],[(0,2,False),(2,8,True),(3,6,True)],[(0,3,False),(2,1,True),(3,0,True)],[(0,4,False),(2,2,True)],[(0,5,False),(2,3,True)],[(0,9,False),(2,4,True),(3,10,True)]],6)]])
	if CJ_N != n * 100 + d:
		# the band layout, worked out once per field size: connectors, the cells left empty beside
		# them, the junction chains and each drone's path with what to do on every cell
		CJ_N = n * 100 + d
		CN = {}
		DR = {}
		CH = []
		q = 3
		while q <= 2 * n - 2:
			if (q // 4) % 2 == 0:
				if q < n - 1:
					c = (0, q)
					DR[(1, q)] = True
					ch = [(0, q - 2), (0, q - 1), c, (0, q + 1), (1, q + 1), (0, q + 2)]
				elif q == n - 1:
					c = (0, q)
					ch = [(0, q - 2), (0, q - 1), c, (1, q), (2, q)]
				else:
					x0 = q - n + 1
					c = (x0, n - 1)
					DR[(x0, n - 2)] = True
					ch = [(x0 - 1, n - 2), (x0 - 2, n - 1), (x0 - 1, n - 1), c, (x0 + 1, n - 1), (x0 + 2, n - 1)]
			else:
				if q < n - 1:
					c = (q, 0)
					DR[(q, 1)] = True
					ch = [(q - 2, 0), (q - 1, 0), c, (q + 1, 0), (q + 1, 1), (q + 2, 0)]
				elif q == n - 1:
					c = (q, 0)
					ch = [(q - 2, 0), (q - 1, 0), c, (q, 1), (q, 2)]
				else:
					y0 = q - n + 1
					c = (n - 1, y0)
					DR[(n - 2, y0)] = True
					ch = [(n - 2, y0 - 1), (n - 1, y0 - 2), (n - 1, y0 - 1), c, (n - 1, y0 + 1), (n - 1, y0 + 2)]
			CN[c] = True
			CH.append(ch)
			q += 4
		JC = {}
		for ch in CH:
			for b in ch:
				JC[b] = True
		# paths: the field's column-by-column snake (cell g is column g // n) cut into one stretch
		# per drone; each drone ends where its stretch started (plant out, fix back), or walks it
		# the other way round to end next to its junction. Junction drones get shorter stretches.
		N = n * n
		CUT = []
		for t in range(d + 1):
			CUT.append(t * N // d)
		HAS = []
		CO = []
		for it in range(2):
			RV = []
			OWN = []
			for t in range(d):
				RV.append(False)
				OWN.append([])
			for c in range(len(CH)):
				ch = CH[c]
				best = None
				for e in [0, len(ch) - 1]:
					cx = ch[e][0]
					cy = ch[e][1]
					if it > 0:
						t0 = CO[c]
						ts = [t0]
					else:
						g = cx * n + cy
						if cx % 2 == 1:
							g = cx * n + n - 1 - cy
						t0 = g * d // N
						ts = range(max(0, t0 - 1), min(d, t0 + 2))
					for t in ts:
						for r in [False, True]:
							if len(OWN[t]) > 0 and r != RV[t]:
								continue
							g = CUT[t]
							if r:
								g = CUT[t + 1] - 1
							ex = g // n
							ey = g % n
							if ex % 2 == 1:
								ey = n - 1 - ey
							ax = abs(cx - ex)
							ay = abs(cy - ey)
							cost = min(ax, n - ax) + min(ay, n - ay) + 1000 * len(OWN[t])
							if best == None or cost < best[0]:
								best = (cost, t, r, e)
				t = best[1]
				RV[t] = best[2]
				if it == 0:
					CO.append(t)
				cells = ch
				if best[3] > 0:
					cells = []
					for b in ch:
						cells.insert(0, b)
				OWN[t].append(cells)
			if it > 0:
				break
			# junction drones get CJ_D cells less per junction
			k = len(CH)
			acc = 0
			adj = []
			for t in range(d):
				adj.append(0)
			ad = {1616: [1, -1, 2, 0, 2, -4, -1, 0, 0, 0, 0, -1, 1, 3, 1, 0], 1204: [3, -2, -1, 0]}
			if n * 100 + d in ad:
				adj = ad[n * 100 + d]
			ma = 0
			for t in range(d):
				ma += adj[t] / d
			cd = CJ_D
			if d < 8:
				cd = CJ_D4
			for t in range(d):
				acc += (N + cd * k) / d - cd * len(OWN[t]) + adj[t] - ma
				CUT[t + 1] = min(N, (acc + 0.5) // 1)
			CUT[d] = N
		for t in range(d):
			cl2 = []
			for cells in OWN[t]:
				# R: the chain's cells, then the band cells next to them; NB[k]: (dir, index in R,
				# is lower) for chain cell k's cactus neighbours
				RC = []
				for b in cells:
					RC.append(b)
				m = len(RC)
				NB = []
				for b in cells:
					v = []
					for dd in range(4):
						x2 = b[0] + DX[dd]
						y2 = b[1] + DY[dd]
						if x2 >= 0 and x2 < n and y2 >= 0 and y2 < n and (((x2 + y2) % 4 != 3 and not (x2, y2) in DR) or (x2, y2) in CN):
							if not (x2, y2) in RC:
								RC.append((x2, y2))
							j = 0
							while RC[j] != (x2, y2):
								j += 1
							v.append((dd, j, dd >= 2))
					NB.append(v)
				cl2.append((RC, NB, m))
			OWN[t] = cl2
		CJ_S = (CN, DR, JC, CUT, RV, OWN)
	sf = not weird and d >= 16
	R0 = R
	if R > 1:
		# the first round on its own: plants it clears could yield weird substance, which the
		# drones of the rounds after it count to tell they are done
		fan(cactus3_job, 0, d, d, (weird, 1, sf, 0, R0))
		go(0, 0)
		harvest()
		R -= 1
	fan(cactus3_job, 0, d, d, (weird, R, sf, R0 - R, R0))
	if get_entity_type() != Entities.Cactus:
		go(0, 0)
	harvest()


# ---- mazes -------------------------------------------------------------------------------------

DIRS = [North, East, South, West]
DX = [0, 1, 0, -1]
DY = [1, 0, -1, 0]
BACK = [2, 3, 0, 1]
# a step's change of cell index (set for the maze's size in mz_explore)
DD = [0, 1, 0, -1]
MAZE_SECS = 90
POLY_FARM = True
WET_PK = True
WET_POLY = True

# ---- shared mazes --------------------------------------------------------------------------
# One maze over the whole field and one drone per start cell (the centres of a grid of blocks).
# Every drone stands on its start before the maze is made, then maps only its own part: a depth
# first walk from its start that stops at other drones' starts and drops whatever hangs off a
# path past the middle between two starts. A fresh maze is a tree, so the cells nearest a start
# along the maze follow from that walk alone and no drone needs anybody else's map: nothing is
# merged, nobody walks out from a leader, and each drone serves as soon as its own walk is done.
# A drone parks at the middle of its cells, goes for the treasure when it lands there (or close
# to its park, racing the owner), and on the way back tries the walls next to its path, since
# every use knocks a few out, then re-plans its shortest ways. A treasure left lying (a cell no
# map covers, from walls knocked out during the walks) is fetched by a drone that knows the cell
# after MZ_RESCUE s, or found by search by the drone of its block after MZ_LOST s. The gold
# count tells everybody when the 300 uses are spent: the owner of the last spot harvests, walks
# to its start and makes the next maze there once the others are back on theirs.

MZ_N = 0
MZ_ME = 0
MZ_PD = {}
MZ_DP = {}
MZ_OWN = {}
MZ_ROOT = 0
MZ_PARK = 0
MZ_CUR = 0
MZ_PATH = {}
MZ_ADJ = {}
MZ_PROBE = {}
MZ_SHORT = True
MZ_ORDER = -1
MZ_RACE = 4
MZ_PRUNE = True
MZ_RACE2 = 0
MZ_PRUNE_MIN = 2
MZ_LOST = 3.0
MZ_GX = 1
MZ_GY = 1
MZ_WAIT = 4
MZ_RESCUE = 1.0
MZ_PARKING = True
MZ_PARK_MIN = 2
MZ_NEXT = True
MZ_EXP_USE = 99
MZ_COST = 0
MZ_GOAL = 0
MZ_NEXT2 = True
MZ_VIA = True
MZ_UP = 0
MZ_EARLY = 4
MZ_RESCUE_E = 0.2
MZ_ADOPT = 4
MZ_AFTER_SUN = True
SUN_MZ = None
SUN_MZ_DONE = False
MZ_SUNW = 3
MZ_GXS = 4
# a maze that pays for two Megafarm levels: the main drone buys the first one mid-maze (MZ_BUY gold),
# then every drone hands half of its cells to a new drone instead of a new maze being made
MZ_BUY = 0
MZ_SPENT = 0
MZ_MD = 0
MZ_KID = None
MERGE_MF = True
# a wall on my map has come down: its shortest ways may leave the tree
MZ_SC = False
MZ_HEAL = True
MZ_HOME = True
MZ_HEALN = 24
# with at least this many cells of my own, ways only to my cells and those a race takes me to
MZ_PRX = 24
# for these drone counts (bits: 2, 4, 8, 16) half the drones map the maze, then each hands half
# of its cells (cut at one tree edge, so the halves are even) to a new drone
MZ_HALF = 2


def mz_starts(n, d):
	g = 1
	while (g + 1) * (g + 1) <= d:
		g += 1
	while d % g != 0:
		g -= 1
	gx = d // g
	st = []
	for j in range(g):
		for i in range(gx):
			st.append((2 * i + 1) * n // (2 * gx) + ((2 * j + 1) * n // (2 * g)) * n)
	return st


def mz_walk(a, b, lim):
	# along the map's tree from cell a to cell b, if that is under lim steps (True if walked)
	n = MZ_N
	pd = MZ_PD
	dp = MZ_DP
	up = []
	down = []
	while dp[a] > dp[b]:
		k = pd[a]
		up.append(BACK[k])
		a = a - DX[k] - DY[k] * n
	while dp[b] > dp[a]:
		k = pd[b]
		down.append(k)
		b = b - DX[k] - DY[k] * n
	while a != b:
		k = pd[a]
		up.append(BACK[k])
		a = a - DX[k] - DY[k] * n
		k = pd[b]
		down.append(k)
		b = b - DX[k] - DY[k] * n
	if len(up) + len(down) >= lim:
		return False
	for k in up:
		move(DIRS[k])
	for i in range(len(down) - 1, -1, -1):
		move(DIRS[down[i]])
	return True


def mz_paths(park):
	# shortest ways from the park over the sides known open, to my cells and to the walked cells
	# a race could take me to (and one step on)
	n = MZ_N
	adj = MZ_ADJ
	own = MZ_OWN
	race = MZ_RACE
	if len(own) < MZ_PRX:
		race = 999
	path = {park: []}
	q = [park]
	i = 0
	while i < len(q):
		x = q[i]
		i += 1
		px = path[x]
		if len(px) >= race and not (x in own):
			continue
		for k in adj[x]:
			y = x + DX[k] + DY[k] * n
			if not (y in path):
				path[y] = px + [k]
				q.append(y)
	return path


def mz_try(x):
	# try the untried sides of cell x (I stand on it); True if one turned out open
	n = MZ_N
	adj = MZ_ADJ
	if x in MZ_PROBE:
		pr = MZ_PROBE[x]
	else:
		px = x % n
		py = x // n
		pr = []
		for k in range(4):
			qx = px + DX[k]
			qy = py + DY[k]
			if qx >= 0 and qy >= 0 and qx < n and qy < n and (qx + qy * n) in adj and not (k in adj[x]):
				pr.append(k)
	if len(pr) == 0:
		MZ_PROBE[x] = pr
		return False
	keep = []
	got = False
	for k in pr:
		if can_move(DIRS[k]):
			y = x + DX[k] + DY[k] * n
			adj[x].append(k)
			adj[y].append(BACK[k])
			if y in MZ_PROBE:
				py = MZ_PROBE[y]
				b = BACK[k]
				if b in py:
					py.remove(b)
			got = True
		else:
			keep.append(k)
	MZ_PROBE[x] = keep
	return got


def mz_dist(a, b):
	n = MZ_N
	pd = MZ_PD
	dp = MZ_DP
	d = 0
	while dp[a] > dp[b]:
		k = pd[a]
		a = a - DX[k] - DY[k] * n
		d += 1
	while dp[b] > dp[a]:
		k = pd[b]
		b = b - DX[k] - DY[k] * n
		d += 1
	while a != b:
		k = pd[a]
		a = a - DX[k] - DY[k] * n
		k = pd[b]
		b = b - DX[k] - DY[k] * n
		d += 2
	return d


def mz_explore(si):
	# si: start cell -> drone index. Depth first from here, never into another start.
	global MZ_PD
	global MZ_DP
	global MZ_OWN
	global MZ_ROOT
	global MZ_PARK
	global MZ_CUR
	global MZ_PATH
	global MZ_ADJ
	global MZ_PROBE
	global MZ_SC
	n = MZ_N
	global DD
	DD = [n, 1, -n, -1]
	me = MZ_ME
	c = get_pos_x() + get_pos_y() * n
	root = c
	rx = c % n
	ry = c // n
	pd = {c: -1}
	dp = {c: 0}
	par = {c: c}
	adj = {c: []}
	order = [c]
	found = []
	stack = []
	kids = []
	ks = []
	for k in range(4):
		if can_move(DIRS[k]):
			nc = c + DX[k] + DY[k] * n
			if nc in dp:
				pass
			elif nc in si:
				pd[nc] = k
				dp[nc] = 1
				found.append(nc)
			else:
				ks.append(k)
	kids.append(ks)
	pending = len(ks)
	nd = 0
	while pending > 0:
		ks = kids[-1]
		if len(ks) > 0:
			k = ks.pop()
			pending -= 1
			nc = c + DD[k]
			if nc in dp:
				continue
			move(DIRS[k])
			if len(si) <= MZ_EXP_USE and get_entity_type() == Entities.Treasure and num_items(Items.Gold) < MZ_GOAL:
				use_item(Items.Weird_Substance, MZ_COST)
			stack.append(k)
			nd = dp[c] + 1
			adj[c].append(k)
			par[nc] = c
			c = nc
			pd[c] = k
			dp[c] = nd
			order.append(c)
			b = BACK[k]
			adj[c] = [b]
			ks = []
			ks2 = []
			hit = False
			tie = False
			# with MZ_ORDER -1 the sides back toward my start's row or column go last on the list
			# (explored first); tw[k] is (DX[k] * cx + DY[k] * cy) * MZ_ORDER > 0
			cx = c % n - rx
			cy = c // n - ry
			if MZ_ORDER < 0:
				tw = [cy < 0, cx < 0, cy > 0, cx > 0]
			elif MZ_ORDER > 0:
				tw = [cy > 0, cx > 0, cy < 0, cx < 0]
			else:
				tw = [False, False, False, False]
			for k2 in range(4):
				if k2 != b and can_move(DIRS[k2]):
					nc = c + DD[k2]
					if nc in dp:
						pass
					elif nc in si:
						pd[nc] = k2
						dp[nc] = nd + 1
						found.append(nc)
						hit = True
						if si[nc] < me:
							tie = True
					elif tw[k2]:
						ks2.append(k2)
					else:
						ks.append(k2)
			if len(ks2) > 0:
				ks = ks + ks2
			kids.append(ks)
			pending += len(ks)
			if MZ_PRUNE and hit and len(si) >= MZ_PRUNE_MIN:
				# whatever hangs off this path past its middle is the other drone's: skip it
				h = nd + 1
				L = nd
				while L >= 0 and (2 * L > h or (2 * L == h and tie)):
					pending -= len(kids[L])
					kids[L] = []
					L -= 1
		else:
			kids.pop()
			k = stack.pop()
			move(DIRS[BACK[k]])
			c = c - DD[k]
	# cut every path to another start at its middle (ties to the lower index)
	cut = {}
	for f in found:
		j = si[f]
		h = dp[f]
		k = pd[f]
		x = f - DX[k] - DY[k] * n
		while x != root:
			if 2 * dp[x] > h or (2 * dp[x] == h and j < me):
				cut[x] = True
				x = par[x]
			else:
				break
	own = {root: True}
	cnt = {root: 1}
	for i in range(1, len(order)):
		x = order[i]
		if par[x] in own and not (x in cut):
			own[x] = True
			cnt[x] = 1
		else:
			cnt[x] = 0
	for i in range(len(order) - 1, 0, -1):
		x = order[i]
		if cnt[x] > 0:
			cnt[par[x]] += cnt[x]
	tot = len(own)
	park = root
	for x in own:
		if 2 * cnt[x] > tot and dp[x] > dp[park]:
			park = x
	# adj: the open sides of every cell walked (tree edges for now; walls only ever come down)
	MZ_ADJ = adj
	MZ_OWN = own
	MZ_SC = False
	MZ_PROBE = {}
	path = mz_paths(park)
	MZ_PATH = path
	MZ_PD = pd
	MZ_DP = dp
	MZ_OWN = own
	MZ_ROOT = root
	MZ_PARK = park
	MZ_CUR = c


def mz_seek(tc, chase):
	# depth first toward cell tc, closer steps first; gives up once the treasure leaves tc.
	# Returns the moves made, a simple path from where it started.
	n = MZ_N
	tx = tc % n
	ty = tc // n
	c = get_pos_x() + get_pos_y() * n
	seen = {c: True}
	stack = []
	while c != tc:
		if chase:
			t = measure()
			if t == None or t[0] + t[1] * n != tc:
				return stack
		x = c % n
		y = c // n
		best = -1
		bd = 999
		for k in range(4):
			nc = c + DX[k] + DY[k] * n
			if not (nc in seen) and can_move(DIRS[k]):
				dd = abs(x + DX[k] - tx) + abs(y + DY[k] - ty)
				if dd < bd:
					bd = dd
					best = k
		if best >= 0:
			move(DIRS[best])
			stack.append(best)
			c = c + DX[best] + DY[best] * n
			seen[c] = True
		else:
			if len(stack) == 0:
				return stack
			k = stack.pop()
			move(DIRS[BACK[k]])
			c = c - DX[k] - DY[k] * n
	return stack


def mz_serve(goal, per, cost, g0, park):
	# 0: done, 1: the maze's uses are spent, 2: I harvested the spent maze
	global MZ_CUR
	global MZ_PATH
	global MZ_SC
	n = MZ_N
	own = MZ_OWN
	known = MZ_DP
	paths = MZ_PATH
	home = MZ_PARK
	race = MZ_RACE
	rep = 0
	lim = g0 + 300 * per
	cur = MZ_CUR
	if park:
		mz_walk(cur, home, 9999)
		cur = home
	last = -1
	seen = 0
	adopt = -1
	while True:
		if MZ_MD > 0:
			if MZ_BUY > 0 and MZ_ME == 0 and num_items(Items.Gold) >= MZ_BUY:
				unlock(Unlocks.Megafarm)
				log("MZ bought " + str(num_unlocked(Unlocks.Megafarm)))
			if max_drones() > MZ_MD:
				MZ_CUR = cur
				return 3
		t = measure()
		if t == None:
			MZ_CUR = cur
			if num_items(Items.Gold) >= goal:
				return 0
			return 1
		c = t[0] + t[1] * n
		go_for = False
		if c != last:
			# a new spot: mine, or close enough to my park to race its owner for it
			last = c
			seen = get_time()
			if num_items(Items.Gold) > lim:
				# this is the next maze already: my map is stale
				MZ_CUR = cur
				return 1
			if c in own:
				go_for = True
			else:
				if num_items(Items.Gold) >= goal:
					return 0
				if park:
					go_for = cur == home and c in paths and len(paths[c]) <= race
				else:
					go_for = c in known and mz_dist(cur, c) <= MZ_RACE2
		elif MZ_LOST > 0 and not (c in known) and (c % n) * MZ_GX // n + ((c // n) * MZ_GY // n) * MZ_GX == MZ_ME:
			# in my block but on nobody's map I know of: after a long wait, search the maze for it
			deadline = seen + MZ_LOST
			while c == last and get_time() < deadline:
				t = measure()
				if t == None:
					c = -2
				else:
					c = t[0] + t[1] * n
			if c == last:
				x = get_pos_x() + get_pos_y() * n
				p = mz_seek(c, True)
				if get_pos_x() + get_pos_y() * n == c:
					use_item(Items.Weird_Substance, cost)
					if MZ_HEAL and x in known:
						# nobody maps this spot: the way I found to it becomes mine, so the next
						# treasure there is fetched at once instead of after another search
						pd = MZ_PD
						adj = MZ_ADJ
						if not (x in adj):
							adj[x] = []
						for k in p:
							y = x + DX[k] + DY[k] * n
							if not (y in known):
								pd[y] = k
								known[y] = known[x] + 1
							if not (y in adj):
								adj[y] = []
							if not (k in adj[x]):
								adj[x].append(k)
								adj[y].append(BACK[k])
							own[y] = True
							if x in paths:
								if not (y in paths) or len(paths[x]) + 1 < len(paths[y]):
									paths[y] = paths[x] + [k]
							x = y
						# and the cells round it that nobody I know of maps, depth first
						st2 = []
						todo = [[]]
						for k in range(4):
							if can_move(DIRS[k]) and not ((x + DX[k] + DY[k] * n) in known):
								todo[0].append(k)
						left = MZ_HEALN
						while len(todo) > 0:
							if len(todo[-1]) > 0 and left > 0:
								k = todo[-1].pop()
								y = x + DX[k] + DY[k] * n
								if y in known or not move(DIRS[k]):
									continue
								left -= 1
								pd[y] = k
								known[y] = known[x] + 1
								adj[x].append(k)
								adj[y] = [BACK[k]]
								own[y] = True
								if x in paths:
									paths[y] = paths[x] + [k]
								st2.append(k)
								x = y
								ks = []
								for k2 in range(4):
									if k2 != BACK[k] and can_move(DIRS[k2]) and not ((x + DX[k2] + DY[k2] * n) in known):
										ks.append(k2)
								todo.append(ks)
							else:
								todo.pop()
								if len(st2) > 0 and len(todo) > 0:
									k = st2.pop()
									move(DIRS[BACK[k]])
									x = x - DX[k] - DY[k] * n
				for i in range(len(p) - 1, -1, -1):
					move(DIRS[BACK[p[i]]])
		elif c in known:
			# not mine, but on my map: fetch it if its owner has not come for a while
			deadline = seen + MZ_RESCUE
			if seen < MZ_UP + MZ_EARLY:
				# the maze is new: its owner is likely still mapping its cells
				deadline = seen + MZ_RESCUE_E
			while c == last and get_time() < deadline:
				t = measure()
				if t == None:
					c = -2
				else:
					c = t[0] + t[1] * n
			go_for = c == last
			if go_for and MZ_ADOPT > 0 and c in MZ_ADJ:
				adopt = c
		else:
			# wait for it to move (skippable: only reads the farm)
			while c == last:
				t = measure()
				if t == None:
					c = -2
				else:
					c = t[0] + t[1] * n
		if go_for:
			if cur == home and c in paths:
				for k in paths[c]:
					move(DIRS[k])
			elif MZ_VIA and cur in paths and c in paths:
				# from where I stand: back to where my way from the park and its way to the
				# spot part, then on (shorter than the map's tree once walls have come down)
				p = paths[cur]
				q = paths[c]
				j = 0
				m = min(len(p), len(q))
				while j < m and p[j] == q[j]:
					j += 1
				if not (MZ_SC and mz_walk(cur, c, len(p) + len(q) - 2 * j)):
					# (while no wall has come down on my map, the ways are its tree: this is its path)
					for i in range(len(p) - 1, j - 1, -1):
						move(DIRS[BACK[p[i]]])
					for i in range(j, len(q)):
						move(DIRS[q[i]])
			else:
				mz_walk(cur, c, 9999)
			cur = c
			if num_items(Items.Gold) >= goal:
				if get_entity_type() == Entities.Treasure:
					harvest()
				return 0
			ok = use_item(Items.Weird_Substance, cost)
			if ok:
				# the treasure can come back to this cell after a find elsewhere: see it as new
				last = -1
			if adopt >= 0:
				mz_adopt(adopt)
				adopt = -1
			if not ok:
				g = num_items(Items.Gold)
				# out of weird substance (a short final maze): cash the treasure in rather than spin
				if (g >= lim or num_items(Items.Weird_Substance) < cost) and get_entity_type() == Entities.Treasure:
					harvest()
					if num_items(Items.Gold) > g:
						MZ_CUR = cur
						return 2
			until = get_time() + rep
			if park:
				nxt = -1
				if ok and MZ_NEXT:
					# where the treasure goes next: if it is mine, go straight there
					t = measure()
					while t != None and t[0] + t[1] * n == c:
						t = measure()
					if t != None:
						nxt = t[0] + t[1] * n
				if nxt in own:
					pass
				elif c in paths:
					p = paths[c]
					# on the way back, look for walls that came down, then re-plan
					x = c
					got = mz_try(x)
					wk = [x]
					for i in range(len(p) - 1, -1, -1):
						if MZ_NEXT2:
							t = measure()
							if t != None:
								y = t[0] + t[1] * n
								if y != nxt and y in own:
									break
							elif MZ_HOME:
								# the maze is gone: off to my start for the next one, the short way
								break
						k = p[i]
						move(DIRS[BACK[k]])
						x = x - DX[k] - DY[k] * n
						wk.append(x)
						if mz_try(x):
							got = True
					if got:
						# every side found open is next to a cell I walked: shorten the ways over
						# those sides and pass the gain on (cheaper than a new search from the park)
						adj = MZ_ADJ
						q = []
						for x2 in wk:
							for k in adj[x2]:
								y = x2 + DX[k] + DY[k] * n
								if not (y in paths):
									pass
								elif len(paths[x2]) + 1 < len(paths[y]):
									paths[y] = paths[x2] + [k]
									q.append(y)
								elif len(paths[y]) + 1 < len(paths[x2]):
									paths[x2] = paths[y] + [BACK[k]]
									q.append(x2)
						j = 0
						while j < len(q):
							x2 = q[j]
							j += 1
							px = paths[x2]
							L = len(px) + 1
							for k in adj[x2]:
								y = x2 + DX[k] + DY[k] * n
								if y in paths and L < len(paths[y]):
									paths[y] = px + [k]
									q.append(y)
						MZ_PATH = paths
						MZ_SC = True
					cur = x
				else:
					mz_walk(cur, home, 9999)
					cur = home
			while get_time() < until:
				pass


def mz_adopt(c):
	# nobody came for spot c on my map: the maps disagree there (a wall that came down while
	# the drones mapped gives two of them different ways round), so c and up to MZ_ADOPT cells
	# joined to it that are not mine become mine
	n = MZ_N
	own = MZ_OWN
	adj = MZ_ADJ
	own[c] = True
	q = [c]
	i = 0
	while i < len(q) and len(q) < MZ_ADOPT:
		x = q[i]
		i += 1
		for k in adj[x]:
			y = x + DX[k] + DY[k] * n
			if not (y in own) and y in adj:
				own[y] = True
				q.append(y)


def mz_split(goal, per, cost, g0, park):
	# give the half of my cells under one tree edge to a new drone (it starts where I stand)
	global MZ_OWN
	global MZ_PARK
	global MZ_PATH
	global MZ_KID
	global MZ_BUY
	global MZ_LOST
	n = MZ_N
	pd = MZ_PD
	dp = MZ_DP
	own = {}
	extra = {}
	md = 0
	for x in MZ_OWN:
		if dp[x] > md:
			md = dp[x]
	lv = []
	for i in range(md + 1):
		lv.append([])
	for x in MZ_OWN:
		lv[dp[x]].append(x)
	for L in range(md + 1):
		for x in lv[L]:
			k = pd[x]
			if k < 0 or (x - DX[k] - DY[k] * n) in own:
				own[x] = True
			else:
				extra[x] = True
	md = 0
	for x in own:
		if dp[x] > md:
			md = dp[x]
	byd = []
	for i in range(md + 1):
		byd.append([])
	for x in own:
		byd[dp[x]].append(x)
	par = {}
	cnt = {}
	for x in own:
		cnt[x] = 1
		k = pd[x]
		if k >= 0:
			par[x] = x - DX[k] - DY[k] * n
	for L in range(md, 0, -1):
		for x in byd[L]:
			cnt[par[x]] += cnt[x]
	tot = len(own)
	root = MZ_ROOT
	best = -1
	bv = 999999
	for x in own:
		if x != root:
			v = abs(2 * cnt[x] - tot)
			if v < bv:
				bv = v
				best = x
	if best < 0:
		return
	sub = {best: True}
	for L in range(dp[best] + 1, md + 1):
		for x in byd[L]:
			if par[x] in sub:
				sub[x] = True
	rest = {}
	for x in own:
		if not (x in sub):
			rest[x] = True
	ts = len(sub)
	pa = best
	for x in sub:
		if 2 * cnt[x] > ts and dp[x] > dp[pa]:
			pa = x
	anc = {}
	x = best
	while x != root:
		x = par[x]
		anc[x] = True
	tr = len(rest)
	pb = root
	for x in rest:
		c = cnt[x]
		if x in anc:
			c -= ts
		if 2 * c > tr and dp[x] > dp[pb]:
			pb = x
	MZ_BUY = 0
	MZ_OWN = sub
	MZ_PARK = pa
	MZ_PATH = mz_paths(pa)
	keep = MZ_LOST
	MZ_LOST = 0
	MZ_KID = None
	h = spawn_drone(mz_kid, goal, per, cost, g0, park)
	MZ_LOST = keep
	for x in extra:
		rest[x] = True
	if h == None:
		MZ_OWN = own
		for x in extra:
			MZ_OWN[x] = True
		MZ_PARK = pb
		MZ_PATH = mz_paths(pb)
		return
	MZ_KID = h
	MZ_OWN = rest
	MZ_PARK = pb
	MZ_PATH = mz_paths(pb)


def mz_kid(goal, per, cost, g0, park):
	global MZ_MD
	MZ_MD = max_drones()
	r = mz_serve(goal, per, cost, g0, park)
	while r == 3:
		sp = MZ_SPENT
		goal -= sp
		g0 -= sp
		MZ_MD = max_drones()
		mz_split(goal, per, cost, g0, park)
		MZ_MD = max_drones()
		r = mz_serve(goal, per, cost, g0, park)
	if r == 2:
		# I emptied the maze: make the next one here once the others can be on their starts
		n = MZ_N
		g = num_items(Items.Gold)
		finds = (goal - g) // per + 1
		if g < goal and num_items(Items.Weird_Substance) >= cost * (min(finds, 300) + 1):
			act = 200 / (400 * 1.5 ** num_unlocked(Unlocks.Speed))
			t0 = get_time()
			plant(Entities.Bush)
			until = t0 + act * (MZ_WAIT + n)
			while get_time() < until:
				pass
			use_item(Items.Weird_Substance, cost)
	if MZ_KID != None:
		wait_for(MZ_KID)
	return 0


def mz_life(me, goal, stop, st, start_at, park):
	r = mz_life2(me, goal, stop, st, start_at, park)
	if MZ_KID != None:
		wait_for(MZ_KID)
	return r


def mz_life2(me, goal, stop, st, start_at, park):
	global MZ_RESCUE
	global MZ_MD
	global MZ_BUY
	global MZ_N
	global MZ_ME
	global MZ_GX
	global MZ_GY
	n = get_world_size()
	g = 1
	while (g + 1) * (g + 1) <= len(st):
		g += 1
	while len(st) % g != 0:
		g -= 1
	MZ_GY = g
	MZ_GX = len(st) // g
	global MZ_COST
	global MZ_GOAL
	MZ_N = n
	MZ_ME = me
	if len(st) < 16:
		# few drones: a rescue trip takes a drone far from home, so wait longer before one
		MZ_RESCUE = 2.0
	else:
		MZ_RESCUE = 1.0
	m = lvl_mult(Unlocks.Mazes)
	cost = n * m
	MZ_COST = cost
	MZ_GOAL = goal
	per = n * n * m
	si = {}
	for i in range(len(st)):
		si[st[i]] = i
	root = st[me]
	go(root % n, root // n)
	if me == 0:
		harvest()
		plant(Entities.Bush)
		while get_time() < start_at:
			pass
		use_item(Items.Weird_Substance, cost)
	while True:
		# wait for the maze on my start cell
		e = get_entity_type()
		while e != Entities.Hedge and e != Entities.Treasure:
			e = get_entity_type()
		g0 = num_items(Items.Gold)
		global MZ_UP
		MZ_UP = get_time()
		if get_pos_x() + get_pos_y() * n != root:
			mz_seek(root, False)
		mz_explore(si)
		if MZ_HALF > 0 and 2 * len(st) <= max_drones() and (MZ_HALF // (2 * len(st))) % 2 == 1:
			keep = MZ_BUY
			mz_split(goal, per, cost, g0, park)
			MZ_BUY = keep
		r = mz_serve(goal, per, cost, g0, park)
		while r == 3:
			# the next Megafarm level is bought: its gold is gone, and there are drones to spare
			sp = MZ_SPENT
			goal -= sp
			g0 -= sp
			MZ_MD = max_drones()
			mz_split(goal, per, cost, g0, park)
			MZ_MD = max_drones()
			r = mz_serve(goal, per, cost, g0, park)
		if r == 0:
			return 0
		act = 200 / (400 * 1.5 ** num_unlocked(Unlocks.Speed))
		if r == 2:
			# I emptied the maze: make the next one at my start, once the others stand on theirs
			t0 = get_time()
			g = num_items(Items.Gold)
			finds = (goal - g) // per + 1
			if g >= goal or get_time() > stop or num_items(Items.Weird_Substance) < cost * (min(finds, 300) + 1):
				return 0
			go(root % n, root // n)
			plant(Entities.Bush)
			until = t0 + act * MZ_WAIT
			while get_time() < until:
				pass
			use_item(Items.Weird_Substance, cost)
		else:
			# wait for the harvest, then for the next maze (or give up when none comes)
			while num_items(Items.Gold) < g0 + 301 * per:
				pass
			if num_items(Items.Gold) >= goal:
				return 0
			if get_pos_x() + get_pos_y() * n != root:
				e = get_entity_type()
				if e != Entities.Hedge and e != Entities.Treasure:
					go(root % n, root // n)
				else:
					mz_seek(root, False)
			until = get_time() + act * (MZ_WAIT + 2 * n + 4)
			e = get_entity_type()
			while e != Entities.Hedge and e != Entities.Treasure and get_time() < until:
				e = get_entity_type()
			if e != Entities.Hedge and e != Entities.Treasure:
				return 0


def mz_prep(goal):
	# what maze_round sets up, for a maze run by the drones of the power round before it
	global MZ_MD
	MZ_MD = 0
	stop = get_time() + MAZE_SECS
	n = get_world_size()
	d = min(max_drones(), n * n)
	st = mz_starts(n, d)
	park = MZ_PARKING and d >= MZ_PARK_MIN
	return (goal, stop, st, park)


def maze_round(s, goal):
	# s is ignored: the maze always covers the whole field. Keeps making mazes (each good for
	# 300 treasures) until goal gold, MAZE_SECS, or too little weird substance for another maze.
	stop = get_time() + MAZE_SECS
	n = get_world_size()
	d = min(max_drones(), n * n)
	park = MZ_PARKING and d >= MZ_PARK_MIN
	if MZ_HALF > 0 and (MZ_HALF // d) % 2 == 1:
		d = d // 2
	st = mz_starts(n, d)
	global MZ_MD
	MZ_MD = 0
	if MZ_BUY > 0:
		MZ_MD = max_drones()
	clear()
	act = 200 / (400 * 1.5 ** num_unlocked(Unlocks.Speed))
	# farthest first, so the walks overlap the spawns
	dist = []
	for i in range(len(st)):
		x = st[i] % n
		y = st[i] // n
		dist.append(min(x, n - x) + min(y, n - y))
	idx = []
	for i in range(1, len(st)):
		idx.append(i)
	for a in range(len(idx)):
		for b in range(a + 1, len(idx)):
			if dist[idx[b]] > dist[idx[a]]:
				tmp = idx[a]
				idx[a] = idx[b]
				idx[b] = tmp
	t = get_time()
	ready = t
	hs = []
	for j in range(len(idx)):
		i = idx[j]
		h = spawn_drone(mz_life, i, goal, stop, st, 0, park)
		if h != None:
			hs.append(h)
		ready = max(ready, t + act * (j + 2 + dist[i]))
	ready = max(ready, get_time() + act * (dist[0] + 2))
	mz_life(0, goal, stop, st, ready + 2 * act, park)
	for h in hs:
		wait_for(h)



# ---- dinosaur snake (dinosaurs.py, whole field) ------------------------------------------------

FREE_LIMIT = 24
PLAN = True
MARGIN = 1
ROOM = 2
SN = 0
SS = 0
SHORTCUT_LIMIT = 0
K2 = 80
HALVES = False
IDX = []
PX = []
PY = []
AHEAD = []
WAY = []
NEXT = []
NB = []
WALK = []
TO = []
occ = []
hist = []
vis = []
fills = [0]
fills2 = [0]
NB2 = []
COR = []
MT = []
MT2 = []
ORD = []
vis2 = []
bad = []
SPLITS = 0
FALLS = 0


NBLK = 0
RDIR = []
RPOS = []
NMODES = 40
JMAX = 1
SKIP = True
TB = None
DV = None
CH = None


def dir_to(a, b):
	if b[0] > a[0]:
		return East
	if b[0] < a[0]:
		return West
	if b[1] > a[1]:
		return North
	return South


def mk_path(j, m, N):
	# cells (x, y) of segment route j (0: one block, mode m; j > 0: j skipped blocks + the
	# apple block, detour into the skipped area at column 2 + 2m), y relative to the segment
	W = N - 1
	p = []
	if j == 0 and m >= 3:
		# a route that reaches some of the block's cells early (found offline: the shortest way
		# to each cell that still leaves a way through the rest, and the routes a search made
		# from them most often when the apple came up inside the block)
		ws = ['ENWNEESSEEEEEEEEEEEENWWWWWWWWWWWNEEEEEEEEEEENWWWWWWWWWWWWWW', 'EENWWNEEESSEEEEEEEEEEENWWWWWWWWWWNEEEEEEEEEENWWWWWWWWWWWWWW', 'EENNESSEEEEEEEEEEENWWWWWWWWWWNEEEEEEEEEENWWWWWWWWWWWWWSSWNN', 'EEENWWWNEEEESSEEEEEEEEEENWWWWWWWWWNEEEEEEEEENWWWWWWWWWWWWWW', 'EEENNESSEEEEEEEEEENWWWWWWWWWNEEEEEEEEENWWWWWWWWWWWWWSESWWNN', 'EEEENWWWWNEEEEESSEEEEEEEEENWWWWWWWWNEEEEEEEENWWWWWWWWWWWWWW', 'EEEENNESSEEEEEEEEENWWWWWWWWNEEEEEEEENWWWWWWWWWWWWWSEESWWWNN', 'EEEEENWWWWWNEEEEEESSEEEEEEEENWWWWWWWNEEEEEEENWWWWWWWWWWWWWW', 'EEEEENNESSEEEEEEEENWWWWWWWNEEEEEEENWWWWWWWWWWWWWSEEESWWWWNN', 'EEEEEENWWWWWWNEEEEEEESSEEEEEEENWWWWWWNEEEEEENWWWWWWWWWWWWWW', 'EEEEEENNESSEEEEEEENWWWWWWNEEEEEENWWWWWWWWWWWWWSEEEESWWWWWNN', 'EEEEEEENWWWWWWWNEEEEEEEESSEEEEEENWWWWWNEEEEENWWWWWWWWWWWWWW', 'EEEEEEENNESSEEEEEENWWWWWNEEEEENWWWWWWWWWWWWWSEEEEESWWWWWWNN', 'EEEEEEEENWWWWWWWWNEEEEEEEEESSEEEEENWWWWNEEEENWWWWWWWWWWWWWW', 'EEEEEEEENNESSEEEEENWWWWNEEEENWWWWWWWWWWWWWSEEEEEESWWWWWWWNN', 'EEEEEEEEENWWWWWWWWWNEEEEEEEEEESSEEEENWWWNEEENWWWWWWWWWWWWWW', 'EEEEEEEEENNESSEEEENWWWNEEENWWWWWWWWWWWWWSEEEEEEESWWWWWWWWNN', 'EEEEEEEEEEEEEENNNWWWWWWWWWWWWWSEEEEEEEEEEEESWWWWWWWWWWWWWNN', 'EEEEEEEEEENWWWWWWWWWWNEEEEEEEEEEESSEEENWWNEENWWWWWWWWWWWWWW', 'EEEEEEEEEENNESSEEENWWNEENWWWWWWWWWWWWWSEEEEEEEESWWWWWWWWWNN', 'EEEEEEEEEEENWWWWWWWWWWWNEEEEEEEEEEEESSEENWNENWWWWWWWWWWWWWW', 'EEEEEEEEEEENNESSEENWNENWWWWWWWWWWWWWSEEEEEEEEESWWWWWWWWWWNN', 'EEEEEEEEEEEENWWWWWWWWWWWWNEEEEEEEEEEEEESSENNNWWWWWWWWWWWWWW', 'EEEEEEEEEEEENNESSENNNWWWWWWWWWWWWWSEEEEEEEEEESWWWWWWWWWWWNN', 'EEEEEEEEEEEENESENNNWSWNWWWWWWWWWWWSEEEEEEEEEESWWWWWWWWWWWNN', 'EEEEEEEEEEEEEENNNWWWWWWWWWSEEEEEEEESWWWWWWWWWWWWWNEEEENWWWW', 'EEEEEEEEEEEEEENNNWWWWWWWWWWWWSEEEEEEEEEEESWWWWWWWWWWWWWNENW', 'EEEEEEEEEEEEEENNNWWWWWWWWSEEEEEEESWWWWWWWWWWWWWNEEEEENWWWWW', 'EEEEEEEEEEEEEENNNWSSWWWWWWWWWWWWWNEEEEEEEEEEEENWWWWWWWWWWWW', 'EEEEEEEEEEEEEENNNWWWWWWWWWWSEEEEEEEEESWWWWWWWWWWWWWNEEENWWW', 'EEEEEEEEEEEEEENNNWWWWSEEESWWWWWWWWWWWWWNEEEEEEEEENWWWWWWWWW', 'EEEEEEEEEEEEEENNNWWWWWWWWWWWSEEEEEEEEEESWWWWWWWWWWWWWNEENWW', 'EENNEEEEEEEEEEESWWWWWWWWWWSEEEEEEEEEEENNNWWWWWWWWWWWWWSSWNN', 'NNESSEEEEEEEEEEEEENWWWWWWWWWWWWNEEEEEEEEEEEENWWWWWWWWWWWWWW', 'EEEEEEEEEEEEEENNNWWWSEESWWWWWWWWWWWWWNEEEEEEEEEENWWWWWWWWWW', 'NNEEEEEEEEEEEEESWWWWWWWWWWWWSEEEEEEEEEEEEENNNWWWWWWWWWWWWWW', 'EEEEEEEEEEEEEENNNWWWWWWWSEEEEEESWWWWWWWWWWWWWNEEEEEENWWWWWW']
		x = 1
		y = 0
		p.append((x, y))
		for c in ws[m - 3]:
			if c == "E":
				x += 1
			elif c == "W":
				x -= 1
			elif c == "N":
				y += 1
			else:
				y -= 1
			p.append((x, y))
		return p
	if j == 0:
		if m == 0:
			for y in range(4):
				if y % 2 == 0:
					xs = range(1, W + 1)
				else:
					xs = range(W, 0, -1)
				for x in xs:
					p.append((x, y))
		elif m == 1:
			for x in range(1, W + 1):
				p.append((x, 0))
			i = 0
			for x in range(W, 0, -1):
				if i % 2 == 0:
					ys = range(1, 4)
				else:
					ys = range(3, 0, -1)
				for y in ys:
					p.append((x, y))
				i += 1
		else:
			i = 0
			for x in range(1, W + 1):
				if i % 2 == 0:
					ys = range(0, 3)
				else:
					ys = range(2, -1, -1)
				for y in ys:
					p.append((x, y))
				i += 1
			for x in range(W, 0, -1):
				p.append((x, 3))
		return p
	a = 2 + 2 * m
	r0 = 4 * j
	for y in range(r0 + 1):
		p.append((1, y))
	for x in range(1, W + 1):
		if x % 2 == 1:
			ys = range(r0, r0 + 3)
		else:
			ys = range(r0 + 2, r0 - 1, -1)
		for y in ys:
			if x != 1 or y != r0:
				p.append((x, y))
		if x == a:
			for ri in range(r0):
				y = r0 - 1 - ri
				if ri % 2 == 0:
					xs = range(a, 1, -1)
				else:
					xs = range(2, a + 1)
				for xx in xs:
					p.append((xx, y))
			for ri in range(r0):
				if ri % 2 == 0:
					xs = range(a + 1, W + 1)
				else:
					xs = range(W, a, -1)
				for xx in xs:
					p.append((xx, ri))
	for x in range(W, 0, -1):
		p.append((x, r0 + 3))
	return p


def mk_job(i, d, tasks, N):
	out = []
	for q in range(i, len(tasks), d):
		j = tasks[q][0]
		m = tasks[q][1]
		p = mk_path(j, m, N)
		h = 4 * (j + 1)
		pos = []
		for c in range(N * h):
			pos.append(0)
		ds = []
		for c in range(len(p)):
			pos[p[c][0] * h + p[c][1]] = c
			if c + 1 < len(p):
				ds.append(dir_to(p[c], p[c + 1]))
		out.append([j, m, ds, pos])
	return out


def block_setup(N):
	# rows 4s..4s+3, columns 1..N-1 form block s; column 0 is the way back down.
	# A segment is one block walked in one of NMODES ways, or j skipped blocks plus the block
	# after them; every route enters at (1, 4s) and leaves at the segment's top left corner.
	# The routes are worked out on BG_BLK drones of their own while the first snake runs
	# (the block phase comes 40 s in); get_blocks() collects them.
	NBLK = N // 4
	# the block routes form a tree (routes that start alike share a branch). DV[m]: pairs
	# DV[m][i]: the branch route m is on at its cell i; TB[branch][x * 4 + y]:
	# the route of that branch that reaches cell (x, y) of the block soonest (a letter)
	TB = ['AAAAACCAADCUAEFUAGFUAIHUAKJUAMLUAONUAQPUASRUAVTUAXWUAZYUAbaBAABB', 'AAAAADDAADDUAEFUAGFUAIHUAKJUAMLUAONUAQPUASRUAVTUAXWUAZYUAbaBAABB', 'AAAAAEEAAEEUAEFUAGFUAIHUAKJUAMLUAONUAQPUASRUAVTUAXWUAZYUAbaBAABB', 'AAAAAGGAAGGUAGGUAGHUAIHUAKJUAMLUAONUAQPUASRUAVTUAXWUAZYUAbaBAABB', 'AAAAAIIAAIIUAIIUAIIUAIJUAKJUAMLUAONUAQPUASRUAVTUAXWUAZYUAbaBAABB', 'AAAAAKKAAKKUAKKUAKKUAKKUAKLUAMLUAONUAQPUASRUAVTUAXWUAZYUAbaBAABB', 'AAAAAMMAAMMUAMMUAMMUAMMUAMMUAMNUAONUAQPUASRUAVTUAXWUAZYUAbaBAABB', 'AAAAAOOAAOOUAOOUAOOUAOOUAOOUAOOUAOPUAQPUASRUAVTUAXWUAZYUAbaBAABB', 'AAAAAQQAAQQUAQQUAQQUAQQUAQQUAQQUAQQUAQRUASRUAVTUAXWUAZYUAbaBAABB', 'AAAAASSAASSUASSUASSUASSUASSUASSUASnUASnUASTUAVTUAXWUAZYUAbaBAABB', 'AAAAAVVAAVVUAVVUAVVUAVVUAVVUAVeUAVnUAVnUAVnUAVWUAXWUAZYUAbaBAABB', 'AAAAAXXAAXXUAXXUAXXUAXXUAXcUAXeUAXnUAXnUAXnUAXhUAXYUAZYUAbaBAABB', 'AAAAAZZAAZZUAZZUAZZUAZgUAZcUAZeUAZnUAZnUAZnUAZhUAZlUAZaUAbaBAABB', 'AAAAAAAAAAAUAAdUAAiUAAgUAAcUAAeUAAnUAAnUAAnUAAhUAAlUAABUAABBAABB', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'AAAABffBBfUUBfdUBfiUBfgUBfcUBfeUBfnUBfnUBfnUBfhUBflUBBBUBBBBBBBB', 'AAAABffBBffBBffBBffBBffBBffBBfBBBfBBBfBBBfBBBfBBBfBBBBBBBBBBBBBB', 'AAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB', 'AAAACCCCCCCCCCmCkCmCkCmCkCmCkCmCkCmCkmmCkmmCkmmCkmmCkmmCkmmCkkCC', 'AAAACCCCCCCCCCCCkCCCkCCCkCCCkCCCkCCCkCCCkkCCkkCCkkCCkkCCkkCCkkCC', 'AAAACCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC', 'AAAADDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD', 'AAAAEEEEEEEFEEFFFFFFFjjFFjjFFjjFFjjFFjjFFjjFFjjFFjjFFjjFFjjFFFFF', 'AAAAEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE', 'AAAAFFFFFFFFFFFFFFFFFjjFFjjFFjjFFjjFFjjFFjjFFjjFFjjFFjjFFjjFFFFF', 'AAAAFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF', 'AAAAGGGGGGGHGGGHGGHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH', 'AAAAGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG', 'AAAAHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH', 'AAAAIIIIIIIJIIIJIIIJIIJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ', 'AAAAIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII', 'AAAAJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ', 'AAAAKKKKKKKLKKKLKKKLKKKLKKLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL', 'AAAAKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK', 'AAAALLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL', 'AAAAMMMMMMMNMMMNMMMNMMMNMMMNMMNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN', 'AAAAMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM', 'AAAANNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN', 'AAAAOOOOOOOPOOOPOOOPOOOPOOOPOOOPOOPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP', 'AAAAOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO', 'AAAAPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP', 'AAAAQQQQQQQRQQQRQQQRQQQRQQQRQQQRQQQRQQRRRRRRRRRRRRRRRRRRRRRRRRRR', 'AAAAQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ', 'AAAARRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR', 'AAAASSSSSSSTSSSTSSSTSSSTSSSTSSSTSSSTSSSTSSTTTTTTTTTTTTTTTTTTTTTT', 'AAAASSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS', 'AAAATTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT', 'AAAAUllUUlUUUldUUliUUlgUUlcUUleUUlnUUlnUUlnUUlhUUllUUllUUllUUUUU', 'AAAAUhhUUhUUUhdUUhiUUhgUUhcUUheUUhnUUhnUUhnUUhhUUhhUUhhUUhhUUUUU', 'AAAAUnnUUnUUUndUUniUUngUUncUUneUUnnUUnnUUnnUUnnUUnnUUnnUUnnUUUUU', 'AAAAUeeUUeUUUedUUeiUUegUUecUUeeUUeeUUeeUUeeUUeeUUeeUUeeUUeeUUUUU', 'AAAAUccUUcUUUcdUUciUUcgUUccUUccUUccUUccUUccUUccUUccUUccUUccUUUUU', 'AAAAUggUUgUUUgdUUgiUUggUUggUUggUUggUUggUUggUUggUUggUUggUUggUUUUU', 'AAAAUiiUUiUUUidUUiiUUiiUUiiUUiiUUiiUUiiUUiiUUiiUUiiUUiiUUiiUUUUU', 'AAAAUddUUdUUUddUUddUUddUUddUUddUUddUUddUUddUUddUUddUUddUUddUUUUU', 'AAAAUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU', 'AAAAVVVVVVVWVVVWVVVWVVVWVVVWVVVWVVVWVVVWVVVWVVWWWWWWWWWWWWWWWWWW', 'AAAAVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV', 'AAAAWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW', 'AAAAXXXXXXXYXXXYXXXYXXXYXXXYXXXYXXXYXXXYXXXYXXXYXXYYYYYYYYYYYYYY', 'AAAAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'AAAAYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY', 'AAAAZZZZZZZaZZZaZZZaZZZaZZZaZZZaZZZaZZZaZZZaZZZaZZZaZZaabbabbbbb', 'AAAAZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ', 'AAAAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'AAAAbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'AAAAcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc', 'AAAAdddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd', 'AAAAeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', 'AAAAffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 'AAAAgggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg', 'AAAAhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh', 'AAAAiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii', 'AAAAjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj', 'AAAAkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk', 'AAAAllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll', 'AAAAmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm', 'AAAAnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn']
	DV = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13, 13, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13, 13, 15, 15, 15, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17], [0, 18, 18, 18, 19, 19, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], [0, 1, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21], [0, 1, 2, 22, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23], [0, 1, 2, 22, 24, 24, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25], [0, 1, 2, 3, 26, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27], [0, 1, 2, 3, 26, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28], [0, 1, 2, 3, 4, 29, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30], [0, 1, 2, 3, 4, 29, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31], [0, 1, 2, 3, 4, 5, 32, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33], [0, 1, 2, 3, 4, 5, 32, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34], [0, 1, 2, 3, 4, 5, 6, 35, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36], [0, 1, 2, 3, 4, 5, 6, 35, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37], [0, 1, 2, 3, 4, 5, 6, 7, 38, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39], [0, 1, 2, 3, 4, 5, 6, 7, 38, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40], [0, 1, 2, 3, 4, 5, 6, 7, 8, 41, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42], [0, 1, 2, 3, 4, 5, 6, 7, 8, 41, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43, 43], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 44, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 44, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13, 13, 15, 15, 15, 47, 47, 48, 49, 49, 49, 50, 51, 52, 53, 54, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 56, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 56, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 59, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 59, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 62, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 62, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 62, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13, 13, 15, 15, 15, 47, 47, 48, 49, 49, 49, 50, 51, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13, 13, 15, 15, 15, 47, 47, 48, 49, 49, 49, 50, 51, 52, 53, 54, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13, 13, 15, 15, 15, 47, 47, 48, 49, 49, 49, 50, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13, 13, 15, 15, 15, 16, 16, 16, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13, 13, 15, 15, 15, 47, 47, 48, 49, 49, 49, 50, 51, 52, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13, 13, 15, 15, 15, 47, 47, 48, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13, 13, 15, 15, 15, 47, 47, 48, 49, 49, 49, 50, 51, 52, 53, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72], [0, 1, 2, 22, 24, 24, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73], [0, 18, 18, 18, 19, 19, 19, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13, 13, 15, 15, 15, 47, 47, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75], [0, 18, 18, 18, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76, 76], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13, 13, 15, 15, 15, 47, 47, 48, 49, 49, 49, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77]]
	CH = {}
	for q in range(40):
		CH["ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn"[q]] = q
	tasks = []
	RDIR = []
	RPOS = []
	for j in range(JMAX + 1):
		RDIR.append([])
		RPOS.append([])
		if j == 0:
			n = NMODES
		else:
			n = (N - 2) // 2
		for m in range(n):
			tasks.append([j, m])
			RDIR[j].append(0)
			RPOS[j].append(0)
	# biggest routes first, each to the drone with the least work so far
	qs = []
	load = []
	for b in range(BG_BLK):
		qs.append([])
		load.append(0)
	q = len(tasks) - 1
	while q >= 0:
		b = 0
		for c in range(BG_BLK):
			if load[c] < load[b]:
				b = c
		qs[b].append(q)
		load[b] += tasks[q][0] + 1
		q -= 1
	hs = []
	for b in range(1, BG_BLK):
		hs.append(spawn_drone(blk_job, qs[b], tasks, N))
	rs = [blk_job(qs[0], tasks, N)]
	for h in hs:
		rs.append(wait_for(h))
	for r in rs:
		for e in r:
			RDIR[e[0]][e[1]] = e[2]
			RPOS[e[0]][e[1]] = e[3]
	return [NBLK, TB, DV, CH, RDIR, RPOS]


def blk_job(qs, tasks, N):
	out = []
	for q in qs:
		j = tasks[q][0]
		m = tasks[q][1]
		p = mk_path(j, m, N)
		h = 4 * (j + 1)
		pos = []
		for c in range(N * h):
			pos.append(0)
		ds = []
		for c in range(len(p)):
			pos[p[c][0] * h + p[c][1]] = c
			if c + 1 < len(p):
				ds.append(dir_to(p[c], p[c + 1]))
		out.append([j, m, ds, pos])
	return out


def get_blocks():
	global BGB
	global NBLK
	global RDIR
	global RPOS
	global TB
	global DV
	global CH
	if BGB != None:
		r = wait_for(BGB)
		BGB = None
		NBLK = r[0]
		TB = r[1]
		DV = r[2]
		CH = r[3]
		RDIR = r[4]
		RPOS = r[5]


BG_BLK = 3
SD1 = []
SW1 = []
ST1 = []
SD2 = []
SW2 = []
ST2 = []
ST0 = []
G2 = None
BGB = []
BGT = None
CX = [1, 1, -1, -1]
CY = [1, -1, -1, 1]


def dn_rows(j, d, a, b):
	# drone j of d: the neighbour tables the free phase needs, for its slice of the cells
	S = SS
	N = SN
	nb = []
	nb2 = []
	cor = []
	for i in range(j * S // d, (j + 1) * S // d):
		row = []
		r2 = []
		q = []
		px = PX[i]
		py = PY[i]
		for k in range(4):
			x = px + DX[k]
			y = py + DY[k]
			if x >= 0 and x < N and y >= 0 and y < N:
				c = IDX[x][y]
				row.append(c)
				r2.append(c)
			else:
				row.append(-1)
				r2.append(S)
			x = px + CX[k]
			y = py + CY[k]
			if x >= 0 and x < N and y >= 0 and y < N:
				q.append(IDX[x][y])
			else:
				q.append(S)
		nb.append(row)
		nb2.append(r2)
		cor.append(q)
	return [nb, nb2, cor]


def cyc_tables(a, b):
	# AHEAD, WAY, TO and NEXT along the cycle, on a drone of its own while the first snake starts
	# (they are first needed when the snake lines up on the cycle); get_tables() collects them
	if a == 1:
		# (a drone of its own) the move history list play() switches to once lined up
		return list(range(16384))
	S = SS
	N = SN
	ah = []
	wy = []
	to = []
	nx = []
	d1 = []
	w1 = []
	t1 = []
	d2 = []
	w2 = []
	t2 = []
	t0 = []
	for i in range(S):
		pairs = []
		px = PX[i]
		py = PY[i]
		for k in range(4):
			x = px + DX[k]
			y = py + DY[k]
			if x >= 0 and x < N and y >= 0 and y < N:
				pairs.append([(IDX[x][y] - i) % S, DIRS[k]])
		ds = []
		ws = []
		ts = []
		while pairs:
			best = pairs[0]
			for p in pairs:
				if p[0] > best[0]:
					best = p
			pairs.remove(best)
			ds.append(best[0])
			ws.append(best[1])
			ts.append((i + best[0]) % S)
			if best[0] == 1:
				nx.append(best[1])
		ah.append(ds)
		wy.append(ws)
		to.append(ts)
		# the shortcuts other than the cycle's next and previous cell, longest first
		e = []
		for q in range(len(ds)):
			if ds[q] != 1 and ds[q] != S - 1:
				e.append(q)
		if len(e) > 0:
			d1.append(ds[e[0]])
			w1.append(ws[e[0]])
			t1.append(ts[e[0]])
		else:
			d1.append(1000000)
			w1.append(0)
			t1.append(0)
		if len(e) > 0:
			# the shorter one (the only one when there is one)
			q = e[len(e) - 1]
			d2.append(ds[q])
			w2.append(ws[q])
			t2.append(ts[q])
		else:
			d2.append(1000000)
			w2.append(0)
			t2.append(0)
		t0.append((i + 1) % S)
	# g[i]: the least d2[i + r] + r, so fewer than g[i] cycle steps from i never meet a shortcut
	g = []
	for i in range(S):
		g.append(0)
	m = 1000000
	for q in range(2 * S - 1, -1, -1):
		i = q % S
		m += 1
		if d2[i] < m:
			m = d2[i]
		g[i] = m
	return [ah, wy, to, nx, d1, w1, t1, d2, w2, t2, t0, g]


def get_tables():
	global BGT
	global AHEAD
	global WAY
	global TO
	global NEXT
	global WALK
	global SD1
	global SW1
	global ST1
	global SD2
	global SW2
	global ST2
	global ST0
	global G2
	if BGT != None:
		r = wait_for(BGT)
		BGT = None
		AHEAD = r[0]
		WAY = r[1]
		TO = r[2]
		NEXT = r[3]
		SD1 = r[4]
		SW1 = r[5]
		ST1 = r[6]
		SD2 = r[7]
		SW2 = r[8]
		ST2 = r[9]
		ST0 = r[10]
		G2 = r[11]
		global HB
		HB = wait_for(BGH)
		if HALVES:
			WALK = []
			for i in range(2 * SS):
				WALK.append(NEXT[i % SS])


DINO_BG = [False]


def dino_bg():
	# the tables the snake needs only later (lining up on the cycle, the block routes), each built
	# on a drone of its own while the first snake runs
	global BGT
	global BGB
	DINO_BG[0] = True
	BGT = spawn_drone(cyc_tables, 0, 0)
	global BGH
	BGH = spawn_drone(cyc_tables, 1, 0)
	if not HALVES:
		BGB = spawn_drone(block_setup, SN)


def dino_setup():
	global SN
	global SS
	global SHORTCUT_LIMIT
	global IDX
	global PX
	global PY
	global NB
	global occ
	global hist
	global vis
	global NB2
	global COR
	global MT
	global MT2
	global ORD
	global vis2
	global bad
	global BGT
	N = get_world_size()
	S = N * N
	SN = N
	SS = S
	SHORTCUT_LIMIT = S * 30 // 100
	IDX = []
	for x in range(N):
		col = []
		for y in range(N):
			col.append(0)
		IDX.append(col)
	PX = []
	PY = []
	if HALVES:
		h = N // 2
		for y in range(N):
			if y % 2 == 0:
				xs = range(h - 1, -1, -1)
			else:
				xs = range(h)
			for x in xs:
				PX.append(x)
				PY.append(y)
		for c in range(N):
			if c % 2 == 0:
				xs = range(h, N)
			else:
				xs = range(N - 1, h - 1, -1)
			for x in xs:
				PX.append(x)
				PY.append(N - 1 - c)
	else:
		PX.append(0)
		PY.append(0)
		for y in range(N):
			if y % 2 == 0:
				xs = range(1, N)
			else:
				xs = range(N - 1, 0, -1)
			for x in xs:
				PX.append(x)
				PY.append(y)
		for y in range(N - 1, 0, -1):
			PX.append(0)
			PY.append(y)
	for i in range(S):
		IDX[PX[i]][PY[i]] = i
	# the free phase's neighbour tables are built by every drone at once, a slice each (before
	# the background drones below take any of the drone limit)
	NB = []
	NB2 = []
	COR = []
	for r in all_drones(dn_rows, 0, 0):
		for e in r[0]:
			NB.append(e)
		for e in r[1]:
			NB2.append(e)
		for e in r[2]:
			COR.append(e)
	DINO_BG[0] = False
	z = [0]
	while len(z) * 2 <= S:
		z = z + z
	while len(z) < S:
		z.append(0)
	occ = z + [1000000000]
	hist = z + []
	vis = z + []
	vis2 = z + [0]
	bad = z + [-5]
	MT = []
	MT2 = []
	PW = [1, 2, 4, 8]
	for m in range(16):
		fr = []
		bl = []
		for k in range(4):
			if (m // PW[k]) % 2 == 0:
				fr.append(k)
			else:
				bl.append(k)
		v = -1
		v2 = 0
		if len(fr) == 1:
			v = 4
		elif len(fr) == 2:
			if (fr[1] - fr[0]) == 1:
				v = fr[0]
			elif fr[0] == 0 and fr[1] == 3:
				v = 3
		elif len(fr) == 3:
			j = bl[0]
			v = 10 + (j + 1) % 4
			v2 = (j + 2) % 4
		MT.append(v)
		MT2.append(v2)
	# ORD[s]: s = sx * 6 + sy * 2 + (|dx| < |dy|); sx/sy: 0 positive, 1 negative, 2 zero
	ORD = []
	for sx in range(3):
		for sy in range(3):
			for mj in range(2):
				hs = [1, 3, -1][sx]
				vs = [0, 2, -1][sy]
				o = []
				if mj == 0:
					if hs >= 0:
						o.append(hs)
					if vs >= 0:
						o.append(vs)
				else:
					if vs >= 0:
						o.append(vs)
					if hs >= 0:
						o.append(hs)
				if len(o) == 0:
					o = [0, 1, 2, 3]
				op = (o[0] + 2) % 4
				for e in [0, 1, 2, 3]:
					if not (e in o) and e != op:
						o.append(e)
				for e in [0, 1, 2, 3]:
					if not (e in o):
						o.append(e)
				ORD.append(o)


NOM = []


def chk(c, low, need):
	# None when moving into c leaves no big enough free side; else the list of c's neighbours
	# that start a small closed side (to keep out of on the next move)
	o = NB2[c]
	m = 0
	if occ[o[0]] >= low:
		m = 1
	if occ[o[1]] >= low:
		m += 2
	if occ[o[2]] >= low:
		m += 4
	if occ[o[3]] >= low:
		m += 8
	v = MT[m]
	if v == 4:
		return alive(c, low, need)
	if v >= 0:
		q = COR[c]
		if v < 4:
			if occ[q[v]] < low:
				return NOM
		elif occ[q[v - 10]] < low and occ[q[MT2[m]]] < low:
			return NOM
	return sides(c, o, low, need)


def alive(c, low, need):
	# c has one way on: grow the free cells beyond it breadth first, a cell at distance D taken
	# once it is free by the time the head could get there (occ < low + D - 1, a step kept for an
	# apple eaten on the way). Good on need cells, or on a body cell left free in time (the head
	# can then follow the tail for ever). None when neither, else NOM.
	fills2[0] += 4
	f = fills2[0]
	vis2[c] = f
	front = [c]
	cnt = 0
	lim = low - 1
	while front:
		lim += 1
		ahead = []
		for x in front:
			for e in NB2[x]:
				o = occ[e]
				if o < lim and vis2[e] != f:
					if o >= low:
						return NOM
					vis2[e] = f
					ahead.append(e)
		cnt += len(ahead)
		if cnt >= need:
			return NOM
		front = ahead
	return None


def sides(c, o, low, need):
	# c splits the free cells around it: grow each side breadth first, a level at a time, until
	# every side is settled. Sides that meet are one region and are judged together. A region is
	# good when it reaches need cells or a body cell that is gone by then. Returns None when no
	# region is good, else the start cells of the sides whose region closed small (every side is
	# grown to the end: one still open when the others are settled may be a dead end too).
	global SPLITS
	SPLITS += 1
	fills2[0] += 4
	f = fills2[0]
	vis2[c] = f
	fr = []
	lb = []
	sc = []
	for e in o:
		if occ[e] < low:
			vis2[e] = f + len(fr) + 1
			fr.append([e])
			lb.append(vis2[e])
			sc.append(e)
	ns = len(fr)
	if ns == 0:
		for e in o:
			if occ[e] < low + 1:
				return NOM
		return None
	grp = []
	cnt = []
	st = []
	for i in range(ns):
		grp.append(i)
		cnt.append(1)
		st.append(0)
	dd = 0
	opn = True
	while opn:
		dd += 1
		gone = low + dd - 1
		for i in range(ns):
			g = grp[i]
			if st[g] == 0 and len(fr[i]) > 0:
				me = lb[i]
				ahead = []
				for x in fr[i]:
					for e in NB2[x]:
						oc = occ[e]
						if oc < low:
							w = vis2[e]
							if w < f:
								vis2[e] = me
								ahead.append(e)
							elif w != me and w != f:
								h = grp[w - f - 1]
								if h != g:
									for j in range(ns):
										if grp[j] == h:
											grp[j] = g
									cnt[g] += cnt[h]
									if st[h] == 1:
										st[g] = 1
						elif oc < gone and e != c:
							st[g] = 1
				cnt[g] += len(ahead)
				fr[i] = ahead
		opn = False
		for g in range(ns):
			if st[g] == 0 and grp[g] == g:
				if cnt[g] >= need:
					st[g] = 1
				else:
					live = False
					for j in range(ns):
						if grp[j] == g and len(fr[j]) > 0:
							live = True
					if live:
						opn = True
					else:
						st[g] = 2
	good = False
	bl = []
	for i in range(ns):
		if st[grp[i]] == 2:
			bl.append(sc[i])
		else:
			good = True
	if good:
		return bl
	return None


def plan(ch, ax, ay, t, low, need):
	# a path to the apple made of up to three straight runs (the two L shapes first, then Z shapes
	# of the same length, then detours a little longer), every cell free when it is reached and
	# passing the split test; the path's cells are written into occ. Returns [cells, dirs].
	# (the L shapes are tried before the other shapes are listed, and every shape is checked
	# run by run: the same paths as checking cell by cell, for fewer ticks)
	dx = ax - PX[ch]
	dy = ay - PY[ch]
	hd = 1
	if dx < 0:
		hd = 3
		dx = -dx
	vd = 0
	if dy < 0:
		vd = 2
		dy = -dy
	cs = [[hd, dx, vd, dy, 0, 0]]
	if dx > 0 and dy > 0:
		cs.append([vd, dy, hd, dx, 0, 0])
	built = False
	q = 0
	while True:
		if q >= len(cs):
			if built:
				return None
			built = True
			if dx > 0 and dy > 0:
				for a in range(1, min(dy, 5)):
					cs.append([vd, a, hd, dx, vd, dy - a])
				for a in range(1, min(dx, 5)):
					cs.append([hd, a, vd, dy, hd, dx - a])
			for e in range(1, 3):
				if dx > 0:
					if dy > 0:
						cs.append([(vd + 2) % 4, e, hd, dx, vd, dy + e])
						cs.append([vd, dy + e, hd, dx, (vd + 2) % 4, e])
					else:
						cs.append([0, e, hd, dx, 2, e])
						cs.append([2, e, hd, dx, 0, e])
				if dy > 0:
					if dx > 0:
						cs.append([(hd + 2) % 4, e, vd, dy, hd, dx + e])
						cs.append([hd, dx + e, vd, dy, (hd + 2) % 4, e])
					else:
						cs.append([1, e, vd, dy, 3, e])
						cs.append([3, e, vd, dy, 1, e])
			if q >= len(cs):
				return None
		sg = cs[q]
		q += 1
		d0 = sg[0]
		n1 = sg[1]
		d1 = sg[2]
		n2 = sg[3]
		d2 = sg[4]
		n3 = sg[5]
		n = n1 + n2 + n3
		if n == 0:
			continue
		f = d2
		if n1 > 0:
			f = d0
		elif n2 > 0:
			f = d1
		if bad[NB2[ch][f]] == t:
			continue
		# every cell free when it is reached, before any split test
		c = ch
		lim = low - 1
		ok = True
		for j in range(n1):
			c = NB2[c][d0]
			lim += 1
			if occ[c] >= lim:
				ok = False
				break
		if not ok:
			continue
		for j in range(n2):
			c = NB2[c][d1]
			lim += 1
			if occ[c] >= lim:
				ok = False
				break
		if not ok:
			continue
		for j in range(n3):
			c = NB2[c][d2]
			lim += 1
			if occ[c] >= lim:
				ok = False
				break
		if not ok:
			continue
		cells = []
		olds = []
		ds = []
		c = ch
		i = t
		w = DIRS[d0]
		for j in range(n1):
			c = NB2[c][d0]
			i += 1
			cells.append(c)
			ds.append(w)
			olds.append(occ[c])
			occ[c] = i
		w = DIRS[d1]
		for j in range(n2):
			c = NB2[c][d1]
			i += 1
			cells.append(c)
			ds.append(w)
			olds.append(occ[c])
			occ[c] = i
		w = DIRS[d2]
		for j in range(n3):
			c = NB2[c][d2]
			i += 1
			cells.append(c)
			ds.append(w)
			olds.append(occ[c])
			occ[c] = i
		nb = chk(c, lim, need)
		if nb != None:
			for x in nb:
				bad[x] = t + n
			return [cells, ds]
		for j in range(n):
			occ[cells[j]] = olds[j]



def free_step(ch, ax, ay, low, need, t):
	# a step towards the apple that passes chk (else the first free one); returns [dir, marks]
	dx = ax - PX[ch]
	dy = ay - PY[ch]
	h = -1
	if dx > 0:
		h = 1
	elif dx < 0:
		h = 3
	v = -1
	if dy > 0:
		v = 0
	elif dy < 0:
		v = 2
	nbs = NB[ch]
	if abs(dx) >= abs(dy):
		order = [h, v, 0, 1, 2, 3]
	else:
		order = [v, h, 0, 1, 2, 3]
	fallback = -1
	for e in order:
		if e >= 0:
			c = nbs[e]
			if c >= 0 and occ[c] < low and bad[c] != t:
				if fallback < 0:
					fallback = e
				r = chk(c, low, need)
				if r != None:
					return [e, r]
	return [fallback, NOM]


HL = 24


def leg(ch, ca, t, k):
	# the free phase's moves from ch to the apple ca at length k, as play() makes them
	# (a planned path, else greedy steps); writes occ. Returns [cells, dirs, ok].
	ax = PX[ca]
	ay = PY[ca]
	low = t + 1 - k
	need = k + ROOM
	pl = plan(ch, ax, ay, t, low, need)
	if pl != None:
		pl.append(True)
		return pl
	cells = []
	ds = []
	while ch != ca:
		low = t + 1 - k
		dx = ax - PX[ch]
		dy = ay - PY[ch]
		if dx > 0:
			s = 0
		elif dx < 0:
			s = 6
		else:
			s = 12
		if dy < 0:
			s += 2
		elif dy == 0:
			s += 4
		if abs(dx) < abs(dy):
			s += 1
		nbs = NB2[ch]
		e = -1
		fb = -1
		mk = NOM
		o = ORD[s]
		lp = len(cells) > 2 * k + 40
		for d in o:
			c = nbs[d]
			if occ[c] < low and bad[c] != t:
				if fb < 0:
					fb = d
					if lp:
						# a long way round: the snake may be going round after its own tail
						# for ever; take the first free way towards the apple
						break
				r = chk(c, low, need)
				if r != None:
					e = d
					mk = r
					break
		if e < 0:
			e = fb
			if e < 0:
				return [cells, ds, False]
		ch = nbs[e]
		t += 1
		occ[ch] = t
		for x in mk:
			bad[x] = t
		cells.append(ch)
		ds.append(DIRS[e])
	return [cells, ds, True]


def fly(tx, ty):
	# to (tx, ty) the short way round, stepping around the snake, which blocks drones
	n = SN
	h = n // 2
	for i in range(3 * n):
		x = get_pos_x()
		y = get_pos_y()
		if x == tx and y == ty:
			return True
		dx = (tx - x) % n
		dy = (ty - y) % n
		a = -1
		b = -1
		if dx > 0:
			if dx <= h:
				a = East
			else:
				a = West
		if dy > 0:
			if dy <= h:
				b = North
			else:
				b = South
		if dx < dy:
			c = a
			a = b
			b = c
		if a != -1 and move(a):
			continue
		if b != -1 and move(b):
			continue
		for d in DIRS:
			if move(d):
				break
	return get_pos_x() == tx and get_pos_y() == ty


def helper(w, x, t, k, p):
	# flies to apple x, works out the snake's moves to it (as the drone that sent it did),
	# sends the next helper off from x (it waits there with this drone), reads the next apple
	# off x as soon as it is there and returns the snake's moves from x to that next apple.
	# The next helper reads the same apple at the same moment and flies straight on, so no
	# spawn is on either drone's way once the apple is up. p: the path to w when this drone
	# was sent off at w before w's apple was there (x then still to be read off w).
	# The game picks the next apple again when the snake steps off it, so a next apple on the
	# way to x is not final: None. None too when the snake's body keeps it from reaching x
	# (the snake may be waiting on x), and when the snake has ended (its bones came in)
	# before x was an apple.
	global bad
	if p == 0:
		# only the snake's moves from w to x, for the helper that flies to x meanwhile
		r = leg(w, x, t, k)
		return [r[0], r[1], r[2], None, None, bad]
	b = None
	if p != None:
		b0 = num_items(Items.Bone)
		while get_entity_type() != Entities.Apple:
			if num_items(Items.Bone) != b0:
				return [None, None, None, None, None, None]
		nxt = measure()
		x = IDX[nxt[0]][nxt[1]]
		if x in p:
			return [None, None, None, None, None, None]
		if abs(PX[x] - PX[w]) + abs(PY[x] - PY[w]) >= 4:
			# a far apple: a drone of its own works out the moves to it while this one flies
			b = spawn_drone(helper, w, x, t, k, 0)
	if not fly(PX[x], PY[x]):
		return [None, None, None, None, None, None]
	if b != None:
		r = wait_for(b)
		c = r[0]
		for i in range(len(c)):
			occ[c[i]] = t + i + 1
		bad = r[5]
	else:
		r = leg(w, x, t, k)
	t += len(r[0])
	h = None
	if k + 2 <= HL:
		h = spawn_drone(helper, x, -1, t, k + 1, r[0])
	b0 = num_items(Items.Bone)
	while get_entity_type() != Entities.Apple:
		if num_items(Items.Bone) != b0:
			return [None, None, None, None, None, None]
	nxt = measure()
	y = IDX[nxt[0]][nxt[1]]
	if y in r[0]:
		# the snake may step on that cell before it gets here, and the game then picks the
		# next apple again: wait for that (as long as the snake's walk here can take)
		y0 = y
		until = get_time() + len(r[0]) * 0.07
		while y == y0 and get_time() < until:
			if num_items(Items.Bone) != b0 or get_entity_type() != Entities.Apple:
				return [None, None, None, None, None, bad]
			nxt = measure()
			y = IDX[nxt[0]][nxt[1]]
		if y in r[0]:
			return [None, None, None, None, None, bad]
	r2 = leg(x, y, t, k + 1)
	return [r2[0], r2[1], r2[2], h, nxt, bad]



def play():
	S = SS
	change_hat(Hats.Dinosaur_Hat)
	ch = IDX[get_pos_x()][get_pos_y()]
	if get_entity_type() != Entities.Apple:
		change_hat(Hats.Straw_Hat)
		return 0
	nxt = measure()
	# the first apple is under the drone and the next one anywhere, its moves at the full 400
	# ticks: a far one is dropped for another (two hat changes, 400 ticks) while the expected
	# saving beats that (from the corner one of 10 moves or fewer, near the middle 7)
	x0 = get_pos_x()
	y0 = get_pos_y()
	lim = 6 + (abs(2 * x0 + 1 - SN) // 2 + abs(2 * y0 + 1 - SN) // 2) // 3
	q = 0
	while nxt != None and abs(nxt[0] - x0) + abs(nxt[1] - y0) > lim and q < 40:
		change_hat(Hats.Straw_Hat)
		change_hat(Hats.Dinosaur_Hat)
		nxt = measure()
		q += 1
	for i in range(S):
		occ[i] = -S - 2
		bad[i] = -5
	t = 0
	occ[ch] = 0
	hist[0] = ch
	ca = ch
	ax = 0
	ay = 0
	k = 0
	lining = True
	m = 0
	cum = 0
	last = False
	done = False
	global SPLITS
	global FALLS
	SPLITS = 0
	FALLS = 0
	tried = -1
	global bad
	if HL >= 2:
		k = 1
		ca = IDX[nxt[0]][nxt[1]]
		h = spawn_drone(helper, ch, ca, t, k, None)
		r = leg(ch, ca, t, k)
		while True:
			cells = r[0]
			ds = r[1]
			for j in range(len(ds)):
				if not move(ds[j]):
					done = True
					break
				t += 1
				hist[t % S] = cells[j]
				occ[cells[j]] = t
			if done or not r[2]:
				done = True
				break
			ch = ca
			if get_entity_type() != Entities.Apple:
				done = True
				break
			if h != None:
				r = wait_for(h)
				if r[5] != None:
					bad = r[5]
			if h == None or r[0] == None:
				nxt = measure()
				if k >= HL:
					break
				k += 1
				ca = IDX[nxt[0]][nxt[1]]
				h = spawn_drone(helper, ch, ca, t, k, None)
				r = leg(ch, ca, t, k)
			else:
				h = r[3]
				nxt = r[4]
				k += 1
				ca = IDX[nxt[0]][nxt[1]]
	while k < FREE_LIMIT and not done:
		if ch == ca:
			if last:
				done = True
				break
			k += 1
			ax = nxt[0]
			ay = nxt[1]
			ca = IDX[ax][ay]
		low = t + 1 - k
		need = k + ROOM
		if PLAN and tried != k:
			tried = k
			pl = plan(ch, ax, ay, t, low, need)
			if pl != None:
				cells = pl[0]
				ds = pl[1]
				for j in range(len(cells)):
					if not move(ds[j]):
						done = True
						break
					t += 1
					hist[t % S] = cells[j]
				if done:
					break
				ch = ca
				if get_entity_type() != Entities.Apple:
					done = True
					break
				nxt = measure()
				if nxt == None:
					last = True
				continue
		dx = ax - PX[ch]
		dy = ay - PY[ch]
		if dx > 0:
			s = 0
		elif dx < 0:
			s = 6
		else:
			s = 12
		if dy < 0:
			s += 2
		elif dy == 0:
			s += 4
		if abs(dx) < abs(dy):
			s += 1
		nbs = NB2[ch]
		e = -1
		fb = -1
		mk = NOM
		for d in ORD[s]:
			c = nbs[d]
			if occ[c] < low and bad[c] != t:
				if fb < 0:
					fb = d
				r = chk(c, low, need)
				if r != None:
					e = d
					mk = r
					break
		if e < 0:
			FALLS += 1
			e = fb
			if e < 0:
				done = True
				break
		ch = nbs[e]
		if not move(DIRS[e]):
			done = True
			break
		t += 1
		hist[t % S] = ch
		occ[ch] = t
		for x in mk:
			bad[x] = t
		if ch == ca:
			if get_entity_type() != Entities.Apple:
				done = True
				break
			nxt = measure()
			if nxt == None:
				last = True
	get_tables()
	# from here on the move history is kept by move count: the last k moves copied over
	global hist
	for q in range(t - k, t + 1):
		HB[q] = hist[q % S]
	hist = HB
	while not done:
		if ch == ca:
			if last:
				done = True
				break
			k += 1
			ax = nxt[0]
			ay = nxt[1]
			ca = IDX[ax][ay]
		low = t + 1 - k
		d = 0
		mk = NOM
		if lining:
			lim = (ca - ch) % S
			room = S - 2 - cum - (k - m)
			if room < lim:
				lim = room
			ds = AHEAD[ch]
			for j in range(len(ds)):
				if ds[j] <= lim:
					c = ch + ds[j]
					if c >= S:
						c -= S
					if occ[c] < low and bad[c] != t:
						r = chk(c, low, k + ROOM)
						if r != None:
							d = ds[j]
							way = WAY[ch][j]
							mk = r
							break
		if d > 0:
			m += 1
			cum += d
			ch += d
			if ch >= S:
				ch -= S
		else:
			m = 0
			cum = 0
			r = free_step(ch, ax, ay, low, k + ROOM, t)
			e = r[0]
			mk = r[1]
			if e < 0:
				done = True
				break
			way = DIRS[e]
			ch = NB[ch][e]
		if not move(way):
			done = True
			break
		t += 1
		hist[t] = ch
		occ[ch] = t
		for x in mk:
			bad[x] = t
		if ch == ca:
			if get_entity_type() != Entities.Apple:
				done = True
				break
			nxt = measure()
			if nxt == None:
				last = True
		if lining:
			if m >= k:
				break
		elif k >= FREE_LIMIT:
			lining = True
	while not done and k < K2:
		if ch == ca:
			if last:
				done = True
				break
			k += 1
			ca = IDX[nxt[0]][nxt[1]]
		L = (hist[t + 1 - k] - ch - 1) % S + 1 - MARGIN
		ao = (ca - ch) % S
		if ao <= L:
			L = ao
		elif L <= 0:
			done = True
			break
		while L > 0:
			if L < G2[ch]:
				# no shortcut fits on any of the next L cells
				for q in range(L):
					move(NEXT[ch])
					ch = ST0[ch]
					t += 1
					hist[t] = ch
				break
			if SD2[ch] > L:
				# SD2 is the shorter shortcut: none fits, the next cell on the cycle
				move(NEXT[ch])
				ch = ST0[ch]
				L -= 1
			else:
				d = SD1[ch]
				if d <= L:
					move(SW1[ch])
					ch = ST1[ch]
				else:
					d = SD2[ch]
					move(SW2[ch])
					ch = ST2[ch]
				L -= d
			t += 1
			hist[t] = ch
		if ch == ca:
			if get_entity_type() != Entities.Apple:
				done = True
				break
			nxt = measure()
			if nxt == None:
				last = True
	if HALVES:
		while not done:
			if ch == ca:
				if last:
					move(NEXT[ch])
					break
				k += 1
				ca = IDX[nxt[0]][nxt[1]]
			far = ca
			if far < ch:
				far += S
			for p in range(ch, far):
				move(WALK[p])
			ch = ca
			if get_entity_type() != Entities.Apple:
				break
			nxt = measure()
			if nxt == None:
				last = True
	elif not done:
		get_blocks()
		N = SN
		W = N - 1
		nb = NBLK
		blast = []
		sst = []
		sj = []
		sm = []
		for b in range(nb):
			blast.append(-S - 2)
			sst.append(b)
			sj.append(0)
			sm.append(0)
		for q in range(t - k, t):
			c = hist[q]
			if PX[c] > 0:
				blast[PY[c] // 4] = q
		x = PX[ch]
		y = PY[ch]
		if x == 0:
			seg = nb
			i = N - 1 - y
		else:
			seg = y // 4
			i = RPOS[0][0][x * 4 + y % 4]
		at = ch == ca
		fr = False
		while True:
			if at:
				if last or k + 1 >= DINO_KT:
					if seg == nb:
						if i < N - 1:
							move(South)
						else:
							move(East)
					else:
						D = RDIR[sj[seg]][sm[seg]]
						if i < len(D):
							move(D[i])
						elif seg + sj[seg] == nb - 1:
							move(West)
						else:
							move(North)
					break
				k += 1
				ax = nxt[0]
				ay = nxt[1]
			else:
				ax = PX[ca]
				ay = PY[ca]
			if ax == 0:
				sa = nb
				ia = N - 1 - ay
			else:
				sa = sst[ay // 4]
				ia = RPOS[sj[sa]][sm[sa]][ax * 4 * (sj[sa] + 1) + ay - 4 * sa]
				if fr and sa == seg and ia > i and sj[seg] == 0:
					# the apple is further on in this block, entered empty: the route of this
					# branch of the tree that gets to it soonest
					la = ax * 4 + ay - 4 * seg
					m = CH[TB[DV[sm[seg]][i]][la]]
					if RPOS[0][m][la] < ia:
						sm[seg] = m
						ia = RPOS[0][m][la]
			while seg != sa or i > ia:
				if seg == nb:
					for q in range(i, N - 1):
						move(South)
					move(East)
					t += N - i
					seg = 0
				else:
					j = sj[seg]
					D = RDIR[j][sm[seg]]
					n = len(D)
					if i == 0:
						for q in D:
							move(q)
					else:
						for q in range(i, n):
							move(D[q])
					e = seg + j
					if e == nb - 1:
						move(West)
					else:
						move(North)
					t += n - i + 1
					for b in range(seg, e + 1):
						blast[b] = t - 1
					seg = e + 1
				i = 0
				fr = False
				if seg < nb and ax > 0:
					ab = ay // 4
					jn = ab - seg
					if jn >= 0:
						e2 = sst[ab] + sj[sst[ab]]
						low = t + 1 - k
						free = True
						for b in range(seg, e2 + 1):
							if blast[b] >= low:
								free = False
						if free:
							ry = ay - 4 * ab
							for b in range(seg, e2 + 1):
								sst[b] = b
								sj[b] = 0
								sm[b] = 0
							if SKIP and jn > 0 and ry <= 2 and ax < W:
								sj[seg] = jn
								sm[seg] = (ax - 1) // 2
								for b in range(seg, ab + 1):
									sst[b] = seg
							elif jn == 0:
								sm[seg] = CH[TB[0][ax * 4 + ry]]
							fr = True
							sa = sst[ab]
							ia = RPOS[sj[sa]][sm[sa]][ax * 4 * (sj[sa] + 1) + ay - 4 * sa]
			if seg == nb:
				for q in range(i, ia):
					move(South)
			else:
				D = RDIR[sj[seg]][sm[seg]]
				for q in range(i, ia):
					move(D[q])
			t += ia - i
			i = ia
			at = True
			if get_entity_type() != Entities.Apple:
				break
			nxt = measure()
			if nxt == None:
				last = True
	change_hat(Hats.Straw_Hat)
	FALLS = num_items(Items.Power)
	SPLITS = num_items(Items.Cactus)
	return k


DINO_GOAL = 0
DINO_KT = 1000000000


def dino_round():
	# a snake of k cells pays k * k * 2 ** (Dinosaurs - 1) bones: it stops at the length that
	# covers what the purchase still needs (DINO_GOAL, set by farm), when that is under a full field
	global DINO_KT
	if SN != get_world_size() or num_items(Items.Power) > FALLS or num_items(Items.Cactus) > SPLITS:
		# no other round since the last snake (it made no power or cactus): its field is empty,
		# and the next snake starts where it ended rather than in the corner
		clear()
	if SN != get_world_size():
		dino_setup()
	if not DINO_BG[0]:
		dino_bg()
	DINO_KT = 1000000000
	need = DINO_GOAL - num_items(Items.Bone)
	if need > 0:
		DINO_KT = (need / lvl_mult(Unlocks.Dinosaurs)) ** 0.5 + 0.000001
	k = play()
	log("snake " + str(k) + " bones " + str(num_items(Items.Bone)))


# ---- what to do for a missing item -------------------------------------------------------------

def carrots_for(n):
	# make sure n carrots are on hand (seeds for pumpkins / sunflowers)
	while num_items(Items.Carrot) < n:
		c = with_seeds({Items.Carrot: n * 2})
		if num_unlocked(Unlocks.Polyculture) > 0 and max_drones() > width():
			# more drones than columns: every drone tends a stretch of the field
			d = min(max_drones(), width() * get_world_size())
			spawn_node(0, d, d, (mixed_seg, (c, c, {Items.Carrot: n}), (False, False)))
		else:
			mixed_round((c, c, {Items.Carrot: n}, 0))


WSB = 60000
CJ_N = 0
CJ_S = 0
CJ_D = 12
CJ_D4 = 6
PREP = True
CJ_P = 5


def farm(item, amount):
	global DINO_GOAL
	if item != Items.Gold:
		power_check()
	cells = width() * get_world_size()
	if item == Items.Hay or item == Items.Wood or item == Items.Carrot:
		n = with_seeds({item: amount})
		mixed_round((n, n))
	elif item == Items.Pumpkin:
		if num_unlocked(Unlocks.Cactus) == 2 and num_unlocked(Unlocks.Expand) >= 7:
			# Cactus 3's pumpkins: one more round in the same batch for the seeds of the cactus
			# rounds after it, instead of a pumpkin round of its own between them
			amount += 24000
		m = lvl_mult(Unlocks.Pumpkins)
		c = cells * 2 * m
		if num_items(Items.Carrot) < c:
			# the seeds of every round this purchase still needs in one go: carrot passes between
			# pumpkin rounds start on a cleared field
			k = (amount - num_items(Items.Pumpkin)) // (cells * min(get_world_size(), 6) * m) + 1
			c = max(c, k * cells * m * 1.1)
		carrots_for(c)
		pumpkin_round(amount)
		e7 = get_cost(Unlocks.Expand)[Items.Pumpkin]
		if num_unlocked(Unlocks.Expand) == 6 and num_items(Items.Pumpkin) >= e7 and num_items(Items.Pumpkin) < e7 + PK_RES:
			# Expand 7 is affordable: first the pumpkins for the cactus seeds after it, made here
			# on the 12x12 field (6,900 in ~5 s) instead of in a 16x16 round later (~20 s with
			# the carrots for its seeds)
			carrots_for(cells * 2 * lvl_mult(Unlocks.Pumpkins))
			pumpkin_round(e7 + PK_RES)
	elif item == Items.Weird_Substance and num_unlocked(Unlocks.Cactus) == 0:
		weird_round(amount)
	elif item == Items.Cactus or item == Items.Weird_Substance:
		pc = 2 * lvl_mult(Unlocks.Cactus)
		while num_items(Items.Pumpkin) < cells * pc:
			farm(Items.Pumpkin, cells * pc)
		# from Mazes 3 on, cactus rounds also make weird substance (an extra pass over 1 cell in 5) until
		# WSB is banked, so the last maze needs no weird round of its own
		w = item == Items.Weird_Substance or (num_unlocked(Unlocks.Mazes) >= 3 and num_items(Items.Weird_Substance) < WSB)
		R = 1
		if not w and CJ_P > 0:
			# every round this purchase needs, with the drones staying out between them
			b = bd_cells_n()
			y = b * b * lvl_mult(Unlocks.Cactus)
			if num_unlocked(Unlocks.Dinosaurs) >= 3:
				# the cactus of every purchase left (Dinosaurs up to 5, Mazes 4) in one batch, so
				# the drones stay out between them
				a2 = 0
				dl = num_unlocked(Unlocks.Dinosaurs)
				cc = get_cost(Unlocks.Dinosaurs)[Items.Cactus]
				while dl < 5:
					a2 += cc
					cc = cc * 6
					dl += 1
				if num_unlocked(Unlocks.Mazes) < 4:
					a2 += get_cost(Unlocks.Mazes)[Items.Cactus]
				if a2 > amount:
					amount = a2
			R = min((amount - num_items(Items.Cactus) + y - 1) // y, num_items(Items.Pumpkin) // (b * pc), (num_items(Items.Power) - 100) // drones(), num_items(Items.Weird_Substance) // (2 * drones()))
			if R < 1:
				R = 1
		cactus_round(w, R)
	elif item == Items.Gold:
		global SUN_MZ_DONE
		n = get_world_size()
		m = lvl_mult(Unlocks.Mazes)
		cost = n * m
		finds = (amount - num_items(Items.Gold)) // (n * n * m) + 2
		s_need = min(finds, 300) * cost
		if num_items(Items.Weird_Substance) < s_need:
			farm(Items.Weird_Substance, s_need)
		else:
			# the maze drones spend about one power a second each: make sure it lasts the round
			pw = min(max_drones(), n * n) * (min(finds, 600) * 0.22 + 12)
			if MZ_BUY > 0:
				f1 = (MZ_BUY - num_items(Items.Gold)) // (n * n * m) + 1
				pw = min(max_drones(), n * n) * (f1 * 0.22 + 12) + 2 * min(max_drones(), n * n) * ((finds - f1) * 0.22 + 12)
			if max_drones() == 1:
				pw = max(pw, 60)
			if num_unlocked(Unlocks.Sunflowers) > 0 and num_items(Items.Power) < pw:
				if num_unlocked(Unlocks.Mazes) >= 4 and SUN_PART:
					# the last maze: a power round just big enough for it
					global MZ_RACE
					# (16 drones, 16x16, ~490 finds: racing a spot's owner from a little further pays)
					MZ_RACE = 5
					global SUN_TARGET
					global SUN_MZ
					SUN_TARGET = pw * PW_MARGIN
					if MZ_AFTER_SUN and MZ_BUY == 0:
						SUN_MZ = mz_prep(amount)
					power_round()
					SUN_TARGET = 0
					SUN_MZ = None
				else:
					power_round()
			if SUN_MZ_DONE:
				SUN_MZ_DONE = False
			else:
				maze_round(n, amount)
	elif item == Items.Bone:
		DINO_GOAL = amount
		ac = 2 * lvl_mult(Unlocks.Dinosaurs) * get_world_size() * get_world_size()
		if num_items(Items.Cactus) < ac:
			farm(Items.Cactus, ac)
		else:
			dino_round()
	else:
		log("no farm for " + str(item))
		mixed_round(({Items.Hay: 100}, {}))


def add_cost(need, u):
	cost = get_cost(u)
	for it in cost:
		if it in need:
			need[it] += cost[it]
		else:
			need[it] = cost[it]


def set_need(plan, i):
	cur = {}
	add_cost(cur, plan[i][0])
	look = {}
	for j in range(i, min(i + 3, len(plan))):
		add_cost(look, plan[j][0])
	raw = {}
	add_cost(raw, plan[i][0])
	return (with_seeds(cur), with_seeds(look), raw)


def with_seeds(need):
	# carrots are planted with wood and hay: one of each per carrot, divided by the companion bonus
	if Items.Carrot in need:
		seeds = need[Items.Carrot]
		if num_unlocked(Unlocks.Polyculture) > 0:
			seeds = seeds // 6
		else:
			seeds = seeds // (lvl_mult(Unlocks.Carrots) * 10)
		for it in [Items.Wood, Items.Hay]:
			if it in need:
				need[it] += seeds
			else:
				need[it] = seeds
	return need


def opening():
	# the first unlocks with tight loops: grass on 1x1, then a 1x3 strip, then bushes for wood
	# Plant before Expand 1 and Speed 1: a 1x1 grass cell gives 2 hay/s at any speed, and on
	# the 1x3 strip the grass can then want one of the bushes as its companion (x5 hay)
	# 1x1 grass regrows in exactly one harvest's time (0.5 s at speed 0): cut it blind
	while num_items(Items.Hay) < 50:
		harvest()
	unlock(Unlocks.Plant)
	while num_items(Items.Hay) < 30:
		harvest()
	unlock(Unlocks.Expand)
	# 1x3: bushes at y 0 and 1; the drone sits on the grass at y 2 while they grow
	due = 0
	while num_unlocked(Unlocks.Expand) < 2:
		y = get_pos_y()
		if y == OG1:
			while get_time() < due:
				if can_harvest():
					harvest()
					if num_unlocked(Unlocks.Speed) == 0 and num_items(Items.Hay) >= 20:
						buy(Unlocks.Speed)
			if can_harvest():
				harvest()
		else:
			e = get_entity_type()
			if e == Entities.Bush:
				while not can_harvest():
					pass
				harvest()
			elif e != None:
				harvest()
			plant(Entities.Bush)
			if y == (OG1 + 1) % 3:
				due = get_time() + 4.5
			if num_unlocked(Unlocks.Speed) > 0:
				buy(Unlocks.Expand)
			elif num_items(Items.Hay) >= 20:
				buy(Unlocks.Speed)
		move(North)
	for u in OPENING_WOOD:
		while num_unlocked(u[0]) < u[1]:
			n = get_world_size()
			w = width()
			if w == 1 and SW_ON:
				# 1x3 strip: bushes on y 0 and 1 are cut the moment they ripen (the strip is
				# growth-bound), and the drone sits on the grass at y 2 cutting hay in between
				go(0, 0)
				ta = get_time()
				while num_unlocked(u[0]) < u[1]:
					for y in range(2):
						if get_entity_type() == Entities.Bush:
							while not can_harvest():
								pass
						harvest()
						plant(Entities.Bush)
						if y == 0:
							ta = get_time()
						move(North)
					if buy(u[0]):
						break
					ta = ta + SW_T
					while get_time() < ta:
						if can_harvest():
							harvest()
					move(North)
				break
			if w == 3:
				# bushes on two columns, the third stays grass: the bushes' companion when they
				# want grass, and cut on every pass (n * n cells in n * n moves on the torus): the
				# hay it banks brings Grass 2 forward by more than the wood it costs
				while num_unlocked(u[0]) < u[1]:
					for k in range(n * n):
						e = get_entity_type()
						if get_pos_x() == 2:
							if can_harvest():
								harvest()
						elif e == Entities.Bush:
							if can_harvest():
								harvest()
								plant(Entities.Bush)
						else:
							if e != None:
								harvest()
							plant(Entities.Bush)
						if k % n == n - 1:
							move(East)
							if buy(u[0]):
								break
						else:
							move(North)
				break
			for x in range(w):
				for y in range(n):
					e = get_entity_type()
					if open_grass(x, y, w, n):
						# kept as grass and cut on the way past: cheap hay for Grass 2 and the carrot seeds, and a
						# companion for the bushes that want grass
						if OG_H and e == Entities.Grass and can_harvest():
							harvest()
					elif e == Entities.Bush:
						if can_harvest():
							harvest()
							plant(Entities.Bush)
					else:
						if e != None:
							harvest()
						plant(Entities.Bush)
					if y < n - 1:
						move(North)
				move(North)
				if w > 1:
					move(East)
				if buy(u[0]):
					break


def open_grass(x, y, w, n):
	if w == 1:
		return y == OG1
	return (x + y) % OG_M == 0 and OG_M > 0


OG1 = 2
# strip: how long after planting the y 0 bush the drone leaves the grass (bushes ripen in 3.2-4.8 s)
SW_ON = True
SW_T = 3.6
OG_H = True
OG_M = 2
# Speed 2 on the 1x3 strip, before Expand 2: the strip is growth-bound (two bushes), so the
# speed costs it little, and the 3x3 farm runs at Speed 2 from its start (~6 s a run)
OPENING_WOOD = [(Unlocks.Expand, 2), (Unlocks.Speed, 2), (Unlocks.Carrots, 1)]



WEIRD_EARLY = True


def weird_early(u, mf):
	# make this cactus round weird (about half its yield as the next maze's weird substance) when
	# that does not add a round: rounds left counting the cactus u still lacks and the maze's weird
	# substance, either way
	n = get_world_size()
	y = bd_cells_n() * bd_cells_n() * lvl_mult(Unlocks.Cactus)
	c = get_cost(u)[Items.Cactus] - num_items(Items.Cactus)
	m = lvl_mult(Unlocks.Mazes)
	if u == Unlocks.Mazes:
		m = m * 2
	g = get_cost(mf)[Items.Gold]
	if MERGE_MF:
		g = g * 5
	w = (g // (n * n * m) + 2) * n * m - num_items(Items.Weird_Substance)
	if w <= 0:
		return False
	rn = (max(c - y, 0) + w + y - 1) // y
	rw = (max(c - y // 2, 0) + max(w - y // 2, 0) + y - 1) // y
	return rw <= rn


def run_plan(plan):
	for i in range(len(plan)):
		u = plan[i][0]
		while num_unlocked(u) < plan[i][1]:
			if buy(u):
				continue
			item = lacking(u)
			if item == Items.Hay or item == Items.Wood or item == Items.Carrot:
				power_check()
				mixed_round(set_need(plan, i))
			elif item == Items.Weird_Substance and num_unlocked(Unlocks.Cactus) == 0:
				power_check()
				g = get_cost(u)[item]
				if u == Unlocks.Mazes and num_unlocked(u) == 0 and i + 2 < len(plan) and Unlocks.Megafarm in (plan[i + 1][0], plan[i + 2][0]):
					# the first maze's own weird substance (one maze cost per treasure) in the same round
					# (Watering 3 sits between Mazes 1 and Megafarm 1 in PLAN, so look two entries ahead)
					n = get_world_size()
					g += ((get_cost(Unlocks.Megafarm)[Items.Gold] - num_items(Items.Gold)) // (n * n) + 2) * n
				weird_round(g)
			elif item == Items.Cactus and WEIRD_EARLY and i + 1 < len(plan) and plan[i + 1][0] == Unlocks.Megafarm and num_unlocked(Unlocks.Mazes) > 0 and weird_early(u, plan[i + 1][0]):
				# the last cactus round before a maze: half its yield as the maze's weird substance
				farm(Items.Weird_Substance, 1)
			elif item == Items.Gold and MERGE_MF and u == Unlocks.Megafarm and i + 1 < len(plan) and plan[i + 1][0] == Unlocks.Megafarm and num_unlocked(Unlocks.Megafarm) >= 2:
				global MZ_BUY
				global MZ_SPENT
				c = get_cost(u)[item]
				MZ_BUY = c
				MZ_SPENT = c
				farm(item, c * 5)
				MZ_BUY = 0
				MZ_SPENT = 0
			else:
				farm(item, get_cost(u)[item])


PLAN = [
	(Unlocks.Speed, 1),
	(Unlocks.Plant, 1),
	(Unlocks.Expand, 1),
	(Unlocks.Speed, 2),
	(Unlocks.Expand, 2),
	(Unlocks.Carrots, 1),
	(Unlocks.Speed, 3),
	(Unlocks.Expand, 3),
	(Unlocks.Grass, 2),
	(Unlocks.Trees, 1),
	(Unlocks.Watering, 1),
	(Unlocks.Trees, 2),
	(Unlocks.Watering, 2),
	(Unlocks.Carrots, 2),
	(Unlocks.Carrots, 3),
	(Unlocks.Grass, 3),
	(Unlocks.Sunflowers, 1),
	(Unlocks.Expand, 4),
	(Unlocks.Speed, 4),
	(Unlocks.Fertilizer, 1),
	(Unlocks.Trees, 3),
	(Unlocks.Mazes, 1),
	(Unlocks.Watering, 3),
	(Unlocks.Megafarm, 1),
	(Unlocks.Watering, 4),
	(Unlocks.Grass, 4),
	(Unlocks.Speed, 5),
	(Unlocks.Pumpkins, 1),
	(Unlocks.Expand, 5),
	(Unlocks.Trees, 4),
	(Unlocks.Carrots, 4),
	(Unlocks.Pumpkins, 2),
	(Unlocks.Polyculture, 1),
	(Unlocks.Grass, 5),
	(Unlocks.Watering, 5),
	(Unlocks.Pumpkins, 3),
	(Unlocks.Trees, 5),
	(Unlocks.Carrots, 5),
	(Unlocks.Watering, 6),
	(Unlocks.Pumpkins, 4),
	(Unlocks.Megafarm, 2),
	(Unlocks.Cactus, 1),
	(Unlocks.Expand, 6),
	(Unlocks.Pumpkins, 5),
	(Unlocks.Cactus, 2),
	(Unlocks.Mazes, 2),
	(Unlocks.Mazes, 3),
	(Unlocks.Megafarm, 3),
	(Unlocks.Megafarm, 4),
	(Unlocks.Expand, 7),
	(Unlocks.Dinosaurs, 1),
	(Unlocks.Dinosaurs, 2),
	(Unlocks.Cactus, 3),
	(Unlocks.Dinosaurs, 3),
	(Unlocks.Dinosaurs, 4),
	(Unlocks.Mazes, 4),
	(Unlocks.Dinosaurs, 5),
	(Unlocks.Leaderboard, 1),
]

# (skipped when the script is restarted on a farm already past the opening: tfwr-sim --fork-at)
if num_unlocked(Unlocks.Carrots) == 0:
	opening()
run_plan(PLAN)
log("done")
