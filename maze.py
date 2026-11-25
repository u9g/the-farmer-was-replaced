DIRS = [North, East, South, West]
DELTA = {North: (0, 1), South: (0, -1), East: (1, 0), West: (-1, 0)}
OPP = {North: South, South: North, East: West, West: East}
OX = 1
OY = 1
LAYOUT = 1  # 0: 8x4 grid, 1: diamond lattice
SETTLE = 6
EXCLUSIVE = True
PRUNE = True
GRAB = False
STALL = 0.5
RESCAN = True
park = None
AIM = False
border = {}  # moves the maker waits so every drone is home before the maze appears

# Drones never die. Each one lives at a fixed home on the open field between mazes,
# maps only the part of a new maze it can reach without crossing another home,
# parks at the middle of that part, and races for any treasure inside it.

homes = []
is_home = {}
me = 0
amount = 0
links = {}
mine = {}  # cell -> list of dirs from my park cell
x = 0
y = 0


def make_homes():
	n = get_world_size()
	result = []
	if LAYOUT == 0:
		for i in range(max_drones()):
			result.append(((i % 8) * 2 * n // 16 + n // 16, (i // 8) * 4 * n // 16 + n // 8))
	else:
		for b in range(8):
			for a in range(4):
				result.append(((4 * a + 2 * b + OX) % n, (2 * b + OY) % n))
	return result


def fly(tx, ty):
	# open field, no walls; gives up if a maze appears around it
	while get_pos_x() < tx:
		if not move(East):
			return
	while get_pos_x() > tx:
		if not move(West):
			return
	while get_pos_y() < ty:
		if not move(North):
			return
	while get_pos_y() > ty:
		if not move(South):
			return


def go(d):
	global x
	global y
	move(d)
	dx, dy = DELTA[d]
	x += dx
	y += dy


def explore():
	# Depth-first walk of my region. Never enters another drone's home, and
	# skips any cell some already-found home is closer to (Voronoi pruning).
	global links
	global border
	links = {}
	border = {}
	bl = []  # [home index, path from my home to the cell next to it, its length, common prefix with trail]
	global dep
	global par
	global pd
	global order
	seen = {(x, y): 1}
	dep = {(x, y): 0}
	par = {(x, y): None}
	pd = {}
	order = [(x, y)]
	trail = []
	pend = []
	while True:
		here = (x, y)
		L = len(trail)
		if GRAB:
			t = measure()
			if t == here:
				if use_item(Items.Weird_Substance, amount):
					if RESCAN:
						rescan()
					while measure() == t:
						pass
				t = measure()
		if not here in links:
			open_dirs = []
			for d in DIRS:
				if can_move(d):
					open_dirs.append(d)
			links[here] = open_dirs
		todo = []
		for d in links[here]:
			dx, dy = DELTA[d]
			nxt = (x + dx, y + dy)
			if not nxt in seen:
				if nxt in is_home:
					if not nxt in border:
						border[nxt] = here
						bl.append([is_home[nxt], list(trail), L, L])
				elif PRUNE and pruned(bl, L, d):
					pass
				else:
					todo.append(d)
		nxt_d = None
		if AIM and len(todo) > 1:
			tx, ty = t
			bi = 0
			bv = 99
			for i in range(len(todo)):
				dx, dy = DELTA[todo[i]]
				v = abs(x + dx - tx) + abs(y + dy - ty)
				if v < bv:
					bv = v
					bi = i
			d = todo[bi]
			todo[bi] = todo[0]
			todo[0] = d
		if len(todo) > 0:
			for i in range(1, len(todo)):
				pend.append((L, todo[i]))
			nxt_d = todo[0]
		else:
			while len(pend) > 0:
				pl, pdir2 = pend.pop()
				while len(trail) > pl:
					back(bl, trail)
				dx, dy = DELTA[pdir2]
				if not (x + dx, y + dy) in seen and not (PRUNE and pruned(bl, pl, pdir2)):
					nxt_d = pdir2
					break
		if nxt_d == None:
			break
		dx, dy = DELTA[nxt_d]
		nc = (x + dx, y + dy)
		seen[nc] = 1
		L = len(trail)
		dep[nc] = L + 1
		par[nc] = (x, y)
		pd[nc] = nxt_d
		order.append(nc)
		for e in bl:
			if e[3] == L and e[2] > L and e[1][L] == nxt_d:
				e[3] = L + 1
		go(nxt_d)
		trail.append(nxt_d)


def back(bl, trail):
	L = len(trail)
	d = trail.pop()
	for e in bl:
		if e[3] == L:
			e[3] = L - 1
	go(OPP[d])


def pruned(bl, L, d):
	for e in bl:
		cp = e[3]
		if cp == L and e[2] > L and e[1][L] == d:
			cp += 1
		dj = e[2] + L + 2 - 2 * cp
		if dj < L + 1 or (dj == L + 1 and e[0] < me):
			return True
	return False


def bfs(src, d0):
	dist = {src: d0}
	queue = [src]
	k = 0
	while k < len(queue):
		cell = queue[k]
		k += 1
		cx, cy = cell
		dc = dist[cell] + 1
		for d in links[cell]:
			dx, dy = DELTA[d]
			nxt = (cx + dx, cy + dy)
			if nxt in links and not nxt in dist:
				dist[nxt] = dc
				queue.append(nxt)
	return dist


def claim():
	# Voronoi cell of my home, ties to the lower index, by one layered
	# multi-source search. Every drone gets the same split from its own map.
	lab = {homes[me]: me}
	layer = [homes[me]]
	seeds = {}
	for h in border:
		b = border[h]
		j = is_home[h]
		if not b in seeds or j < seeds[b]:
			seeds[b] = j
	first = True
	while len(layer) > 0:
		cand = {}
		for cell in layer:
			lc = lab[cell]
			cx, cy = cell
			for d in links[cell]:
				dx, dy = DELTA[d]
				nxt = (cx + dx, cy + dy)
				if nxt in links and not nxt in lab:
					if not nxt in cand or lc < cand[nxt]:
						cand[nxt] = lc
		if first:
			first = False
			for b in seeds:
				if not b in lab:
					if not b in cand or seeds[b] < cand[b]:
						cand[b] = seeds[b]
		layer = []
		for cell in cand:
			lab[cell] = cand[cell]
			layer.append(cell)
	region = {}
	for cell in lab:
		if lab[cell] == me:
			region[cell] = 1
	return region


def route(a, b):
	# dirs from a to b along the exploring tree
	up = []
	down = []
	while a != b:
		if dep[a] >= dep[b]:
			up.append(OPP[pd[a]])
			a = par[a]
		else:
			down.append(pd[b])
			b = par[b]
	k = len(down) - 1
	while k >= 0:
		up.append(down[k])
		k -= 1
	return up


def settle():
	# Pick the 1-median of my cells, walk there, build paths to every cell.
	global mine
	global park
	region = claim()
	n = len(region)
	size = {}
	for cell in region:
		size[cell] = 1
	k = len(order) - 1
	while k > 0:
		cell = order[k]
		if cell in region:
			p = par[cell]
			if p in region:
				size[p] = size[p] + size[cell]
		k -= 1
	best = homes[me]
	for cell in order:
		if cell in region and size[cell] * 2 > n:
			best = cell
	# walk to best along the exploring tree
	for d in route((x, y), best):
		go(d)
	park = best
	mine = {best: []}
	queue = [best]
	k = 0
	while k < len(queue):
		cell = queue[k]
		k += 1
		cx, cy = cell
		for d in links[cell]:
			dx, dy = DELTA[d]
			nxt = (cx + dx, cy + dy)
			if nxt in region and not nxt in mine:
				q = list(mine[cell])
				q.append(d)
				mine[nxt] = q
				queue.append(nxt)


def rescan():
	# Walls only ever open while a maze is reused. Look for new openings here.
	here = (get_pos_x(), get_pos_y())
	if not here in links:
		return
	old = links[here]
	if len(old) == 4:
		return
	hx, hy = here
	found = False
	for d in DIRS:
		if not d in old and can_move(d):
			old.append(d)
			dx, dy = DELTA[d]
			n = (hx + dx, hy + dy)
			if n in links:
				links[n].append(OPP[d])
			if here in mine and n in mine:
				found = True
	if found:
		rebuild()


def rebuild():
	global mine
	region = mine
	mine = {park: []}
	queue = [park]
	k = 0
	while k < len(queue):
		cell = queue[k]
		k += 1
		cx, cy = cell
		for d in links[cell]:
			dx, dy = DELTA[d]
			nxt = (cx + dx, cy + dy)
			if nxt in region and not nxt in mine:
				q = list(mine[cell])
				q.append(d)
				mine[nxt] = q
				queue.append(nxt)


def serve():
	cur = []  # dirs from park cell to where I stand
	k = 0  # I stand at cur[:k]
	last = None
	since = 0
	while True:
		t = measure()
		if t == None:
			return
		p = None
		if t in mine:
			p = mine[t]
		elif t != last:
			last = t
			since = get_time()
		elif k == 0 and t in links and get_time() - since > STALL:
			# nobody came: fetch it even though it is not mine
			p = route(park, t)
		if p != None:
			lp = len(p)
			c = 0
			while c < k and c < lp and cur[c] == p[c]:
				c += 1
			while k > c:
				k -= 1
				move(OPP[cur[k]])
			while c < lp:
				move(p[c])
				c += 1
			cur = p
			k = lp
			if num_items(Items.Weird_Substance) < amount:
				harvest()
				return
			if get_entity_type() == Entities.Treasure:
				tk = get_tick_count()
				if use_item(Items.Weird_Substance, amount):
					if RESCAN:
						rescan()
					while measure() == t:
						pass
				elif get_tick_count() - tk < 50 and get_entity_type() == Entities.Treasure:
					# refused at once on a real treasure: it is spent
					harvest()
					return
		elif k > 0:
			k -= 1
			move(OPP[cur[k]])
			if RESCAN:
				rescan()


def life():
	global x
	global y
	while True:
		hx, hy = homes[me]
		fly(hx, hy)
		while measure() == None:
			pass
		x = get_pos_x()
		y = get_pos_y()
		explore()
		settle()
		serve()


def worker():
	life()


clear()
amount = get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
homes = make_homes()
for i in range(len(homes)):
	is_home[homes[i]] = i
for i in range(1, len(homes)):
	me = i
	spawn_drone(worker)
me = 0
first = True
while True:
	hx, hy = homes[0]
	fly(hx, hy)
	if get_entity_type() != None:
		harvest()
	plant(Entities.Bush)
	if first:
		k = 40
		first = False
	else:
		k = SETTLE
	while k > 1:
		move(East)
		move(West)
		k -= 2
	use_item(Items.Weird_Substance, amount)
	quick_print("maze", get_time())
	x = hx
	y = hy
	explore()
	settle()
	serve()
