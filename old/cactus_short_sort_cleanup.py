# Cactus farm: cactus_sort_only.py with truncated sorts and a free "cleanup" slot.
#
# Rows get ROW_R odd-even rounds, columns COL_R rounds (16 = full sort). With CLEAN = 1 the
# final slot of every column batch is spent on cleanup instead of a swap: every drone whose own
# cactus still makes an unsorted vertical pair harvests it. Each such grown, unsorted cactus pops
# alone (its partner is unsorted, so the pop cannot spread), leaving a hole. Holes count as sorted
# neighbours, so everything left on the field is sorted and the final harvest pops it all.

ROW_R = 14
COL_R = 12
CLEAN = 1

clear()

N = get_world_size()
H = N // 2

L = max_drones() // H
while L > 1 and (N % L != 0 or (N // L) % 2 != 0):
	L -= 1
S = N // L
HS = S // 2

SLOT_TICKS = 204
HARVEST_LAG_TICKS = 40

t = get_time()
move(North)
move(South)
TICK = (get_time() - t) / 400
SLOT = TICK * SLOT_TICKS
BATCH_R = ROW_R * SLOT
BATCH_C = (COL_R + CLEAN) * SLOT
PLANT = 3 * SLOT
TRANSIT = 2 * (HS - 1) * SLOT
CLEAN_AT = COL_R * SLOT
FINAL_AT = COL_R * SLOT + TICK * 100
HARVEST_AT = BATCH_C - SLOT + TICK * HARVEST_LAG_TICKS

ROW_PH = range(ROW_R // 2)
COL_PH = range(COL_R // 2)
ROW_X = ROW_R % 2
COL_X = COL_R % 2
FIRST_START = []
FIRST_END = []
SECOND_END = []
for k in range(H + 1):
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


def sort_low_first(low, high, t, ph, xt):
	for k in ph:
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
	if xt:
		if measure(low) > measure():
			swap(low)


def sort_high_first(low, high, t, ph, xt):
	for k in ph:
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
	if xt:
		if measure() > measure(high):
			swap(high)


def sort_low_only(low, t, ph, xt):
	for k in ph:
		e = t + FIRST_START[k]
		while get_time() < e:
			pass
		if measure(low) > measure():
			swap(low)
	if xt:
		wait_until(t + FIRST_START[len(ph)])
		if measure(low) > measure():
			swap(low)


def sort_high_only(high, t, ph, xt):
	for k in ph:
		e = t + FIRST_START[k]
		while get_time() < e:
			pass
		if measure() > measure(high):
			swap(high)
	if xt:
		wait_until(t + FIRST_START[len(ph)])
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

		for b in range(S):
			x = get_pos_x()
			plant(Entities.Cactus)
			if x % 2:
				swap(West)
				plant(Entities.Cactus)
				t += PLANT
				wait_until(t)
				if x < N - 1:
					sort_low_first(West, East, t, ROW_PH, ROW_X)
				else:
					sort_low_only(West, t, ROW_PH, ROW_X)
			else:
				swap(East)
				plant(Entities.Cactus)
				t += PLANT
				wait_until(t)
				if x > 0:
					sort_high_first(West, East, t, ROW_PH, ROW_X)
				else:
					sort_high_only(East, t, ROW_PH, ROW_X)
			wait_until(t + BATCH_R)
			t += BATCH_R
			if b < S - 1:
				move(North)
				t += SLOT

		shift(-d, d)
		t += TRANSIT

		for b in range(S):
			y = get_pos_y()
			border = False
			if y % 2:
				if y < N - 1:
					sort_low_first(South, North, t, COL_PH, COL_X)
				else:
					sort_low_only(South, t, COL_PH, COL_X)
					border = True
			else:
				if y > 0:
					sort_high_first(South, North, t, COL_PH, COL_X)
				else:
					sort_high_only(North, t, COL_PH, COL_X)
					border = True
			if CLEAN:
				wait_until(t + CLEAN_AT)
				bad = False
				m = measure()
				if m != None:
					if y > 0:
						v = measure(South)
						if v != None and v > m:
							bad = True
					if y < N - 1:
						v = measure(North)
						if v != None and m > v:
							bad = True
				if bad:
					harvest()
			if border and b == S - 1:
				if CLEAN:
					wait_until(t + FINAL_AT)
				else:
					wait_until(t + HARVEST_AT)
				if get_entity_type() == Entities.Cactus:
					harvest()
					quick_print("MAINH", get_time(), num_items(Items.Cactus))
			else:
				wait_until(t + BATCH_C)
			t += BATCH_C
			if b < S - 1:
				move(East)
				t += SLOT

		shift(d, -d)
		t += TRANSIT


start = get_time() + SLOT * (L * H + 2 * N + 5 * S + 8)
for j in range(L):
	for i in range(H):
		if i + j > 0:
			spawn_drone(worker, 1 + 2 * i, S * j, 2 * (i % HS) - (HS - 1), start)
worker(1, 0, 1 - HS, start)
