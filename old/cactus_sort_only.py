# Cactus farm: stationary drones run a clock-synchronised parallel sort.
#
# Half a line of drones (every second tile) can reach every neighbouring pair of that line without
# moving, so a line of N cacti is sorted in N time slots of one swap each (odd-even transposition
# sort). All drones share the game clock, so nobody waits on anybody: each drone only acts inside
# its slot. The drones are spawned once and keep their formation forever.
#
# One harvest = sort every row (L rows at a time), then every column, then one drone harvests.
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

# A swap slot costs exactly 204 ticks: two measures, the comparison, the if and the swap.
SLOT_TICKS = 204
HARVEST_LAG_TICKS = 40

t = get_time()
move(North)
move(South)
TICK = (get_time() - t) / 400
SLOT = TICK * SLOT_TICKS
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


# The four sorters below are one drone's share of a line sort that starts at time t. A drone that
# swaps is busy for exactly one slot; a drone that does not swap idles until its slot ends.
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

	while True:
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

		# Turn the row formation into a column formation.
		shift(-d, d)
		t += TRANSIT

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
		t += TRANSIT


start = get_time() + SLOT * (L * H + 2 * N + 5 * S + 8)
for j in range(L):
	for i in range(H):
		if i + j > 0:
			spawn_drone(worker, 1 + 2 * i, S * j, 2 * (i % HS) - (HS - 1), start)
worker(1, 0, 1 - HS, start)
