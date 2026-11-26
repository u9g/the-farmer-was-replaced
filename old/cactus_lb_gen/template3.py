# Leaderboards.Cactus entry: two harvests of 725 cacti each (2 * 725^2 * 32 >= 33,554,432).
#
# Layout: every diagonal with x + y divisible by 3 is a wall (left empty), so the cacti form strips
# two diagonals wide. A strip is a zigzag path whose low cells (x + y = 1 mod 3) only touch high
# cells to their north and east, and whose high cells only touch low cells to their south and
# west, so swapping an out-of-order pair never puts another pair out of order. The strips are
# joined into one field by gate tiles on the walls near the strip ends (a serpentine through the
# field); the two smallest corner strips are left out and their walls planted instead.
#
# The cells are walked in one serpentine order, cut into 32 chunks, one per drone (the d* functions
# below, generated offline; each drone builds only its own chunk's lists). A drone plants its chunk
# in order and keeps the value of every cactus it planted. A plain strip cell is compared with the
# one planted just before it and swapped if out of order; near a gate, every out-of-order pair in
# the chunk is repaired (walking to it), so the chunk is always sorted. Chunks are cut only between
# plain strip cells at least two steps from a gate, and the drone that plants the later of the two
# cut cells checks that pair once, late enough that the other drone is done with its first cells.
#
# Drone 0 harvests one second after the last cactus was planted (it watches the pumpkin count,
# which drops by a fixed amount per cactus). Every drone then replants backwards (with its own cut
# for that direction), and drone 0 harvests again. If the goal is still not met they go round again.

GOAL = 33554432
N = get_world_size()
DIRS = [North, East, South, West]
SEED_COST = 64
GROW = 1.0001
# A pair across a chunk cut is checked no earlier than this, so the neighbouring drone has finished
# with its first cells (it plants them first and never touches them again).
GUARD_A = 2.0
GUARD_B = 0.7

#DATA#


def wait_until(e):
	while get_time() < e:
		pass


def travel(x, y):
	dx = x - get_pos_x()
	if dx < 0:
		dx += N
	if dx <= N // 2:
		for _ in range(dx):
			move(East)
	else:
		for _ in range(N - dx):
			move(West)
	dy = y - get_pos_y()
	if dy < 0:
		dy += N
	if dy <= N // 2:
		for _ in range(dy):
			move(North)
	else:
		for _ in range(N - dy):
			move(South)


def walk(cx, cy, x, y):
	if x > cx:
		for _ in range(x - cx):
			move(East)
	else:
		for _ in range(cx - x):
			move(West)
	if y > cy:
		for _ in range(y - cy):
			move(North)
	else:
		for _ in range(cy - y):
			move(South)


# d = [xs, ys, nb, ext, mv, pj, pd, pu]: cells in the order this pass plants them; nb[i] = flat
# (index, direction, 1 if that neighbour is above) triples for every neighbour in the chunk; ext =
# [direction, above] of the pair across the cut at the last cell, or []; mv[i] = direction from the
# cell before, or -1; pj[i] = index of the one earlier neighbour to compare with (pd, pu its
# direction and side), -2 for none, -1 when the cell needs the full repair.
def run(c, d, fresh, left, guard):
	xs = d[0]
	ys = d[1]
	nb = d[2]
	mv = d[4]
	pj = d[5]
	pd = d[6]
	pu = d[7]
	n = len(xs)
	vals = []
	for _ in range(n):
		vals.append(None)
	cx = get_pos_x()
	cy = get_pos_y()
	away = True
	for i in range(n):
		x = xs[i]
		y = ys[i]
		quick_print("C", c, fresh, i, get_time()) #DBG
		m = mv[i]
		if away or m < 0:
			walk(cx, cy, x, y)
			away = False
		else:
			move(DIRS[m])
		cx = x
		cy = y
		if fresh:
			till()
		elif left:
			if get_entity_type() != None:
				harvest()
		plant(Entities.Cactus)
		va = measure()
		vals[i] = va
		j = pj[i]
		if j >= 0:
			vj = vals[j]
			if pu[i] == 1:
				if va > vj:
					swap(DIRS[pd[i]])
					vals[i] = vj
					vals[j] = va
			elif va < vj:
				swap(DIRS[pd[i]])
				vals[i] = vj
				vals[j] = va
		elif j == -1:
			work = [i]
			while len(work) > 0:
				a = work.pop()
				e = nb[a]
				m = len(e)
				k = 0
				while k < m:
					j = e[k]
					vj = vals[j]
					if vj != None:
						va = vals[a]
						if e[k + 2] == 1:
							bad = va > vj
						else:
							bad = va < vj
						if bad:
							ax = xs[a]
							ay = ys[a]
							bx = xs[j]
							by = ys[j]
							if abs(ax - cx) + abs(ay - cy) <= abs(bx - cx) + abs(by - cy):
								walk(cx, cy, ax, ay)
								cx = ax
								cy = ay
								swap(DIRS[e[k + 1]])
							else:
								walk(cx, cy, bx, by)
								cx = bx
								cy = by
								swap(DIRS[(e[k + 1] + 2) % 4])
							vals[a] = vj
							vals[j] = va
							work.append(j)
							work.append(a)
							k = m
					k += 3
			away = cx != x or cy != y
	quick_print("X", c, fresh, get_time()) #DBG
	ex = d[3]
	if len(ex) > 0:
		i = n - 1
		walk(cx, cy, xs[i], ys[i])
		wait_until(guard)
		w = DIRS[ex[0]]
		v = measure(w)
		while v == None:
			v = measure(w)
		h = measure()
		if ex[1] == 1:
			if h > v:
				swap(w)
		elif h < v:
			swap(w)


def worker(c):
	da = FA[c]()
	db = FB[c]()
	quick_print("S", c, get_time()) #DBG
	travel(da[0][0], da[1][0])
	forward = True
	fresh = True
	left = False
	pump = PUMP0
	last = 0
	guard = GUARD_A
	while True:
		if forward:
			run(c, da, fresh, left, guard)
			travel(db[0][0], db[1][0])
		else:
			run(c, db, fresh, left, guard)
			travel(da[0][0], da[1][0])
		pump -= SEED_COST * NA
		if c == 0:
			while num_items(Items.Pumpkin) > pump:
				pass
			wait_until(get_time() + GROW)
			harvest()
			quick_print("H", get_time()) #DBG
		while num_items(Items.Cactus) <= last:
			pass
		got = num_items(Items.Cactus)
		left = got - last < FULL
		last = got
		guard = get_time() + GUARD_B
		if last >= GOAL:
			return
		forward = not forward
		fresh = False


def launch(xs):
	while len(xs) > 1:
		half = len(xs) // 2
		keep = []
		rest = []
		for k in range(len(xs)):
			if k < half:
				keep.append(xs[k])
			else:
				rest.append(xs[k])
		spawn_drone(launch, rest)
		xs = keep
	worker(xs[0])


FULL = 32 * NA * NA
PUMP0 = num_items(Items.Pumpkin)
CS = []
for ci in range(len(FA)):
	CS.append(ci)
launch(CS)
