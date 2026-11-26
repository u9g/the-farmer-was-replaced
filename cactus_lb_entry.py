# Leaderboards.Cactus entry: two harvests of a 32x32 field with diagonal walls.
#
# Every tile with x + y divisible by 4 is left empty, except gate tiles. A harvest only needs
# every cactus to be no bigger than its north and east neighbours, and the walls cut every such
# chain to at most three cacti inside a strip between two walls, so sorting only moves a cactus a
# step or two instead of across the field. Gates sit on the walls every 12 tiles along the
# diagonal, shifted by 6 on every other wall, so a chain can pass at most one gate. 809 tiles hold
# a cactus; a harvest of that is about 20.9M, so two harvests make the 33,554,432 goal (about 15.4s simulated).
#
# One drone per column. It plants the column end to end (tilling the first time), sorting each
# new cactus into its neighbours as it lands, then sweeps end to end while another whole sweep
# fits before the deadline. On every cactus it swaps in the most inverted neighbour, up to REPS
# times. Neighbouring columns start at opposite ends, so their drones rarely meet.
#
# At the deadline five drones spread over the field take turns to harvest, HARVEST_TICKS apart:
# a harvest that starts next to an unsorted cactus pops almost nothing, so the next one tries
# from elsewhere unless a big harvest has already landed. Every drone checks the goal at the
# same instant, and all of them stop together once it is met.

GOAL = 33554432
N = get_world_size()

SORT_SLOTS = 126
REPS = 3
PLANT_SLOTS = 70
TILL_SLOTS = 26
SWEEP_SLOTS = 42
START_SLOTS = 26
GAP_TICKS = 60
HARVESTERS = [0, 9, 17, 25, 31]
HARVEST_TICKS = 15
BIG_HARVEST = 32 * 400 * 400


# Gates: on wall diagonal d, every tile whose x - y is a multiple of GATE_STEP, shifted by half a
# step on every other wall. A north/east chain crossing one strip moves x - y by at most 4, so it
# never reaches a second gate.
GATE_STEP = 12


def is_gate(cx, cy):
	d = cx + cy
	if d == 0 or d % 4 != 0:
		return False
	off = 0
	if (d // 4) % 2 == 1:
		off = GATE_STEP // 2
	# A diagonal too short to hold a gate at the offset gets one at its end.
	lim = d
	if 2 * (N - 1) - d < lim:
		lim = 2 * (N - 1) - d
	if lim < off:
		return cx - cy == lim
	return (cx - cy - off) % GATE_STEP == 0


# Which tiles of column cx hold a cactus (all False outside the field). Each drone works out only
# the three columns it needs, after it has been spawned: building the whole field up front cost the
# first drone about 2 seconds before it could spawn anyone.
def column(cx):
	col = []
	for cy in range(N):
		col.append(False)
	if cx < 0 or cx >= N:
		return col
	for cy in range(N):
		col[cy] = (cx + cy) % 4 != 0 or is_gate(cx, cy)
	return col


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


def fix(CN, CE, CS, CW, y):
	for _ in range(REPS):
		h = measure()
		if h == None:
			return
		best = 0
		bd = None
		if CN[y]:
			v = measure(North)
			if v != None and h - v > best:
				best = h - v
				bd = North
		if CE[y]:
			v = measure(East)
			if v != None and h - v > best:
				best = h - v
				bd = East
		if CS[y]:
			v = measure(South)
			if v != None and v - h > best:
				best = v - h
				bd = South
		if CW[y]:
			v = measure(West)
			if v != None and v - h > best:
				best = v - h
				bd = West
		if bd == None:
			return
		swap(bd)


def worker(x, t0):
	col = column(x)
	right = column(x + 1)
	left = column(x - 1)
	CN = []
	CE = []
	CS = []
	CW = []
	for y in range(N):
		n = False
		e = False
		so = False
		w = False
		if col[y]:
			if y + 1 < N:
				n = col[y + 1]
			if x + 1 < N:
				e = right[y]
			if y > 0:
				so = col[y - 1]
			if x > 0:
				w = left[y]
		CN.append(n)
		CE.append(e)
		CS.append(so)
		CW.append(w)
	# Even columns start at the bottom and odd ones at the top, so neighbouring columns mostly
	# sweep in opposite directions and two drones rarely stand side by side.
	y = 0
	if x % 2 == 1:
		y = N - 1
	go(x, y)
	extra = TILL_SLOTS
	while True:
		wait_until(t0)
		# Plant from this end of the column to the other, sorting each cactus into its
		# neighbours as it lands.
		step = North
		dy = 1
		if y > N // 2:
			step = South
			dy = -1
		for _ in range(N):
			if col[y]:
				if extra > 0:
					till()
				plant(Entities.Cactus)
				fix(CN, CE, CS, CW, y)
			if 0 <= y + dy and y + dy < N:
				move(step)
				y += dy
		th = t0 + SLOT * (PLANT_SLOTS + extra + SORT_SLOTS)
		wait_until(t0 + SLOT * (PLANT_SLOTS + extra))
		extra = 0
		# Sweep end to end while another whole sweep fits before the harvest.
		while get_time() + SLOT * SWEEP_SLOTS < th:
			step = North
			dy = 1
			if y > N // 2:
				step = South
				dy = -1
			for _ in range(N):
				if col[y]:
					fix(CN, CE, CS, CW, y)
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
		if turn >= 0 and not col[y]:
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
