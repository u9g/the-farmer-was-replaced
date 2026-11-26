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
			for k in range(n):
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


def power_check():
	if num_unlocked(Unlocks.Sunflowers) == 0 or width() < 6:
		return
	if num_items(Items.Power) < 60 * drones():
		power_round()


# ---- pumpkins ----------------------------------------------------------------------------------

def pumpkin_job(i, d, a, b):
	n = get_world_size()
	todo = []
	for x in my_cols(i, d):
		go(x, 0)
		for y in range(n):
			e = get_entity_type()
			if e != Entities.Pumpkin:
				clear_cell()
				soil()
				if WET_PK:
					wet()
				plant(Entities.Pumpkin)
				todo.append((x, y))
			elif not can_harvest():
				todo.append((x, y))
			move(North)
	# revisit only the cells not yet grown; a pumpkin that died is replanted and revisited
	while len(todo) > 0:
		nt = []
		for c in todo:
			go(c[0], c[1])
			while get_entity_type() == Entities.Pumpkin and not can_harvest():
				pass
			if get_entity_type() != Entities.Pumpkin:
				if num_items(Items.Carrot) < 1:
					return 0
				clear_cell()
				plant(Entities.Pumpkin)
				if num_items(Items.Fertilizer) >= 1:
					use_item(Items.Fertilizer)
				nt.append(c)
		todo = nt
	return 0


def pumpkin_round():
	all_drones(pumpkin_job, 0, 0)
	if get_entity_type() == Entities.Pumpkin:
		harvest()


# ---- cactus ------------------------------------------------------------------------------------

def cactus_plant_job(i, d, a, b):
	n = get_world_size()
	for x in my_cols(i, d):
		go(x, 0)
		for y in range(n):
			if get_entity_type() != Entities.Cactus:
				clear_cell()
				soil()
				plant(Entities.Cactus)
			move(North)
	return 0


def sort_line(fwd, back, n):
	# drone stands at the start of a line of n cacti; shaker sort, ascending along fwd
	lo = 0
	hi = n - 1
	pos = 0
	while lo < hi:
		last = lo
		while pos < hi:
			if measure() > measure(fwd):
				swap(fwd)
				last = pos
			move(fwd)
			pos += 1
		hi = last
		if lo >= hi:
			break
		last = hi
		while pos > lo:
			if measure() < measure(back):
				swap(back)
				last = pos
			move(back)
			pos -= 1
		lo = last


