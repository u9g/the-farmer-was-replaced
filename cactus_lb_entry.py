# Leaderboards.Cactus entry: two harvests of a 32x32 field with diagonal walls every 3 tiles.
#
# A harvest only needs every cactus to be no bigger than its north and east neighbours. Every tile
# with x + y divisible by 3 is left empty, except gate tiles, so outside the gates each cactus is
# either "low" (x + y = 1 mod 3: its only partners are its north and east neighbours) or "high"
# (x + y = 2 mod 3: only south and west). Swapping an inverted low/high pair always makes the low
# tile smaller and the high tile bigger, so a pair that is in order never goes out of order again,
# and checking each pair once, when its second tile is planted, sorts everything away from gates.
#
# Gates join the strips between walls: on wall diagonal d, every tile whose x - y is a multiple of
# 12 (shifted by 6 plus the parity of d on every other wall), and the end tile of a diagonal too
# short to hold one. 741 tiles hold a cactus; a harvest of that is about 17.6M, so two harvests
# make the 33,554,432 goal (about 13.7s simulated). ROLE below was generated offline from these
# rules. Gates and the tiles next to them are sorted greedily (swap in the most inverted
# neighbour), in two sweeps of each column after planting (three when the first harvest came up short).
#
# One drone per column. Even columns start at the bottom and odd ones at the top, and every drone
# turns round each time, so neighbouring columns always walk in opposite directions. A pair across
# two columns is checked by the drone walking up from row 16 on, and by the one walking down below
# row 16: that is the drone that plants the pair's second tile.
#
# At the deadline five drones spread over the field take turns to harvest, HARVEST_TICKS apart:
# a harvest that starts next to an unsorted cactus pops almost nothing, so the next one tries
# from elsewhere unless a big harvest has already landed. Every drone checks the goal at the
# same instant, and all of them stop together once it is met.

GOAL = 33554432
N = get_world_size()

SWEEPS = 2
# Slots per sweep, and the harvest size above which a field gets an extra sweep.
SWEEP_SLOTS = 48
TIGHT = 733
FULL = 741
REPS = 3
PLANT_SLOTS = 70
TILL_SLOTS = 26
START_SLOTS = 26
GAP_TICKS = 60
HARVESTERS = [0, 9, 17, 25, 31]
HARVEST_TICKS = 15
BIG_HARVEST = 32 * 400 * 400


# Tile roles, generated offline: 0 empty, 1 low, 2 high, 3 gate, 4 low next to a gate, 5 high next to a gate.
# 741 cacti.
ROLE = [
	[0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1],
	[1, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5],
	[5, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3],
	[3, 4, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4],
	[4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2],
	[2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0],
	[0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4],
	[1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2],
	[5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0],
	[0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1],
	[1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2],
	[5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0],
	[3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1],
	[4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5],
	[2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3],
	[0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4],
	[1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2],
	[2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0],
	[0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4],
	[1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2],
	[5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0],
	[0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1],
	[1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2],
	[5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0],
	[3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1],
	[4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 2],
	[2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0],
	[0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 1],
	[1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 2, 0, 4, 2, 0, 1, 2],
	[2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0, 1, 5, 3, 4, 2, 0, 1, 2, 0, 1, 5, 0],
	[0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2, 0, 1, 5, 0, 1, 5, 3, 4],
	[1, 2, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 4, 2, 0, 1, 2, 0, 1, 5, 3, 4, 2, 0, 4, 2],
]


def wait_until(e):
	while get_time() < e:
		pass


def go(x, y):
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


def tick_time():
	t = get_time()
	move(North)
	move(South)
	return (get_time() - t) / 400


TICK = tick_time()
SLOT = TICK * 205


def greedy(col, right, left, y):
	# Swap in the most inverted neighbour, up to REPS times (gates and the tiles next to them).
	for _ in range(REPS):
		h = measure()
		if h == None:
			return
		best = 0
		bd = None
		if y + 1 < N and col[y + 1] > 0:
			v = measure(North)
			if v != None and h - v > best:
				best = h - v
				bd = North
		if right[y] > 0:
			v = measure(East)
			if v != None and h - v > best:
				best = h - v
				bd = East
		if y > 0 and col[y - 1] > 0:
			v = measure(South)
			if v != None and v - h > best:
				best = v - h
				bd = South
		if left[y] > 0:
			v = measure(West)
			if v != None and v - h > best:
				best = v - h
				bd = West
		if bd == None:
			return
		swap(bd)


