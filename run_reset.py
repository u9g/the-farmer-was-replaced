# Fastest reset: from a 1x1 farm to unlocking the leaderboard again (1M gold, 2M bone).
# Run with run_reset_lb.py (leaderboard_run(Leaderboards.Fastest_Reset, "run_reset", 256)).
#
# Early game: one drone on a mixed farm. Every cell grows whatever the next few unlocks are
# shortest of (hay, wood, carrots), and two columns grow sunflowers for power once the farm is 6x6.
# After that the script works through PLAN: for each unlock it cannot afford yet it runs a round
# for the first item it lacks, using every drone (pumpkin field, sorted cactus field, one maze per
# drone, the dinosaur snake), with a sunflower round whenever power runs low.

T0 = get_time()


def log(msg):
	quick_print(get_time() - T0, msg)


def width():
	if num_unlocked(Unlocks.Expand) == 1:
		return 1
	return get_world_size()


def lacking(u):
	cost = get_cost(u)
	for item in cost:
		if num_items(item) < cost[item]:
			return item
	return None


def buy(u):
	if lacking(u) == None and unlock(u):
		log(str(u) + " " + str(num_unlocked(u)))
		return True
	return False


def lvl_mult(u):
	n = num_unlocked(u)
	if n <= 1:
		return 1
	return 2 ** (n - 1)


def go(tx, ty):
	n = get_world_size()
	w = width()
	dx = (tx - get_pos_x()) % w
	if dx <= w // 2:
		for _ in range(dx):
			move(East)
	else:
		for _ in range(w - dx):
			move(West)
	dy = (ty - get_pos_y()) % n
	if dy <= n // 2:
		for _ in range(dy):
			move(North)
	else:
		for _ in range(n - dy):
			move(South)


def soil():
	if get_ground_type() != Grounds.Soil:
		till()


def clear_cell():
	# harvest whatever stands here, so something else can be planted
	if get_entity_type() != None:
		harvest()


# ---- running a job on every drone ------------------------------------------------------------

def drones():
	return min(max_drones(), width())


def all_drones(job, a, b):
	# job(i, d, a, b) runs on drone i of d; returns the list of results
	d = drones()
	hs = []
	for i in range(1, d):
		h = spawn_drone(job, i, d, a, b)
		if h != None:
			hs.append(h)
	res = [job(0, d, a, b)]
	for h in hs:
		res.append(wait_for(h))
	return res


