# Bone farm: the dinosaur hat played as snake on the whole field.
#
# Bones come when the hat is taken off: tail length squared, times the upgrade bonus. So every run
# fills the field as far as it can before cashing in.
#
# A game has three stages:
#   free:     tail shorter than FREE_LIMIT. Head straight for the apple, stepping round the tail,
#             with a flood fill before any step next to a wall or the tail so it never boxes
#             itself in. Early moves cost twice a normal action, so short paths pay most here.
#   shortcut: tail shorter than SHORTCUT_LIMIT. Run along a Hamiltonian cycle over the field
#             (column 0 down, the other columns as rows snaking left and right), cutting ahead:
#             of its neighbours the drone takes the one furthest along the cycle that neither
#             passes the apple nor gets within MARGIN of the tail end. The tail stays in cycle
#             order, so the drone can never get stuck.
#   cycle:    follow the cycle only. Shortcuts here leave holes in the tail that the apple later
#             lands in, a full lap away, so a long tail just follows the cycle.
# Between free and shortcut the drone only moves forward along the cycle (into free tiles) until
# its whole tail lies along the cycle in order.
#
# measure() on an apple gives the next apple's position, so the apple is always known. Needs an
# even world size.

clear()

N = get_world_size()
S = N * N

# Tail lengths at which the free stage and the shortcut stage end.
FREE_LIMIT = 16
SHORTCUT_LIMIT = S * 30 // 100
MARGIN = 1
# Free stage: a step must leave at least the tail length plus this many tiles reachable.
ROOM = 2

while N % 2 != 0:
	print("dinosaurs: needs an even world size")

# Cycle order: (0,0), row 0 east over x = 1..N-1, row 1 west, ... ending at (1, N-1), then down
# column 0 from (0, N-1) to (0, 1).
IDX = []
for x in range(N):
	col = []
	for y in range(N):
		col.append(0)
	IDX.append(col)
PX = []
PY = []
i = 0
PX.append(0)
PY.append(0)
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

# Per cycle position: neighbours as (steps ahead on the cycle, direction), furthest first.
DIRS = [North, East, South, West]
DXS = [0, 1, 0, -1]
DYS = [1, 0, -1, 0]
AHEAD = []
WAY = []
for i in range(S):
	pairs = []
	for k in range(4):
		x = PX[i] + DXS[k]
		y = PY[i] + DYS[k]
		if x >= 0 and x < N and y >= 0 and y < N:
			pairs.append([(IDX[x][y] - i) % S, DIRS[k]])
	# furthest first (at most four, so a plain selection sort)
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
	AHEAD.append(ds)
	WAY.append(ws)

# The step along the cycle from each position.
NEXT = []
for i in range(S):
	ds = AHEAD[i]
	for k in range(len(ds)):
		if ds[k] == 1:
			NEXT.append(WAY[i][k])

# Per cycle position: the neighbour in each direction (North, East, South, West), or -1.
NB = []
for i in range(S):
	row = []
	for k in range(4):
		x = PX[i] + DXS[k]
		y = PY[i] + DYS[k]
		if x >= 0 and x < N and y >= 0 and y < N:
			row.append(IDX[x][y])
		else:
			row.append(-1)
	NB.append(row)

# The cycle's directions twice over, so a walk along it never has to wrap.
WALK = []
for i in range(2 * S):
	WALK.append(NEXT[i % S])

# occ[c]: move number at which the head last entered tile c. After move t the tail holds the tiles
# entered at moves t - k .. t - 1. hist[t % S]: the tile entered at move t.
occ = []
hist = []
for i in range(S):
	occ.append(0)
	hist.append(0)


# Flood-fill marks, a fresh number per fill so the marks never need clearing.
vis = []
for i in range(S):
	vis.append(0)
fills = [0]


# Whether the head, stepping onto `start` with the move after move low + k - 1, can avoid getting
# shut in: either at least `need` free tiles can be reached from there, or some tail tile can,
# that will have moved on by the time the head gets to it.
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


# Whether stepping from ch onto the free tile c leaves room. Only a tile with a wall or tail
# beside it can lead into a pocket, so only those get the flood fill.
def safe(c, ch, low, need):
	for g in NB[c]:
		if g != ch and (g < 0 or occ[g] >= low):
			return roomy(c, low, need)
	return True


# A step towards the apple into a free tile with room behind it for the tail, or -1 if there is
# no free tile. Returns the direction index; the tile is NB[ch][index].
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


# One game: put the hat on, grow the tail as long as possible, take it off. Returns the length.
def play():
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
	# free stage while lining is False, then lining up along the cycle
	lining = FREE_LIMIT <= 0
	m = 0
	cum = 0
	last = False
	done = False

	# Free stage and lining up. The drone is on the apple whenever ch == ca, and moving off eats it.
	while True:
		if ch == ca:
			if last:
				done = True
				break
			k += 1
			ax = nxt[0]
			ay = nxt[1]
			ca = IDX[ax][ay]
		# tiles entered at move low or later are tail once this move is made
		low = t + 1 - k

		d = 0
		if lining:
			# forward along the cycle into a free tile, the chain of such moves kept under a lap
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
			# the whole tail now lies along the cycle in order
			if m >= k:
				break
		elif k >= FREE_LIMIT:
			lining = True

	# Shortcut stage: hist only, as a ring buffer of the tail.
	while not done and k < SHORTCUT_LIMIT:
		if ch == ca:
			if last:
				done = True
				break
			k += 1
			ca = IDX[nxt[0]][nxt[1]]
		t += 1
		# steps along the cycle to the tail end once this move is made
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

	# Long tail: follow the cycle from apple to apple.
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


while True:
	quick_print("tail", play(), "bones", num_items(Items.Bone))
