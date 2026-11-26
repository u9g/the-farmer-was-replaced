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
# for the first item it lacks, using every drone (pumpkin field watered for faster growth, sorted
# cactus field, one maze shared by all drones and mapped by drones splitting at its forks, the
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


def all_drones(job, a, b):
	# job(i, d, a, b) runs on drone i of d; returns the list of results
	d = drones()
	hs = []
	for i in range(1, d):
		h = spawn_drone(job, i, d, a, b)
		if h != None:
			hs.append(h)
	res = [job(0, d, a, b)]
	for h in hs:
		res.append(wait_for(h))
	return res


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
	if POLY:
		# claim the companion's cell; if it is taken by another type, replant for a new companion
		for _ in range(3):
			comp = get_companion()
			if comp == None:
				return
			cp = comp[1]
			if cp[0] >= COLS[0] and cp[0] < COLS[1] and cp != pos:
				if cp not in WANT:
					WANT[cp] = (comp[0], pos)
					REQ[pos] = cp
					return
				if WANT[cp][0] == comp[0]:
					REQ[pos] = cp
					return
			harvest()
			if c != Entities.Grass or get_ground_type() == Grounds.Soil:
				if not plant(c):
					return


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
		for x in my_cols(i, d):
			go(x, 0)
			ce = choose(True)
			co = choose(False)
			if ce == co and not POLY and num_unlocked(Unlocks.Plant) > 0:
				# a mix of crop types lets some plants find their companion (x5 even before polyculture)
				if ce == Entities.Grass:
					co = Entities.Bush
				else:
					co = Entities.Grass
			if x % 2 == 0:
				cs = [ce, co]
			else:
				cs = [co, ce]
			for y in range(n):
				mixed_cell(strip, weird, cs[y % 2])
				move(North)
		return 0
	# one drone, no polyculture: pass after pass until the current unlock is affordable;
	# a torus walk (n - 1 steps north per column, then east) visits n * n cells in n * n moves
	while True:
		for x in range(w):
			if get_pos_x() != x:
				go(x, get_pos_y())
			ce = choose(True)
			co = choose(False)
			if ce == co and not POLY and num_unlocked(Unlocks.Plant) > 0:
				# a mix of crop types lets some plants find their companion (x5 even before polyculture)
				if ce == Entities.Grass:
					co = Entities.Bush
				else:
					co = Entities.Grass
			sx = SUN_STRIP and x < SUN_COLS and w >= 6 and num_unlocked(Unlocks.Sunflowers) > 0
			for k in range(n):
				if sx:
					sun_cell()
				else:
					if (x + get_pos_y()) % 2 == 0:
						c = ce
					else:
						c = co
					if w * n <= 3:
						tend_wait(c)
					else:
						tend_plain(c)
				if k < n - 1 or w == 1:
					move(North)
		cur = NEED[0]
		done = True
		for it in cur:
			if num_items(it) < cur[it]:
				done = False
		if done:
			return 0
		for k in PEND:
			PEND[k] = 0


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
	all_drones(mixed_job, need, (strip, weird))


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


def poly_job(i, d, need, flags):
	passes = 2
	strip = flags[0]
	global PW_T
	global PW_BY
	n = get_world_size()
	c0 = i * n // d
	c1 = (i + 1) * n // d
	if strip:
		c0 = 2
	PW_C0[0] = c0
	PW_C1[0] = c1
	if len(PW_T) != n * n:
		PW_T = []
		PW_BY = []
		for c in range(n * n):
			PW_T.append(None)
			PW_BY.append(-1)
	if strip:
		go(0, 0)
		for x in range(2):
			for y in range(n):
				sun_cell()
				move(North)
			move(East)
	go(c0, 0)
	for p in range(passes):
		have = {Items.Carrot: num_items(Items.Carrot), Items.Wood: num_items(Items.Wood), Items.Hay: num_items(Items.Hay)}
		done = True
		for it in need:
			if have[it] < need[it]:
				done = False
		if done:
			return 0
		hay = Items.Hay in need and have[Items.Hay] < need[Items.Hay]
		if p % 2 == 0:
			xs = range(c0, c1)
		else:
			xs = range(c1 - 1, c0 - 1, -1)
		for x in xs:
			have = {Items.Carrot: num_items(Items.Carrot), Items.Wood: num_items(Items.Wood), Items.Hay: num_items(Items.Hay)}
			t = pw_crop(need, have, n)
			if get_pos_y() == 0:
				ys = range(n)
				dy = North
			else:
				ys = range(n - 1, -1, -1)
				dy = South
			k = 0
			for y in ys:
				c = x * n + y
				if (x + y) % 2 == 0:
					pw_cell_crop(c, n, t, 2)
				else:
					pw_cell_servant(c, hay)
				k += 1
				if k < n:
					move(dy)
			if p % 2 == 0:
				if x < c1 - 1:
					move(East)
			elif x > c0:
				move(West)
	return 0