def my_cols(i, d):
	w = width()
	return range(i * w // d, (i + 1) * w // d)


# ---- mixed farm (hay, wood, carrots) -----------------------------------------------------------

NEED = ({}, {})
POLY = False
PEND = {Items.Hay: 0, Items.Wood: 0, Items.Carrot: 0, Items.Weird_Substance: 0}
SUN = {}


def yield_of(e):
	f = 1
	if POLY:
		f = 5 * 2 ** num_unlocked(Unlocks.Polyculture) * 0.6
	if e == Entities.Tree:
		return 5 * lvl_mult(Unlocks.Trees) * f
	if e == Entities.Bush:
		return lvl_mult(Unlocks.Trees) * f
	if e == Entities.Carrot:
		return lvl_mult(Unlocks.Carrots) * f
	return 0


def item_of(e):
	if e == Entities.Carrot:
		return Items.Carrot
	if e == Entities.Grass:
		return Items.Hay
	return Items.Wood


def short(item):
	# NEED = (current unlock's cost, the next few unlocks' cost); the current one comes first
	r = 0
	have = num_items(item) + PEND[item]
	cur = NEED[0]
	if item in cur and cur[item] > have:
		r = 10 + (cur[item] - have) / cur[item]
	look = NEED[1]
	if item in look and look[item] > have:
		r += (look[item] - have) / look[item]
	return r


def choose(even):
	best = Entities.Grass
	bs = short(Items.Hay)
	if num_unlocked(Unlocks.Plant) > 0:
		s = max(short(Items.Wood), short(Items.Weird_Substance))
		if s > bs:
			if num_unlocked(Unlocks.Trees) == 0:
				bs = s
				best = Entities.Bush
			elif even:
				bs = s
				best = Entities.Tree
	if num_unlocked(Unlocks.Carrots) > 0:
		s = short(Items.Carrot)
		if s > bs:
			c = get_cost(Entities.Carrot)
			ok = True
			for it in c:
				if num_items(it) < c[it]:
					ok = False
			if ok:
				best = Entities.Carrot
	return best


def sun_max():
	m = 0
	for k in SUN:
		if SUN[k] > m:
			m = SUN[k]
	return m


def sun_cell():
	# sunflower strip: only the highest-numbered sunflower is cut (8x power)
	pos = (get_pos_x(), get_pos_y())
	e = get_entity_type()
	if e == Entities.Sunflower and pos in SUN:
		if not can_harvest() or SUN[pos] < sun_max() or len(SUN) < 10:
			return
		harvest()
	elif e != None:
		harvest()
	soil()
	if plant(Entities.Sunflower):
		SUN[pos] = measure()
	elif pos in SUN:
		SUN.pop(pos)


def mixed_cell(strip, weird):
	if strip and get_pos_x() < 2:
		sun_cell()
		return
	tend_mixed()
	# plus shapes centred where (x + 2y) % 5 == 0 tile the field: the west and south arms were
	# just replanted, the north and east arms are cut later in this same pass
	if weird and (get_pos_x() + 2 * get_pos_y()) % 5 == 0:
		if num_items(Items.Weird_Substance) >= 1:
			use_item(Items.Weird_Substance)
		elif num_items(Items.Fertilizer) >= 1:
			use_item(Items.Fertilizer)


WANT = {}
REQ = {}
COLS = [0, 0]


def tend_mixed():
	e = get_entity_type()
	pos = (get_pos_x(), get_pos_y())
	if e != None and e != Entities.Grass and not can_harvest():
		# a growing plant stays, unless a neighbour needs another type here as its companion
		if pos not in WANT or WANT[pos][0] == e:
			return
	if e != None:
		harvest()
	if pos in REQ:
		# this plant's companion claim ends with its harvest
		c = REQ.pop(pos)
		if c in WANT and WANT[c][1] == pos:
			WANT.pop(c)
	if pos in WANT:
		c = WANT[pos][0]
	else:
		c = choose((pos[0] + pos[1]) % 2 == 0)
	if c == Entities.Grass:
		if get_ground_type() == Grounds.Soil:
			plant(Entities.Grass)
	else:
		if c == Entities.Carrot:
			soil()
		if not plant(c):
			return
		PEND[item_of(c)] += yield_of(c)
	if POLY:
		# claim the companion's cell; if it is taken by another type, replant for a new companion
		for _ in range(3):
			comp = get_companion()
			if comp == None:
				return
			cp = comp[1]
			if cp[0] >= COLS[0] and cp[0] < COLS[1] and cp != pos:
				if cp not in WANT:
					WANT[cp] = (comp[0], pos)
					REQ[pos] = cp
					return
				if WANT[cp][0] == comp[0]:
					REQ[pos] = cp
					return
			harvest()
			if c != Entities.Grass or get_ground_type() == Grounds.Soil:
				if not plant(c):
					return


def mixed_job(i, d, need, flags):
	global NEED
	global POLY
	NEED = need
	POLY = num_unlocked(Unlocks.Polyculture) > 0
	cols = my_cols(i, d)
	COLS[0] = cols[0]
	COLS[1] = cols[0] + len(cols)
	if flags[0]:
		COLS[0] = 2
	strip = flags[0]
	weird = flags[1]
	for k in PEND:
		PEND[k] = 0
	n = get_world_size()
	if width() * n == 1:
		if can_harvest():
			harvest()
		return 0
	for x in my_cols(i, d):
		go(x, 0)
		for y in range(n):
			mixed_cell(strip, weird)
			move(North)
	return 0


def mixed_round(need):
	strip = drones() == 1 and num_unlocked(Unlocks.Sunflowers) > 0 and get_world_size() >= 6
	weird = Items.Weird_Substance in need[0] and num_unlocked(Unlocks.Fertilizer) > 0
	all_drones(mixed_job, need, (strip, weird))


# ---- power -------------------------------------------------------------------------------------

def sun_plant_job(i, d, a, b):
	n = get_world_size()
	cells = []
	for x in my_cols(i, d):
		go(x, 0)
		for y in range(n):
			if get_entity_type() != Entities.Sunflower:
				clear_cell()
				soil()
				plant(Entities.Sunflower)
			cells.append((x, y, measure()))
			move(North)
	return cells


def sun_cut_job(i, d, cells, v):
	for c in cells[i]:
		if c[2] == v:
			go(c[0], c[1])
			while not can_harvest():
				pass
			harvest()
	return 0


def power_round():
	n = width() * get_world_size()
	if num_items(Items.Carrot) < n:
		return
	cells = all_drones(sun_plant_job, 0, 0)
	for v in range(15, 6, -1):
		all_drones(sun_cut_job, cells, v)


def power_check():
	if num_unlocked(Unlocks.Sunflowers) == 0 or width() < 6:
		return
	if drones() == 1 and get_world_size() < 8:
		return
	if num_items(Items.Power) < 60 * drones():
		power_round()


# ---- pumpkins ----------------------------------------------------------------------------------

def pumpkin_job(i, d, a, b):
	n = get_world_size()
	todo = []
	for x in my_cols(i, d):
		go(x, 0)
		for y in range(n):
			e = get_entity_type()
			if e != Entities.Pumpkin:
				clear_cell()
				soil()
				plant(Entities.Pumpkin)
				todo.append((x, y))
			elif not can_harvest():
				todo.append((x, y))
			move(North)
	# revisit only the cells not yet grown; a pumpkin that died is replanted and revisited
	while len(todo) > 0:
		nt = []
		for c in todo:
			go(c[0], c[1])
			while get_entity_type() == Entities.Pumpkin and not can_harvest():
				pass
			if get_entity_type() != Entities.Pumpkin:
				if num_items(Items.Carrot) < 1:
					return 0
				clear_cell()
				plant(Entities.Pumpkin)
				nt.append(c)
		todo = nt
	return 0


def pumpkin_round():
	all_drones(pumpkin_job, 0, 0)
	if get_entity_type() == Entities.Pumpkin:
		harvest()


# ---- cactus ------------------------------------------------------------------------------------

def cactus_plant_job(i, d, a, b):
	n = get_world_size()
	for x in my_cols(i, d):
		go(x, 0)
		for y in range(n):
			if get_entity_type() != Entities.Cactus:
				clear_cell()
				soil()
				plant(Entities.Cactus)
			move(North)
	return 0


def sort_line(fwd, back, n):
	# drone stands at the start of a line of n cacti; shaker sort, ascending along fwd
	lo = 0
	hi = n - 1
	pos = 0
	while lo < hi:
		last = lo
		while pos < hi:
			if measure() > measure(fwd):
				swap(fwd)
				last = pos
			move(fwd)
			pos += 1
		hi = last
		if lo >= hi:
			break
		last = hi
		while pos > lo:
			if measure() < measure(back):
				swap(back)
				last = pos
			move(back)
			pos -= 1
		lo = last


def cactus_rows_job(i, d, a, b):
	n = get_world_size()
	for y in range(i * n // d, (i + 1) * n // d):
		go(0, y)
		sort_line(East, West, n)
	return 0


def cactus_cols_job(i, d, a, b):
	n = get_world_size()
	for x in my_cols(i, d):
		go(x, 0)
		sort_line(North, South, n)
	return 0


def weird_job(i, d, a, b):
	# toggle weirdness on plus shapes: centres at (x + 2y) % 5 == 0 cover the plane once
	n = get_world_size()
	for x in my_cols(i, d):
		for y in range(n):
			if (x + 2 * y) % 5 == 0:
				go(x, y)
				if num_items(Items.Weird_Substance) >= 1:
					use_item(Items.Weird_Substance)
				elif num_items(Items.Fertilizer) >= 1:
					use_item(Items.Fertilizer)
	return 0


def cactus_round(weird):
	all_drones(cactus_plant_job, 0, 0)
	all_drones(cactus_rows_job, 0, 0)
	all_drones(cactus_cols_job, 0, 0)
	if weird:
		all_drones(weird_job, 0, 0)
	go(0, 0)
	harvest()


# ---- mazes -------------------------------------------------------------------------------------

DIRS = [North, East, South, West]
DX = [0, 1, 0, -1]
DY = [1, 0, -1, 0]


def maze_map(rx, ry, s):
	# depth-first walk over the whole maze; returns open[x][y] = list of direction indexes
	opens = []
	seen = []
	for x in range(s):
		opens.append([])
		seen.append([])
		for y in range(s):
			opens[x].append([])
			seen[x].append(False)
	x = get_pos_x() - rx
	y = get_pos_y() - ry
	stack = []
	seen[x][y] = True
	for k in range(4):
		if can_move(DIRS[k]):
			opens[x][y].append(k)
	nxt = [0]
	while True:
		moved = False
		while nxt[-1] < len(opens[x][y]):
			k = opens[x][y][nxt[-1]]
			nxt[-1] += 1
			nx = x + DX[k]
			ny = y + DY[k]
			if not seen[nx][ny]:
				move(DIRS[k])
				stack.append(k)
				x = nx
				y = ny
				seen[x][y] = True
				for k2 in range(4):
					if can_move(DIRS[k2]):
						opens[x][y].append(k2)
				nxt.append(0)
				moved = True
				break
		if moved:
			continue
		if len(stack) == 0:
			return opens
		k = stack.pop()
		nxt.pop()
		move(DIRS[(k + 2) % 4])
		x = x - DX[k]
		y = y - DY[k]


def maze_path(opens, s, sx, sy, tx, ty):
	# breadth-first search from target back to start; returns the moves from start
	came = []
	for x in range(s):
		came.append([])
		for y in range(s):
			came[x].append(-1)
	came[tx][ty] = 4
	front = [(tx, ty)]
	while len(front) > 0 and came[sx][sy] == -1:
		nf = []
		for c in front:
			for k in opens[c[0]][c[1]]:
				nx = c[0] + DX[k]
				ny = c[1] + DY[k]
				if came[nx][ny] == -1:
					came[nx][ny] = (k + 2) % 4
					nf.append((nx, ny))
		front = nf
	path = []
	x = sx
	y = sy
	while came[x][y] != 4:
		k = came[x][y]
		path.append(k)
		x += DX[k]
		y += DY[k]
	return path


def maze_job(i, d, s, goal, start, stop):
	k = get_world_size() // s
	rx = (i % k) * s
	ry = (i // k) * s
	mult = lvl_mult(Unlocks.Mazes)
	cost = s * mult
	go(rx + s // 2, ry + s // 2)
	clear_cell()
	plant(Entities.Bush)
	# no maze may exist while other drones still walk to their regions
	while get_time() < start:
		pass
	while num_items(Items.Gold) < goal and num_items(Items.Weird_Substance) >= cost and get_time() < stop:
		if get_entity_type() != Entities.Bush:
			clear_cell()
			plant(Entities.Bush)
		use_item(Items.Weird_Substance, cost)
		opens = maze_map(rx, ry, s)
		while True:
			t = measure()
			path = maze_path(opens, s, get_pos_x() - rx, get_pos_y() - ry, t[0] - rx, t[1] - ry)
			for kk in path:
				move(DIRS[kk])
			if num_items(Items.Gold) >= goal or num_items(Items.Weird_Substance) < cost or get_time() > stop:
				harvest()
				break
			if not use_item(Items.Weird_Substance, cost):
				harvest()
				break
			while get_entity_type() == Entities.Treasure:
				pass
		go(rx + s // 2, ry + s // 2)
	return 0


def maze_layout():
	# k x k regions of size s, one drone each
	n = get_world_size()
	d = drones()
	k = 1
	while k * k < d or n % k != 0:
		k += 1
	while n // k < 3:
		k -= 1
		while n % k != 0:
			k -= 1
	return (k, n // k, min(d, k * k))


def maze_round(goal):
	n = get_world_size()
	lay = maze_layout()
	k = lay[0]
	s = lay[1]
	d = lay[2]
	clear()
	act = 200 / (400 * 1.5 ** num_unlocked(Unlocks.Speed))
	start = get_time() + act * (d + n + 8)
	stop = start + 40
	hs = []
	for i in range(1, d):
		h = spawn_drone(maze_job, i, d, s, goal, start, stop)
		if h != None:
			hs.append(h)
	maze_job(0, d, s, goal, start, stop)
	for h in hs:
		wait_for(h)
	clear()


# ---- dinosaur snake (dinosaurs.py, whole field) ------------------------------------------------

FREE_LIMIT = 16
MARGIN = 1
ROOM = 2
SN = 0
SS = 0
SHORTCUT_LIMIT = 0
IDX = []
PX = []
PY = []
AHEAD = []
WAY = []
NEXT = []
NB = []
WALK = []
occ = []
hist = []
vis = []
fills = [0]


def dino_setup():
	global SN
	global SS
	global SHORTCUT_LIMIT
	global IDX
	global PX
	global PY
	global AHEAD
	global WAY
	global NEXT
	global NB
	global WALK
	global occ
	global hist
	global vis
	N = get_world_size()
	S = N * N
	SN = N
	SS = S
	SHORTCUT_LIMIT = S * 30 // 100
	IDX = []
	for x in range(N):
		col = []
		for y in range(N):
			col.append(0)
		IDX.append(col)
	PX = [0]
	PY = [0]
	i = 0
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
	AHEAD = []
	WAY = []
	for i in range(S):
		pairs = []
		for k in range(4):
			x = PX[i] + DX[k]
			y = PY[i] + DY[k]
			if x >= 0 and x < N and y >= 0 and y < N:
				pairs.append([(IDX[x][y] - i) % S, DIRS[k]])
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
	NEXT = []
	for i in range(S):
		ds = AHEAD[i]
		for k in range(len(ds)):
			if ds[k] == 1:
				NEXT.append(WAY[i][k])
	NB = []
	for i in range(S):
		row = []
		for k in range(4):
			x = PX[i] + DX[k]
			y = PY[i] + DY[k]
			if x >= 0 and x < N and y >= 0 and y < N:
				row.append(IDX[x][y])
			else:
				row.append(-1)
		NB.append(row)
	WALK = []
	for i in range(2 * S):
		WALK.append(NEXT[i % S])
	occ = []
	hist = []
	vis = []
	for i in range(S):
		occ.append(0)
		hist.append(0)
		vis.append(0)


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


def safe(c, ch, low, need):
	for g in NB[c]:
		if g != ch and (g < 0 or occ[g] >= low):
			return roomy(c, low, need)
	return True


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


def play():
	S = SS
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
	lining = FREE_LIMIT <= 0
	m = 0
	cum = 0
	last = False
	done = False
	while True:
		if ch == ca:
			if last:
				done = True
				break
			k += 1
			ax = nxt[0]
			ay = nxt[1]
			ca = IDX[ax][ay]
		low = t + 1 - k
		d = 0
		if lining:
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
			if m >= k:
				break
		elif k >= FREE_LIMIT:
			lining = True
	while not done and k < SHORTCUT_LIMIT:
		if ch == ca:
			if last:
				done = True
				break
			k += 1
			ca = IDX[nxt[0]][nxt[1]]
		t += 1
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


def dino_round():
	clear()
	if SN != get_world_size():
		dino_setup()
	k = play()
	log("snake " + str(k) + " bones " + str(num_items(Items.Bone)))


# ---- what to do for a missing item -------------------------------------------------------------

def carrots_for(n):
	# make sure n carrots are on hand (seeds for pumpkins / sunflowers)
	while num_items(Items.Carrot) < n:
		c = with_seeds({Items.Carrot: n * 2})
		mixed_round((c, c))


def farm(item, amount):
	power_check()
	cells = width() * get_world_size()
	if item == Items.Hay or item == Items.Wood or item == Items.Carrot:
		n = with_seeds({item: amount})
		mixed_round((n, n))
	elif item == Items.Pumpkin:
		carrots_for(cells * 2 * lvl_mult(Unlocks.Pumpkins))
		pumpkin_round()
	elif item == Items.Weird_Substance and num_unlocked(Unlocks.Cactus) == 0:
		n = with_seeds({Items.Weird_Substance: amount, Items.Wood: amount, Items.Hay: amount})
		mixed_round((n, n))
	elif item == Items.Cactus or item == Items.Weird_Substance:
		pc = 2 * lvl_mult(Unlocks.Cactus)
		while num_items(Items.Pumpkin) < cells * pc:
			farm(Items.Pumpkin, cells * pc)
		cactus_round(item == Items.Weird_Substance)
	elif item == Items.Gold:
		lay = maze_layout()
		s = lay[1]
		cost = s * lvl_mult(Unlocks.Mazes)
		finds = (amount - num_items(Items.Gold)) // (s * s * lvl_mult(Unlocks.Mazes)) + 1 + lay[2]
		s_need = finds * cost
		if num_unlocked(Unlocks.Cactus) > 0:
			s_need = min(s_need, cost * 4 * lay[2] * 30)
		if num_items(Items.Weird_Substance) < s_need:
			farm(Items.Weird_Substance, s_need)
		else:
			maze_round(amount)
	elif item == Items.Bone:
		ac = 2 * lvl_mult(Unlocks.Dinosaurs) * get_world_size() * get_world_size()
		if num_items(Items.Cactus) < ac:
			farm(Items.Cactus, ac)
		else:
			dino_round()
	else:
		log("no farm for " + str(item))
		mixed_round(({Items.Hay: 100}, {}))


def add_cost(need, u):
	cost = get_cost(u)
	for it in cost:
		if it in need:
			need[it] += cost[it]
		else:
			need[it] = cost[it]


def set_need(plan, i):
	cur = {}
	add_cost(cur, plan[i][0])
	look = {}
	for j in range(i, min(i + 3, len(plan))):
		add_cost(look, plan[j][0])
	return (with_seeds(cur), with_seeds(look))


def with_seeds(need):
	# carrots are planted with wood and hay: one of each per carrot, divided by the companion bonus
	if Items.Carrot in need:
		seeds = need[Items.Carrot]
		if num_unlocked(Unlocks.Polyculture) > 0:
			seeds = seeds // 6
		for it in [Items.Wood, Items.Hay]:
			if it in need:
				need[it] += seeds
			else:
				need[it] = seeds
	return need


def run_plan(plan):
	for i in range(len(plan)):
		u = plan[i][0]
		while num_unlocked(u) < plan[i][1]:
			if buy(u):
				continue
			item = lacking(u)
			if item == Items.Hay or item == Items.Wood or item == Items.Carrot:
				power_check()
				mixed_round(set_need(plan, i))
			elif item == Items.Weird_Substance and num_unlocked(Unlocks.Cactus) == 0:
				power_check()
				mixed_round(set_need(plan, i))
			else:
				farm(item, get_cost(u)[item])


PLAN = [
	(Unlocks.Speed, 1),
	(Unlocks.Expand, 1),
	(Unlocks.Plant, 1),
	(Unlocks.Expand, 2),
	(Unlocks.Speed, 2),
	(Unlocks.Carrots, 1),
	(Unlocks.Speed, 3),
	(Unlocks.Expand, 3),
	(Unlocks.Trees, 1),
	(Unlocks.Expand, 4),
	(Unlocks.Carrots, 2),
	(Unlocks.Carrots, 3),
	(Unlocks.Grass, 2),
	(Unlocks.Grass, 3),
	(Unlocks.Sunflowers, 1),
	(Unlocks.Pumpkins, 1),
	(Unlocks.Polyculture, 1),
	(Unlocks.Trees, 2),
	(Unlocks.Speed, 4),
	(Unlocks.Expand, 5),
	(Unlocks.Trees, 3),
	(Unlocks.Speed, 5),
	(Unlocks.Grass, 4),
	(Unlocks.Carrots, 4),
	(Unlocks.Pumpkins, 2),
	(Unlocks.Pumpkins, 3),
	(Unlocks.Pumpkins, 4),
	(Unlocks.Fertilizer, 1),
	(Unlocks.Cactus, 1),
	(Unlocks.Mazes, 1),
	(Unlocks.Megafarm, 1),
	(Unlocks.Mazes, 2),
	(Unlocks.Megafarm, 2),
	(Unlocks.Expand, 6),
	(Unlocks.Mazes, 3),
	(Unlocks.Megafarm, 3),
	(Unlocks.Cactus, 2),
	(Unlocks.Expand, 7),
	(Unlocks.Megafarm, 4),
	(Unlocks.Dinosaurs, 1),
	(Unlocks.Dinosaurs, 2),
	(Unlocks.Dinosaurs, 3),
	(Unlocks.Dinosaurs, 4),
	(Unlocks.Mazes, 4),
	(Unlocks.Leaderboard, 1),
]

run_plan(PLAN)
log("done")
