GROW = 1.0001
WDT = 0.0390625
HV = #HV#
NSIG = #NSIG#

#DATA#


def wait_until(e):
	while get_time() < e:
		pass


def fm(B, T):
	n = 0
	while n < 12:
		n += 1
		v = measure()
		if v == None:
			return
		bd = None
		bv = v
		for d in B:
			w = measure(d)
			while w == None:
				w = measure(d)
			if w > bv:
				bv = w
				bd = d
		if bd != None:
			swap(bd)
		else:
			td = None
			tv = v
			for d in T:
				w = measure(d)
				while w == None:
					w = measure(d)
				if w < tv:
					tv = w
					td = d
			if td != None:
				swap(td)
			else:
				return


def cx(BS, CS):
	for e in CS:
		if e[3]:
			move(e[0])
			fm([], e[1])
			move(e[2])
	for e in BS:
		if e[3]:
			move(e[0])
			fm(e[1], [])
			move(e[2])
	n = 0
	while n < 10:
		n += 1
		g = measure()
		hit = False
		for e in CS:
			if not hit:
				w = measure(e[0])
				if w != None and g > w:
					swap(e[0])
					move(e[0])
					fm([], e[1])
					move(e[2])
					hit = True
		if not hit:
			for e in BS:
				if not hit:
					w = measure(e[0])
					if w != None and g < w:
						swap(e[0])
						move(e[0])
						fm(e[1], [])
						move(e[2])
						hit = True
		if not hit:
			return


def sf(p, GT):
	L = GT[p]
	n = len(L)
	k = 0
	cap = 0
	while k < n:
		d = L[k]
		w = measure(d)
		if w != None:
			v = measure()
			b = False
			if L[k + 1]:
				if v > w:
					b = True
			elif v < w:
				b = True
			if b:
				swap(d)
				if L[k + 2]:
					q = L[k + 4]
					if q in GT:
						move(d)
						sf(q, GT)
						move(L[k + 3])
				cap += 1
				if cap < 30:
					k = -5
		k += 5


def goto(x, y):
	while get_pos_x() < x:
		move(East)
	while get_pos_x() > x:
		move(West)
	while get_pos_y() < y:
		move(North)
	while get_pos_y() > y:
		move(South)


def cc(RD, EDG, NS, AX, AY):
	V = []
	for i in range(NS):
		V.append(0)
	i = 0
	for e in RD:
		goto(e[0], e[1])
		V[i] = measure()
		for f in e[2]:
			V[f[1]] = measure(f[0])
		i += 1
	S = []
	ch = True
	n = 0
	while ch and n < 40:
		ch = False
		n += 1
		for e in EDG:
			a = V[e[0]]
			b = V[e[1]]
			if a > b:
				V[e[0]] = b
				V[e[1]] = a
				S.append(e)
				ch = True
	for e in S:
		goto(e[2], e[3])
		swap(e[4])
	goto(AX, AY)


def worker(c):
	tl = FA[c]()
	BA[c]()
	wait_until(tl + GROW)
	if c == HV:
		w0 = num_items(Items.Water)
		while (get_time() // WDT) - num_items(Items.Water) < NSIG + USED:
			pass
		harvest()
	else:
		use_item(Items.Water)
		while num_items(Items.Cactus) <= 0:
			pass
	TB[c]()
	tl = FB[c]()
	BB[c]()
	wait_until(tl + GROW)
	if c == HV:
		while num_drones() > 1:
			pass
		harvest()


def launch(c):
	for st_ in LP[c]:
		for m in st_[0]:
			move(m)
		spawn_drone(launch, st_[1])
	worker(c)


USED = 0
launch(0)
