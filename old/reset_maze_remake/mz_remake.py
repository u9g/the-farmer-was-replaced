DIRS = [North, East, South, West]
DX = [0, 1, 0, -1]
DY = [1, 0, -1, 0]
BACK = [2, 3, 0, 1]
N = get_world_size()
M = 2 ** (num_unlocked(Unlocks.Mazes) - 1)
COST = N * M
K = 2
LIM = 4
GOAL = 1000000
EDGE = False


def go(tx, ty):
	while get_pos_x() < tx:
		move(East)
	while get_pos_x() > tx:
		move(West)
	while get_pos_y() < ty:
		move(North)
	while get_pos_y() > ty:
		move(South)


def make():
	plant(Entities.Bush)
	use_item(Items.Weird_Substance, COST)


def seek(tx, ty, depth, came):
	# depth-limited DFS through the maze for (tx, ty); stays at the treasure when found
	if get_pos_x() == tx and get_pos_y() == ty:
		return True
	if depth == 0:
		return False
	order = []
	x = get_pos_x()
	y = get_pos_y()
	for k in range(4):
		if k != came:
			dd = abs(x + DX[k] - tx) + abs(y + DY[k] - ty)
			j = len(order)
			order.append((dd, k))
			while j > 0 and order[j - 1][0] > dd:
				order[j] = order[j - 1]
				order[j - 1] = (dd, k)
				j -= 1
	for p in order:
		k = p[1]
		if p[0] <= depth - 1 and move(DIRS[k]):
			if seek(tx, ty, depth - 1, BACK[k]):
				return True
			move(DIRS[BACK[k]])
	return False


def life(me, px, py, parks):
	go(px, py)
	last = None
	while num_items(Items.Gold) < GOAL:
		if get_entity_type() != Entities.Hedge and get_entity_type() != Entities.Treasure:
			continue
		v = num_items(Items.Weird_Substance)
		if v == last:
			continue
		t = measure()
		if t == None:
			continue
		last = v
		tx = t[0]
		ty = t[1]
		# the drone nearest (Manhattan) to the treasure acts; ties to the lower id
		best = 0
		bd = 999
		for i in range(len(parks)):
			d = abs(parks[i][0] - tx) + abs(parks[i][1] - ty)
			if d < bd:
				bd = d
				best = i
		if best != me:
			continue
		if bd <= K:
			seek(tx, ty, LIM, -1)
		harvest()
		go(px, py)
		if num_items(Items.Gold) < GOAL:
			make()


def parks_of():
	ps = []
	if EDGE:
		# 16 cells round the border
		for i in range(4):
			ps.append((2 + 4 * i, 0))
			ps.append((2 + 4 * i, N - 1))
		for i in range(4):
			ps.append((0, 2 + 4 * i))
			ps.append((N - 1, 2 + 4 * i))
		return ps[:max_drones()]
	g = 4
	for j in range(g):
		for i in range(g):
			ps.append((i * N // g + N // (2 * g), j * N // g + N // (2 * g)))
	return ps


t0 = get_time()
w0 = num_items(Items.Weird_Substance)
clear()
P = parks_of()
HS = []
for i in range(1, len(P)):
	HS.append(spawn_drone(life, i, P[i][0], P[i][1], P))
go(P[0][0], P[0][1])
while get_time() < t0 + 1.5:
	pass
make()
life(0, P[0][0], P[0][1], P)
for h in HS:
	wait_for(h)
quick_print("MAZE", get_time() - t0, "weird", w0 - num_items(Items.Weird_Substance), "gold", num_items(Items.Gold))
unlock(Unlocks.Leaderboard)