def low_check(d):
	# This tile must be no bigger than the one in direction d.
	h = measure()
	v = measure(d)
	if h != None and v != None and h > v:
		swap(d)


def high_check(d):
	# This tile must be no smaller than the one in direction d.
	h = measure()
	v = measure(d)
	if h != None and v != None and v > h:
		swap(d)


def worker(x, t0):
	col = ROLE[x]
	right = []
	left = []
	for y in range(N):
		right.append(0)
		left.append(0)
	if x + 1 < N:
		right = ROLE[x + 1]
	if x > 0:
		left = ROLE[x - 1]
	up = x % 2 == 0
	y = 0
	if not up:
		y = N - 1
	go(x, y)
	extra = TILL_SLOTS
	while True:
		up = y == 0
		wait_until(t0)
		got = num_items(Items.Cactus)
		# Plant the column end to end. Every low/high pair is checked once, by whichever drone
		# plants its second tile: the column's own drone for vertical pairs, and for pairs across
		# columns the drone walking up from row 16 on and the one walking down below it.
		step = North
		dy = 1
		if not up:
			step = South
			dy = -1
		for _ in range(N):
			r = col[y]
			if r > 0:
				if extra > 0:
					till()
				plant(Entities.Cactus)
				late = (up and y >= N // 2) or (not up and y < N // 2)
				if r == 3:
					greedy(col, right, left, y)
				elif r == 1 or r == 4:
					if not up and y + 1 < N and col[y + 1] > 0:
						low_check(North)
					if late and right[y] > 0:
						low_check(East)
				else:
					if up and y > 0 and col[y - 1] > 0:
						high_check(South)
					if late and left[y] > 0:
						high_check(West)
			if 0 <= y + dy and y + dy < N:
				move(step)
				y += dy
		# A field gets one more sweep when it can finish the goal but only if it comes out almost
		# perfect (the first harvest came up short). Every drone reads the count at the same instant (t0), so all
		# agree.
		sweeps = SWEEPS
		need = GOAL - got
		if need > 32 * TIGHT * TIGHT and need <= 32 * FULL * FULL:
			sweeps = SWEEPS + 1
		th = t0 + SLOT * (PLANT_SLOTS + extra + sweeps * SWEEP_SLOTS)
		wait_until(t0 + SLOT * (PLANT_SLOTS + extra))
		extra = 0
		# Sweep end to end while another whole sweep fits before the harvest: low tiles check
		# their north and east pairs, gates and their neighbours swap in the most inverted one.
		for _ in range(sweeps):
			step = North
			dy = 1
			if y > N // 2:
				step = South
				dy = -1
			for _ in range(N):
				r = col[y]
				if r >= 3:
					greedy(col, right, left, y)
				elif r == 1:
					if y + 1 < N and col[y + 1] > 0:
						low_check(North)
					if right[y] > 0:
						low_check(East)
				if 0 <= y + dy and y + dy < N:
					move(step)
					y += dy
		# Harvesters take turns a few ticks apart: a harvest that starts next to an unsorted
		# cactus pops almost nothing, and then the next one tries from elsewhere.
		turn = -1
		for k in range(len(HARVESTERS)):
			if HARVESTERS[k] == x:
				turn = k
		back = None
		if turn >= 0 and col[y] == 0:
			if y == 0:
				move(North)
				y += 1
				back = South
			else:
				move(South)
				y -= 1
				back = North
		wait_until(th)
		before = num_items(Items.Cactus)
		if turn >= 0:
			wait_until(th + TICK * HARVEST_TICKS * turn)
			if num_items(Items.Cactus) - before < BIG_HARVEST:
				harvest()
		if back != None:
			move(back)
			if back == North:
				y += 1
			else:
				y -= 1
		t0 = th + TICK * (GAP_TICKS + HARVEST_TICKS * len(HARVESTERS))
		wait_until(t0)
		if num_items(Items.Cactus) >= GOAL:
			return


def launch(xs, t0):
	while len(xs) > 1:
		half = len(xs) // 2
		keep = []
		rest = []
		for k in range(len(xs)):
			if k < half:
				keep.append(xs[k])
			else:
				rest.append(xs[k])
		spawn_drone(launch, rest, t0)
		xs = keep
	worker(xs[0], t0)


XS = []
for cx in range(N):
	XS.append(cx)
launch(XS, get_time() + SLOT * START_SLOTS)