# ---- weird substance before cactus ------------------------------------------------------------
# Trees on one checkerboard colour, grass on the other. Plus shapes centred where (x + 2y) % 5 == 0
# tile the field, so one weird substance per centre turns every plant weird once a pass; a weird
# plant gives half its yield as weird substance. Fertilizer starts it off (it only marks its own
# cell).

def wsub_job(i, d, goal, b):
	n = get_world_size()
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
					if e == Entities.Tree:
						# every tree is cut once a pass, so each is toggled exactly once
						while not can_harvest():
							pass
						harvest()
						plant(Entities.Tree)
					else:
						if e != None:
							harvest()
						plant(Entities.Tree)
				elif get_ground_type() == Grounds.Soil:
					# back to grassland, so grass stands here and regrows by itself
					if e != None and can_harvest():
						harvest()
					till()
				elif e == Entities.Grass:
					if can_harvest():
						harvest()
				elif e != None:
					if can_harvest():
						harvest()
				if (x + 2 * y) % 5 == 0:
					if num_items(Items.Weird_Substance) >= 1:
						use_item(Items.Weird_Substance)
					elif num_items(Items.Fertilizer) >= 1:
						use_item(Items.Fertilizer)
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
			cells.append((x, y, measure()))
			move(North)
	return cells


def sun_cut_job(i, d, cells, v):
	for c in cells[i]:
		if c[2] == v:
			go(c[0], c[1])
			while not can_harvest():
				pass
			harvest()
	return 0


def power_round():
	n = width() * get_world_size()
	if num_items(Items.Carrot) < n:
		return
	cells = all_drones(sun_plant_job, 0, 0)
	for v in range(15, 6, -1):
		all_drones(sun_cut_job, cells, v)


SUN_STRIP = True
SUN_COLS = 2


def power_check():
	if num_unlocked(Unlocks.Sunflowers) == 0 or width() < 6 or (SUN_STRIP and drones() == 1):
		return
	if num_items(Items.Power) < 60 * drones():
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

PK_WLO = 0.4
PK_FA = 2


def pk_wet():
	if get_water() < PK_WLO and num_items(Items.Water) >= 1:
		use_item(Items.Water)


