# Maze leaderboard (many drones): 16 separate 8x8 mazes, two drones in each, all in parallel.
# 16 mazes x 301 treasures x 8*8 x 32 gold is exactly the goal (9,863,168).
# Both drones of a maze run the same DFS from the bush cell, so they map the same tree without
# talking. Each then picks the same two-median split (the tree cut whose two sides' medians have
# the least total distance), parks at the median of its side and serves the treasures that land
# there, walking back toward its median between them. A maze that runs out (301 treasures) is
# harvested and made again from the same bush cell.
#
# The "remake the maze until a drone is a step from the treasure" idea (31 drones around the edge
# of one 32x32 maze) was tried in the simulator: about 1.5 s per treasure, 462 s for the board,
# since a fresh treasure is within one open step of a drone only ~7% of the time.

GOAL = 9863168
S = 8
NC = 64
SYNC = 0.07  # wait after mapping so a partner's DFS never sees a wall our first use_item opened
STALL = 1.5  # nobody took the treasure for this long: fetch it anyway
ENDGAME = 300000  # gold short of the goal below which walks check the goal every move
CUT = 24  # cuts tried: |64 - 2 * side| <= CUT
BUSH = [(12, 12), (20, 12), (12, 20), (20, 20), (4, 12), (12, 4), (28, 12), (12, 28), (20, 4), (4, 20), (28, 20), (20, 28), (4, 28), (28, 4), (28, 28), (4, 4)]
DIRS = [North, East, South, West]
OPP = {North: South, South: North, East: West, West: East}
STEP = {North: S, East: 1, South: -S, West: -1}

amt = 0
mi = 0
role = 0
cx = 0
cy = 0
par = []
pd = []
dep = []
pre = []
kids = []
lo = 0
hi = 0
hp = {}
hc = {}
order = []


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


def explore():
	# DFS of the whole maze; stops on the last new cell. Returns that cell.
	global par
	global pd
	global dep
	global pre
	global kids
	global order
	order = []
	par = []
	pd = []
	dep = []
	pre = []
	kids = []
	for k in range(NC):
		par.append(-1)
		pd.append(None)
		dep.append(0)
		pre.append(-1)
		kids.append([])
	c = (get_pos_x() - cx) + S * (get_pos_y() - cy)
	pre[c] = 0
	order.append(c)
	cnt = 1
	stk = []
	i = 0
	while cnt < NC:
		if i < 4:
			d = DIRS[i]
			i += 1
			if can_move(d):
				nb = c + STEP[d]
				if pre[nb] < 0:
					if num_items(Items.Gold) >= GOAL:
						return -1
					move(d)
					order.append(nb)
					pre[nb] = cnt
					cnt += 1
					par[nb] = c
					pd[nb] = d
					dep[nb] = dep[c] + 1
					kids[c].append(nb)
					stk.append(i)
					c = nb
					i = 0
		else:
			i = stk.pop()
			move(OPP[pd[c]])
			c = par[c]
	return c


def split():
	# Two medians: the Voronoi cells of two centres in a tree are the two sides of one edge, so
	# try the near-balanced cuts and keep the one whose sides' 1-medians have the least total
	# distance. Sets lo/hi (the cut subtree's preorder range) and returns my median cell.
	global lo
	global hi
	size = []
	down = []
	for k in range(NC):
		size.append(1)
		down.append(0)
	k = NC - 1
	while k > 0:
		c = order[k]
		p = par[c]
		size[p] += size[c]
		down[p] += down[c] + size[c]
		k -= 1
	r = order[0]
	best = -1
	bv = 0
	bh0 = r
	bh1 = r
	for k in range(1, NC):
		c = order[k]
		sc = size[c]
		if abs(NC - 2 * sc) <= CUT:
			# cut subtree: walk from c toward its heavy child
			cost = down[c]
			h1 = c
			while True:
				nxt = -1
				for ch in kids[h1]:
					if size[ch] * 2 > sc:
						nxt = ch
				if nxt < 0:
					break
				cost += sc - 2 * size[nxt]
				h1 = nxt
			# the rest, rooted at r, with the subtree taken off its ancestors
			m = NC - sc
			cost += down[r] - down[c] - sc * dep[c]
			l0 = pre[c]
			h0 = r
			while True:
				nxt = -1
				for ch in kids[h0]:
					s = size[ch]
					p = pre[ch]
					if p <= l0 and l0 < p + s:
						s -= sc
					if s * 2 > m:
						nxt = ch
						ns = s
				if nxt < 0:
					break
				cost += m - 2 * ns
				h0 = nxt
			if best < 0 or cost < bv:
				best = c
				bv = cost
				bh0 = h0
				bh1 = h1
	lo = pre[best]
	hi = lo + size[best]
	if role == 1:
		return bh1
	return bh0


