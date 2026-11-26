GOAL = 33554432
SEED_COST = 64
GROW = 1.0001
NA = #NA#
NB = #NB#
HV = #HV#
KD = #KD#

#DATA#


def wait_until(e):
	while get_time() < e:
		pass


def need(q, up, T, V):
	if not q in T:
		return False
	if up:
		L = T[q][0]
	else:
		L = T[q][1]
	vq = V[q]
	k = 0
	n = len(L)
	while k < n:
		r = L[k + 1]
		if r in V:
			if up:
				if vq > V[r]:
					return True
			elif vq < V[r]:
				return True
		elif L[k + 2]:
			return True
		k += 4
	return False


def settle(p, T, V):
	cap = 0
	while cap < 40:
		cap += 1
		v = measure()
		V[p] = v
		e = T[p]
		hit = False
		L = e[0]
		k = 0
		n = len(L)
		while k < n:
			if True:
				d = L[k]
				w = measure(d)
				if w != None:
					q = L[k + 1]
					V[q] = w
					if v > w:
						swap(d)
						V[p] = w
						V[q] = v
						if need(q, True, T, V):
							move(d)
							settle(q, T, V)
							move(L[k + 3])
						hit = True
						k = n
			k += 4
		if not hit:
			L = e[1]
			k = 0
			n = len(L)
			while k < n:
				if True:
					d = L[k]
					w = measure(d)
					if w != None:
						q = L[k + 1]
						V[q] = w
						if v < w:
							swap(d)
							V[p] = w
							V[q] = v
							if need(q, False, T, V):
								move(d)
								settle(q, T, V)
								move(L[k + 3])
							hit = True
							k = n
				k += 4
		if not hit:
			return


def run(d, fresh, kd):
	P = d[0]
	M = d[1]
	T = d[2]
	V = {}
	n = len(P)
	if kd > n - 8:
		kd = n - 8
	if kd < 0:
		kd = 0
	for i in range(n):
		for m in M[i]:
			move(m)
		if fresh:
			till()
		elif get_entity_type() != None:
			harvest()
		plant(Entities.Cactus)
		if i < n - kd:
			settle(P[i], T, V)
	if kd > 0:
		R = d[4]
		i = n - 1
		while i >= n - kd:
			if i < n - 1:
				for m in R[i]:
					move(m)
			settle(P[i], T, V)
			i -= 1


def pretill(db):
	for st in db[3]:
		for m in st[0]:
			move(m)
		if st[1]:
			till()


def travel(p):
	x = p // 32
	y = p % 32
	dx = (x - get_pos_x()) % 32
	if dx <= 16:
		for _ in range(dx):
			move(East)
	else:
		for _ in range(32 - dx):
			move(West)
	dy = (y - get_pos_y()) % 32
	if dy <= 16:
		for _ in range(dy):
			move(North)
	else:
		for _ in range(32 - dy):
			move(South)


def clearchunk(d):
	for p in d[0]:
		travel(p)
		if get_entity_type() != None:
			harvest()


def recover(c, bar):
	da = FA[c]()
	db = FB[c]()
	clearchunk(da)
	clearchunk(db)
	travel(db[0][0])
	wait_until(bar)
	run(db, False, KD)


def worker(c):
	da = FA[c]()
	run(da, True, 0)
	db = FB[c]()
	pump = PUMP0 - SEED_COST * NA
	if c == HV:
		while num_items(Items.Pumpkin) > pump:
			pass
		wait_until(get_time() + GROW)
		harvest()
		pretill(db)
	else:
		pretill(db)
		while num_items(Items.Cactus) <= 0:
			pass
	run(db, False, KD)
	if c != HV:
		return
	while True:
		pump -= SEED_COST * NB
		while num_items(Items.Pumpkin) > pump:
			pass
		t = get_time() + GROW
		while num_drones() > 1:
			pass
		wait_until(t)
		harvest()
		if num_items(Items.Cactus) >= GOAL:
			return
		# a harvest came up short: helpers clear both chunks and replant B
		pump = num_items(Items.Pumpkin)
		bar = get_time() + 5
		for k in range(32):
			if k != HV:
				spawn_drone(recover, k, bar)
		recover(HV, bar)


LP = #LP#


def launch(c):
	for st in LP[c]:
		for m in st[0]:
			move(m)
		spawn_drone(launch, st[1])
	worker(c)


PUMP0 = num_items(Items.Pumpkin)
launch(0)
