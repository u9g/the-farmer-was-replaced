# Cactus farm: asynchronous two-dimensional greedy sort with a deadline harvest.
#
# A harvest pops every cactus that is no bigger than its north and east neighbours and no smaller
# than its south and west ones, so the goal is only that every row and every column is
# non-decreasing; swapping ANY inverted neighbour pair is progress toward it.
#
# Each of the 32 drones owns a 2x4 block (2 columns, 4 rows) and walks round it in a ring. On every
# tile it measures itself and its four neighbours (1 tick each) and swaps the most inverted pair,
# across block borders too; if nothing is inverted it steps to the next tile of its ring. No clock
# slots, no idle waiting: a drone works whenever there is something to fix where it stands.
#
# At a fixed deadline everyone stops. Drone H1 harvests the south-west corner. If the cactus count
# shows that harvest was tiny (an unsorted cell next to the corner), drone H2 harvests the north-east
# corner instead. A soft harvest leaves the few unsorted cells standing; they are simply sorted along
# with the next field (planting skips occupied tiles).
#
# Two drones at the ends of one inverted pair can see it at the same tick and both swap it back
# and forth forever. A drone that swaps the same way twice in a row (impossible without such a
# race) waits a drone-specific few ticks, which breaks the tie.

clear()

N = get_world_size()
PLANT_SLOTS = 15
SORT_SLOTS = 100
WALK_MARGIN = 2

t = get_time()
move(North)
move(South)
TICK = (get_time() - t) / 400
SLOT = TICK * 205

# Ring through a 2x4 block: up the left column, down the right one.
RX = [0, 0, 0, 0, 1, 1, 1, 1]
RY = [0, 1, 2, 3, 3, 2, 1, 0]
RM = [North, North, North, East, South, South, South, West]
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


# role: 0 sorter, 1 harvests the south-west corner, 2 harvests the north-east corner if 1 failed.
def worker(bx, by, t0, role):
	# Per ring tile, the neighbour directions that exist (None measures the own tile, which can
	# never look inverted) and, for the two harvesters, how early to stop to reach the corner.
	DE = []
	DN = []
	DW = []
	DS = []
	WALK = []
	for i in range(8):
		x = bx + RX[i]
		y = by + RY[i]
		DE.append(None)
		DN.append(None)
		DW.append(None)
		DS.append(None)
		if x < N - 1:
			DE[i] = East
		if y < N - 1:
			DN[i] = North
		if x > 0:
			DW[i] = West
		if y > 0:
			DS[i] = South
		if role == 1:
			WALK.append(SLOT * (RX[i] + RY[i] + WALK_MARGIN))
		elif role == 2:
			WALK.append(SLOT * (1 - RX[i] + 3 - RY[i] + WALK_MARGIN))
		else:
			WALK.append(0)
	inner = bx > 0 and by > 0 and bx + 2 < N and by + 4 < N
	delay = TICK * (3 + 7 * ((bx // 2 + by) % 5))

	go(bx, by)
	for i in range(8):
		if get_ground_type() != Grounds.Soil:
			till()
		move(RM[i])
	i = 0
	lastc = num_items(Items.Cactus)
	while True:
		# Plant the block (a leftover from a soft harvest makes plant() fail cheaply).
		wait_until(t0)
		plant(Entities.Cactus)
		for _ in range(7):
			move(RM[i])
			i = NX[i]
			plant(Entities.Cactus)
		end = t0 + SLOT * (PLANT_SLOTS + SORT_SLOTS)
		wait_until(t0 + SLOT * PLANT_SLOTS + TICK * 60)

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
			wait_until(end + TICK * 40)
			harvest()
		elif role == 2:
			go(N - 1, N - 1)
			i = 4
			wait_until(end + TICK * 60)
			# The shared inventory tells H2 whether H1's harvest worked.
			if num_items(Items.Cactus) - lastc < 80000:
				harvest()
			lastc = num_items(Items.Cactus)
		t0 = end + TICK * 280


start = get_time() + SLOT * 90
for by in range(0, N, 4):
	for bx in range(0, N, 2):
		if bx + by > 0:
			role = 0
			if bx + 2 == N and by + 4 == N:
				role = 2
			spawn_drone(worker, bx, by, start, role)
worker(0, 0, start, 1)
