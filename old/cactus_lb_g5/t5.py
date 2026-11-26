WDT = 0.0390625
NSIG = #NSIG#

def wait_until(e):
	while get_time() < e:
		pass


def fmc(B, T):
	n = 0
	while n < 16:
		v = measure()
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
			n += 1
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
				n += 1
			else:
				return n
	return n


def fm(B, T):
	fmc(B, T)


def jf(J, P, order):
	work = list(order)
	st = order[0]
	cur = st
	while len(work) > 0:
		c = work.pop(0)
		for m in P[cur][c]:
			move(m)
		cur = c
		e = J[c]
		go = True
		while go:
			v = measure()
			bi = -1
			bv = v
			i = 0
			for d in e[0]:
				w = measure(d)
				while w == None:
					w = measure(d)
				if w > bv:
					bv = w
					bi = i
				i += 1
			if bi >= 0:
				swap(e[0][bi])
				k = e[2][bi]
				if k >= 0 and not (k in work):
					work.append(k)
			else:
				ti = -1
				tv = v
				i = 0
				for d in e[1]:
					w = measure(d)
					while w == None:
						w = measure(d)
					if w < tv:
						tv = w
						ti = i
					i += 1
				if ti >= 0:
					swap(e[1][ti])
					k = e[3][ti]
					if k >= 0 and not (k in work):
						work.append(k)
				else:
					go = False
	for m in P[cur][st]:
		move(m)


def xcasw(d, up):
	w = measure(d)
	while w == None:
		w = measure(d)
	t = get_time() + 0.05
	while get_time() < t:
		pass
	w = measure(d)
	if up:
		if measure() > w:
			swap(d)
	elif measure() < w:
		swap(d)


def xcas(d, up):
	w = measure(d)
	while w == None:
		w = measure(d)
	if up:
		if measure() > w:
			swap(d)
	elif measure() < w:
		swap(d)


#DATA#

w0()
