# Cactus farm on sunflower power.
#
# Sorting: stationary drones run a clock-synchronised parallel sort. Half a line of drones (every
# second tile) can reach every neighbouring pair of that line without moving, so a line of N cacti
# is sorted in N time slots of one swap each (odd-even transposition sort). All drones share the
# game clock, so nobody waits on anybody: each drone only acts inside its slot. The drones are
# spawned once and keep their formation forever.
#
# Power: drones run twice as fast while there is power, so whenever power runs low the whole
# field grows one batch of sunflowers, cut biggest first for the 8x bonus.
#
# Needs at least get_world_size() / 2 drones.

clear()

N = get_world_size()
H = N // 2

# L lines are sorted at once, each by H drones. S is the spacing between those lines (must be even).
L = max_drones() // H
while L > 1 and (N % L != 0 or (N // L) % 2 != 0):
	L -= 1
S = N // L
HS = S // 2
M = 2 * S

# Slots given to each petal count when cutting sunflowers: enough for a drone to reach and cut
# every sunflower of that size in its block.
SUNFLOWER_WINDOW = 3 * S

# A swap slot costs exactly 204 ticks: two measures, the comparison, the if and the swap.
SLOT_TICKS = 204
HARVEST_LAG_TICKS = 40
SUNFLOWER_GROW = 8.45

# Power to stock up before going back to cacti. 0 grows one batch of sunflowers whenever power
# runs low (about every 9 harvests). A big number, say 60000, spends several minutes on
# sunflowers first and then harvests cacti without a break until that power is used up.
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
SORT_TIME = SLOT * (2 * S * N + 3 * S + 2 * (S - 1) + 4 * (HS - 1))

# A cactus needs a second to grow. On a small field the last row is planted later than that
# before the harvest, so the whole cycle pauses for the difference.
GROW_PAD = max(0, 1.05 - SLOT * (S * N + N + S + 2 * HS - 3))
CYCLE_TIME = SORT_TIME + GROW_PAD

# How many harvests one batch of sunflowers pays for. A drone burns one power per 30 actions and
# a batch gives 8 power per sunflower.
BATCH_TIME = SLOT * (2 * M + 9 * SUNFLOWER_WINDOW + S) + SUNFLOWER_GROW
BURN = L * H / (TICK * 6000)
CYCLES_PER_BATCH = (0.97 * 8 * (N * N - 10) - BATCH_TIME * BURN) // (CYCLE_TIME * BURN)

# Power is only worth it if the time spent on sunflowers costs less than the doubled speed gives.
USE_POWER = CYCLES_PER_BATCH * (2 * SORT_TIME - CYCLE_TIME) > BATCH_TIME

# Below POWER_LOW there is not enough left for another harvest plus growing the next batch.
POWER_BATCH = 8 * (N * N - 10) - BATCH_TIME * BURN
POWER_LOW = BURN * (CYCLE_TIME + BATCH_TIME + 4)
if not USE_POWER:
	if num_items(Items.Power) > 0:
		burn_power()
	TICK_NOW = tick_time()
	TICK = TICK_NOW
	SLOT = TICK * SLOT_TICKS
	GROW_PAD = max(0, 1.05 - SLOT * (S * N + N + S + 2 * HS - 3))

SLOT_NOW = TICK_NOW * SLOT_TICKS
BATCH = N * SLOT
PLANT = 3 * SLOT
TRANSIT = 2 * (HS - 1) * SLOT
HARVEST_AT = BATCH - SLOT + TICK * HARVEST_LAG_TICKS

PHASES = range(H)
FIRST_START = []
FIRST_END = []
SECOND_END = []
for k in PHASES:
	FIRST_START.append(2 * k * SLOT)
	FIRST_END.append((2 * k + 1) * SLOT)
	SECOND_END.append((2 * k + 2) * SLOT)

OPPOSITE = {North: South, South: North, East: West, West: East}


def wait_until(e):
	while get_time() < e:
		pass


def shift(dx, dy):
	if dx > 0:
		for _ in range(dx):
			move(East)
	else:
		for _ in range(-dx):
			move(West)
	if dy > 0:
		for _ in range(dy):
			move(North)
	else:
		for _ in range(-dy):
			move(South)


# The four sorters below are the share of one drone in a line sort that starts at time t. A drone
# that swaps is busy for exactly one slot; a drone that does not swap idles until its slot ends.
def sort_low_first(low, high, t):
	for k in PHASES:
		if measure(low) > measure():
			swap(low)
		else:
			e = t + FIRST_END[k]
			while get_time() < e:
				pass
		if measure() > measure(high):
			swap(high)
		else:
			e = t + SECOND_END[k]
			while get_time() < e:
				pass


def sort_high_first(low, high, t):
	for k in PHASES:
		if measure() > measure(high):
			swap(high)
		else:
			e = t + FIRST_END[k]
			while get_time() < e:
				pass
		if measure(low) > measure():
			swap(low)
		else:
			e = t + SECOND_END[k]
			while get_time() < e:
				pass


# Drones on the border have only one pair, so they skip every second slot. These return before the
# final slot, which the border drone has free (the harvester uses it).
def sort_low_only(low, t):
	for k in PHASES:
		e = t + FIRST_START[k]
		while get_time() < e:
			pass
		if measure(low) > measure():
			swap(low)


def sort_high_only(high, t):
	for k in PHASES:
		e = t + FIRST_START[k]
		while get_time() < e:
			pass
		if measure() > measure(high):
			swap(high)


# One harvest: sort every row (L rows at a time), then every column, then one drone harvests.
def cactus_cycle(d, t):
	wait_until(t)

	# Rows. Each drone plants its own tile and the tile beside it, then sorts.
	for b in range(S):
		x = get_pos_x()
		plant(Entities.Cactus)
		if x % 2:
			swap(West)
			plant(Entities.Cactus)
			t += PLANT
			if x < N - 1:
				sort_low_first(West, East, t)
			else:
				sort_low_only(West, t)
				wait_until(t + BATCH)
		else:
			swap(East)
			plant(Entities.Cactus)
			t += PLANT
			if x > 0:
				sort_high_first(West, East, t)
			else:
				sort_high_only(East, t)
				wait_until(t + BATCH)
		t += BATCH
		if b < S - 1:
			move(North)
			t += SLOT

	# Turn the row formation into a column formation. Everybody reads the power level at the same
	# instant here, so that all drones agree on whether sunflowers come next.
	shift(-d, d)
	t += TRANSIT + GROW_PAD
	wait_until(t)
	power = num_items(Items.Power)

	# Columns.
	for b in range(S):
		y = get_pos_y()
		border = False
		if y % 2:
			if y < N - 1:
				sort_low_first(South, North, t)
			else:
				sort_low_only(South, t)
				border = True
		else:
			if y > 0:
				sort_high_first(South, North, t)
			else:
				sort_high_only(North, t)
				border = True
		if border:
			if b == S - 1 and get_pos_x() < S:
				# Everyone else makes their last swap at the start of the final slot.
				wait_until(t + HARVEST_AT)
				harvest()
			else:
				wait_until(t + BATCH)
		t += BATCH
		if b < S - 1:
			move(East)
			t += SLOT

	# Back to a row formation (shifted by one tile, which flips which pairs each drone owns).
	shift(d, -d)
	return t + TRANSIT, power


# One batch of sunflowers. Each drone owns the 2 x S block it also plants cacti in and walks it as
# a loop. Petal counts 15 down to 7 each get a time window, so that across the whole field every
# sunflower is the biggest one left when it is cut.
def sunflower_batch(t, slot):
	wait_until(t)
	side = East
	if get_pos_x() % 2:
		side = West
	forward = []
	for _ in range(S - 1):
		forward.append(North)
	forward.append(side)
	for _ in range(S - 1):
		forward.append(South)
	forward.append(OPPOSITE[side])

	petals = []
	for i in range(M):
		plant(Entities.Sunflower)
		petals.append(measure())
		if i < M - 1:
			move(forward[i])
	at = M - 1

	ripe = t + M * 2 * slot + SUNFLOWER_GROW
	window = SUNFLOWER_WINDOW * slot
	for size in range(15, 6, -1):
		todo = []
		for i in range(M):
			if petals[i] == size:
				todo.append(i)
		while todo:
			# nearest tile of this size along the loop
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
					move(forward[at])
					at = (at + 1) % M
			else:
				for _ in range(M - ahead):
					at = (at - 1) % M
					move(OPPOSITE[forward[at]])
			wait_until(ripe + (15 - size) * window)
			harvest()

	# walk back to the first tile of the loop
	if at <= S:
		for _ in range(at):
			at -= 1
			move(OPPOSITE[forward[at]])
	else:
		for _ in range(M - at):
			move(forward[at])
			at += 1
	return ripe + 9 * window + S * slot


def worker(x, y, d, t):
	shift(x, y)
	for _ in range(S):
		if get_ground_type() != Grounds.Soil:
			till()
		move(West)
		if get_ground_type() != Grounds.Soil:
			till()
		move(East)
		move(North)

	if not USE_POWER:
		while True:
			t, power = cactus_cycle(d, t)

	power = num_items(Items.Power)
	slot = SLOT_NOW
	while True:
		if power < POWER_LOW:
			batches = 1
			if POWER_BANK > power:
				batches = (POWER_BANK - power) // POWER_BATCH + 1
			for _ in range(batches):
				t = sunflower_batch(t, slot)
				slot = SLOT
		t, power = cactus_cycle(d, t)


start = get_time() + SLOT_NOW * (L * H + 2 * N + 5 * S + 8)
for j in range(L):
	for i in range(H):
		if i + j > 0:
			spawn_drone(worker, 1 + 2 * i, S * j, 2 * (i % HS) - (HS - 1), start)
worker(1, 0, 1 - HS, start)