def pk_wet2():
	# a replanted cell is likely to be among the last to grow: water it more
	w = get_water()
	s = num_items(Items.Water)
	if w < 0.75 and s >= 1:
		use_item(Items.Water, min(s, (1 - w) // 0.25))


def pk_job(i, d, a):
	n = get_world_size()
	p = snake(i, d)
	px = p[0]
	py = p[1]
	L = len(px)
	seed = get_cost(Entities.Pumpkin)[Items.Carrot]
	go(px[0], py[0])
	todo = []
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
			if px[t + 1] != px[t]:
				move(East)
			elif py[t + 1] > py[t]:
				move(North)
			else:
				move(South)
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
					if e != Entities.Dead_Pumpkin and e != None:
						harvest()
					if num_items(Items.Carrot) < seed:
						return 0
					plant(Entities.Pumpkin)
					pk_wet2()
					if not alone:
						nt.append(t)
						break
		todo = nt
	return 0


def pumpkin_round():
	# every drone returns once its columns have grown, so the field is one pumpkin by then
	d = drones()
	fan(pk_job, 0, d, d, 0)
	if get_entity_type() == Entities.Pumpkin:
		harvest()


def pumpkin_until(goal):
	# pumpkin rounds until the inventory holds goal pumpkins (or carrots run out)
	seed = get_cost(Entities.Pumpkin)[Items.Carrot]
	n = get_world_size()
	while num_items(Items.Pumpkin) < goal and num_items(Items.Carrot) >= seed * n * n:
		pumpkin_round()


# ---- cactus ------------------------------------------------------------------------------------
# Entry point: cactus_round(weird). weird=True makes every cactus weird before the harvest.
# Every drone owns whole columns and walks them as one snake path, back and forth. It plants its
# path, then sorts in place with no barrier: on each cell it measures the cell and its four
# neighbours (across other drones' columns too) and swaps the most inverted pair, staying on the
# cell until it is in order, then steps on. A drone stops once every cell of its path was in order
# when it last looked. Then the field is harvested from the south-west corner.

def cactus_job(i, d, a):
	n = get_world_size()
	p = snake(i, d)
	px = p[0]
	py = p[1]
	L = len(px)
	F = []
	B = [None]
	DE = []
	DN = []
	DW = []
	DS = []
	for k in range(L):
		x = px[k]
		y = py[k]
		if k < L - 1:
			F.append(step_dir(x, y, px[k + 1], py[k + 1]))
			B.append(step_dir(px[k + 1], py[k + 1], x, y))
		else:
			F.append(None)
		DE.append(None)
		DN.append(None)
		DW.append(None)
		DS.append(None)
		if x < n - 1:
			DE[k] = East
		if y < n - 1:
			DN[k] = North
		if x > 0:
			DW[k] = West
		if y > 0:
			DS[k] = South
	go(px[0], py[0])
	for k in range(L):
		if get_entity_type() != Entities.Cactus:
			clear_cell()
			soil()
			plant(Entities.Cactus)
		if k < L - 1:
			move(F[k])
	k = L - 1
	st = -1
	lo = L
	hi = -1
	ld = None
	delay = 3 + 7 * (i % 5)
	while lo > 0 or hi < L - 1:
		h = measure()
		e = measure(DE[k])
		if e == None:
			e = h
		nn = measure(DN[k])
		if nn == None:
			nn = h
		w = measure(DW[k])
		if w == None:
			w = h
		s = measure(DS[k])
		if s == None:
			s = h
		if e < nn:
			mlo = e
			dl = DE[k]
		else:
			mlo = nn
			dl = DN[k]
		if w > s:
			mhi = w
			dh = DW[k]
		else:
			mhi = s
			dh = DS[k]
		dd = None
		if h - mlo > mhi - h:
			if h > mlo:
				dd = dl
		elif mhi > h:
			dd = dh
		if dd != None:
			swap(dd)
			lo = L
			hi = -1
			if dd == ld:
				t = get_tick_count() + delay
				while get_tick_count() < t:
					pass
				ld = None
			else:
				ld = dd
		else:
			ld = None
			if k < lo:
				lo = k
			if k > hi:
				hi = k
			if lo == 0 and hi == L - 1:
				break
			if k + st < 0 or k + st >= L:
				st = -st
			if st > 0:
				move(F[k])
			else:
				move(B[k])
			k += st
	return 0


def weird_job(i, d, a):
	# toggle weirdness on plus shapes: centres at (x + 2y) % 5 == 0 cover the plane once
	n = get_world_size()
	for x in my_cols(i, d):
		for y in range(n):
			if (x + 2 * y) % 5 == 0:
				go(x, y)
				if num_items(Items.Weird_Substance) >= 1:
					use_item(Items.Weird_Substance)
				elif num_items(Items.Fertilizer) >= 1:
					use_item(Items.Fertilizer)
	return 0


def cactus_round(weird):
	d = drones()
	fan(cactus_job, 0, d, d, 0)
	if weird:
		fan(weird_job, 0, d, d, 0)
	go(0, 0)
	harvest()


# ---- mazes -------------------------------------------------------------------------------------

DIRS = [North, East, South, West]
DX = [0, 1, 0, -1]
DY = [1, 0, -1, 0]
BACK = [2, 3, 0, 1]
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
MZ_PRUNE_MIN = 4
MZ_LOST = 3.0
MZ_GX = 1
MZ_GY = 1
MZ_WAIT = 12
MZ_RESCUE = 1.0
MZ_PARKING = True


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


def mz_walk(a, b):
	# along the map's tree from cell a to cell b
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
	for k in up:
		move(DIRS[k])
	for i in range(len(down) - 1, -1, -1):
		move(DIRS[down[i]])


def mz_paths(park):
	# shortest ways from the park to every walked cell over the sides known open
	n = MZ_N
	adj = MZ_ADJ
	path = {park: []}
	q = [park]
	i = 0
	while i < len(q):
		x = q[i]
		i += 1
		px = path[x]
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
	n = MZ_N
	me = MZ_ME
	c = get_pos_x() + get_pos_y() * n
	root = c
	rx = c % n
	ry = c // n
	pd = {c: -1}
	dp = {c: 0}
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
			if (c + DX[k] + DY[k] * n) in dp:
				continue
			move(DIRS[k])
			stack.append(k)
			nd = dp[c] + 1
			c = c + DX[k] + DY[k] * n
			pd[c] = k
			dp[c] = nd
			order.append(c)
			b = BACK[k]
			ks = []
			ks2 = []
			hit = False
			tie = False
			cx = c % n - rx
			cy = c // n - ry
			for k2 in range(4):
				if k2 != b and can_move(DIRS[k2]):
					nc = c + DX[k2] + DY[k2] * n
					if nc in dp:
						pass
					elif nc in si:
						pd[nc] = k2
						dp[nc] = nd + 1
						found.append(nc)
						hit = True
						if si[nc] < me:
							tie = True
					elif MZ_ORDER != 0 and (DX[k2] * cx + DY[k2] * cy) * MZ_ORDER > 0:
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
			c = c - DX[k] - DY[k] * n
	# cut every path to another start at its middle (ties to the lower index)
	cut = {}
	for f in found:
		j = si[f]
		h = dp[f]
		x = f
		while x != root:
			if 2 * dp[x] > h or (2 * dp[x] == h and j < me):
				cut[x] = True
				k = pd[x]
				x = x - DX[k] - DY[k] * n
			else:
				break
	own = {root: True}
	cnt = {root: 1}
	for i in range(1, len(order)):
		x = order[i]
		k = pd[x]
		p = x - DX[k] - DY[k] * n
		if p in own and not (x in cut):
			own[x] = True
			cnt[x] = 1
		else:
			cnt[x] = 0
	for i in range(len(order) - 1, 0, -1):
		x = order[i]
		if cnt[x] > 0:
			k = pd[x]
			p = x - DX[k] - DY[k] * n
			cnt[p] += cnt[x]
	tot = len(own)
	park = root
	for x in own:
		if 2 * cnt[x] > tot and dp[x] > dp[park]:
			park = x
	# the open sides of every cell walked (tree edges for now; walls only ever come down),
	# and the sides toward other walked cells still to be tried
	adj = {}
	for x in order:
		adj[x] = []
	for i in range(1, len(order)):
		x = order[i]
		k = pd[x]
		p = x - DX[k] - DY[k] * n
		adj[p].append(k)
		adj[x].append(BACK[k])
	MZ_ADJ = adj
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
	n = MZ_N
	own = MZ_OWN
	known = MZ_DP
	paths = MZ_PATH
	home = MZ_PARK
	race = MZ_RACE
	rep = 200 / (400 * 1.5 ** num_unlocked(Unlocks.Speed)) + 0.001
	lim = g0 + 300 * per
	cur = MZ_CUR
	if park:
		mz_walk(cur, home)
		cur = home
	last = -1
	seen = 0
	while True:
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
				p = mz_seek(c, True)
				if get_pos_x() + get_pos_y() * n == c:
					use_item(Items.Weird_Substance, cost)
				for i in range(len(p) - 1, -1, -1):
					move(DIRS[BACK[p[i]]])
		elif c in known:
			# not mine, but on my map: fetch it if its owner has not come for a while
			deadline = seen + MZ_RESCUE
			while c == last and get_time() < deadline:
				t = measure()
				if t == None:
					c = -2
				else:
					c = t[0] + t[1] * n
			go_for = c == last
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
			else:
				mz_walk(cur, c)
			cur = c
			if num_items(Items.Gold) >= goal:
				if get_entity_type() == Entities.Treasure:
					harvest()
				return 0
			if not use_item(Items.Weird_Substance, cost):
				g = num_items(Items.Gold)
				if g >= lim and get_entity_type() == Entities.Treasure:
					harvest()
					if num_items(Items.Gold) > g:
						MZ_CUR = cur
						return 2
			until = get_time() + rep
			if park:
				if c in paths:
					p = paths[c]
					if MZ_SHORT:
						# on the way back, look for walls that came down, then re-plan
						x = c
						got = mz_try(x)
						for i in range(len(p) - 1, -1, -1):
							k = p[i]
							move(DIRS[BACK[k]])
							x = x - DX[k] - DY[k] * n
							if mz_try(x):
								got = True
						if got:
							paths = mz_paths(home)
							MZ_PATH = paths
					else:
						for i in range(len(p) - 1, -1, -1):
							move(DIRS[BACK[p[i]]])
				else:
					mz_walk(cur, home)
				cur = home
			while get_time() < until:
				pass


def mz_life(me, goal, stop, st, start_at, park):
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
	MZ_N = n
	MZ_ME = me
	m = lvl_mult(Unlocks.Mazes)
	cost = n * m
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
		if get_pos_x() + get_pos_y() * n != root:
			mz_seek(root, False)
		mz_explore(si)
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


def maze_round(s, goal):
	# s is ignored: the maze always covers the whole field. Keeps making mazes (each good for
	# 300 treasures) until goal gold, MAZE_SECS, or too little weird substance for another maze.
	stop = get_time() + MAZE_SECS
	n = get_world_size()
	d = min(max_drones(), n * n)
	st = mz_starts(n, d)
	park = MZ_PARKING and d >= 4
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

FREE_LIMIT = 16
MARGIN = 1
ROOM = 2
SN = 0
SS = 0
SHORTCUT_LIMIT = 0
IDX = []
PX = []
PY = []
AHEAD = []
WAY = []
NEXT = []
NB = []
WALK = []
occ = []
hist = []
vis = []
fills = [0]


def dn_rows(j, d, a0, b0):
	N = SN
	S = SS
	ah = []
	wy = []
	nb = []
	for i in range(j * S // d, (j + 1) * S // d):
		pairs = []
		row = []
		for k in range(4):
			x = PX[i] + DX[k]
			y = PY[i] + DY[k]
			if x >= 0 and x < N and y >= 0 and y < N:
				pairs.append([(IDX[x][y] - i) % S, DIRS[k]])
				row.append(IDX[x][y])
			else:
				row.append(-1)
		nb.append(row)
		ds = []
		ws = []
		while pairs:
			best = pairs[0]
			for p in pairs:
				if p[0] > best[0]:
					best = p
			pairs.remove(best)
			ds.append(best[0])
			ws.append(best[1])
		ah.append(ds)
		wy.append(ws)
	return [ah, wy, nb]


def dino_setup():
	global SN
	global SS
	global SHORTCUT_LIMIT
	global IDX
	global PX
	global PY
	global AHEAD
	global WAY
	global NEXT
	global NB
	global WALK
	global occ
	global hist
	global vis
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
	PX = [0]
	PY = [0]
	i = 0
	for y in range(N):
		if y % 2 == 0:
			xs = range(1, N)
		else:
			xs = range(N - 1, 0, -1)
		for x in xs:
			i += 1
			IDX[x][y] = i
			PX.append(x)
			PY.append(y)
	for y in range(N - 1, 0, -1):
		i += 1
		IDX[0][y] = i
		PX.append(0)
		PY.append(y)
	# the neighbour tables are built by every drone at once, a slice each
	AHEAD = []
	WAY = []
	NB = []
	for r in all_drones(dn_rows, 0, 0):
		for row in r[0]:
			AHEAD.append(row)
		for row in r[1]:
			WAY.append(row)
		for row in r[2]:
			NB.append(row)
	NEXT = []
	for i in range(S):
		ds = AHEAD[i]
		for k in range(len(ds)):
			if ds[k] == 1:
				NEXT.append(WAY[i][k])
	WALK = []
	for i in range(2 * S):
		WALK.append(NEXT[i % S])
	occ = []
	hist = []
	vis = []
	for i in range(S):
		occ.append(0)
		hist.append(0)
		vis.append(0)


def roomy(start, low, need):
	fills[0] += 1
	f = fills[0]
	vis[start] = f
	front = [start]
	cnt = 1
	dd = 0
	while front:
		dd += 1
		gone = low + dd - 1
		ahead = []
		for c in front:
			for e in NB[c]:
				if e >= 0 and vis[e] != f:
					vis[e] = f
					o = occ[e]
					if o < low:
						ahead.append(e)
						cnt += 1
					elif o < gone:
						return True
		if cnt >= need:
			return True
		front = ahead
	return False


def safe(c, ch, low, need):
	for g in NB[c]:
		if g != ch and g >= 0 and occ[g] >= low:
			return roomy(c, low, need)
	return True


def free_step(ch, ax, ay, low, need):
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
			if c >= 0 and occ[c] < low:
				if fallback < 0:
					fallback = e
				if safe(c, ch, low, need):
					return e
	return fallback


def play():
	S = SS
	change_hat(Hats.Dinosaur_Hat)
	ch = IDX[get_pos_x()][get_pos_y()]
	if get_entity_type() != Entities.Apple:
		change_hat(Hats.Straw_Hat)
		return 0
	nxt = measure()
	for i in range(S):
		occ[i] = -S - 2
	t = 0
	occ[ch] = 0
	hist[0] = ch
	ca = ch
	ax = 0
	ay = 0
	k = 0
	lining = FREE_LIMIT <= 0
	m = 0
	cum = 0
	last = False
	done = False
	while True:
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
					if occ[c] < low and safe(c, ch, low, k + ROOM):
						d = ds[j]
						way = WAY[ch][j]
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
			e = free_step(ch, ax, ay, low, k + ROOM)
			if e < 0:
				done = True
				break
			way = DIRS[e]
			ch = NB[ch][e]
		if not move(way):
			done = True
			break
		t += 1
		hist[t % S] = ch
		occ[ch] = t
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
	while not done and k < SHORTCUT_LIMIT:
		if ch == ca:
			if last:
				done = True
				break
			k += 1
			ca = IDX[nxt[0]][nxt[1]]
		t += 1
		dt = (hist[(t - k) % S] - ch - 1) % S + 1 - MARGIN
		lim = (ca - ch) % S
		if dt < lim:
			lim = dt
		ds = AHEAD[ch]
		d = 1
		way = NEXT[ch]
		for j in range(len(ds)):
			if ds[j] <= lim:
				d = ds[j]
				way = WAY[ch][j]
				break
		if not move(way):
			done = True
			break
		ch += d
		if ch >= S:
			ch -= S
		hist[t % S] = ch
		if ch == ca:
			if get_entity_type() != Entities.Apple:
				done = True
				break
			nxt = measure()
			if nxt == None:
				last = True
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
			if not move(WALK[p]):
				done = True
				break
		if done:
			break
		ch = ca
		if get_entity_type() != Entities.Apple:
			break
		nxt = measure()
		if nxt == None:
			last = True
	change_hat(Hats.Straw_Hat)
	return k


def dino_round():
	clear()
	if SN != get_world_size():
		dino_setup()
	k = play()
	log("snake " + str(k) + " bones " + str(num_items(Items.Bone)))


# ---- what to do for a missing item -------------------------------------------------------------

def carrots_for(n):
	# make sure n carrots are on hand (seeds for pumpkins / sunflowers)
	while num_items(Items.Carrot) < n:
		c = with_seeds({Items.Carrot: n * 2})
		mixed_round((c, c))


def farm(item, amount):
	power_check()
	cells = width() * get_world_size()
	if item == Items.Hay or item == Items.Wood or item == Items.Carrot:
		n = with_seeds({item: amount})
		mixed_round((n, n))
	elif item == Items.Pumpkin:
		carrots_for(cells * 2 * lvl_mult(Unlocks.Pumpkins))
		pumpkin_round()
	elif item == Items.Weird_Substance and num_unlocked(Unlocks.Cactus) == 0:
		weird_round(amount)
	elif item == Items.Cactus or item == Items.Weird_Substance:
		pc = 2 * lvl_mult(Unlocks.Cactus)
		while num_items(Items.Pumpkin) < cells * pc:
			farm(Items.Pumpkin, cells * pc)
		cactus_round(item == Items.Weird_Substance)
	elif item == Items.Gold:
		n = get_world_size()
		m = lvl_mult(Unlocks.Mazes)
		cost = n * m
		finds = (amount - num_items(Items.Gold)) // (n * n * m) + 2
		s_need = min(finds, 300) * cost
		if num_items(Items.Weird_Substance) < s_need:
			farm(Items.Weird_Substance, s_need)
		else:
			maze_round(n, amount)
	elif item == Items.Bone:
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
	return (with_seeds(cur), with_seeds(look))


def with_seeds(need):
	# carrots are planted with wood and hay: one of each per carrot, divided by the companion bonus
	if Items.Carrot in need:
		seeds = need[Items.Carrot]
		if num_unlocked(Unlocks.Polyculture) > 0:
			seeds = seeds // 6
		for it in [Items.Wood, Items.Hay]:
			if it in need:
				need[it] += seeds
			else:
				need[it] = seeds
	return need


def opening():
	# the first unlocks with tight loops: grass on 1x1, then a 1x3 strip, then bushes for wood
	while not (num_unlocked(Unlocks.Speed) >= 1 and num_unlocked(Unlocks.Expand) >= 1):
		if can_harvest():
			harvest()
		if num_unlocked(Unlocks.Speed) == 0:
			buy(Unlocks.Speed)
		elif num_unlocked(Unlocks.Expand) == 0:
			buy(Unlocks.Expand)
	while num_unlocked(Unlocks.Plant) == 0:
		# grass regrows in 0.5 s, faster than a harvest and a move: stay on one cell
		if can_harvest():
			harvest()
			buy(Unlocks.Plant)
	for u in OPENING_WOOD:
		while num_unlocked(u[0]) < u[1]:
			n = get_world_size()
			w = width()
			for x in range(w):
				for y in range(n):
					e = get_entity_type()
					if e == Entities.Bush:
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


OPENING_WOOD = [(Unlocks.Expand, 2), (Unlocks.Speed, 2), (Unlocks.Carrots, 1)]



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
				weird_round(get_cost(u)[item])
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
	(Unlocks.Watering, 1),
	(Unlocks.Expand, 3),
	(Unlocks.Trees, 1),
	(Unlocks.Trees, 2),
	(Unlocks.Watering, 2),
	(Unlocks.Expand, 4),
	(Unlocks.Carrots, 2),
	(Unlocks.Carrots, 3),
	(Unlocks.Grass, 2),
	(Unlocks.Grass, 3),
	(Unlocks.Sunflowers, 1),
	(Unlocks.Pumpkins, 1),
	(Unlocks.Speed, 4),
	(Unlocks.Fertilizer, 1),
	(Unlocks.Mazes, 1),
	(Unlocks.Megafarm, 1),
	(Unlocks.Watering, 3),
	(Unlocks.Polyculture, 1),
	(Unlocks.Trees, 3),
	(Unlocks.Grass, 4),
	(Unlocks.Speed, 5),
	(Unlocks.Expand, 5),
	(Unlocks.Watering, 4),
	(Unlocks.Carrots, 4),
	(Unlocks.Pumpkins, 2),
	(Unlocks.Watering, 5),
	(Unlocks.Pumpkins, 3),
	(Unlocks.Pumpkins, 4),
	(Unlocks.Megafarm, 2),
	(Unlocks.Cactus, 1),
	(Unlocks.Cactus, 2),
	(Unlocks.Expand, 6),
	(Unlocks.Mazes, 2),
	(Unlocks.Mazes, 3),
	(Unlocks.Megafarm, 3),
	(Unlocks.Megafarm, 4),
	(Unlocks.Expand, 7),
	(Unlocks.Dinosaurs, 1),
	(Unlocks.Dinosaurs, 2),
	(Unlocks.Dinosaurs, 3),
	(Unlocks.Dinosaurs, 4),
	(Unlocks.Mazes, 4),
	(Unlocks.Leaderboard, 1),
]

opening()
run_plan(PLAN)
log("done")