def cactus_rows_job(i, d, a, b):
	n = get_world_size()
	for y in range(i * n // d, (i + 1) * n // d):
		go(0, y)
		sort_line(East, West, n)
	return 0


def cactus_cols_job(i, d, a, b):
	n = get_world_size()
	for x in my_cols(i, d):
		go(x, 0)
		sort_line(North, South, n)
	return 0


def weird_job(i, d, a, b):
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
	all_drones(cactus_plant_job, 0, 0)
	all_drones(cactus_rows_job, 0, 0)
	all_drones(cactus_cols_job, 0, 0)
	if weird:
		all_drones(weird_job, 0, 0)
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
# The field is cut into q x q mazes of size s. A leader drone per maze makes the maze, maps it
# with one depth-first walk, splits it into territories around h home cells, and spawns the
# other h - 1 workers, which inherit the map. Every worker polls where the treasure is and goes
# for it only when it lies in its own territory, then walks back home.

MZ_S = 0
MZ_RX = 0
MZ_RY = 0
OPENS = []
OWNER = []
PDIR = []
HOMES = []
CPATH = []
DEPTH = []
PARK = []
MZ_STAY = True
MZ_PAR = True
MZ_PARKING = True


def mz_map():
	# depth-first walk from the drone's cell; OPENS[c] = open directions of local cell c
	global OPENS
	s = MZ_S
	opens = []
	for c in range(s * s):
		opens.append(None)
	x = get_pos_x() - MZ_RX
	y = get_pos_y() - MZ_RY
	c = x + y * s
	o = []
	for k in range(4):
		if can_move(DIRS[k]):
			o.append(k)
	opens[c] = o
	stack = []
	nxt = [0]
	while True:
		o = opens[c]
		i = nxt[-1]
		moved = False
		while i < len(o):
			k = o[i]
			i += 1
			nc = c + DX[k] + DY[k] * s
			if opens[nc] == None:
				nxt[-1] = i
				move(DIRS[k])
				stack.append(k)
				c = nc
				o2 = []
				for k2 in range(4):
					if can_move(DIRS[k2]):
						o2.append(k2)
				opens[c] = o2
				nxt.append(0)
				moved = True
				break
		if moved:
			continue
		if len(stack) == 0:
			OPENS = opens
			return
		k = stack.pop()
		nxt.pop()
		move(DIRS[BACK[k]])
		c = c - DX[k] - DY[k] * s


def mz_branch(k0):
	# walk into direction k0 from here, map that whole branch of the maze tree depth first and
	# come back; at a fork, a free drone takes one of the branches. Returns [cell, opens] pairs.
	s = MZ_S
	out = []
	hs = []
	move(DIRS[k0])
	stack = [k0]
	c = (get_pos_x() - MZ_RX) + (get_pos_y() - MZ_RY) * s
	o = []
	for k in range(4):
		if can_move(DIRS[k]):
			o.append(k)
	out.append([c, o])
	kids = [[]]
	for k in o:
		if k != BACK[k0]:
			kids[0].append(k)
	while True:
		ks = kids[-1]
		if len(ks) > 0:
			k = ks.pop()
			if len(ks) > 0 and num_drones() < max_drones():
				h = spawn_drone(mz_branch, k)
				if h != None:
					hs.append(h)
					continue
			move(DIRS[k])
			stack.append(k)
			c = c + DX[k] + DY[k] * s
			o = []
			for k2 in range(4):
				if can_move(DIRS[k2]):
					o.append(k2)
			out.append([c, o])
			nk = []
			for k2 in o:
				if k2 != BACK[k]:
					nk.append(k2)
			kids.append(nk)
		else:
			kids.pop()
			k = stack.pop()
			move(DIRS[BACK[k]])
			c = c - DX[k] - DY[k] * s
			if len(stack) == 0:
				break
	for h in hs:
		for e in wait_for(h):
			out.append(e)
	return out


def mz_map_par():
	global OPENS
	s = MZ_S
	opens = []
	for c in range(s * s):
		opens.append(None)
	c = (get_pos_x() - MZ_RX) + (get_pos_y() - MZ_RY) * s
	o = []
	for k in range(4):
		if can_move(DIRS[k]):
			o.append(k)
	opens[c] = o
	hs = []
	mine = []
	for i in range(len(o)):
		if i < len(o) - 1 and num_drones() < max_drones():
			h = spawn_drone(mz_branch, o[i])
			if h != None:
				hs.append(h)
				continue
		mine.append(o[i])
	for k in mine:
		for e in mz_branch(k):
			opens[e[0]] = e[1]
	for h in hs:
		for e in wait_for(h):
			opens[e[0]] = e[1]
	OPENS = opens



def mz_split(h, start):
	# h homes spread over the maze; every cell goes to the home nearest along the maze
	global OWNER
	global PDIR
	global HOMES
	global CPATH
	global DEPTH
	global PARK
	s = MZ_S
	g = 1
	while g * g < h:
		g += 1
	homes = []
	for j in range(g):
		for i in range(g):
			if len(homes) < h:
				hx = (2 * i + 1) * s // (2 * g)
				hy = (2 * j + 1) * s // (2 * g)
				homes.append(hx + hy * s)
	owner = []
	pdir = []
	depth = []
	for c in range(s * s):
		owner.append(-1)
		pdir.append(-1)
		depth.append(0)
	front = []
	for i in range(len(homes)):
		owner[homes[i]] = i
		front.append(homes[i])
	while len(front) > 0:
		nf = []
		for c in front:
			oc = owner[c]
			for k in OPENS[c]:
				nc = c + DX[k] + DY[k] * s
				if owner[nc] == -1:
					owner[nc] = oc
					pdir[nc] = k
					depth[nc] = depth[c] + 1
					nf.append(nc)
		front = nf
	# path from the start cell to every home
	seen = []
	for c in range(s * s):
		seen.append(-1)
	seen[start] = 4
	front = [start]
	while len(front) > 0:
		nf = []
		for c in front:
			for k in OPENS[c]:
				nc = c + DX[k] + DY[k] * s
				if seen[nc] == -1:
					seen[nc] = k
					nf.append(nc)
		front = nf
	cpath = []
	for hc in homes:
		p = []
		c = hc
		while c != start:
			k = seen[c]
			p.append(k)
			c = c - DX[k] - DY[k] * s
		q = []
		for i in range(len(p) - 1, -1, -1):
			q.append(p[i])
		cpath.append(q)
	OWNER = owner
	PDIR = pdir
	DEPTH = depth
	# park cell of each territory: the cell whose removal leaves no piece over half of it
	size = []
	for c in range(s * s):
		size.append(1)
	order = []
	for c in range(s * s):
		order.append(c)
	# children before parents: sort by depth, deepest first (bucket by depth)
	md = 0
	for c in range(s * s):
		if depth[c] > md:
			md = depth[c]
	buckets = []
	for dd in range(md + 1):
		buckets.append([])
	for c in range(s * s):
		buckets[depth[c]].append(c)
	tot = []
	for i in range(len(homes)):
		tot.append(0)
	for c in range(s * s):
		tot[owner[c]] += 1
	for dd in range(md, 0, -1):
		for c in buckets[dd]:
			k = pdir[c]
			p = c - DX[k] - DY[k] * s
			size[p] += size[c]
	park = []
	for i in range(len(homes)):
		c = homes[i]
		half = tot[i] // 2
		while True:
			nxt = -1
			for k in OPENS[c]:
				nc = c + DX[k] + DY[k] * s
				if owner[nc] == i and pdir[nc] == k and depth[nc] == depth[c] + 1 and size[nc] > half:
					nxt = nc
			if nxt < 0:
				break
			c = nxt
		park.append(c)
	PARK = park
	HOMES = homes
	CPATH = cpath


def mz_work(me, goal, cost, stop):
	s = MZ_S
	for k in CPATH[me]:
		move(DIRS[k])
	# the treasure moves one action after a use; no other use can bring it back sooner
	rep = 200 / (400 * 1.5 ** num_unlocked(Unlocks.Speed)) + 0.001
	home = HOMES[me]
	cur = home
	while True:
		t = measure()
		if t == None:
			return 0
		c = (t[0] - MZ_RX) + (t[1] - MZ_RY) * s
		if OWNER[c] == me:
			if MZ_STAY:
				# along the tree of this territory: up from here to the meeting cell, down to c
				a = cur
				b = c
				up = []
				down = []
				while DEPTH[a] > DEPTH[b]:
					k = PDIR[a]
					up.append(BACK[k])
					a = a - DX[k] - DY[k] * s
				while DEPTH[b] > DEPTH[a]:
					k = PDIR[b]
					down.append(k)
					b = b - DX[k] - DY[k] * s
				while a != b:
					k = PDIR[a]
					up.append(BACK[k])
					a = a - DX[k] - DY[k] * s
					k = PDIR[b]
					down.append(k)
					b = b - DX[k] - DY[k] * s
				for k in up:
					move(DIRS[k])
				for i in range(len(down) - 1, -1, -1):
					move(DIRS[down[i]])
				cur = c
				if num_items(Items.Gold) >= goal or get_time() > stop or not use_item(Items.Weird_Substance, cost):
					harvest()
					return 0
				until = get_time() + rep
				if MZ_PARKING and len(HOMES) >= 4:
					a = cur
					b = PARK[me]
					up = []
					down = []
					while DEPTH[a] > DEPTH[b]:
						k = PDIR[a]
						up.append(BACK[k])
						a = a - DX[k] - DY[k] * s
					while DEPTH[b] > DEPTH[a]:
						k = PDIR[b]
						down.append(k)
						b = b - DX[k] - DY[k] * s
					while a != b:
						k = PDIR[a]
						up.append(BACK[k])
						a = a - DX[k] - DY[k] * s
						k = PDIR[b]
						down.append(k)
						b = b - DX[k] - DY[k] * s
					for k in up:
						move(DIRS[k])
					for i in range(len(down) - 1, -1, -1):
						move(DIRS[down[i]])
					cur = PARK[me]
				while get_time() < until:
					pass
			else:
				p = []
				while c != home:
					k = PDIR[c]
					p.append(k)
					c = c - DX[k] - DY[k] * s
				for i in range(len(p) - 1, -1, -1):
					move(DIRS[p[i]])
				if num_items(Items.Gold) >= goal or get_time() > stop or not use_item(Items.Weird_Substance, cost):
					harvest()
					return 0
				until = get_time() + rep
				for k in p:
					move(DIRS[BACK[k]])
				while get_time() < until:
					pass


def mz_lead(rx, ry, s, h, goal, start, stop):
	global MZ_S
	global MZ_RX
	global MZ_RY
	MZ_S = s
	MZ_RX = rx
	MZ_RY = ry
	cost = s * lvl_mult(Unlocks.Mazes)
	go(rx + s // 2, ry + s // 2)
	harvest()
	plant(Entities.Bush)
	# no maze may exist while other leaders still walk to their mazes
	while get_time() < start:
		pass
	use_item(Items.Weird_Substance, cost)
	if MZ_PAR:
		mz_map_par()
	else:
		mz_map()
	start = (get_pos_x() - rx) + (get_pos_y() - ry) * s
	mz_split(h, start)
	hs = []
	for i in range(1, h):
		d = spawn_drone(mz_work, i, goal, cost, stop)
		if d != None:
			hs.append(d)
	mz_work(0, goal, cost, stop)
	for d in hs:
		wait_for(d)
	return 0


def maze_round(s, goal):
	stop = get_time() + MAZE_SECS
	n = get_world_size()
	q = n // s
	d = max_drones()
	nm = q * q
	h = d // nm
	clear()
	act = 200 / (400 * 1.5 ** num_unlocked(Unlocks.Speed))
	start = get_time() + act * (nm + n + 4)
	hs = []
	for i in range(1, nm):
		dd = spawn_drone(mz_lead, (i % q) * s, (i // q) * s, s, h, goal, start, stop)
		if dd != None:
			hs.append(dd)
	mz_lead(0, 0, s, h, goal, start, stop)
	for dd in hs:
		wait_for(dd)



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
		if can_harvest():
			harvest()
		move(North)
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
	(Unlocks.Watering, 2),
	(Unlocks.Expand, 4),
	(Unlocks.Carrots, 2),
	(Unlocks.Carrots, 3),
	(Unlocks.Grass, 2),
	(Unlocks.Grass, 3),
	(Unlocks.Sunflowers, 1),
	(Unlocks.Pumpkins, 1),
	(Unlocks.Speed, 4),
	(Unlocks.Trees, 2),
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