def paths(home):
	# for every cell of my side: the route from home, by its treasure tuple
	global hp
	global hc
	hp = {}
	hc = {}
	fp = {home: []}
	q = [home]
	k = 0
	while k < len(q):
		c = q[k]
		k += 1
		t = (cx + c % S, cy + c // S)
		f = fp[c]
		hp[t] = f
		hc[t] = c
		for m in kids[c]:
			p = pre[m]
			if (lo <= p and p < hi) == (role == 1) and not m in fp:
				r = list(f)
				r.append(pd[m])
				fp[m] = r
				q.append(m)
		m = par[c]
		if m >= 0 and not m in fp:
			p = pre[m]
			if (lo <= p and p < hi) == (role == 1):
				r = list(f)
				r.append(OPP[pd[c]])
				fp[m] = r
				q.append(m)


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


def walk(p):
	# near the end, stop the moment the goal is met
	if GOAL - num_items(Items.Gold) > ENDGAME:
		for d in p:
			move(d)
		return True
	for d in p:
		if num_items(Items.Gold) >= GOAL:
			return False
		move(d)
	return True


def serve(home):
	# returns True when the maze was harvested and has to be made again
	cur = home
	back = []
	bk = 0
	while num_items(Items.Gold) < GOAL:
		t = measure()
		if t == None:
			return True
		if t in hp:
			if cur == home:
				p = hp[t]
			else:
				tx, ty = t
				p = path(cur, (tx - cx) + S * (ty - cy))
			if not walk(p):
				return False
			cur = hc[t]
			back = hp[t]
			bk = len(back) - 1
			if get_entity_type() == Entities.Treasure:
				if use_item(Items.Weird_Substance, amt):
					while measure() == t:
						pass
				else:
					harvest()
					return True
		elif cur != home:
			d = OPP[back[bk]]
			bk -= 1
			move(d)
			cur += STEP[d]
		else:
			since = get_time()
			while measure() == t and num_items(Items.Gold) < GOAL and get_time() - since < STALL:
				pass
			if measure() == t and num_items(Items.Gold) < GOAL:
				# nobody came (our maps disagree): fetch it
				tx, ty = t
				tl = (tx - cx) + S * (ty - cy)
				if not walk(path(cur, tl)):
					return False
				if get_entity_type() == Entities.Treasure:
					use_item(Items.Weird_Substance, amt)
					while measure() == t:
						pass
				back = path(home, tl)
				bk = len(back) - 1
				cur = tl
	return False


def run():
	while True:
		last = explore()
		if last < 0:
			return
		home = split()
		paths(home)
		if not walk(path(last, home)):
			return
		t0 = get_time()
		while get_time() < t0 + SYNC:
			pass
		if not serve(home):
			return
		# maze harvested after 301 treasures: make it again from the bush cell
		bx, by = BUSH[mi]
		goto(bx, by)
		if num_items(Items.Gold) >= GOAL:
			return
		# the partner plants the bush when it gets there; the planter makes the maze once it sees it,
		# so both are inside
		if role == 0:
			while get_entity_type() != Entities.Bush and num_items(Items.Gold) < GOAL:
				pass
			if num_items(Items.Gold) >= GOAL:
				return
			use_item(Items.Weird_Substance, amt)
		else:
			plant(Entities.Bush)
			while measure() == None and num_items(Items.Gold) < GOAL:
				pass
			if num_items(Items.Gold) >= GOAL:
				return


def partner():
	while measure() == None:
		pass
	run()


def planter():
	global role
	global cx
	global cy
	bx, by = BUSH[mi]
	cx = bx - 4
	cy = by - 4
	goto(bx, by)
	plant(Entities.Bush)
	role = 1
	spawn_drone(partner)
	role = 0
	use_item(Items.Weird_Substance, amt)
	run()


amt = S * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
for k in range(len(BUSH) - 1):
	mi = k
	spawn_drone(planter)
mi = len(BUSH) - 1
planter()
