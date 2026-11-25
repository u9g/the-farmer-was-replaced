# Cactus farm on sunflower power, sorted by a two-dimensional mesh sort.
#
# Sorting: a harvest pops every cactus that is no bigger than its north and east neighbours and no
# smaller than its south and west ones, so swapping ANY inverted neighbour pair is progress. Each
# drone owns a block 2 tiles wide and 4 tall and walks round it in a ring. On every tile it
# measures itself and its four neighbours and swaps the most inverted pair, across block borders
# too; if nothing is inverted it steps on. At a fixed deadline everyone stops and one drone
# harvests from the south-west corner. The few cacti still unsorted then are left standing and
# are sorted along with the next field.
#
# Walls: the harvest treats a missing cactus as sorted, so an empty column and row through the
# middle split the field into four regions of about 8x8 that only have to sort themselves. Values
# travel half as far, so a field sorts in about 54 slots instead of 100. Each wall has gates where
# a cactus stands in the wall line and an empty "pocket" sits two tiles away; the gates let the
# harvest spread from one region to the next. 225 of the 256 tiles hold a cactus, so each harvest
# is about 77% the size, but the cycle is about 36% shorter.
#
# Power: drones run twice as fast while there is power, so whenever power runs low the whole
# field grows one batch of sunflowers, cut biggest first for the 8x bonus.
#
# Needs one drone per block: get_world_size() squared / 8 (32 drones on a 16x16 field).
#
# Run as the main file it farms forever. Imported, it waits for run(goal), which stops every drone
# once the shared inventory holds goal cacti (cactus_lb_entry.py uses that for the leaderboard).

clear()

N = get_world_size()

