# Maze leaderboard (many drones), whole board: one 32x32 maze, 32 drones.
# 301 treasures x 32*32 x 32 gold is exactly the goal (9,863,168). Each drone owns the cells that
# are closer to its start cell (along the maze) than to any other drone's start cell. It maps only
# that region with a DFS that does not enter a cell some already-found start cell is closer to,
# parks at the region's median, and serves the treasures that land in it. Only one drone moves at
# a time, and it is almost always starting from its median.

GOAL = 9863168
LAST = 32768  # gold of one treasure
STALL = 1.0
PER_STEP = 0.03  # extra wait per step of my route before I fetch someone else's treasure
SEEK = 30  # moves a drone still mapping spends looking for a stalled treasure  # nobody took the treasure for this long: anyone who has mapped the cell fetches it
DIRS = [North, East, South, West]
OPP = {North: South, South: North, East: West, West: East}
DXY = {North: (0, 1), South: (0, -1), East: (1, 0), West: (-1, 0)}

me = 0
amt = 0
homes = []
is_home = {}
par = {}
pd = {}
dep = {}
order = []
known = []  # [home index, cell next to it, path to that cell, its length, common prefix with trail]
hp = {}


def make_homes():
	result = []
	for i in range(32):
		result.append(((i % 8) * 4 + 2, (i // 8) * 8 + 4))
	return result


def goto(tx, ty):
	n = get_world_size()
	dx = (tx - get_pos_x() + n) % n
	dy = (ty - get_pos_y() + n) % n
	if dx * 2 <= n:
		for i in range(dx):
			move(East)
	else:
		for i in range(n - dx):
			move(West)
	if dy * 2 <= n:
		for i in range(dy):
			move(North)
	else:
		for i in range(n - dy):
			move(South)


def pruned(L, d):
	# would the cell one step along d from my trail end (depth L + 1) be closer to a found home?
	for e in known:
		cp = e[4]
		if cp == L and e[3] > L and e[2][L] == d:
			cp += 1
		dj = e[3] + L + 2 - 2 * cp
		if dj < L + 1 or (dj == L + 1 and e[0] < me):
			return True
	return False


def explore():
	global par
	global pd
	global dep
	global order
	global known
	h = homes[me]
	par = {h: None}
	pd = {}
	dep = {h: 0}
	order = [h]
	known = []
	x, y = h
	trail = []
	pend = []  # (trail length, dir) still to try
	found = {}
	seen_t = None
	sought = None
	t_since = 0
	while True:
		L = len(trail)
		c = (x, y)
		t = measure()
		if t != seen_t:
			seen_t = t
			t_since = get_time()
		elif t != sought and get_time() - t_since > STALL and seeker(t) == me:
			sought = t
			seek(t, c, SEEK)
		todo = []
		for d in DIRS:
			if can_move(d):
				dx, dy = DXY[d]
				nb = ((x + dx) % 32, (y + dy) % 32)
				if not nb in dep:
					if nb in is_home:
						if not nb in found:
							found[nb] = 1
							known.append([is_home[nb], c, list(trail), L, L])
					elif not pruned(L, d):
						todo.append(d)
		nd = None
		if len(todo) > 0:
			for i in range(1, len(todo)):
				pend.append((L, todo[i]))
			nd = todo[0]
		else:
			while len(pend) > 0:
				pl, d = pend.pop()
				while len(trail) > pl:
					b = trail.pop()
					L = len(trail) + 1
					for e in known:
						if e[4] == L:
							e[4] = L - 1
					move(OPP[b])
					dx, dy = DXY[OPP[b]]
					x = (x + dx) % 32
					y = (y + dy) % 32
				L = len(trail)
				dx, dy = DXY[d]
				nb = ((x + dx) % 32, (y + dy) % 32)
				if not nb in dep and not pruned(L, d):
					nd = d
					break
		if nd == None:
			return (x, y)
		c = (x, y)
		for e in known:
			if e[4] == L and e[3] > L and e[2][L] == nd:
				e[4] = L + 1
		move(nd)
		dx, dy = DXY[nd]
		x = (x + dx) % 32
		y = (y + dy) % 32
		nb = (x, y)
		par[nb] = c
		pd[nb] = nd
		dep[nb] = L + 1
		order.append(nb)
		trail.append(nd)


def claim():
	# my Voronoi cell inside what I mapped: one layered search from my home and the found homes
	h = homes[me]
	lab = {h: me}
	layer = [h]
	seeds = {}
	for e in known:
		a = e[1]
		if not a in seeds or e[0] < seeds[a]:
			seeds[a] = e[0]
	first = True
	while len(layer) > 0:
		cand = {}
		for c in layer:
			lc = lab[c]
			nbs = []
			p = par[c]
			if p != None:
				nbs.append(p)
			for k in kids[c]:
				nbs.append(k)
			for m in nbs:
				if not m in lab:
					if not m in cand or lc < cand[m]:
						cand[m] = lc
		if first:
			first = False
			for a in seeds:
				if not a in lab:
					if not a in cand or seeds[a] < cand[a]:
						cand[a] = seeds[a]
		layer = []
		for c in cand:
			lab[c] = cand[c]
			layer.append(c)
	region = {}
	for c in lab:
		if lab[c] == me:
			region[c] = 1
	return region


kids = {}


def settle(last):
	# median of my region; routes from it to every region cell; walk there
	global kids
	global hp
	kids = {}
	for c in order:
		kids[c] = []
	for c in order:
		p = par[c]
		if p != None:
			kids[p].append(c)
	region = claim()
	n = len(region)
	size = {}
	for c in region:
		size[c] = 1
	k = len(order) - 1
	while k > 0:
		c = order[k]
		if c in region:
			p = par[c]
			if p in region:
				size[p] += size[c]
		k -= 1
	best = homes[me]
	while True:
		nxt = None
		for ch in kids[best]:
			if ch in region and size[ch] * 2 > n:
				nxt = ch
		if nxt == None:
			break
		best = nxt
	hp = {best: []}
	q = [best]
	k = 0
	while k < len(q):
		c = q[k]
		k += 1
		f = hp[c]
		nbs = []
		for ch in kids[c]:
			nbs.append(ch)
		p = par[c]
		if p != None:
			nbs.append(p)
		for m in nbs:
			if m in region and not m in hp:
				r = list(f)
				if m == p:
					r.append(OPP[pd[c]])
				else:
					r.append(pd[m])
				hp[m] = r
				q.append(m)
	for d in path(last, best):
		move(d)
	return best


def path(a, b):
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


def grab(t):
	if get_entity_type() == Entities.Treasure:
		if use_item(Items.Weird_Substance, amt):
			while measure() == t:
				pass
		elif num_items(Items.Gold) >= GOAL - LAST:
			# refused: either another drone just moved it (it leaves after one action) or it is the
			# 301st, which takes no more weird substance and is harvested
			t1 = get_time()
			while get_time() < t1 + 0.05:
				pass
			if measure() == t and get_entity_type() == Entities.Treasure:
				if not use_item(Items.Weird_Substance, amt):
					harvest()


def seek(t, start, budget):
	# t is in no one's map (or its owner is still mapping): walk to my mapped cell nearest it, search
	# outward from there trying the directions toward it first, take it, and come back to start
	tx, ty = t
	best = start
	sx, sy = start
	bd = abs(sx - tx) + abs(sy - ty)
	for c in dep:
		cx, cy = c
		v = abs(cx - tx) + abs(cy - ty)
		if v < bd:
			bd = v
			best = c
	for d in path(start, best):
		move(d)
	x, y = best
	vis = {best: 1}
	trail = []
	steps = 0
	while (x, y) != t and measure() == t and steps < budget:
		steps += 1
		nd = None
		bv = 99
		for d in DIRS:
			dx, dy = DXY[d]
			nb = (x + dx, y + dy)
			if not nb in vis and can_move(d):
				v = abs(x + dx - tx) + abs(y + dy - ty)
				if v < bv:
					bv = v
					nd = d
		if nd == None:
			if len(trail) == 0:
				break
			d = trail.pop()
			move(OPP[d])
			dx, dy = DXY[OPP[d]]
			x += dx
			y += dy
		else:
			move(nd)
			dx, dy = DXY[nd]
			x += dx
			y += dy
			vis[(x, y)] = 1
			trail.append(nd)
	if (x, y) == t:
		grab(t)
	k = len(trail) - 1
	while k >= 0:
		move(OPP[trail[k]])
		k -= 1
	for d in path(best, start):
		move(d)


def serve(home):
	while num_items(Items.Gold) < GOAL:
		t = measure()
		if t == None:
			return
		if t in hp:
			p = hp[t]
			for d in p:
				move(d)
			grab(t)
			k = len(p) - 1
			while k >= 0:
				move(OPP[p[k]])
				k -= 1
		else:
			since = get_time()
			while measure() == t and num_items(Items.Gold) < GOAL and get_time() - since < STALL:
				pass
			if measure() == t and num_items(Items.Gold) < GOAL:
				if t in dep:
					# the drone with the shortest route goes first; the rest see it gone
					p = path(home, t)
					wait = since + STALL + PER_STEP * len(p)
					while measure() == t and get_time() < wait:
						pass
					if measure() != t:
						continue
					for d in p:
						move(d)
					grab(t)
					for d in path(t, home):
						move(d)
				else:
					while measure() == t and num_items(Items.Gold) < GOAL and get_time() - since < 2 * STALL:
						pass
					if measure() == t and num_items(Items.Gold) < GOAL and seeker(t) == me:
						seek(t, home, 999)


def seeker(t):
	tx, ty = t
	bi = 0
	bd = 99
	for i in range(32):
		hx, hy = homes[i]
		v = abs(hx - tx) + abs(hy - ty)
		if v < bd:
			bd = v
			bi = i
	return bi


def life():
	hx, hy = homes[me]
	goto(hx, hy)
	while measure() == None:
		pass
	last = explore()
	home = settle(last)
	serve(home)


def worker():
	life()


amt = get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
homes = make_homes()
for i in range(len(homes)):
	is_home[homes[i]] = i
# farthest homes first, so the last drone arrives early
t0 = get_time()
worst = 0
k = 0
for dd in range(32, -1, -1):
	for i in range(1, 32):
		hx, hy = homes[i]
		if min(hx, 32 - hx) + min(hy, 32 - hy) == dd:
			me = i
			spawn_drone(worker)
			k += 1
			worst = max(worst, k + 1 + dd)
me = 0
dt = (get_time() - t0) / k
hx, hy = homes[0]
goto(hx, hy)
plant(Entities.Bush)
while get_time() < t0 + (worst + 2) * dt:
	pass
use_item(Items.Weird_Substance, amt)
life()