# Wall tiles are left empty. XS are wall columns and YS wall rows.
XS = [N // 2]
YS = [N // 2]
WALL = []
for wx in range(N):
	col = []
	for wy in range(N):
		col.append(False)
	WALL.append(col)
for w in XS:
	for wy in range(N):
		WALL[w][wy] = True
for h in YS:
	for wx in range(N):
		WALL[wx][h] = True
# Gates: at the bottom of each band of rows a wall column gets a cactus, with a pocket two tiles
# west of it; the wall rows get the same at x = 0, with the pocket two tiles south.
BANDS = [0]
for h in YS:
	BANDS.append(h + 1)
for y0 in BANDS:
	for w in XS:
		WALL[w][y0] = False
		WALL[w - 2][y0] = True
for h in YS:
	WALL[0][h] = False
	WALL[0][h - 2] = True


def is_wall(x, y):
	if x < 0 or y < 0 or x >= N or y >= N:
		return True
	return WALL[x][y]


S = 4
M = 2 * S
DRONES = (N // 2) * (N // S)

# Every block needs its own drone. A bigger field than the drones can cover has to use the
# line-sorting script instead.
while DRONES > max_drones() or N % S != 0:
	print("cactus mesh sort: this field needs", DRONES, "drones")

# Slots of one cactus field: planting the block, then sorting until the deadline.
PLANT_SLOTS = 15
SORT_SLOTS = 54
SLOT_TICKS = 205
WALK_MARGIN = 2
HARVEST_LAG_TICKS = 40
CYCLE_GAP_TICKS = 280

# Slots given to each petal count when cutting sunflowers: enough for a drone to reach and cut
# every sunflower of that size in its block.
SUNFLOWER_WINDOW = 3 * S
SUNFLOWER_GROW = 8.45

# Power to stock up before going back to cacti. 0 grows one batch of sunflowers whenever power
# runs low. A big number, say 60000, spends several minutes on sunflowers first and then harvests
# cacti without a break until that power is used up.
POWER_BANK = 24000


def drain():
	while num_items(Items.Power) > 0:
		pass


def burn_power():
	burners = []
	while num_drones() < max_drones():
		burners.append(spawn_drone(drain))
	drain()
	for b in burners:
		wait_for(b)


def tick_time():
	t = get_time()
	move(North)
	move(South)
	return (get_time() - t) / 400


# Too little power to last until the first sunflowers are cut: burn it off so the speed is known.
if 0 < num_items(Items.Power) and num_items(Items.Power) < 12 * N * N:
	burn_power()

TICK_NOW = tick_time()
TICK = TICK_NOW
if num_items(Items.Power) == 0:
	TICK = TICK_NOW / 2

SLOT = TICK * SLOT_TICKS
CYCLE_TIME = SLOT * (PLANT_SLOTS + SORT_SLOTS) + TICK * CYCLE_GAP_TICKS

# How many harvests one batch of sunflowers pays for. A drone burns one power per 30 actions and
# a batch gives 8 power per sunflower.
BATCH_TIME = SLOT * (2 * M + 9 * SUNFLOWER_WINDOW + S + M) + SUNFLOWER_GROW
BURN = DRONES / (TICK * 6000)
CYCLES_PER_BATCH = (0.97 * 8 * (N * N - 10) - BATCH_TIME * BURN) // (CYCLE_TIME * BURN)

# Power is only worth it if the time spent on sunflowers costs less than the doubled speed gives.
USE_POWER = CYCLES_PER_BATCH * CYCLE_TIME > BATCH_TIME

# Below POWER_LOW there is not enough left for another harvest plus growing the next batch.
POWER_BATCH = 8 * (N * N - 10) - BATCH_TIME * BURN
POWER_LOW = BURN * (CYCLE_TIME + BATCH_TIME + 4)
if not USE_POWER:
	if num_items(Items.Power) > 0:
		burn_power()
	TICK_NOW = tick_time()
	TICK = TICK_NOW
	SLOT = TICK * SLOT_TICKS

SLOT_NOW = TICK_NOW * SLOT_TICKS

# Ring through a block: up the left column, down the right one.
RX = [0, 0, 0, 0, 1, 1, 1, 1]
RY = [0, 1, 2, 3, 3, 2, 1, 0]
RM = [North, North, North, East, South, South, South, West]
RB = [East, South, South, South, West, North, North, North]
NX = [1, 2, 3, 4, 5, 6, 7, 0]


def wait_until(e):
	while get_time() < e:
		pass


def go(x, y):
	while get_pos_x() < x:
		move(East)
	while get_pos_x() > x:
		move(West)
	while get_pos_y() < y:
		move(North)
	while get_pos_y() > y:
		move(South)


# One batch of sunflowers, starting and ending on the first tile of the ring. Petal counts 15 down
# to 7 each get a time window, so that across the whole field every sunflower is the biggest one
# left when it is cut. A tile still holding a cactus is skipped.
def sunflower_batch(t, slot):
	wait_until(t)
	petals = []
	for i in range(M):
		if plant(Entities.Sunflower):
			petals.append(measure())
		else:
			petals.append(0)
		if i < M - 1:
			move(RM[i])
	at = M - 1

	ripe = t + M * 2 * slot + SUNFLOWER_GROW
	window = SUNFLOWER_WINDOW * slot
	for size in range(15, 6, -1):
		todo = []
		for i in range(M):
			if petals[i] == size:
				todo.append(i)
		while todo:
			# nearest tile of this size along the ring
			best = todo[0]
			best_far = M
			for i in todo:
				far = (i - at) % M
				if far > S:
					far = M - far
				if far < best_far:
					best = i
					best_far = far
			todo.remove(best)
			ahead = (best - at) % M
			if ahead <= S:
				for _ in range(ahead):
					move(RM[at])
					at = (at + 1) % M
			else:
				for _ in range(M - ahead):
					at = (at - 1) % M
					move(RB[(at + 1) % M])
			wait_until(ripe + (15 - size) * window)
			harvest()

	# walk back to the first tile of the ring
	if at <= S:
		for _ in range(at):
			move(RB[at])
			at -= 1
	else:
		for _ in range(M - at):
			move(RM[at])
			at += 1
	return ripe + 9 * window + S * slot


# role: 0 sorter, 1 harvests the south-west corner, 2 harvests the north-east corner if 1 failed.
# goal: stop once this many cacti are in the inventory (None runs forever).
def worker(bx, by, t0, role, goal):
	# Per ring tile, the neighbour directions that exist (None measures the own tile, which can
	# never look inverted) and, for the two harvesters, how early to stop to reach the corner.
	DE = []
	DN = []
	DW = []
	DS = []
	WALK = []
	ISW = []
	for i in range(8):
		x = bx + RX[i]
		y = by + RY[i]
		DE.append(None)
		DN.append(None)
		DW.append(None)
		DS.append(None)
		ISW.append(is_wall(x, y))
		if not is_wall(x + 1, y):
			DE[i] = East
		if not is_wall(x, y + 1):
			DN[i] = North
		if not is_wall(x - 1, y):
			DW[i] = West
		if not is_wall(x, y - 1):
			DS[i] = South
		if role == 1:
			WALK.append(SLOT * (RX[i] + RY[i] + WALK_MARGIN))
		elif role == 2:
			WALK.append(SLOT * (1 - RX[i] + 3 - RY[i] + WALK_MARGIN))
		else:
			WALK.append(0)
	inner = True
	for ix in range(bx - 1, bx + 3):
		for iy in range(by - 1, by + 5):
			if is_wall(ix, iy):
				inner = False
	# Two drones at the ends of one inverted pair can both swap it, back and forth forever. A drone
	# that swaps the same way twice in a row waits a few ticks of its own, which breaks the tie.
	delay = TICK * (3 + 7 * ((bx // 2 + by) % 5))

	go(bx, by)
	for i in range(8):
		if get_ground_type() != Grounds.Soil:
			till()
		move(RM[i])
	i = 0
	lastc = num_items(Items.Cactus)
	slot = SLOT_NOW
	# Everybody reads the power level at the same instant, so that all drones agree on whether
	# sunflowers come next.
	wait_until(t0)
	power = num_items(Items.Power)
	while True:
		# Every drone checks at the same instant, after the last harvest has landed, so that they
		# all stop together.
		wait_until(t0)
		if goal != None and num_items(Items.Cactus) >= goal:
			return
		if USE_POWER and power < POWER_LOW:
			while i != 0:
				move(RM[i])
				i = NX[i]
			t0 += M * slot
			batches = 1
			if POWER_BANK > power:
				batches = (POWER_BANK - power) // POWER_BATCH + 1
			for _ in range(batches):
				t0 = sunflower_batch(t0, slot)
				slot = SLOT

		# Plant the block (a leftover from the last harvest makes plant() fail cheaply).
		wait_until(t0)
		if not ISW[i]:
			plant(Entities.Cactus)
		for _ in range(7):
			move(RM[i])
			i = NX[i]
			if not ISW[i]:
				plant(Entities.Cactus)
		end = t0 + SLOT * (PLANT_SLOTS + SORT_SLOTS)
		wait_until(t0 + SLOT * PLANT_SLOTS + TICK * 60)
		power = num_items(Items.Power)

		ld = None
		if inner:
			while get_time() < end:
				h = measure()
				e = measure(East)
				n = measure(North)
				if e < n:
					lo = e
					dl = East
				else:
					lo = n
					dl = North
				w = measure(West)
				s = measure(South)
				if w > s:
					hi = w
					dh = West
				else:
					hi = s
					dh = South
				if h - lo > hi - h:
					if h > lo:
						swap(dl)
						if dl == ld:
							wait_until(get_time() + delay)
							ld = None
						else:
							ld = dl
					else:
						move(RM[i])
						i = NX[i]
						ld = None
				elif hi > h:
					swap(dh)
					if dh == ld:
						wait_until(get_time() + delay)
						ld = None
					else:
						ld = dh
				else:
					move(RM[i])
					i = NX[i]
					ld = None
		else:
			while get_time() + WALK[i] < end:
				if ISW[i]:
					move(RM[i])
					i = NX[i]
					continue
				h = measure()
				e = measure(DE[i])
				n = measure(DN[i])
				if e < n:
					lo = e
					dl = DE[i]
				else:
					lo = n
					dl = DN[i]
				w = measure(DW[i])
				s = measure(DS[i])
				if w > s:
					hi = w
					dh = DW[i]
				else:
					hi = s
					dh = DS[i]
				if h - lo > hi - h:
					if h > lo and dl != None:
						swap(dl)
						if dl == ld:
							wait_until(get_time() + delay)
							ld = None
						else:
							ld = dl
					else:
						move(RM[i])
						i = NX[i]
						ld = None
				elif hi > h and dh != None:
					swap(dh)
					if dh == ld:
						wait_until(get_time() + delay)
						ld = None
					else:
						ld = dh
				else:
					move(RM[i])
					i = NX[i]
					ld = None

		if role == 1:
			go(0, 0)
			i = 0
			wait_until(end + TICK * HARVEST_LAG_TICKS)
			harvest()
		elif role == 2:
			go(N - 1, N - 1)
			i = 4
			wait_until(end + TICK * (HARVEST_LAG_TICKS + 20))
			# The shared inventory tells this drone whether the first harvest worked.
			if num_items(Items.Cactus) - lastc < SMALL_HARVEST:
				harvest()
			lastc = num_items(Items.Cactus)
		t0 = end + TICK * CYCLE_GAP_TICKS


# Under a fifth of a full field counts as a failed first harvest.
SMALL_HARVEST = num_unlocked(Unlocks.Cactus)
SMALL_HARVEST = N * N * N * N * 2 ** (SMALL_HARVEST - 1) // 5


def run(goal):
	start = get_time() + SLOT_NOW * 90
	for by in range(0, N, 4):
		for bx in range(0, N, 2):
			if bx + by > 0:
				role = 0
				if bx + 2 == N and by + 4 == N:
					role = 2
				spawn_drone(worker, bx, by, start, role, goal)
	# The other drones stop on the same check, and the program ends once all of them have.
	worker(0, 0, start, 1, goal)


if __name__ == "__main__":
	run(None)
