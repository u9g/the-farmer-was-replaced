WDT = 0.0390625
NSIG = 43

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


def xcasq(d, up):
	w = measure(d)
	while w == None:
		w = measure(d)
	if up:
		if measure() <= w:
			return
	elif measure() >= w:
		return
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


KA = 3
KB = 6
KP = 6
PD = False


def pkA(x, y):
	global PD
	plant(Entities.Cactus)
	if PD:
		swap(x)
		plant(Entities.Cactus)
		PD = False
	swap(y)
	plant(Entities.Cactus)


def pkq():
	global PD
	plant(Entities.Cactus)
	t = get_time() - 0.0658
	if PD:
		t = get_time()
		swap(East)
		plant(Entities.Cactus)
		PD = False
	swap(North)
	plant(Entities.Cactus)
	return t


def pkB(x):
	global PD
	plant(Entities.Cactus)
	if PD:
		if measure() <= 3:
			swap(West)
			plant(Entities.Cactus)
			swap(x)
			plant(Entities.Cactus)
			PD = False
			move(North)
			plant(Entities.Cactus)
			move(West)
			return
		swap(x)
		plant(Entities.Cactus)
		PD = False
	v = measure()
	if v >= 6:
		swap(North)
		plant(Entities.Cactus)
		move(West)
		plant(Entities.Cactus)
		move(North)
	elif v <= 3:
		swap(West)
		plant(Entities.Cactus)
		move(North)
		plant(Entities.Cactus)
		move(West)
	else:
		move(West)
		plant(Entities.Cactus)
		move(North)
		PD = True


def pkC(x):
	global PD
	plant(Entities.Cactus)
	if PD:
		if measure() >= 6:
			swap(East)
			plant(Entities.Cactus)
			swap(x)
			plant(Entities.Cactus)
			PD = False
			move(South)
			plant(Entities.Cactus)
			move(East)
			return
		swap(x)
		plant(Entities.Cactus)
		PD = False
	v = measure()
	if v <= 3:
		swap(South)
		plant(Entities.Cactus)
		move(East)
		plant(Entities.Cactus)
		move(South)
	elif v >= 6:
		swap(East)
		plant(Entities.Cactus)
		move(South)
		plant(Entities.Cactus)
		move(East)
	else:
		move(East)
		plant(Entities.Cactus)
		move(South)
		PD = True


def hlp(FS, MS, RS, j, lo, e):
	while j < lo:
		for d in MS[j]:
			move(d)
		j += 1
	while j < e:
		FS[j]()
		for d in MS[j]:
			move(d)
		j += 1
	FS[e]()


def own(FS, MS, RS, j, e, DL):
	SP = (0, 0, 0, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10, 10, 11, 12, 13, 13, 14, 15, 16, 16, 17, 18, 19, 20, 20, 21, 22)
	while j < e:
		if e - j >= 2 and get_time() + 0.09 * (e - j + 1) > DL:
			a = SP[e - j + 1]
			h = spawn_drone(hlp, FS, MS, RS, j, j + a, e)
			if h:
				e = j + a - 1
		FS[j]()
		for d in MS[j]:
			move(d)
		j += 1
	FS[e]()


def fsS_NE():
	while True:
		v = measure()
		a = measure(South)
		if a == None:
			continue
		while a > v:
			swap(South)
			v = measure()
			a = measure(South)
		a = measure(North)
		b = measure(East)
		if not a != None != b:
			continue
		if a >= v <= b:
			return
		if b < a:
			swap(East)
		else:
			swap(North)
		break
	while True:
		v = measure()
		a = measure(South)
		while a > v:
			swap(South)
			v = measure()
			a = measure(South)
		a = measure(North)
		b = measure(East)
		if a >= v <= b:
			return
		if b < a:
			swap(East)
		else:
			swap(North)


def fsSW_E():
	while True:
		v = measure()
		a = measure(South)
		b = measure(West)
		if not a != None != b:
			continue
		while not a <= v >= b:
			if b > a:
				swap(West)
			else:
				swap(South)
			v = measure()
			a = measure(South)
			b = measure(West)
		a = measure(East)
		if a == None:
			continue
		if a >= v:
			return
		swap(East)
		break
	while True:
		v = measure()
		a = measure(South)
		b = measure(West)
		while not a <= v >= b:
			if b > a:
				swap(West)
			else:
				swap(South)
			v = measure()
			a = measure(South)
			b = measure(West)
		a = measure(East)
		if a >= v:
			return
		swap(East)


def fsSW_N():
	while True:
		v = measure()
		a = measure(South)
		b = measure(West)
		if not a != None != b:
			continue
		while not a <= v >= b:
			if b > a:
				swap(West)
			else:
				swap(South)
			v = measure()
			a = measure(South)
			b = measure(West)
		a = measure(North)
		if a == None:
			continue
		if a >= v:
			return
		swap(North)
		break
	while True:
		v = measure()
		a = measure(South)
		b = measure(West)
		while not a <= v >= b:
			if b > a:
				swap(West)
			else:
				swap(South)
			v = measure()
			a = measure(South)
			b = measure(West)
		a = measure(North)
		if a >= v:
			return
		swap(North)


def fSW_NE():
	v = measure()
	s = measure(South)
	w = measure(West)
	if not s <= v >= w:
		if w > s:
			swap(West)
			q = w
			w = v
			v = q
		else:
			swap(South)
			q = s
			s = v
			v = q
	a = measure(North)
	b = measure(East)
	while not a >= v <= b:
		if b < a:
			swap(East)
			q = b
			b = v
			v = q
		else:
			swap(North)
			q = a
			a = v
			v = q
		if not s <= v >= w:
			if w > s:
				swap(West)
				q = w
				w = v
				v = q
			else:
				swap(South)
				q = s
				s = v
				v = q


def fsSW_NE():
	while True:
		v = measure()
		a = measure(South)
		b = measure(West)
		if not a != None != b:
			continue
		while not a <= v >= b:
			if b > a:
				swap(West)
			else:
				swap(South)
			v = measure()
			a = measure(South)
			b = measure(West)
		a = measure(North)
		b = measure(East)
		if not a != None != b:
			continue
		if a >= v <= b:
			return
		if b < a:
			swap(East)
		else:
			swap(North)
		break
	while True:
		v = measure()
		a = measure(South)
		b = measure(West)
		while not a <= v >= b:
			if b > a:
				swap(West)
			else:
				swap(South)
			v = measure()
			a = measure(South)
			b = measure(West)
		a = measure(North)
		b = measure(East)
		if a >= v <= b:
			return
		if b < a:
			swap(East)
		else:
			swap(North)


def fsW_NE():
	while True:
		v = measure()
		a = measure(West)
		if a == None:
			continue
		while a > v:
			swap(West)
			v = measure()
			a = measure(West)
		a = measure(North)
		b = measure(East)
		if not a != None != b:
			continue
		if a >= v <= b:
			return
		if b < a:
			swap(East)
		else:
			swap(North)
		break
	while True:
		v = measure()
		a = measure(West)
		while a > v:
			swap(West)
			v = measure()
			a = measure(West)
		a = measure(North)
		b = measure(East)
		if a >= v <= b:
			return
		if b < a:
			swap(East)
		else:
			swap(North)


def w0():
	def w16():
		def w24():
			def w27():
				move(West)
				move(South)
				move(South)
				def w29():
					def w30():
						def w31():
							till()
							plant(Entities.Cactus)
							move(North)
							till()
							plant(Entities.Cactus)
							if measure() < measure(South):
								swap(South)
							move(West)
							till()
							plant(Entities.Cactus)
							move(West)
							till()
							plant(Entities.Cactus)
							move(West)
							move(West)
							till()
							plant(Entities.Cactus)
							move(East)
							till()
							plant(Entities.Cactus)
							move(South)
							till()
							plant(Entities.Cactus)
							move(East)
							till()
							plant(Entities.Cactus)
							move(South)
							till()
							plant(Entities.Cactus)
							move(East)
							till()
							plant(Entities.Cactus)
							if measure() < measure(West):
								swap(West)
							move(South)
							till()
							plant(Entities.Cactus)
							if measure() > measure(North):
								swap(North)
							move(East)
							till()
							plant(Entities.Cactus)
							if measure() < measure(West):
								swap(West)
							move(South)
							till()
							plant(Entities.Cactus)
							move(South)
							till()
							plant(Entities.Cactus)
							move(South)
							move(South)
							till()
							plant(Entities.Cactus)
							move(North)
							till()
							plant(Entities.Cactus)
							move(West)
							till()
							plant(Entities.Cactus)
							move(North)
							till()
							plant(Entities.Cactus)
							move(West)
							till()
							plant(Entities.Cactus)
							move(North)
							till()
							plant(Entities.Cactus)
							if measure() < measure(South):
								swap(South)
							move(West)
							till()
							plant(Entities.Cactus)
							if measure() > measure(East):
								swap(East)
							move(North)
							till()
							plant(Entities.Cactus)
							if measure() < measure(South):
								swap(South)
							tl = get_time()
							xcas(West, 0)
							move(East)
							move(East)
							move(South)
							move(South)
							wk = [0, 1, 2, 3]
							cur = 0
							qi = 0
							qn = 4
							q0 = True
							q1 = True
							q2 = True
							q3 = True
							q0 = False
							while True:
								v = measure()
								ja = measure(South)
								while ja == None:
									ja = measure(South)
								jb = measure(West)
								while jb == None:
									jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(East)
								while ja == None:
									ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											v = measure()
										else:
											swap(South)
											v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
								break
							q1 = False
							move(East)
							move(South)
							while True:
								v = measure()
								ja = measure(South)
								while ja == None:
									ja = measure(South)
								jb = measure(West)
								while jb == None:
									jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(North)
								while ja == None:
									ja = measure(North)
								if ja >= v:
									break
								swap(North)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											v = measure()
										else:
											swap(South)
											v = measure()
									ja = measure(North)
									if ja >= v:
										break
									swap(North)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
								break
							q2 = False
							move(North)
							while True:
								v = measure()
								ja = measure(South)
								while ja == None:
									ja = measure(South)
								jb = measure(West)
								while jb == None:
									jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										if not q0:
											wk.append(0)
											qn += 1
											q0 = True
										v = measure()
									else:
										swap(South)
										if not q1:
											wk.append(1)
											qn += 1
											q1 = True
										v = measure()
								ja = measure(North)
								while ja == None:
									ja = measure(North)
								if ja >= v:
									break
								swap(North)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											if not q0:
												wk.append(0)
												qn += 1
												q0 = True
											v = measure()
										else:
											swap(South)
											if not q1:
												wk.append(1)
												qn += 1
												q1 = True
											v = measure()
									ja = measure(North)
									if ja >= v:
										break
									swap(North)
									if not q3:
										wk.append(3)
										qn += 1
										q3 = True
								break
							q3 = False
							move(North)
							while True:
								v = measure()
								ja = measure(South)
								while ja == None:
									ja = measure(South)
								if ja > v:
									swap(South)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
									v = measure()
								ja = measure(North)
								while ja == None:
									ja = measure(North)
								if ja >= v:
									break
								swap(North)
								while True:
									v = measure()
									ja = measure(South)
									if ja > v:
										swap(South)
										if not q2:
											wk.append(2)
											qn += 1
											q2 = True
										v = measure()
									ja = measure(North)
									if ja >= v:
										break
									swap(North)
								break
							cur = 3
							qi = 4
							while qi < qn:
								cx = wk[qi]
								qi += 1
								if cx == 0:
									q0 = False
									if cur == 1:
										move(West)
										move(North)
									elif cur == 2:
										move(West)
									elif cur == 3:
										move(West)
										move(South)
									cur = 0
									while True:
										v = measure()
										ja = measure(South)
										jb = measure(West)
										if not ja <= v >= jb:
											if jb > ja:
												swap(West)
												v = measure()
											else:
												swap(South)
												v = measure()
										ja = measure(East)
										if ja >= v:
											break
										swap(East)
										if not q2:
											wk.append(2)
											qn += 1
											q2 = True
								elif cx == 1:
									q1 = False
									if cur == 0:
										move(East)
										move(South)
									elif cur == 2:
										move(South)
									elif cur == 3:
										move(South)
										move(South)
									cur = 1
									while True:
										v = measure()
										ja = measure(South)
										jb = measure(West)
										if not ja <= v >= jb:
											if jb > ja:
												swap(West)
												v = measure()
											else:
												swap(South)
												v = measure()
										ja = measure(North)
										if ja >= v:
											break
										swap(North)
										if not q2:
											wk.append(2)
											qn += 1
											q2 = True
								elif cx == 2:
									q2 = False
									if cur == 0:
										move(East)
									elif cur == 1:
										move(North)
									elif cur == 3:
										move(South)
									cur = 2
									while True:
										v = measure()
										ja = measure(South)
										jb = measure(West)
										if not ja <= v >= jb:
											if jb > ja:
												swap(West)
												if not q0:
													wk.append(0)
													qn += 1
													q0 = True
												v = measure()
											else:
												swap(South)
												if not q1:
													wk.append(1)
													qn += 1
													q1 = True
												v = measure()
										ja = measure(North)
										if ja >= v:
											break
										swap(North)
										if not q3:
											wk.append(3)
											qn += 1
											q3 = True
								else:
									q3 = False
									if cur == 0:
										move(East)
										move(North)
									elif cur == 1:
										move(North)
										move(North)
									elif cur == 2:
										move(North)
									cur = 3
									while True:
										v = measure()
										ja = measure(South)
										if ja > v:
											swap(South)
											if not q2:
												wk.append(2)
												qn += 1
												q2 = True
											v = measure()
										ja = measure(North)
										if ja >= v:
											break
										swap(North)
							if cur == 1:
								move(West)
								move(West)
								move(North)
								move(North)
								move(North)
								move(North)
								move(North)
							elif cur == 2:
								move(West)
								move(West)
								move(North)
								move(North)
								move(North)
								move(North)
							elif cur == 3:
								move(West)
								move(West)
								move(North)
								move(North)
								move(North)
							else:
								move(West)
								move(North)
								move(North)
								move(North)
								move(North)
							wk = [0, 1, 2, 3]
							cur = 0
							qi = 0
							qn = 4
							q0 = True
							q1 = True
							q2 = True
							q3 = True
							q0 = False
							while True:
								v = measure()
								ja = measure(South)
								while ja == None:
									ja = measure(South)
								jb = measure(West)
								while jb == None:
									jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(North)
								while ja == None:
									ja = measure(North)
								if ja >= v:
									break
								swap(North)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											v = measure()
										else:
											swap(South)
											v = measure()
									ja = measure(North)
									if ja >= v:
										break
									swap(North)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
								break
							q1 = False
							move(West)
							move(North)
							while True:
								v = measure()
								ja = measure(South)
								while ja == None:
									ja = measure(South)
								jb = measure(West)
								while jb == None:
									jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(East)
								while ja == None:
									ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											v = measure()
										else:
											swap(South)
											v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
								break
							q2 = False
							move(East)
							while True:
								v = measure()
								ja = measure(South)
								while ja == None:
									ja = measure(South)
								jb = measure(West)
								while jb == None:
									jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										if not q1:
											wk.append(1)
											qn += 1
											q1 = True
										v = measure()
									else:
										swap(South)
										if not q0:
											wk.append(0)
											qn += 1
											q0 = True
										v = measure()
								ja = measure(East)
								while ja == None:
									ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											if not q1:
												wk.append(1)
												qn += 1
												q1 = True
											v = measure()
										else:
											swap(South)
											if not q0:
												wk.append(0)
												qn += 1
												q0 = True
											v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
									if not q3:
										wk.append(3)
										qn += 1
										q3 = True
								break
							q3 = False
							move(East)
							while True:
								v = measure()
								ja = measure(West)
								while ja == None:
									ja = measure(West)
								if ja > v:
									swap(West)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
									v = measure()
								ja = measure(East)
								while ja == None:
									ja = measure(East)
								if ja >= v:
									break
								swap(East)
								while True:
									v = measure()
									ja = measure(West)
									if ja > v:
										swap(West)
										if not q2:
											wk.append(2)
											qn += 1
											q2 = True
										v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
								break
							cur = 3
							qi = 4
							while qi < qn:
								cx = wk[qi]
								qi += 1
								if cx == 0:
									q0 = False
									if cur == 1:
										move(East)
										move(South)
									elif cur == 2:
										move(South)
									elif cur == 3:
										move(West)
										move(South)
									cur = 0
									while True:
										v = measure()
										ja = measure(South)
										jb = measure(West)
										if not ja <= v >= jb:
											if jb > ja:
												swap(West)
												v = measure()
											else:
												swap(South)
												v = measure()
										ja = measure(North)
										if ja >= v:
											break
										swap(North)
										if not q2:
											wk.append(2)
											qn += 1
											q2 = True
								elif cx == 1:
									q1 = False
									if cur == 0:
										move(West)
										move(North)
									elif cur == 2:
										move(West)
									elif cur == 3:
										move(West)
										move(West)
									cur = 1
									while True:
										v = measure()
										ja = measure(South)
										jb = measure(West)
										if not ja <= v >= jb:
											if jb > ja:
												swap(West)
												v = measure()
											else:
												swap(South)
												v = measure()
										ja = measure(East)
										if ja >= v:
											break
										swap(East)
										if not q2:
											wk.append(2)
											qn += 1
											q2 = True
								elif cx == 2:
									q2 = False
									if cur == 0:
										move(North)
									elif cur == 1:
										move(East)
									elif cur == 3:
										move(West)
									cur = 2
									while True:
										v = measure()
										ja = measure(South)
										jb = measure(West)
										if not ja <= v >= jb:
											if jb > ja:
												swap(West)
												if not q1:
													wk.append(1)
													qn += 1
													q1 = True
												v = measure()
											else:
												swap(South)
												if not q0:
													wk.append(0)
													qn += 1
													q0 = True
												v = measure()
										ja = measure(East)
										if ja >= v:
											break
										swap(East)
										if not q3:
											wk.append(3)
											qn += 1
											q3 = True
								else:
									q3 = False
									if cur == 0:
										move(East)
										move(North)
									elif cur == 1:
										move(East)
										move(East)
									elif cur == 2:
										move(East)
									cur = 3
									while True:
										v = measure()
										ja = measure(West)
										if ja > v:
											swap(West)
											if not q2:
												wk.append(2)
												qn += 1
												q2 = True
											v = measure()
										ja = measure(East)
										if ja >= v:
											break
										swap(East)
							c = cur
							e = tl + 0.9345
							P = []
							if c == 0:
								if get_time() < e:
									move(South)
									if get_time() < e:
										move(South)
										if get_time() < e:
											move(South)
										else:
											P.append((South,))
									else:
										P.append((South, South,))
								else:
									P.append((South, South, South,))
							elif c == 1:
								if get_time() < e:
									move(East)
									if get_time() < e:
										move(South)
										if get_time() < e:
											move(South)
											if get_time() < e:
												move(South)
												if get_time() < e:
													move(South)
												else:
													P.append((South,))
											else:
												P.append((South, South,))
										else:
											P.append((South, South, South,))
									else:
										P.append((South, South, South, South,))
								else:
									P.append((East, South, South, South, South,))
							elif c == 2:
								if get_time() < e:
									move(South)
									if get_time() < e:
										move(South)
										if get_time() < e:
											move(South)
											if get_time() < e:
												move(South)
											else:
												P.append((South,))
										else:
											P.append((South, South,))
									else:
										P.append((South, South, South,))
								else:
									P.append((South, South, South, South,))
							elif c == 3:
								if get_time() < e:
									move(West)
									if get_time() < e:
										move(South)
										if get_time() < e:
											move(South)
											if get_time() < e:
												move(South)
												if get_time() < e:
													move(South)
												else:
													P.append((South,))
											else:
												P.append((South, South,))
										else:
											P.append((South, South, South,))
									else:
										P.append((South, South, South, South,))
								else:
									P.append((West, South, South, South, South,))
							wuT = tl + 0.9676
							while get_time() < wuT:
								pass
							if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
								if get_entity_type() == Entities.Cactus:
									harvest()
								else:
									use_item(Items.Water)
							else:
								use_item(Items.Water)
							for q in P:
								for d in q:
									move(d)
							hb = 0
							while num_items(Items.Cactus) <= 0:
								hb = get_time()
							plant(Entities.Cactus)
							move(West)
							plant(Entities.Cactus)
							if measure() > measure(East):
								swap(East)
							move(North)
							plant(Entities.Cactus)
							if measure() < measure(South):
								swap(South)
							move(West)
							plant(Entities.Cactus)
							if measure() > measure(East):
								swap(East)
							move(North)
							plant(Entities.Cactus)
							if measure() < measure(South):
								swap(South)
							move(West)
							plant(Entities.Cactus)
							if measure() > measure(East):
								swap(East)
							move(North)
							plant(Entities.Cactus)
							if measure() < measure(South):
								swap(South)
							move(West)
							plant(Entities.Cactus)
							if measure() > measure(East):
								swap(East)
							move(North)
							plant(Entities.Cactus)
							if measure() < measure(South):
								swap(South)
							move(West)
							plant(Entities.Cactus)
							move(West)
							plant(Entities.Cactus)
							move(West)
							plant(Entities.Cactus)
							swap(West)
							plant(Entities.Cactus)
							move(South)
							plant(Entities.Cactus)
							move(East)
							plant(Entities.Cactus)
							move(South)
							plant(Entities.Cactus)
							move(East)
							plant(Entities.Cactus)
							move(South)
							plant(Entities.Cactus)
							move(East)
							plant(Entities.Cactus)
							move(South)
							plant(Entities.Cactus)
							move(East)
							plant(Entities.Cactus)
							move(South)
							plant(Entities.Cactus)
							move(East)
							plant(Entities.Cactus)
							tl = get_time()
							if measure() < measure(West):
								swap(West)
							xcas(South, 0)
							move(West)
							if measure() > measure(North):
								swap(North)
							move(North)
							if measure() < measure(West):
								swap(West)
							move(West)
							if measure() > measure(North):
								swap(North)
							move(North)
							if measure() < measure(West):
								swap(West)
							move(West)
							if measure() > measure(North):
								swap(North)
							move(North)
							if measure() < measure(West):
								swap(West)
							move(West)
							move(North)
							wk = [0, 1, 2, 3]
							cur = 0
							qi = 0
							qn = 4
							q0 = True
							q1 = True
							q2 = True
							q3 = True
							q0 = False
							while True:
								v = measure()
								ja = measure(South)
								while ja == None:
									ja = measure(South)
								jb = measure(West)
								while jb == None:
									jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(North)
								while ja == None:
									ja = measure(North)
								if ja >= v:
									break
								swap(North)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											v = measure()
										else:
											swap(South)
											v = measure()
									ja = measure(North)
									if ja >= v:
										break
									swap(North)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
								break
							q1 = False
							move(West)
							move(North)
							while True:
								v = measure()
								ja = measure(South)
								while ja == None:
									ja = measure(South)
								jb = measure(West)
								while jb == None:
									jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(East)
								while ja == None:
									ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											v = measure()
										else:
											swap(South)
											v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
								break
							q2 = False
							move(East)
							while True:
								v = measure()
								ja = measure(South)
								while ja == None:
									ja = measure(South)
								jb = measure(West)
								while jb == None:
									jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										if not q1:
											wk.append(1)
											qn += 1
											q1 = True
										v = measure()
									else:
										swap(South)
										if not q0:
											wk.append(0)
											qn += 1
											q0 = True
										v = measure()
								ja = measure(East)
								while ja == None:
									ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											if not q1:
												wk.append(1)
												qn += 1
												q1 = True
											v = measure()
										else:
											swap(South)
											if not q0:
												wk.append(0)
												qn += 1
												q0 = True
											v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
									if not q3:
										wk.append(3)
										qn += 1
										q3 = True
								break
							q3 = False
							move(East)
							while True:
								v = measure()
								ja = measure(West)
								while ja == None:
									ja = measure(West)
								if ja > v:
									swap(West)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
									v = measure()
								ja = measure(East)
								while ja == None:
									ja = measure(East)
								if ja >= v:
									break
								swap(East)
								while True:
									v = measure()
									ja = measure(West)
									if ja > v:
										swap(West)
										if not q2:
											wk.append(2)
											qn += 1
											q2 = True
										v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
								break
							cur = 3
							qi = 4
							while qi < qn:
								cx = wk[qi]
								qi += 1
								if cx == 0:
									q0 = False
									if cur == 1:
										move(East)
										move(South)
									elif cur == 2:
										move(South)
									elif cur == 3:
										move(West)
										move(South)
									cur = 0
									while True:
										v = measure()
										ja = measure(South)
										jb = measure(West)
										if not ja <= v >= jb:
											if jb > ja:
												swap(West)
												v = measure()
											else:
												swap(South)
												v = measure()
										ja = measure(North)
										if ja >= v:
											break
										swap(North)
										if not q2:
											wk.append(2)
											qn += 1
											q2 = True
								elif cx == 1:
									q1 = False
									if cur == 0:
										move(West)
										move(North)
									elif cur == 2:
										move(West)
									elif cur == 3:
										move(West)
										move(West)
									cur = 1
									while True:
										v = measure()
										ja = measure(South)
										jb = measure(West)
										if not ja <= v >= jb:
											if jb > ja:
												swap(West)
												v = measure()
											else:
												swap(South)
												v = measure()
										ja = measure(East)
										if ja >= v:
											break
										swap(East)
										if not q2:
											wk.append(2)
											qn += 1
											q2 = True
								elif cx == 2:
									q2 = False
									if cur == 0:
										move(North)
									elif cur == 1:
										move(East)
									elif cur == 3:
										move(West)
									cur = 2
									while True:
										v = measure()
										ja = measure(South)
										jb = measure(West)
										if not ja <= v >= jb:
											if jb > ja:
												swap(West)
												if not q1:
													wk.append(1)
													qn += 1
													q1 = True
												v = measure()
											else:
												swap(South)
												if not q0:
													wk.append(0)
													qn += 1
													q0 = True
												v = measure()
										ja = measure(East)
										if ja >= v:
											break
										swap(East)
										if not q3:
											wk.append(3)
											qn += 1
											q3 = True
								else:
									q3 = False
									if cur == 0:
										move(East)
										move(North)
									elif cur == 1:
										move(East)
										move(East)
									elif cur == 2:
										move(East)
									cur = 3
									while True:
										v = measure()
										ja = measure(West)
										if ja > v:
											swap(West)
											if not q2:
												wk.append(2)
												qn += 1
												q2 = True
											v = measure()
										ja = measure(East)
										if ja >= v:
											break
										swap(East)
							if tl + 0.9676 > hb + 2.6:
								wuT = tl + 0.9676
								while get_time() < wuT:
									pass
						spawn_drone(w31)
						move(West)
						move(West)
						move(West)
						move(West)
						move(South)
						move(South)
						till()
						plant(Entities.Cactus)
						move(North)
						till()
						plant(Entities.Cactus)
						if measure() < measure(South):
							swap(South)
						move(West)
						till()
						plant(Entities.Cactus)
						if measure() > measure(East):
							swap(East)
						move(North)
						till()
						plant(Entities.Cactus)
						if measure() < measure(South):
							swap(South)
						move(West)
						till()
						plant(Entities.Cactus)
						if measure() > measure(East):
							swap(East)
						move(North)
						till()
						plant(Entities.Cactus)
						if measure() < measure(South):
							swap(South)
						move(West)
						till()
						plant(Entities.Cactus)
						move(West)
						till()
						plant(Entities.Cactus)
						move(West)
						till()
						plant(Entities.Cactus)
						move(South)
						till()
						plant(Entities.Cactus)
						move(East)
						till()
						plant(Entities.Cactus)
						move(South)
						till()
						plant(Entities.Cactus)
						move(East)
						till()
						plant(Entities.Cactus)
						if measure() < measure(West):
							swap(West)
						move(South)
						till()
						plant(Entities.Cactus)
						if measure() > measure(North):
							swap(North)
						move(East)
						till()
						plant(Entities.Cactus)
						if measure() < measure(West):
							swap(West)
						move(South)
						till()
						plant(Entities.Cactus)
						if measure() > measure(North):
							swap(North)
						move(East)
						till()
						plant(Entities.Cactus)
						if measure() < measure(West):
							swap(West)
						move(South)
						till()
						plant(Entities.Cactus)
						if measure() > measure(North):
							swap(North)
						move(East)
						till()
						plant(Entities.Cactus)
						if measure() < measure(West):
							swap(West)
						move(South)
						till()
						plant(Entities.Cactus)
						if measure() > measure(North):
							swap(North)
						move(East)
						till()
						plant(Entities.Cactus)
						if measure() < measure(West):
							swap(West)
						move(South)
						till()
						plant(Entities.Cactus)
						if measure() > measure(North):
							swap(North)
						move(East)
						till()
						plant(Entities.Cactus)
						if measure() < measure(West):
							swap(West)
						move(South)
						till()
						plant(Entities.Cactus)
						if measure() > measure(North):
							swap(North)
						tl = get_time()
						move(West)
						move(West)
						move(West)
						move(West)
						move(West)
						move(West)
						move(North)
						move(North)
						move(North)
						move(North)
						move(North)
						move(North)
						move(North)
						wk = [0, 1, 2, 3]
						cur = 0
						qi = 0
						qn = 4
						q0 = True
						q1 = True
						q2 = True
						q3 = True
						q0 = False
						while True:
							v = measure()
							ja = measure(South)
							while ja == None:
								ja = measure(South)
							jb = measure(West)
							while jb == None:
								jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(North)
							while ja == None:
								ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(North)
								if ja >= v:
									break
								swap(North)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
							break
						q1 = False
						move(West)
						move(North)
						while True:
							v = measure()
							ja = measure(South)
							while ja == None:
								ja = measure(South)
							jb = measure(West)
							while jb == None:
								jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(East)
							while ja == None:
								ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
							break
						q2 = False
						move(East)
						while True:
							v = measure()
							ja = measure(South)
							while ja == None:
								ja = measure(South)
							jb = measure(West)
							while jb == None:
								jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									if not q1:
										wk.append(1)
										qn += 1
										q1 = True
									v = measure()
								else:
									swap(South)
									if not q0:
										wk.append(0)
										qn += 1
										q0 = True
									v = measure()
							ja = measure(East)
							while ja == None:
								ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										if not q1:
											wk.append(1)
											qn += 1
											q1 = True
										v = measure()
									else:
										swap(South)
										if not q0:
											wk.append(0)
											qn += 1
											q0 = True
										v = measure()
								ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
							break
						q3 = False
						move(East)
						while True:
							v = measure()
							ja = measure(West)
							while ja == None:
								ja = measure(West)
							if ja > v:
								swap(West)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								v = measure()
							ja = measure(East)
							while ja == None:
								ja = measure(East)
							if ja >= v:
								break
							swap(East)
							while True:
								v = measure()
								ja = measure(West)
								if ja > v:
									swap(West)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
									v = measure()
								ja = measure(East)
								if ja >= v:
									break
								swap(East)
							break
						cur = 3
						qi = 4
						while qi < qn:
							cx = wk[qi]
							qi += 1
							if cx == 0:
								q0 = False
								if cur == 1:
									move(East)
									move(South)
								elif cur == 2:
									move(South)
								elif cur == 3:
									move(West)
									move(South)
								cur = 0
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											v = measure()
										else:
											swap(South)
											v = measure()
									ja = measure(North)
									if ja >= v:
										break
									swap(North)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
							elif cx == 1:
								q1 = False
								if cur == 0:
									move(West)
									move(North)
								elif cur == 2:
									move(West)
								elif cur == 3:
									move(West)
									move(West)
								cur = 1
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											v = measure()
										else:
											swap(South)
											v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
							elif cx == 2:
								q2 = False
								if cur == 0:
									move(North)
								elif cur == 1:
									move(East)
								elif cur == 3:
									move(West)
								cur = 2
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											if not q1:
												wk.append(1)
												qn += 1
												q1 = True
											v = measure()
										else:
											swap(South)
											if not q0:
												wk.append(0)
												qn += 1
												q0 = True
											v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
									if not q3:
										wk.append(3)
										qn += 1
										q3 = True
							else:
								q3 = False
								if cur == 0:
									move(East)
									move(North)
								elif cur == 1:
									move(East)
									move(East)
								elif cur == 2:
									move(East)
								cur = 3
								while True:
									v = measure()
									ja = measure(West)
									if ja > v:
										swap(West)
										if not q2:
											wk.append(2)
											qn += 1
											q2 = True
										v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
						c = cur
						e = tl + 0.9345
						P = []
						if c == 0:
							if get_time() < e:
								move(East)
								if get_time() < e:
									move(East)
									if get_time() < e:
										move(South)
										if get_time() < e:
											move(South)
											if get_time() < e:
												move(South)
												if get_time() < e:
													move(South)
													if get_time() < e:
														move(South)
														if get_time() < e:
															move(South)
														else:
															P.append((South,))
													else:
														P.append((South, South,))
												else:
													P.append((South, South, South,))
											else:
												P.append((South, South, South, South,))
										else:
											P.append((South, South, South, South, South,))
									else:
										P.append((South, South, South, South, South, South,))
								else:
									P.append((East, South, South, South, South, South, South,))
							else:
								P.append((East, East, South, South, South, South, South, South,))
						elif c == 1:
							if get_time() < e:
								move(East)
								if get_time() < e:
									move(East)
									if get_time() < e:
										move(East)
										if get_time() < e:
											move(South)
											if get_time() < e:
												move(South)
												if get_time() < e:
													move(South)
													if get_time() < e:
														move(South)
														if get_time() < e:
															move(South)
															if get_time() < e:
																move(South)
																if get_time() < e:
																	move(South)
																else:
																	P.append((South,))
															else:
																P.append((South, South,))
														else:
															P.append((South, South, South,))
													else:
														P.append((South, South, South, South,))
												else:
													P.append((South, South, South, South, South,))
											else:
												P.append((South, South, South, South, South, South,))
										else:
											P.append((South, South, South, South, South, South, South,))
									else:
										P.append((East, South, South, South, South, South, South, South,))
								else:
									P.append((East, East, South, South, South, South, South, South, South,))
							else:
								P.append((East, East, East, South, South, South, South, South, South, South,))
						elif c == 2:
							if get_time() < e:
								move(East)
								if get_time() < e:
									move(East)
									if get_time() < e:
										move(South)
										if get_time() < e:
											move(South)
											if get_time() < e:
												move(South)
												if get_time() < e:
													move(South)
													if get_time() < e:
														move(South)
														if get_time() < e:
															move(South)
															if get_time() < e:
																move(South)
															else:
																P.append((South,))
														else:
															P.append((South, South,))
													else:
														P.append((South, South, South,))
												else:
													P.append((South, South, South, South,))
											else:
												P.append((South, South, South, South, South,))
										else:
											P.append((South, South, South, South, South, South,))
									else:
										P.append((South, South, South, South, South, South, South,))
								else:
									P.append((East, South, South, South, South, South, South, South,))
							else:
								P.append((East, East, South, South, South, South, South, South, South,))
						elif c == 3:
							if get_time() < e:
								move(East)
								if get_time() < e:
									move(South)
									if get_time() < e:
										move(South)
										if get_time() < e:
											move(South)
											if get_time() < e:
												move(South)
												if get_time() < e:
													move(South)
													if get_time() < e:
														move(South)
														if get_time() < e:
															move(South)
														else:
															P.append((South,))
													else:
														P.append((South, South,))
												else:
													P.append((South, South, South,))
											else:
												P.append((South, South, South, South,))
										else:
											P.append((South, South, South, South, South,))
									else:
										P.append((South, South, South, South, South, South,))
								else:
									P.append((South, South, South, South, South, South, South,))
							else:
								P.append((East, South, South, South, South, South, South, South,))
						wuT = tl + 0.9676
						while get_time() < wuT:
							pass
						if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
							if get_entity_type() == Entities.Cactus:
								harvest()
							else:
								use_item(Items.Water)
						else:
							use_item(Items.Water)
						for q in P:
							for d in q:
								move(d)
						hb = 0
						while num_items(Items.Cactus) <= 0:
							hb = get_time()
						plant(Entities.Cactus)
						move(North)
						plant(Entities.Cactus)
						if measure() < measure(South):
							swap(South)
						move(West)
						plant(Entities.Cactus)
						if measure() > measure(East):
							swap(East)
						move(North)
						plant(Entities.Cactus)
						if measure() < measure(South):
							swap(South)
						move(West)
						plant(Entities.Cactus)
						if measure() > measure(East):
							swap(East)
						move(North)
						plant(Entities.Cactus)
						if measure() < measure(South):
							swap(South)
						move(West)
						plant(Entities.Cactus)
						if measure() > measure(East):
							swap(East)
						move(North)
						plant(Entities.Cactus)
						if measure() < measure(South):
							swap(South)
						move(West)
						plant(Entities.Cactus)
						move(North)
						plant(Entities.Cactus)
						move(West)
						plant(Entities.Cactus)
						move(North)
						plant(Entities.Cactus)
						move(West)
						plant(Entities.Cactus)
						move(North)
						plant(Entities.Cactus)
						move(West)
						plant(Entities.Cactus)
						move(West)
						plant(Entities.Cactus)
						move(West)
						plant(Entities.Cactus)
						swap(West)
						plant(Entities.Cactus)
						move(South)
						plant(Entities.Cactus)
						move(East)
						plant(Entities.Cactus)
						move(South)
						tw = 0
						if get_time() > 6.0:
							if use_item(Items.Water, 4):
								tw = 1
						plant(Entities.Cactus)
						tl = get_time()
						if tw:
							tl = tl - 0.0988
						xcas(East, 1)
						move(North)
						wk = [0, 1, 2, 3]
						cur = 0
						qi = 0
						qn = 4
						q0 = True
						q1 = True
						q2 = True
						q3 = True
						q0 = False
						while True:
							v = measure()
							ja = measure(South)
							while ja == None:
								ja = measure(South)
							jb = measure(West)
							while jb == None:
								jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(North)
							while ja == None:
								ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(North)
								if ja >= v:
									break
								swap(North)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
							break
						q1 = False
						move(West)
						move(North)
						while True:
							v = measure()
							ja = measure(South)
							while ja == None:
								ja = measure(South)
							jb = measure(West)
							while jb == None:
								jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(East)
							while ja == None:
								ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
							break
						q2 = False
						move(East)
						while True:
							v = measure()
							ja = measure(South)
							while ja == None:
								ja = measure(South)
							jb = measure(West)
							while jb == None:
								jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									if not q1:
										wk.append(1)
										qn += 1
										q1 = True
									v = measure()
								else:
									swap(South)
									if not q0:
										wk.append(0)
										qn += 1
										q0 = True
									v = measure()
							ja = measure(East)
							while ja == None:
								ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										if not q1:
											wk.append(1)
											qn += 1
											q1 = True
										v = measure()
									else:
										swap(South)
										if not q0:
											wk.append(0)
											qn += 1
											q0 = True
										v = measure()
								ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
							break
						q3 = False
						move(East)
						while True:
							v = measure()
							ja = measure(West)
							while ja == None:
								ja = measure(West)
							if ja > v:
								swap(West)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								v = measure()
							ja = measure(East)
							while ja == None:
								ja = measure(East)
							if ja >= v:
								break
							swap(East)
							while True:
								v = measure()
								ja = measure(West)
								if ja > v:
									swap(West)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
									v = measure()
								ja = measure(East)
								if ja >= v:
									break
								swap(East)
							break
						cur = 3
						qi = 4
						while qi < qn:
							cx = wk[qi]
							qi += 1
							if cx == 0:
								q0 = False
								if cur == 1:
									move(East)
									move(South)
								elif cur == 2:
									move(South)
								elif cur == 3:
									move(West)
									move(South)
								cur = 0
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											v = measure()
										else:
											swap(South)
											v = measure()
									ja = measure(North)
									if ja >= v:
										break
									swap(North)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
							elif cx == 1:
								q1 = False
								if cur == 0:
									move(West)
									move(North)
								elif cur == 2:
									move(West)
								elif cur == 3:
									move(West)
									move(West)
								cur = 1
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											v = measure()
										else:
											swap(South)
											v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
							elif cx == 2:
								q2 = False
								if cur == 0:
									move(North)
								elif cur == 1:
									move(East)
								elif cur == 3:
									move(West)
								cur = 2
								while True:
									v = measure()
									ja = measure(South)
									jb = measure(West)
									if not ja <= v >= jb:
										if jb > ja:
											swap(West)
											if not q1:
												wk.append(1)
												qn += 1
												q1 = True
											v = measure()
										else:
											swap(South)
											if not q0:
												wk.append(0)
												qn += 1
												q0 = True
											v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
									if not q3:
										wk.append(3)
										qn += 1
										q3 = True
							else:
								q3 = False
								if cur == 0:
									move(East)
									move(North)
								elif cur == 1:
									move(East)
									move(East)
								elif cur == 2:
									move(East)
								cur = 3
								while True:
									v = measure()
									ja = measure(West)
									if ja > v:
										swap(West)
										if not q2:
											wk.append(2)
											qn += 1
											q2 = True
										v = measure()
									ja = measure(East)
									if ja >= v:
										break
									swap(East)
						if cur == 1:
							move(East)
							move(East)
							move(East)
						elif cur == 2:
							move(East)
							move(East)
						elif cur == 3:
							move(East)
						else:
							move(East)
							move(East)
							move(North)
						if measure() < measure(South):
							swap(South)
						move(South)
						if measure() > measure(East):
							swap(East)
						move(East)
						if measure() < measure(South):
							swap(South)
						move(South)
						if measure() > measure(East):
							swap(East)
						move(East)
						if measure() < measure(South):
							swap(South)
						move(South)
						if measure() > measure(East):
							swap(East)
						if tl + 0.9676 > hb + 2.6:
							wuT = tl + 0.9676
							while get_time() < wuT:
								pass
					spawn_drone(w30)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(South)
					move(South)
					move(South)
					till()
					plant(Entities.Cactus)
					xcas(North, 1)
					move(East)
					till()
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					till()
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					till()
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					till()
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					till()
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					till()
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					till()
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					till()
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					till()
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					till()
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					till()
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					till()
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					till()
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					till()
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(East)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(North)
					move(North)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					move(West)
					till()
					plant(Entities.Cactus)
					if measure() > measure(East):
						swap(East)
					move(North)
					till()
					plant(Entities.Cactus)
					if measure() < measure(South):
						swap(South)
					tl = get_time()
					xcasw(West, 0)
					move(South)
					move(South)
					move(South)
					wk = [0, 1, 2, 3]
					cur = 0
					qi = 0
					qn = 4
					q0 = True
					q1 = True
					q2 = True
					q3 = True
					q0 = False
					while True:
						v = measure()
						ja = measure(South)
						while ja == None:
							ja = measure(South)
						jb = measure(West)
						while jb == None:
							jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						while ja == None:
							ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
						break
					q1 = False
					move(East)
					move(South)
					while True:
						v = measure()
						ja = measure(South)
						while ja == None:
							ja = measure(South)
						jb = measure(West)
						while jb == None:
							jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						while ja == None:
							ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
						break
					q2 = False
					move(North)
					while True:
						v = measure()
						ja = measure(South)
						while ja == None:
							ja = measure(South)
						jb = measure(West)
						while jb == None:
							jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
							else:
								swap(South)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
						ja = measure(North)
						while ja == None:
							ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									if not q0:
										wk.append(0)
										qn += 1
										q0 = True
									v = measure()
								else:
									swap(South)
									if not q1:
										wk.append(1)
										qn += 1
										q1 = True
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
						break
					q3 = False
					move(North)
					while True:
						v = measure()
						ja = measure(South)
						while ja == None:
							ja = measure(South)
						if ja > v:
							swap(South)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(North)
						while ja == None:
							ja = measure(North)
						if ja >= v:
							break
						swap(North)
						while True:
							v = measure()
							ja = measure(South)
							if ja > v:
								swap(South)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
						break
					cur = 3
					qi = 4
					while qi < qn:
						cx = wk[qi]
						qi += 1
						if cx == 0:
							q0 = False
							if cur == 1:
								move(West)
								move(North)
							elif cur == 2:
								move(West)
							elif cur == 3:
								move(West)
								move(South)
							cur = 0
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
						elif cx == 1:
							q1 = False
							if cur == 0:
								move(East)
								move(South)
							elif cur == 2:
								move(South)
							elif cur == 3:
								move(South)
								move(South)
							cur = 1
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(North)
								if ja >= v:
									break
								swap(North)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
						elif cx == 2:
							q2 = False
							if cur == 0:
								move(East)
							elif cur == 1:
								move(North)
							elif cur == 3:
								move(South)
							cur = 2
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										if not q0:
											wk.append(0)
											qn += 1
											q0 = True
										v = measure()
									else:
										swap(South)
										if not q1:
											wk.append(1)
											qn += 1
											q1 = True
										v = measure()
								ja = measure(North)
								if ja >= v:
									break
								swap(North)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
						else:
							q3 = False
							if cur == 0:
								move(East)
								move(North)
							elif cur == 1:
								move(North)
								move(North)
							elif cur == 2:
								move(North)
							cur = 3
							while True:
								v = measure()
								ja = measure(South)
								if ja > v:
									swap(South)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
									v = measure()
								ja = measure(North)
								if ja >= v:
									break
								swap(North)
					c = cur
					e = tl + 0.9345
					P = []
					if c == 0:
						if get_time() < e:
							move(West)
							if get_time() < e:
								move(West)
								if get_time() < e:
									move(West)
									if get_time() < e:
										move(North)
										if get_time() < e:
											move(North)
											if get_time() < e:
												move(North)
												if get_time() < e:
													move(North)
													if get_time() < e:
														move(North)
													else:
														P.append((North,))
												else:
													P.append((North, North,))
											else:
												P.append((North, North, North,))
										else:
											P.append((North, North, North, North,))
									else:
										P.append((North, North, North, North, North,))
								else:
									P.append((West, North, North, North, North, North,))
							else:
								P.append((West, West, North, North, North, North, North,))
						else:
							P.append((West, West, West, North, North, North, North, North,))
					elif c == 1:
						if get_time() < e:
							move(West)
							if get_time() < e:
								move(West)
								if get_time() < e:
									move(West)
									if get_time() < e:
										move(West)
										if get_time() < e:
											move(North)
											if get_time() < e:
												move(North)
												if get_time() < e:
													move(North)
													if get_time() < e:
														move(North)
														if get_time() < e:
															move(North)
															if get_time() < e:
																move(North)
															else:
																P.append((North,))
														else:
															P.append((North, North,))
													else:
														P.append((North, North, North,))
												else:
													P.append((North, North, North, North,))
											else:
												P.append((North, North, North, North, North,))
										else:
											P.append((North, North, North, North, North, North,))
									else:
										P.append((West, North, North, North, North, North, North,))
								else:
									P.append((West, West, North, North, North, North, North, North,))
							else:
								P.append((West, West, West, North, North, North, North, North, North,))
						else:
							P.append((West, West, West, West, North, North, North, North, North, North,))
					elif c == 2:
						if get_time() < e:
							move(West)
							if get_time() < e:
								move(West)
								if get_time() < e:
									move(West)
									if get_time() < e:
										move(West)
										if get_time() < e:
											move(North)
											if get_time() < e:
												move(North)
												if get_time() < e:
													move(North)
													if get_time() < e:
														move(North)
														if get_time() < e:
															move(North)
														else:
															P.append((North,))
													else:
														P.append((North, North,))
												else:
													P.append((North, North, North,))
											else:
												P.append((North, North, North, North,))
										else:
											P.append((North, North, North, North, North,))
									else:
										P.append((West, North, North, North, North, North,))
								else:
									P.append((West, West, North, North, North, North, North,))
							else:
								P.append((West, West, West, North, North, North, North, North,))
						else:
							P.append((West, West, West, West, North, North, North, North, North,))
					elif c == 3:
						if get_time() < e:
							move(West)
							if get_time() < e:
								move(West)
								if get_time() < e:
									move(West)
									if get_time() < e:
										move(West)
										if get_time() < e:
											move(North)
											if get_time() < e:
												move(North)
												if get_time() < e:
													move(North)
													if get_time() < e:
														move(North)
													else:
														P.append((North,))
												else:
													P.append((North, North,))
											else:
												P.append((North, North, North,))
										else:
											P.append((North, North, North, North,))
									else:
										P.append((West, North, North, North, North,))
								else:
									P.append((West, West, North, North, North, North,))
							else:
								P.append((West, West, West, North, North, North, North,))
						else:
							P.append((West, West, West, West, North, North, North, North,))
					wuT = tl + 0.9676
					while get_time() < wuT:
						pass
					if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
						if get_entity_type() == Entities.Cactus:
							harvest()
						else:
							use_item(Items.Water)
					else:
						use_item(Items.Water)
					for q in P:
						for d in q:
							move(d)
					hb = 0
					while num_items(Items.Cactus) <= 0:
						hb = get_time()
					plant(Entities.Cactus)
					move(East)
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					plant(Entities.Cactus)
					swap(South)
					plant(Entities.Cactus)
					move(South)
					move(South)
					plant(Entities.Cactus)
					swap(South)
					plant(Entities.Cactus)
					move(West)
					plant(Entities.Cactus)
					move(North)
					plant(Entities.Cactus)
					move(West)
					plant(Entities.Cactus)
					move(North)
					plant(Entities.Cactus)
					move(West)
					plant(Entities.Cactus)
					move(North)
					plant(Entities.Cactus)
					move(West)
					plant(Entities.Cactus)
					move(North)
					plant(Entities.Cactus)
					move(West)
					plant(Entities.Cactus)
					move(North)
					if use_item(Items.Water, 4):
						plant(Entities.Cactus)
						tw = get_time() - 0.0988
					else:
						plant(Entities.Cactus)
						tw = 0
					tl = get_time()
					if tw:
						tl = tw
					if measure() < measure(South):
						swap(South)
					xcas(West, 0)
					move(South)
					if measure() > measure(East):
						swap(East)
					move(East)
					if measure() < measure(South):
						swap(South)
					move(South)
					if measure() > measure(East):
						swap(East)
					move(East)
					if measure() < measure(South):
						swap(South)
					move(South)
					if measure() > measure(East):
						swap(East)
					move(East)
					if measure() < measure(South):
						swap(South)
					move(East)
					move(South)
					wk = [0, 1, 2, 3]
					cur = 0
					qi = 0
					qn = 4
					q0 = True
					q1 = True
					q2 = True
					q3 = True
					q0 = False
					while True:
						v = measure()
						ja = measure(South)
						while ja == None:
							ja = measure(South)
						jb = measure(West)
						while jb == None:
							jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						while ja == None:
							ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
						break
					q1 = False
					move(East)
					move(South)
					while True:
						v = measure()
						ja = measure(South)
						while ja == None:
							ja = measure(South)
						jb = measure(West)
						while jb == None:
							jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						while ja == None:
							ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
						break
					q2 = False
					move(North)
					while True:
						v = measure()
						ja = measure(South)
						while ja == None:
							ja = measure(South)
						jb = measure(West)
						while jb == None:
							jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
							else:
								swap(South)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
						ja = measure(North)
						while ja == None:
							ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									if not q0:
										wk.append(0)
										qn += 1
										q0 = True
									v = measure()
								else:
									swap(South)
									if not q1:
										wk.append(1)
										qn += 1
										q1 = True
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
						break
					q3 = False
					move(North)
					while True:
						v = measure()
						ja = measure(South)
						while ja == None:
							ja = measure(South)
						if ja > v:
							swap(South)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(North)
						while ja == None:
							ja = measure(North)
						if ja >= v:
							break
						swap(North)
						while True:
							v = measure()
							ja = measure(South)
							if ja > v:
								swap(South)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
						break
					cur = 3
					qi = 4
					while qi < qn:
						cx = wk[qi]
						qi += 1
						if cx == 0:
							q0 = False
							if cur == 1:
								move(West)
								move(North)
							elif cur == 2:
								move(West)
							elif cur == 3:
								move(West)
								move(South)
							cur = 0
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
						elif cx == 1:
							q1 = False
							if cur == 0:
								move(East)
								move(South)
							elif cur == 2:
								move(South)
							elif cur == 3:
								move(South)
								move(South)
							cur = 1
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(North)
								if ja >= v:
									break
								swap(North)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
						elif cx == 2:
							q2 = False
							if cur == 0:
								move(East)
							elif cur == 1:
								move(North)
							elif cur == 3:
								move(South)
							cur = 2
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										if not q0:
											wk.append(0)
											qn += 1
											q0 = True
										v = measure()
									else:
										swap(South)
										if not q1:
											wk.append(1)
											qn += 1
											q1 = True
										v = measure()
								ja = measure(North)
								if ja >= v:
									break
								swap(North)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
						else:
							q3 = False
							if cur == 0:
								move(East)
								move(North)
							elif cur == 1:
								move(North)
								move(North)
							elif cur == 2:
								move(North)
							cur = 3
							while True:
								v = measure()
								ja = measure(South)
								if ja > v:
									swap(South)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
									v = measure()
								ja = measure(North)
								if ja >= v:
									break
								swap(North)
					if tl + 0.9676 > hb + 2.6:
						wuT = tl + 0.9676
						while get_time() < wuT:
							pass
				spawn_drone(w29)
				def w28():
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(South)
					move(South)
					till()
					plant(Entities.Cactus)
					move(West)
					till()
					plant(Entities.Cactus)
					if measure() > measure(East):
						swap(East)
					move(North)
					till()
					plant(Entities.Cactus)
					if measure() < measure(South):
						swap(South)
					move(West)
					till()
					plant(Entities.Cactus)
					if measure() > measure(East):
						swap(East)
					move(North)
					till()
					plant(Entities.Cactus)
					if measure() < measure(South):
						swap(South)
					move(West)
					till()
					plant(Entities.Cactus)
					if measure() > measure(East):
						swap(East)
					move(North)
					till()
					plant(Entities.Cactus)
					if measure() < measure(South):
						swap(South)
					move(West)
					till()
					plant(Entities.Cactus)
					move(West)
					till()
					plant(Entities.Cactus)
					move(West)
					move(West)
					till()
					plant(Entities.Cactus)
					move(East)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(East)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(East)
					till()
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					till()
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					till()
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					till()
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					till()
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					till()
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					till()
					plant(Entities.Cactus)
					if measure() < measure(West):
						swap(West)
					move(South)
					till()
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					tl = get_time()
					if measure() > measure(North):
						swap(North)
					xcas(East, 1)
					move(North)
					if measure() < measure(West):
						swap(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(North)
					move(North)
					move(North)
					move(North)
					move(North)
					wk = [0, 1, 2, 3]
					cur = 0
					qi = 0
					qn = 4
					q0 = True
					q1 = True
					q2 = True
					q3 = True
					q0 = False
					while True:
						v = measure()
						ja = measure(South)
						while ja == None:
							ja = measure(South)
						jb = measure(West)
						while jb == None:
							jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						while ja == None:
							ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
						break
					q1 = False
					move(West)
					move(North)
					while True:
						v = measure()
						ja = measure(South)
						while ja == None:
							ja = measure(South)
						jb = measure(West)
						while jb == None:
							jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						while ja == None:
							ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
						break
					q2 = False
					move(East)
					while True:
						v = measure()
						ja = measure(South)
						while ja == None:
							ja = measure(South)
						jb = measure(West)
						while jb == None:
							jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
							else:
								swap(South)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
						ja = measure(East)
						while ja == None:
							ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									if not q1:
										wk.append(1)
										qn += 1
										q1 = True
									v = measure()
								else:
									swap(South)
									if not q0:
										wk.append(0)
										qn += 1
										q0 = True
									v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
						break
					q3 = False
					move(East)
					while True:
						v = measure()
						ja = measure(West)
						while ja == None:
							ja = measure(West)
						if ja > v:
							swap(West)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(East)
						while ja == None:
							ja = measure(East)
						if ja >= v:
							break
						swap(East)
						while True:
							v = measure()
							ja = measure(West)
							if ja > v:
								swap(West)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
						break
					cur = 3
					qi = 4
					while qi < qn:
						cx = wk[qi]
						qi += 1
						if cx == 0:
							q0 = False
							if cur == 1:
								move(East)
								move(South)
							elif cur == 2:
								move(South)
							elif cur == 3:
								move(West)
								move(South)
							cur = 0
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(North)
								if ja >= v:
									break
								swap(North)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
						elif cx == 1:
							q1 = False
							if cur == 0:
								move(West)
								move(North)
							elif cur == 2:
								move(West)
							elif cur == 3:
								move(West)
								move(West)
							cur = 1
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										v = measure()
									else:
										swap(South)
										v = measure()
								ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
						elif cx == 2:
							q2 = False
							if cur == 0:
								move(North)
							elif cur == 1:
								move(East)
							elif cur == 3:
								move(West)
							cur = 2
							while True:
								v = measure()
								ja = measure(South)
								jb = measure(West)
								if not ja <= v >= jb:
									if jb > ja:
										swap(West)
										if not q1:
											wk.append(1)
											qn += 1
											q1 = True
										v = measure()
									else:
										swap(South)
										if not q0:
											wk.append(0)
											qn += 1
											q0 = True
										v = measure()
								ja = measure(East)
								if ja >= v:
									break
								swap(East)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
						else:
							q3 = False
							if cur == 0:
								move(East)
								move(North)
							elif cur == 1:
								move(East)
								move(East)
							elif cur == 2:
								move(East)
							cur = 3
							while True:
								v = measure()
								ja = measure(West)
								if ja > v:
									swap(West)
									if not q2:
										wk.append(2)
										qn += 1
										q2 = True
									v = measure()
								ja = measure(East)
								if ja >= v:
									break
								swap(East)
					c = cur
					e = tl + 0.9345
					P = []
					if c == 0:
						if get_time() < e:
							move(East)
							if get_time() < e:
								move(South)
							else:
								P.append((South,))
						else:
							P.append((East, South,))
					elif c == 1:
						if get_time() < e:
							move(East)
							if get_time() < e:
								move(East)
								if get_time() < e:
									move(South)
									if get_time() < e:
										move(South)
									else:
										P.append((South,))
								else:
									P.append((South, South,))
							else:
								P.append((East, South, South,))
						else:
							P.append((East, East, South, South,))
					elif c == 2:
						if get_time() < e:
							move(East)
							if get_time() < e:
								move(South)
								if get_time() < e:
									move(South)
								else:
									P.append((South,))
							else:
								P.append((South, South,))
						else:
							P.append((East, South, South,))
					elif c == 3:
						if get_time() < e:
							move(South)
							if get_time() < e:
								move(South)
							else:
								P.append((South,))
						else:
							P.append((South, South,))
					wuT = tl + 0.9676
					while get_time() < wuT:
						pass
					if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
						if get_entity_type() == Entities.Cactus:
							harvest()
						else:
							use_item(Items.Water)
					else:
						use_item(Items.Water)
					for q in P:
						for d in q:
							move(d)
					hb = 0
					while num_items(Items.Cactus) <= 0:
						hb = get_time()
					plant(Entities.Cactus)
					move(South)
					plant(Entities.Cactus)
					if measure() > measure(North):
						swap(North)
					move(East)
					plant(Entities.Cactus)
					move(South)
					plant(Entities.Cactus)
					move(East)
					plant(Entities.Cactus)
					move(South)
					plant(Entities.Cactus)
					move(East)
					plant(Entities.Cactus)
					move(South)
					plant(Entities.Cactus)
					move(East)
					plant(Entities.Cactus)
					move(South)
					plant(Entities.Cactus)
					move(East)
					plant(Entities.Cactus)
					move(South)
					plant(Entities.Cactus)
					move(East)
					plant(Entities.Cactus)
					move(South)
					plant(Entities.Cactus)
					move(East)
					plant(Entities.Cactus)
					move(South)
					plant(Entities.Cactus)
					move(East)
					plant(Entities.Cactus)
					move(South)
					plant(Entities.Cactus)
					move(East)
					plant(Entities.Cactus)
					move(South)
					plant(Entities.Cactus)
					move(East)
					plant(Entities.Cactus)
					move(South)
					plant(Entities.Cactus)
					move(East)
					tw = 0
					if get_time() > 6.0:
						if use_item(Items.Water, 4):
							tw = 1
					plant(Entities.Cactus)
					tl = get_time()
					if tw:
						tl = tl - 0.0988
					if measure() < measure(West):
						swap(West)
					xcas(South, 0)
					move(West)
					if measure() > measure(North):
						swap(North)
					move(North)
					if measure() < measure(West):
						swap(West)
					move(West)
					if measure() > measure(North):
						swap(North)
					move(North)
					if measure() < measure(West):
						swap(West)
					move(West)
					if measure() > measure(North):
						swap(North)
					move(North)
					if measure() < measure(West):
						swap(West)
					move(West)
					if measure() > measure(North):
						swap(North)
					move(North)
					if measure() < measure(West):
						swap(West)
					move(West)
					if measure() > measure(North):
						swap(North)
					move(North)
					if measure() < measure(West):
						swap(West)
					move(West)
					if measure() > measure(North):
						swap(North)
					move(North)
					if measure() < measure(West):
						swap(West)
					move(West)
					if measure() > measure(North):
						swap(North)
					move(North)
					if measure() < measure(West):
						swap(West)
					move(West)
					if measure() > measure(North):
						swap(North)
					move(North)
					if measure() < measure(West):
						swap(West)
					move(West)
					if measure() > measure(North):
						swap(North)
					move(North)
					if measure() < measure(West):
						swap(West)
					move(West)
					if measure() > measure(North):
						swap(North)
					move(North)
					if measure() < measure(West):
						swap(West)
					if tl + 0.9676 > hb + 2.6:
						wuT = tl + 0.9676
						while get_time() < wuT:
							pass
				spawn_drone(w28)
				move(West)
				move(West)
				move(West)
				move(West)
				move(West)
				move(West)
				move(West)
				move(West)
				move(South)
				move(South)
				move(South)
				move(South)
				move(South)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				if measure() > measure(North):
					swap(North)
				move(East)
				till()
				plant(Entities.Cactus)
				if measure() < measure(West):
					swap(West)
				move(South)
				till()
				plant(Entities.Cactus)
				if measure() > measure(North):
					swap(North)
				move(East)
				till()
				plant(Entities.Cactus)
				if measure() < measure(West):
					swap(West)
				move(South)
				till()
				plant(Entities.Cactus)
				if measure() > measure(North):
					swap(North)
				move(East)
				till()
				plant(Entities.Cactus)
				if measure() < measure(West):
					swap(West)
				move(South)
				till()
				plant(Entities.Cactus)
				if measure() > measure(North):
					swap(North)
				move(East)
				till()
				plant(Entities.Cactus)
				if measure() < measure(West):
					swap(West)
				move(South)
				till()
				plant(Entities.Cactus)
				if measure() > measure(North):
					swap(North)
				move(East)
				till()
				plant(Entities.Cactus)
				if measure() < measure(West):
					swap(West)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				move(South)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				tl = get_time()
				xcas(North, 1)
				move(East)
				wk = [0, 1, 2, 3]
				cur = 0
				qi = 0
				qn = 4
				q0 = True
				q1 = True
				q2 = True
				q3 = True
				q0 = False
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(East)
					while ja == None:
						ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					break
				q1 = False
				move(East)
				move(South)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					break
				q2 = False
				move(North)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						else:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
							else:
								swap(South)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					break
				q3 = False
				move(North)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					if ja > v:
						swap(South)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
					break
				cur = 3
				qi = 4
				while qi < qn:
					cx = wk[qi]
					qi += 1
					if cx == 0:
						q0 = False
						if cur == 1:
							move(West)
							move(North)
						elif cur == 2:
							move(West)
						elif cur == 3:
							move(West)
							move(South)
						cur = 0
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
					elif cx == 1:
						q1 = False
						if cur == 0:
							move(East)
							move(South)
						elif cur == 2:
							move(South)
						elif cur == 3:
							move(South)
							move(South)
						cur = 1
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
					elif cx == 2:
						q2 = False
						if cur == 0:
							move(East)
						elif cur == 1:
							move(North)
						elif cur == 3:
							move(South)
						cur = 2
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									if not q0:
										wk.append(0)
										qn += 1
										q0 = True
									v = measure()
								else:
									swap(South)
									if not q1:
										wk.append(1)
										qn += 1
										q1 = True
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
					else:
						q3 = False
						if cur == 0:
							move(East)
							move(North)
						elif cur == 1:
							move(North)
							move(North)
						elif cur == 2:
							move(North)
						cur = 3
						while True:
							v = measure()
							ja = measure(South)
							if ja > v:
								swap(South)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
				if cur == 1:
					move(North)
					move(North)
					move(North)
				elif cur == 2:
					move(North)
					move(North)
				elif cur == 3:
					move(North)
				else:
					move(East)
					move(North)
					move(North)
				if measure() < measure(West):
					swap(West)
				move(West)
				if measure() > measure(North):
					swap(North)
				move(North)
				if measure() < measure(West):
					swap(West)
				move(West)
				if measure() > measure(North):
					swap(North)
				move(North)
				if measure() < measure(West):
					swap(West)
				move(West)
				if measure() > measure(North):
					swap(North)
				e = tl + 0.9345
				P = []
				if get_time() < e:
					move(West)
					if get_time() < e:
						move(West)
						if get_time() < e:
							move(West)
							if get_time() < e:
								move(North)
							else:
								P.append((North,))
						else:
							P.append((West, North,))
					else:
						P.append((West, West, North,))
				else:
					P.append((West, West, West, North,))
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
				if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
					if get_entity_type() == Entities.Cactus:
						harvest()
					else:
						use_item(Items.Water)
				else:
					use_item(Items.Water)
				for q in P:
					for d in q:
						move(d)
				hb = 0
				while num_items(Items.Cactus) <= 0:
					hb = get_time()
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				if measure() > measure(East):
					swap(East)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				tw = 0
				if get_time() > 6.0:
					if use_item(Items.Water, 4):
						tw = 1
				plant(Entities.Cactus)
				tl = get_time()
				if tw:
					tl = tl - 0.0988
				if measure() > measure(East):
					swap(East)
				xcas(North, 1)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				if tl + 0.9676 > hb + 2.6:
					wuT = tl + 0.9676
					while get_time() < wuT:
						pass
			spawn_drone(w27)
			def w26():
				move(West)
				move(West)
				move(West)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				if measure() > measure(East):
					swap(East)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				tl = get_time()
				if measure() < measure(South):
					swap(South)
				xcas(West, 0)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				e = tl + 0.9345
				P = []
				if get_time() < e:
					move(East)
					if get_time() < e:
						move(North)
					else:
						P.append((North,))
				else:
					P.append((East, North,))
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
				if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
					if get_entity_type() == Entities.Cactus:
						harvest()
					else:
						use_item(Items.Water)
				else:
					use_item(Items.Water)
				for q in P:
					for d in q:
						move(d)
				hb = 0
				while num_items(Items.Cactus) <= 0:
					hb = get_time()
				plant(Entities.Cactus)
				move(East)
				plant(Entities.Cactus)
				if measure() < measure(West):
					swap(West)
				move(South)
				plant(Entities.Cactus)
				if measure() > measure(North):
					swap(North)
				move(East)
				plant(Entities.Cactus)
				if measure() < measure(West):
					swap(West)
				move(South)
				plant(Entities.Cactus)
				swap(South)
				plant(Entities.Cactus)
				move(South)
				move(South)
				plant(Entities.Cactus)
				swap(South)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				tw = 0
				if get_time() > 6.0:
					if use_item(Items.Water, 4):
						tw = 1
				plant(Entities.Cactus)
				tl = get_time()
				if tw:
					tl = tl - 0.0988
				if measure() > measure(East):
					swap(East)
				xcas(North, 1)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(South)
				if measure() > measure(East):
					swap(East)
				move(East)
				if measure() < measure(South):
					swap(South)
				move(East)
				move(South)
				wk = [0, 1, 2, 3]
				cur = 0
				qi = 0
				qn = 4
				q0 = True
				q1 = True
				q2 = True
				q3 = True
				q0 = False
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(East)
					while ja == None:
						ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					break
				q1 = False
				move(East)
				move(South)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					break
				q2 = False
				move(North)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						else:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
							else:
								swap(South)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					break
				q3 = False
				move(North)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					if ja > v:
						swap(South)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
					break
				cur = 3
				qi = 4
				while qi < qn:
					cx = wk[qi]
					qi += 1
					if cx == 0:
						q0 = False
						if cur == 1:
							move(West)
							move(North)
						elif cur == 2:
							move(West)
						elif cur == 3:
							move(West)
							move(South)
						cur = 0
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
					elif cx == 1:
						q1 = False
						if cur == 0:
							move(East)
							move(South)
						elif cur == 2:
							move(South)
						elif cur == 3:
							move(South)
							move(South)
						cur = 1
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
					elif cx == 2:
						q2 = False
						if cur == 0:
							move(East)
						elif cur == 1:
							move(North)
						elif cur == 3:
							move(South)
						cur = 2
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									if not q0:
										wk.append(0)
										qn += 1
										q0 = True
									v = measure()
								else:
									swap(South)
									if not q1:
										wk.append(1)
										qn += 1
										q1 = True
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
					else:
						q3 = False
						if cur == 0:
							move(East)
							move(North)
						elif cur == 1:
							move(North)
							move(North)
						elif cur == 2:
							move(North)
						cur = 3
						while True:
							v = measure()
							ja = measure(South)
							if ja > v:
								swap(South)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
				if tl + 0.9676 > hb + 2.6:
					wuT = tl + 0.9676
					while get_time() < wuT:
						pass
			spawn_drone(w26)
			def w25():
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				till()
				plant(Entities.Cactus)
				move(South)
				move(South)
				move(South)
				move(South)
				move(South)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				if measure() < measure(South):
					swap(South)
				move(West)
				till()
				plant(Entities.Cactus)
				if measure() > measure(East):
					swap(East)
				move(North)
				till()
				plant(Entities.Cactus)
				if measure() < measure(South):
					swap(South)
				move(West)
				till()
				plant(Entities.Cactus)
				if measure() > measure(East):
					swap(East)
				move(North)
				till()
				plant(Entities.Cactus)
				if measure() < measure(South):
					swap(South)
				move(West)
				till()
				plant(Entities.Cactus)
				if measure() > measure(East):
					swap(East)
				move(North)
				till()
				plant(Entities.Cactus)
				if measure() < measure(South):
					swap(South)
				move(West)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(West)
				move(West)
				till()
				plant(Entities.Cactus)
				move(East)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				move(North)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				move(North)
				till()
				plant(Entities.Cactus)
				tl = get_time()
				move(West)
				fsSW_NE()
				move(West)
				move(North)
				fsS_NE()
				move(North)
				if measure() < measure(West):
					swap(West)
				move(West)
				move(North)
				wk = [0, 1, 2, 3]
				cur = 0
				qi = 0
				qn = 4
				q0 = True
				q1 = True
				q2 = True
				q3 = True
				q0 = False
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					break
				q1 = False
				move(West)
				move(North)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(East)
					while ja == None:
						ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					break
				q2 = False
				move(East)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						else:
							swap(South)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
					ja = measure(East)
					while ja == None:
						ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
							else:
								swap(South)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					break
				q3 = False
				move(East)
				while True:
					v = measure()
					ja = measure(West)
					while ja == None:
						ja = measure(West)
					if ja > v:
						swap(West)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						v = measure()
					ja = measure(East)
					while ja == None:
						ja = measure(East)
					if ja >= v:
						break
					swap(East)
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
					break
				cur = 3
				qi = 4
				while qi < qn:
					cx = wk[qi]
					qi += 1
					if cx == 0:
						q0 = False
						if cur == 1:
							move(East)
							move(South)
						elif cur == 2:
							move(South)
						elif cur == 3:
							move(West)
							move(South)
						cur = 0
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
					elif cx == 1:
						q1 = False
						if cur == 0:
							move(West)
							move(North)
						elif cur == 2:
							move(West)
						elif cur == 3:
							move(West)
							move(West)
						cur = 1
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
					elif cx == 2:
						q2 = False
						if cur == 0:
							move(North)
						elif cur == 1:
							move(East)
						elif cur == 3:
							move(West)
						cur = 2
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									if not q1:
										wk.append(1)
										qn += 1
										q1 = True
									v = measure()
								else:
									swap(South)
									if not q0:
										wk.append(0)
										qn += 1
										q0 = True
									v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
					else:
						q3 = False
						if cur == 0:
							move(East)
							move(North)
						elif cur == 1:
							move(East)
							move(East)
						elif cur == 2:
							move(East)
						cur = 3
						while True:
							v = measure()
							ja = measure(West)
							if ja > v:
								swap(West)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
				c = cur
				e = tl + 0.9345
				P = []
				if c == 0:
					if get_time() < e:
						move(East)
						if get_time() < e:
							move(East)
							if get_time() < e:
								move(East)
							else:
								P.append((East,))
						else:
							P.append((East, East,))
					else:
						P.append((East, East, East,))
				elif c == 1:
					if get_time() < e:
						move(East)
						if get_time() < e:
							move(East)
							if get_time() < e:
								move(East)
								if get_time() < e:
									move(East)
									if get_time() < e:
										move(South)
									else:
										P.append((South,))
								else:
									P.append((East, South,))
							else:
								P.append((East, East, South,))
						else:
							P.append((East, East, East, South,))
					else:
						P.append((East, East, East, East, South,))
				elif c == 2:
					if get_time() < e:
						move(East)
						if get_time() < e:
							move(East)
							if get_time() < e:
								move(East)
								if get_time() < e:
									move(South)
								else:
									P.append((South,))
							else:
								P.append((East, South,))
						else:
							P.append((East, East, South,))
					else:
						P.append((East, East, East, South,))
				elif c == 3:
					if get_time() < e:
						move(East)
						if get_time() < e:
							move(East)
							if get_time() < e:
								move(South)
							else:
								P.append((South,))
						else:
							P.append((East, South,))
					else:
						P.append((East, East, South,))
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
				if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
					if get_entity_type() == Entities.Cactus:
						harvest()
					else:
						use_item(Items.Water)
				else:
					use_item(Items.Water)
				for q in P:
					for d in q:
						move(d)
				hb = 0
				while num_items(Items.Cactus) <= 0:
					hb = get_time()
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				if measure() > measure(East):
					swap(East)
				move(North)
				plant(Entities.Cactus)
				if measure() < measure(South):
					swap(South)
				move(West)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				swap(West)
				plant(Entities.Cactus)
				move(South)
				plant(Entities.Cactus)
				move(East)
				plant(Entities.Cactus)
				move(South)
				plant(Entities.Cactus)
				move(East)
				plant(Entities.Cactus)
				if measure() < measure(West):
					swap(West)
				move(South)
				plant(Entities.Cactus)
				swap(South)
				plant(Entities.Cactus)
				move(East)
				plant(Entities.Cactus)
				move(South)
				pkC(None)
				pkA(West, South)
				move(East)
				plant(Entities.Cactus)
				tl = get_time()
				move(West)
				fsSW_NE()
				move(West)
				move(North)
				fSW_NE()
				move(West)
				move(North)
				fsS_NE()
				move(West)
				move(North)
				move(North)
				wk = [0, 1, 2, 3]
				cur = 0
				qi = 0
				qn = 4
				q0 = True
				q1 = True
				q2 = True
				q3 = True
				q0 = False
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					break
				q1 = False
				move(West)
				move(North)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(East)
					while ja == None:
						ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					break
				q2 = False
				move(East)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						else:
							swap(South)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
					ja = measure(East)
					while ja == None:
						ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
							else:
								swap(South)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					break
				q3 = False
				move(East)
				while True:
					v = measure()
					ja = measure(West)
					while ja == None:
						ja = measure(West)
					if ja > v:
						swap(West)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						v = measure()
					ja = measure(East)
					while ja == None:
						ja = measure(East)
					if ja >= v:
						break
					swap(East)
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
					break
				cur = 3
				qi = 4
				while qi < qn:
					cx = wk[qi]
					qi += 1
					if cx == 0:
						q0 = False
						if cur == 1:
							move(East)
							move(South)
						elif cur == 2:
							move(South)
						elif cur == 3:
							move(West)
							move(South)
						cur = 0
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
					elif cx == 1:
						q1 = False
						if cur == 0:
							move(West)
							move(North)
						elif cur == 2:
							move(West)
						elif cur == 3:
							move(West)
							move(West)
						cur = 1
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
					elif cx == 2:
						q2 = False
						if cur == 0:
							move(North)
						elif cur == 1:
							move(East)
						elif cur == 3:
							move(West)
						cur = 2
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									if not q1:
										wk.append(1)
										qn += 1
										q1 = True
									v = measure()
								else:
									swap(South)
									if not q0:
										wk.append(0)
										qn += 1
										q0 = True
									v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
					else:
						q3 = False
						if cur == 0:
							move(East)
							move(North)
						elif cur == 1:
							move(East)
							move(East)
						elif cur == 2:
							move(East)
						cur = 3
						while True:
							v = measure()
							ja = measure(West)
							if ja > v:
								swap(West)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
				if tl + 0.9676 > hb + 2.6:
					wuT = tl + 0.9676
					while get_time() < wuT:
						pass
			spawn_drone(w25)
			move(South)
			move(South)
			move(South)
			move(South)
			till()
			move(South)
			till()
			move(East)
			move(East)
			move(East)
			move(East)
			move(East)
			move(East)
			move(East)
			move(East)
			move(East)
			move(East)
			move(East)
			move(East)
			move(East)
			move(East)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			tl = get_time()
			fsSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fsSW_NE()
			e = tl + 0.9345
			P = []
			if get_time() < e:
				move(East)
				if get_time() < e:
					move(South)
				else:
					P.append((South,))
			else:
				P.append((East, South,))
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
			if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
				if get_entity_type() == Entities.Cactus:
					harvest()
				else:
					use_item(Items.Water)
			else:
				use_item(Items.Water)
			for q in P:
				for d in q:
					move(d)
			hb = 0
			while num_items(Items.Cactus) <= 0:
				hb = get_time()
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			move(East)
			plant(Entities.Cactus)
			swap(North)
			pkC(None)
			pkC(West)
			pkC(West)
			pkC(West)
			pkC(West)
			pkC(West)
			pkA(West, South)
			tl = get_time()
			DL = tl + 0.9676
			if DL < hb + 2.6:
				DL = hb + 2.6
			TFS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
			TMS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
			TRS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
			h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 6, 7)
			if h:
				own(TFS, TMS, TRS, 0, 5, DL)
			else:
				fsSW_NE()
				move(West)
				move(North)
				h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 6, 7)
				if h:
					own(TFS, TMS, TRS, 1, 5, DL)
				else:
					fSW_NE()
					move(West)
					move(North)
					h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 6, 7)
					if h:
						own(TFS, TMS, TRS, 2, 5, DL)
					else:
						fSW_NE()
						move(West)
						move(North)
						h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 7)
						if h:
							own(TFS, TMS, TRS, 3, 6, DL)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 7, 7)
							if h:
								own(TFS, TMS, TRS, 4, 6, DL)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 7, 7)
								if h:
									own(TFS, TMS, TRS, 5, 6, DL)
								else:
									fSW_NE()
									move(West)
									move(North)
									fSW_NE()
									move(West)
									move(North)
									fsSW_NE()
			if tl + 0.9676 > hb + 2.6:
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
		spawn_drone(w24)
		def w21():
			def w22():
				def w23():
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(South)
					till()
					plant(Entities.Cactus)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					till()
					plant(Entities.Cactus)
					move(East)
					move(North)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(East)
					move(North)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(East)
					move(North)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(East)
					move(North)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(East)
					move(North)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(East)
					move(North)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(South)
					till()
					plant(Entities.Cactus)
					move(East)
					move(North)
					till()
					plant(Entities.Cactus)
					tl = get_time()
					move(South)
					till()
					use_item(Items.Water, 4)
					plant(Entities.Cactus)
					fsSW_NE()
					move(West)
					move(North)
					fSW_NE()
					move(West)
					move(North)
					fSW_NE()
					move(West)
					move(North)
					fSW_NE()
					move(West)
					move(North)
					fSW_NE()
					move(West)
					move(North)
					fSW_NE()
					move(West)
					move(North)
					fsSW_NE()
					e = tl + 0.9345
					P = []
					if get_time() < e:
						move(East)
					else:
						P.append((East,))
					wuT = tl + 0.9676
					while get_time() < wuT:
						pass
					if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
						if get_entity_type() == Entities.Cactus:
							harvest()
						else:
							use_item(Items.Water)
					else:
						use_item(Items.Water)
					for q in P:
						for d in q:
							move(d)
					hb = 0
					while num_items(Items.Cactus) <= 0:
						hb = get_time()
					plant(Entities.Cactus)
					move(South)
					pkC(None)
					pkC(West)
					pkC(West)
					pkC(West)
					pkC(West)
					pkC(West)
					pkA(West, South)
					move(East)
					plant(Entities.Cactus)
					move(South)
					tw = 0
					if get_time() > 6.0:
						if use_item(Items.Water, 4):
							tw = 1
					plant(Entities.Cactus)
					tl = get_time()
					if tw:
						tl = tl - 0.0988
					DL = tl + 0.9676
					if DL < hb + 2.6:
						DL = hb + 2.6
					TFS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
					TMS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
					TRS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
					h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 6, 7)
					if h:
						own(TFS, TMS, TRS, 0, 5, DL)
					else:
						fsSW_NE()
						move(West)
						move(North)
						h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 6, 7)
						if h:
							own(TFS, TMS, TRS, 1, 5, DL)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 6, 7)
							if h:
								own(TFS, TMS, TRS, 2, 5, DL)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 7)
								if h:
									own(TFS, TMS, TRS, 3, 6, DL)
								else:
									fSW_NE()
									move(West)
									move(North)
									h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 7, 7)
									if h:
										own(TFS, TMS, TRS, 4, 6, DL)
									else:
										fSW_NE()
										move(West)
										move(North)
										h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 7, 7)
										if h:
											own(TFS, TMS, TRS, 5, 6, DL)
										else:
											fSW_NE()
											move(West)
											move(North)
											fSW_NE()
											move(West)
											move(North)
											fsSW_NE()
					if tl + 0.9676 > hb + 2.6:
						wuT = tl + 0.9676
						while get_time() < wuT:
							pass
				spawn_drone(w23)
				move(West)
				move(West)
				move(West)
				move(West)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				till()
				plant(Entities.Cactus)
				move(East)
				move(North)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				move(North)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				move(North)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				move(South)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				if measure() < measure(South):
					swap(South)
				move(West)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				move(South)
				till()
				plant(Entities.Cactus)
				tl = get_time()
				move(East)
				fsW_NE()
				move(East)
				move(East)
				move(South)
				wk = [0, 1, 2, 3, 4]
				cur = 0
				qi = 0
				qn = 5
				q0 = True
				q1 = True
				q2 = True
				q3 = True
				q4 = True
				q0 = False
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(East)
					while ja == None:
						ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					break
				q1 = False
				move(East)
				move(South)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					break
				q2 = False
				move(North)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						else:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
							else:
								swap(South)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					break
				q3 = False
				move(North)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					if ja > v:
						swap(South)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q4:
						wk.append(4)
						qn += 1
						q4 = True
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q4:
							wk.append(4)
							qn += 1
							q4 = True
					break
				q4 = False
				move(North)
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					jb = measure(West)
					while jb == None:
						jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
							v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
					break
				cur = 4
				qi = 5
				while qi < qn:
					cx = wk[qi]
					qi += 1
					if cx == 0:
						q0 = False
						if cur == 1:
							move(West)
							move(North)
						elif cur == 2:
							move(West)
						elif cur == 3:
							move(West)
							move(South)
						elif cur == 4:
							move(West)
							move(South)
							move(South)
						cur = 0
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
					elif cx == 1:
						q1 = False
						if cur == 0:
							move(East)
							move(South)
						elif cur == 2:
							move(South)
						elif cur == 3:
							move(South)
							move(South)
						elif cur == 4:
							move(South)
							move(South)
							move(South)
						cur = 1
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
					elif cx == 2:
						q2 = False
						if cur == 0:
							move(East)
						elif cur == 1:
							move(North)
						elif cur == 3:
							move(South)
						elif cur == 4:
							move(South)
							move(South)
						cur = 2
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									if not q0:
										wk.append(0)
										qn += 1
										q0 = True
									v = measure()
								else:
									swap(South)
									if not q1:
										wk.append(1)
										qn += 1
										q1 = True
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
					elif cx == 3:
						q3 = False
						if cur == 0:
							move(East)
							move(North)
						elif cur == 1:
							move(North)
							move(North)
						elif cur == 2:
							move(North)
						elif cur == 4:
							move(South)
						cur = 3
						while True:
							v = measure()
							ja = measure(South)
							if ja > v:
								swap(South)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
								v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
							if not q4:
								wk.append(4)
								qn += 1
								q4 = True
					else:
						q4 = False
						if cur == 0:
							move(East)
							move(North)
							move(North)
						elif cur == 1:
							move(North)
							move(North)
							move(North)
						elif cur == 2:
							move(North)
							move(North)
						elif cur == 3:
							move(North)
						cur = 4
						while True:
							v = measure()
							ja = measure(South)
							jb = measure(West)
							if not ja <= v >= jb:
								if jb > ja:
									swap(West)
									v = measure()
								else:
									swap(South)
									if not q3:
										wk.append(3)
										qn += 1
										q3 = True
									v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
				if cur == 1:
					move(North)
					move(North)
					move(North)
					move(North)
					move(West)
				elif cur == 2:
					move(North)
					move(North)
					move(North)
					move(West)
				elif cur == 3:
					move(North)
					move(North)
					move(West)
				elif cur == 4:
					move(North)
					move(West)
				else:
					move(North)
					move(North)
					move(North)
				fSW_NE()
				move(West)
				move(North)
				fsSW_NE()
				e = tl + 0.9345
				P = []
				if get_time() < e:
					move(South)
					if get_time() < e:
						move(South)
						if get_time() < e:
							move(South)
							if get_time() < e:
								move(South)
								if get_time() < e:
									move(South)
									if get_time() < e:
										move(South)
										if get_time() < e:
											move(South)
											if get_time() < e:
												move(South)
												if get_time() < e:
													move(South)
												else:
													P.append((South,))
											else:
												P.append((South, South,))
										else:
											P.append((South, South, South,))
									else:
										P.append((South, South, South, South,))
								else:
									P.append((South, South, South, South, South,))
							else:
								P.append((South, South, South, South, South, South,))
						else:
							P.append((South, South, South, South, South, South, South,))
					else:
						P.append((South, South, South, South, South, South, South, South,))
				else:
					P.append((South, South, South, South, South, South, South, South, South,))
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
				if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
					if get_entity_type() == Entities.Cactus:
						harvest()
					else:
						use_item(Items.Water)
				else:
					use_item(Items.Water)
				for q in P:
					for d in q:
						move(d)
				hb = 0
				while num_items(Items.Cactus) <= 0:
					hb = get_time()
				plant(Entities.Cactus)
				move(East)
				plant(Entities.Cactus)
				if measure() < measure(West):
					swap(West)
				move(South)
				plant(Entities.Cactus)
				move(East)
				plant(Entities.Cactus)
				move(South)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				if measure() < measure(South):
					swap(South)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				swap(South)
				pkB(None)
				pkB(East)
				pkA(East, North)
				move(West)
				plant(Entities.Cactus)
				tl = get_time()
				move(East)
				fsSW_NE()
				move(East)
				move(South)
				fSW_NE()
				move(East)
				move(South)
				fSW_NE()
				move(East)
				move(South)
				fsW_NE()
				move(East)
				move(East)
				move(East)
				wk = [3, 2, 1, 0]
				cur = 3
				qi = 0
				qn = 4
				q3 = True
				q2 = True
				q1 = True
				q0 = True
				q3 = False
				while True:
					v = measure()
					ja = measure(South)
					while ja == None:
						ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					jb = measure(East)
					while jb == None:
						jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
					break
				q2 = False
				move(East)
				move(South)
				while True:
					v = measure()
					ja = measure(West)
					while ja == None:
						ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					if ja >= v:
						break
					swap(North)
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
					break
				q1 = False
				move(West)
				while True:
					v = measure()
					ja = measure(West)
					while ja == None:
						ja = measure(West)
					if ja > v:
						swap(West)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					while ja == None:
						ja = measure(North)
					jb = measure(East)
					while jb == None:
						jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					else:
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
						else:
							swap(North)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
					break
				q0 = False
				move(West)
				while True:
					v = measure()
					ja = measure(West)
					while ja == None:
						ja = measure(West)
					if ja > v:
						swap(West)
						v = measure()
					ja = measure(East)
					while ja == None:
						ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
					break
				cur = 0
				qi = 4
				while qi < qn:
					cx = wk[qi]
					qi += 1
					if cx == 0:
						q0 = False
						if cur == 1:
							move(West)
						elif cur == 2:
							move(West)
							move(West)
						elif cur == 3:
							move(West)
							move(South)
						cur = 0
						while True:
							v = measure()
							ja = measure(West)
							if ja > v:
								swap(West)
								v = measure()
							ja = measure(East)
							if ja >= v:
								break
							swap(East)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
					elif cx == 1:
						q1 = False
						if cur == 0:
							move(East)
						elif cur == 2:
							move(West)
						elif cur == 3:
							move(South)
						cur = 1
						while True:
							v = measure()
							ja = measure(West)
							if ja > v:
								swap(West)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
							ja = measure(North)
							jb = measure(East)
							if ja >= v <= jb:
								break
							if jb < ja:
								swap(East)
								if not q2:
									wk.append(2)
									qn += 1
									q2 = True
							else:
								swap(North)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
					elif cx == 2:
						q2 = False
						if cur == 0:
							move(East)
							move(East)
						elif cur == 1:
							move(East)
						elif cur == 3:
							move(East)
							move(South)
						cur = 2
						while True:
							v = measure()
							ja = measure(West)
							if ja > v:
								swap(West)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
							ja = measure(North)
							if ja >= v:
								break
							swap(North)
					else:
						q3 = False
						if cur == 0:
							move(East)
							move(North)
						elif cur == 1:
							move(North)
						elif cur == 2:
							move(West)
							move(North)
						cur = 3
						while True:
							v = measure()
							ja = measure(South)
							if ja > v:
								swap(South)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
							ja = measure(North)
							jb = measure(East)
							if ja >= v <= jb:
								break
							if jb < ja:
								swap(East)
							else:
								swap(North)
				if tl + 0.9676 > hb + 2.6:
					wuT = tl + 0.9676
					while get_time() < wuT:
						pass
			spawn_drone(w22)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			tl = get_time()
			move(East)
			fsSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fsSW_NE()
			e = tl + 0.9345
			P = []
			if get_time() < e:
				move(East)
				if get_time() < e:
					move(East)
					if get_time() < e:
						move(East)
					else:
						P.append((East,))
				else:
					P.append((East, East,))
			else:
				P.append((East, East, East,))
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
			if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
				if get_entity_type() == Entities.Cactus:
					harvest()
				else:
					use_item(Items.Water)
			else:
				use_item(Items.Water)
			for q in P:
				for d in q:
					move(d)
			hb = 0
			while num_items(Items.Cactus) <= 0:
				hb = get_time()
			plant(Entities.Cactus)
			move(East)
			plant(Entities.Cactus)
			swap(North)
			plant(Entities.Cactus)
			swap(South)
			plant(Entities.Cactus)
			move(South)
			move(South)
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			swap(South)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			if measure() < measure(South):
				swap(South)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			swap(South)
			pkB(None)
			pkA(East, North)
			tl = get_time()
			fsSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fsW_NE()
			move(East)
			move(East)
			move(South)
			wk = [0, 1, 2, 3, 4]
			cur = 0
			qi = 0
			qn = 5
			q0 = True
			q1 = True
			q2 = True
			q3 = True
			q4 = True
			q0 = False
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						v = measure()
					else:
						swap(South)
						v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				break
			q1 = False
			move(East)
			move(South)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						v = measure()
					else:
						swap(South)
						v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				break
			q2 = False
			move(North)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					else:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						else:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				break
			q3 = False
			move(North)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q4:
					wk.append(4)
					qn += 1
					q4 = True
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q4:
						wk.append(4)
						qn += 1
						q4 = True
				break
			q4 = False
			move(North)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						v = measure()
					else:
						swap(South)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
						v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
							v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
				break
			cur = 4
			qi = 5
			while qi < qn:
				cx = wk[qi]
				qi += 1
				if cx == 0:
					q0 = False
					if cur == 1:
						move(West)
						move(North)
					elif cur == 2:
						move(West)
					elif cur == 3:
						move(West)
						move(South)
					elif cur == 4:
						move(West)
						move(South)
						move(South)
					cur = 0
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				elif cx == 1:
					q1 = False
					if cur == 0:
						move(East)
						move(South)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(South)
						move(South)
					elif cur == 4:
						move(South)
						move(South)
						move(South)
					cur = 1
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				elif cx == 2:
					q2 = False
					if cur == 0:
						move(East)
					elif cur == 1:
						move(North)
					elif cur == 3:
						move(South)
					elif cur == 4:
						move(South)
						move(South)
					cur = 2
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
							else:
								swap(South)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
				elif cx == 3:
					q3 = False
					if cur == 0:
						move(East)
						move(North)
					elif cur == 1:
						move(North)
						move(North)
					elif cur == 2:
						move(North)
					elif cur == 4:
						move(South)
					cur = 3
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q4:
							wk.append(4)
							qn += 1
							q4 = True
				else:
					q4 = False
					if cur == 0:
						move(East)
						move(North)
						move(North)
					elif cur == 1:
						move(North)
						move(North)
						move(North)
					elif cur == 2:
						move(North)
						move(North)
					elif cur == 3:
						move(North)
					cur = 4
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
			if tl + 0.9676 > hb + 2.6:
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
		spawn_drone(w21)
		def w18():
			def w19():
				def w20():
					move(West)
					till()
					move(West)
					till()
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					till()
					plant(Entities.Cactus)
					move(West)
					move(West)
					move(West)
					move(West)
					move(West)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					move(West)
					move(South)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					move(West)
					move(South)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					move(West)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					move(West)
					move(South)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					move(West)
					move(South)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					move(West)
					move(South)
					till()
					plant(Entities.Cactus)
					move(North)
					till()
					plant(Entities.Cactus)
					tl = get_time()
					fsSW_NE()
					move(East)
					move(South)
					fSW_NE()
					move(East)
					move(South)
					fSW_NE()
					move(East)
					move(South)
					fSW_NE()
					move(East)
					move(South)
					fSW_NE()
					move(East)
					move(South)
					fSW_NE()
					move(East)
					move(South)
					fsSW_NE()
					e = tl + 0.9345
					P = []
					if get_time() < e:
						move(East)
						if get_time() < e:
							move(East)
							if get_time() < e:
								move(South)
								if get_time() < e:
									move(South)
									if get_time() < e:
										move(South)
										if get_time() < e:
											move(South)
											if get_time() < e:
												move(South)
											else:
												P.append((South,))
										else:
											P.append((South, South,))
									else:
										P.append((South, South, South,))
								else:
									P.append((South, South, South, South,))
							else:
								P.append((South, South, South, South, South,))
						else:
							P.append((East, South, South, South, South, South,))
					else:
						P.append((East, East, South, South, South, South, South,))
					wuT = tl + 0.9676
					while get_time() < wuT:
						pass
					if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
						if get_entity_type() == Entities.Cactus:
							harvest()
						else:
							use_item(Items.Water)
					else:
						use_item(Items.Water)
					for q in P:
						for d in q:
							move(d)
					hb = 0
					while num_items(Items.Cactus) <= 0:
						hb = get_time()
					plant(Entities.Cactus)
					move(South)
					pkC(None)
					pkC(West)
					pkC(West)
					pkC(West)
					pkC(West)
					pkC(West)
					pkC(West)
					pkA(West, South)
					move(East)
					plant(Entities.Cactus)
					move(South)
					if use_item(Items.Water, 4):
						plant(Entities.Cactus)
						tw = get_time() - 0.0988
					else:
						plant(Entities.Cactus)
						tw = 0
					tl = get_time()
					if tw:
						tl = tw
					DL = tl + 0.9676
					if DL < hb + 2.6:
						DL = hb + 2.6
					TFS = (fsSW_N, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
					TMS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
					TRS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
					h = get_time() + 0.8100 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 7, 8)
					if h:
						own(TFS, TMS, TRS, 0, 6, DL)
					else:
						fsSW_N()
						move(West)
						move(North)
						h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 7, 8)
						if h:
							own(TFS, TMS, TRS, 1, 6, DL)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 7, 8)
							if h:
								own(TFS, TMS, TRS, 2, 6, DL)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 8)
								if h:
									own(TFS, TMS, TRS, 3, 6, DL)
								else:
									fSW_NE()
									move(West)
									move(North)
									h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 8, 8)
									if h:
										own(TFS, TMS, TRS, 4, 7, DL)
									else:
										fSW_NE()
										move(West)
										move(North)
										h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 8, 8)
										if h:
											own(TFS, TMS, TRS, 5, 7, DL)
										else:
											fSW_NE()
											move(West)
											move(North)
											h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 6, 8, 8)
											if h:
												own(TFS, TMS, TRS, 6, 7, DL)
											else:
												fSW_NE()
												move(West)
												move(North)
												fSW_NE()
												move(West)
												move(North)
												fsSW_NE()
					if tl + 0.9676 > hb + 2.6:
						wuT = tl + 0.9676
						while get_time() < wuT:
							pass
				spawn_drone(w20)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				move(East)
				till()
				plant(Entities.Cactus)
				move(East)
				move(East)
				move(East)
				move(South)
				move(South)
				move(South)
				move(South)
				move(South)
				move(South)
				move(South)
				move(South)
				till()
				plant(Entities.Cactus)
				move(West)
				move(South)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				move(South)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				move(South)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				move(South)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				move(South)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				move(South)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				move(West)
				move(South)
				till()
				plant(Entities.Cactus)
				move(North)
				till()
				plant(Entities.Cactus)
				tl = get_time()
				fsSW_NE()
				move(East)
				move(South)
				fSW_NE()
				move(East)
				move(South)
				fSW_NE()
				move(East)
				move(South)
				fSW_NE()
				move(East)
				move(South)
				fSW_NE()
				move(East)
				move(South)
				fSW_NE()
				move(East)
				move(South)
				fsSW_NE()
				e = tl + 0.9345
				P = []
				if get_time() < e:
					move(South)
					if get_time() < e:
						move(South)
						if get_time() < e:
							move(South)
							if get_time() < e:
								move(South)
								if get_time() < e:
									move(South)
								else:
									P.append((South,))
							else:
								P.append((South, South,))
						else:
							P.append((South, South, South,))
					else:
						P.append((South, South, South, South,))
				else:
					P.append((South, South, South, South, South,))
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
				if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
					if get_entity_type() == Entities.Cactus:
						harvest()
					else:
						use_item(Items.Water)
				else:
					use_item(Items.Water)
				for q in P:
					for d in q:
						move(d)
				hb = 0
				while num_items(Items.Cactus) <= 0:
					hb = get_time()
					if (get_time() // WDT) - num_items(Items.Water) >= NSIG + 1:
						harvest()
				while num_items(Items.Cactus) <= 0:
					hb = get_time()
				plant(Entities.Cactus)
				move(East)
				plant(Entities.Cactus)
				swap(North)
				pkC(None)
				pkC(West)
				pkC(West)
				pkC(West)
				pkC(West)
				pkC(West)
				pkC(West)
				pkA(West, South)
				tl = get_time()
				if use_item(Items.Water, 4):
					tl = get_time() - 0.0988
				DL = tl + 0.9676
				if DL < hb + 2.6:
					DL = hb + 2.6
				TFS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
				TMS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
				TRS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
				h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 6, 7)
				if h:
					own(TFS, TMS, TRS, 0, 5, DL)
				else:
					fsSW_NE()
					move(West)
					move(North)
					h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 6, 7)
					if h:
						own(TFS, TMS, TRS, 1, 5, DL)
					else:
						fSW_NE()
						move(West)
						move(North)
						h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 6, 7)
						if h:
							own(TFS, TMS, TRS, 2, 5, DL)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 7)
							if h:
								own(TFS, TMS, TRS, 3, 6, DL)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 7, 7)
								if h:
									own(TFS, TMS, TRS, 4, 6, DL)
								else:
									fSW_NE()
									move(West)
									move(North)
									h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 7, 7)
									if h:
										own(TFS, TMS, TRS, 5, 6, DL)
									else:
										fSW_NE()
										move(West)
										move(North)
										fSW_NE()
										move(West)
										move(North)
										fsSW_NE()
				if tl + 0.9676 > hb + 2.6:
					wuT = tl + 0.9676
					while get_time() < wuT:
						pass
			spawn_drone(w19)
			move(East)
			move(East)
			move(East)
			move(East)
			till()
			plant(Entities.Cactus)
			move(East)
			move(East)
			move(South)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			till()
			plant(Entities.Cactus)
			move(West)
			till()
			plant(Entities.Cactus)
			move(West)
			move(West)
			till()
			plant(Entities.Cactus)
			move(East)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			till()
			plant(Entities.Cactus)
			if measure() < measure(West):
				swap(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			tl = get_time()
			move(North)
			fsSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fsS_NE()
			move(West)
			move(North)
			move(North)
			wk = [0, 1, 2, 3, 4]
			cur = 0
			qi = 0
			qn = 5
			q0 = True
			q1 = True
			q2 = True
			q3 = True
			q4 = True
			q0 = False
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						v = measure()
					else:
						swap(South)
						v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				break
			q1 = False
			move(West)
			move(North)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						v = measure()
					else:
						swap(South)
						v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				break
			q2 = False
			move(East)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					else:
						swap(South)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						else:
							swap(South)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				break
			q3 = False
			move(East)
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q4:
					wk.append(4)
					qn += 1
					q4 = True
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q4:
						wk.append(4)
						qn += 1
						q4 = True
				break
			q4 = False
			move(East)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
						v = measure()
					else:
						swap(South)
						v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
				break
			cur = 4
			qi = 5
			while qi < qn:
				cx = wk[qi]
				qi += 1
				if cx == 0:
					q0 = False
					if cur == 1:
						move(East)
						move(South)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(West)
						move(South)
					elif cur == 4:
						move(West)
						move(West)
						move(South)
					cur = 0
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				elif cx == 1:
					q1 = False
					if cur == 0:
						move(West)
						move(North)
					elif cur == 2:
						move(West)
					elif cur == 3:
						move(West)
						move(West)
					elif cur == 4:
						move(West)
						move(West)
						move(West)
					cur = 1
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				elif cx == 2:
					q2 = False
					if cur == 0:
						move(North)
					elif cur == 1:
						move(East)
					elif cur == 3:
						move(West)
					elif cur == 4:
						move(West)
						move(West)
					cur = 2
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
							else:
								swap(South)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
				elif cx == 3:
					q3 = False
					if cur == 0:
						move(East)
						move(North)
					elif cur == 1:
						move(East)
						move(East)
					elif cur == 2:
						move(East)
					elif cur == 4:
						move(West)
					cur = 3
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q4:
							wk.append(4)
							qn += 1
							q4 = True
				else:
					q4 = False
					if cur == 0:
						move(East)
						move(East)
						move(North)
					elif cur == 1:
						move(East)
						move(East)
						move(East)
					elif cur == 2:
						move(East)
						move(East)
					elif cur == 3:
						move(East)
					cur = 4
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
			c = cur
			e = tl + 0.9345
			P = []
			if c == 0:
				if get_time() < e:
					move(East)
					if get_time() < e:
						move(South)
					else:
						P.append((South,))
				else:
					P.append((East, South,))
			elif c == 1:
				if get_time() < e:
					move(East)
					if get_time() < e:
						move(East)
						if get_time() < e:
							move(South)
							if get_time() < e:
								move(South)
							else:
								P.append((South,))
						else:
							P.append((South, South,))
					else:
						P.append((East, South, South,))
				else:
					P.append((East, East, South, South,))
			elif c == 2:
				if get_time() < e:
					move(East)
					if get_time() < e:
						move(South)
						if get_time() < e:
							move(South)
						else:
							P.append((South,))
					else:
						P.append((South, South,))
				else:
					P.append((East, South, South,))
			elif c == 3:
				if get_time() < e:
					move(South)
					if get_time() < e:
						move(South)
					else:
						P.append((South,))
				else:
					P.append((South, South,))
			elif c == 4:
				if get_time() < e:
					move(West)
					if get_time() < e:
						move(South)
						if get_time() < e:
							move(South)
						else:
							P.append((South,))
					else:
						P.append((South, South,))
				else:
					P.append((West, South, South,))
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
			if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
				if get_entity_type() == Entities.Cactus:
					harvest()
				else:
					use_item(Items.Water)
			else:
				use_item(Items.Water)
			for q in P:
				for d in q:
					move(d)
			hb = 0
			while num_items(Items.Cactus) <= 0:
				hb = get_time()
			plant(Entities.Cactus)
			move(South)
			pkC(None)
			pkC(West)
			pkC(West)
			pkC(West)
			pkC(West)
			pkC(West)
			pkC(West)
			pkA(West, South)
			move(East)
			plant(Entities.Cactus)
			move(South)
			if use_item(Items.Water, 4):
				plant(Entities.Cactus)
				tw = get_time() - 0.0988
			else:
				plant(Entities.Cactus)
				tw = 0
			tl = get_time()
			if tw:
				tl = tw
			DL = tl + 0.9676
			if DL < hb + 2.6:
				DL = hb + 2.6
			TFS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsS_NE)
			TMS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
			TRS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
			h = get_time() + 0.8100 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 7, 8)
			if h:
				own(TFS, TMS, TRS, 0, 6, DL)
			else:
				fsSW_NE()
				move(West)
				move(North)
				h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 7, 8)
				if h:
					own(TFS, TMS, TRS, 1, 6, DL)
				else:
					fSW_NE()
					move(West)
					move(North)
					h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 7, 8)
					if h:
						own(TFS, TMS, TRS, 2, 6, DL)
					else:
						fSW_NE()
						move(West)
						move(North)
						h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 8)
						if h:
							own(TFS, TMS, TRS, 3, 6, DL)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 8, 8)
							if h:
								own(TFS, TMS, TRS, 4, 7, DL)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 8, 8)
								if h:
									own(TFS, TMS, TRS, 5, 7, DL)
								else:
									fSW_NE()
									move(West)
									move(North)
									h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 6, 8, 8)
									if h:
										own(TFS, TMS, TRS, 6, 7, DL)
									else:
										fSW_NE()
										move(West)
										move(North)
										fSW_NE()
										move(West)
										move(North)
										fsS_NE()
			if tl + 0.9676 > hb + 2.6:
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
		spawn_drone(w18)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(South)
		move(South)
		move(South)
		move(South)
		move(South)
		move(South)
		move(South)
		def w17():
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			tl = get_time()
			move(North)
			fsSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fsSW_NE()
			e = tl + 0.9345
			P = []
			if get_time() < e:
				move(East)
				if get_time() < e:
					move(North)
					if get_time() < e:
						move(North)
						if get_time() < e:
							move(North)
							if get_time() < e:
								move(North)
							else:
								P.append((North,))
						else:
							P.append((North, North,))
					else:
						P.append((North, North, North,))
				else:
					P.append((North, North, North, North,))
			else:
				P.append((East, North, North, North, North,))
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
			if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
				if get_entity_type() == Entities.Cactus:
					harvest()
				else:
					use_item(Items.Water)
			else:
				use_item(Items.Water)
			for q in P:
				for d in q:
					move(d)
			hb = 0
			while num_items(Items.Cactus) <= 0:
				hb = get_time()
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			swap(South)
			pkB(None)
			pkB(East)
			pkA(East, North)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			swap(West)
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			move(East)
			plant(Entities.Cactus)
			move(South)
			tw = 0
			if get_time() > 6.0:
				if use_item(Items.Water, 4):
					tw = 1
			plant(Entities.Cactus)
			tl = get_time()
			if tw:
				tl = tl - 0.0988
			xcas(East, 1)
			move(North)
			wk = [0, 1, 2, 3, 4]
			cur = 0
			qi = 0
			qn = 5
			q0 = True
			q1 = True
			q2 = True
			q3 = True
			q4 = True
			q0 = False
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						v = measure()
					else:
						swap(South)
						v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				break
			q1 = False
			move(West)
			move(North)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						v = measure()
					else:
						swap(South)
						v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				break
			q2 = False
			move(East)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					else:
						swap(South)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						else:
							swap(South)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				break
			q3 = False
			move(East)
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q4:
					wk.append(4)
					qn += 1
					q4 = True
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q4:
						wk.append(4)
						qn += 1
						q4 = True
				break
			q4 = False
			move(East)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
						v = measure()
					else:
						swap(South)
						v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
				break
			cur = 4
			qi = 5
			while qi < qn:
				cx = wk[qi]
				qi += 1
				if cx == 0:
					q0 = False
					if cur == 1:
						move(East)
						move(South)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(West)
						move(South)
					elif cur == 4:
						move(West)
						move(West)
						move(South)
					cur = 0
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				elif cx == 1:
					q1 = False
					if cur == 0:
						move(West)
						move(North)
					elif cur == 2:
						move(West)
					elif cur == 3:
						move(West)
						move(West)
					elif cur == 4:
						move(West)
						move(West)
						move(West)
					cur = 1
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				elif cx == 2:
					q2 = False
					if cur == 0:
						move(North)
					elif cur == 1:
						move(East)
					elif cur == 3:
						move(West)
					elif cur == 4:
						move(West)
						move(West)
					cur = 2
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
							else:
								swap(South)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
				elif cx == 3:
					q3 = False
					if cur == 0:
						move(East)
						move(North)
					elif cur == 1:
						move(East)
						move(East)
					elif cur == 2:
						move(East)
					elif cur == 4:
						move(West)
					cur = 3
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q4:
							wk.append(4)
							qn += 1
							q4 = True
				else:
					q4 = False
					if cur == 0:
						move(East)
						move(East)
						move(North)
					elif cur == 1:
						move(East)
						move(East)
						move(East)
					elif cur == 2:
						move(East)
						move(East)
					elif cur == 3:
						move(East)
					cur = 4
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q3:
									wk.append(3)
									qn += 1
									q3 = True
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
			if cur == 1:
				move(East)
				move(East)
				move(East)
				move(East)
				move(South)
			elif cur == 2:
				move(East)
				move(East)
				move(East)
				move(South)
			elif cur == 3:
				move(East)
				move(East)
				move(South)
			elif cur == 4:
				move(East)
				move(South)
			else:
				move(East)
				move(East)
				move(East)
			fsSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fsSW_NE()
			if tl + 0.9676 > hb + 2.6:
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
		spawn_drone(w17)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		till()
		move(East)
		move(South)
		move(South)
		move(South)
		move(South)
		move(South)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		tl = get_time()
		move(East)
		move(North)
		till()
		use_item(Items.Water, 4)
		plant(Entities.Cactus)
		move(West)
		fsSW_NE()
		move(West)
		move(North)
		fSW_NE()
		move(West)
		move(North)
		fSW_NE()
		move(West)
		move(North)
		fSW_NE()
		move(West)
		move(North)
		fSW_NE()
		move(West)
		move(North)
		fsSW_NE()
		e = tl + 0.9345
		P = []
		if get_time() < e:
			move(East)
			if get_time() < e:
				move(North)
				if get_time() < e:
					move(North)
					if get_time() < e:
						move(North)
					else:
						P.append((North,))
				else:
					P.append((North, North,))
			else:
				P.append((North, North, North,))
		else:
			P.append((East, North, North, North,))
		wuT = tl + 0.9676
		while get_time() < wuT:
			pass
		if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
			if get_entity_type() == Entities.Cactus:
				harvest()
			else:
				use_item(Items.Water)
		else:
			use_item(Items.Water)
		for q in P:
			for d in q:
				move(d)
		hb = 0
		while num_items(Items.Cactus) <= 0:
			hb = get_time()
		plant(Entities.Cactus)
		move(North)
		plant(Entities.Cactus)
		move(West)
		plant(Entities.Cactus)
		swap(South)
		pkB(None)
		pkB(East)
		pkB(East)
		pkB(East)
		pkB(East)
		pkB(East)
		pkA(East, North)
		move(West)
		plant(Entities.Cactus)
		move(North)
		tw = 0
		if get_time() > 6.0:
			if use_item(Items.Water, 4):
				tw = 1
		plant(Entities.Cactus)
		tl = get_time()
		if tw:
			tl = tl - 0.0988
		DL = tl + 0.9676
		if DL < hb + 2.6:
			DL = hb + 2.6
		TFS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		TMS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
		TRS = ((North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West))
		h = get_time() + 0.8100 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 7, 8)
		if h:
			own(TFS, TMS, TRS, 0, 6, DL)
		else:
			fsSW_NE()
			move(East)
			move(South)
			h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 7, 8)
			if h:
				own(TFS, TMS, TRS, 1, 6, DL)
			else:
				fSW_NE()
				move(East)
				move(South)
				h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 7, 8)
				if h:
					own(TFS, TMS, TRS, 2, 6, DL)
				else:
					fSW_NE()
					move(East)
					move(South)
					h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 8)
					if h:
						own(TFS, TMS, TRS, 3, 6, DL)
					else:
						fSW_NE()
						move(East)
						move(South)
						h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 8, 8)
						if h:
							own(TFS, TMS, TRS, 4, 7, DL)
						else:
							fSW_NE()
							move(East)
							move(South)
							h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 8, 8)
							if h:
								own(TFS, TMS, TRS, 5, 7, DL)
							else:
								fSW_NE()
								move(East)
								move(South)
								h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 6, 8, 8)
								if h:
									own(TFS, TMS, TRS, 6, 7, DL)
								else:
									fSW_NE()
									move(East)
									move(South)
									fSW_NE()
									move(East)
									move(South)
									fsSW_NE()
		if tl + 0.9676 > hb + 2.6:
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
	spawn_drone(w16)
	def w12():
		def w14():
			def w15():
				move(West)
				move(West)
				move(West)
				move(West)
				move(West)
				move(West)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
				till()
				move(West)
				move(West)
				move(West)
				move(West)
				move(North)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				move(North)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				move(North)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				move(North)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				move(North)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				move(North)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				move(North)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(East)
				move(North)
				till()
				plant(Entities.Cactus)
				move(South)
				till()
				plant(Entities.Cactus)
				move(South)
				plant(Entities.Cactus)
				tl = get_time()
				xcas(East, 1)
				move(North)
				fsSW_N()
				move(West)
				move(North)
				fSW_NE()
				move(West)
				move(North)
				fSW_NE()
				move(West)
				move(North)
				fSW_NE()
				move(West)
				move(North)
				fSW_NE()
				move(West)
				move(North)
				fSW_NE()
				move(West)
				move(North)
				fSW_NE()
				move(West)
				move(North)
				fsSW_NE()
				e = tl + 0.9345
				P = []
				if get_time() < e:
					move(East)
					if get_time() < e:
						move(East)
						if get_time() < e:
							move(East)
						else:
							P.append((East,))
					else:
						P.append((East, East,))
				else:
					P.append((East, East, East,))
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
				if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
					if get_entity_type() == Entities.Cactus:
						harvest()
					else:
						use_item(Items.Water)
				else:
					use_item(Items.Water)
				for q in P:
					for d in q:
						move(d)
				hb = 0
				while num_items(Items.Cactus) <= 0:
					hb = get_time()
				plant(Entities.Cactus)
				move(North)
				pkB(None)
				pkB(East)
				pkB(East)
				pkB(East)
				pkB(East)
				pkB(East)
				pkB(East)
				pkA(East, North)
				move(West)
				if use_item(Items.Water, 4):
					plant(Entities.Cactus)
					tw = get_time() - 0.0988
				else:
					plant(Entities.Cactus)
					tw = 0
				tl = get_time()
				if tw:
					tl = tw
				move(East)
				DL = tl + 0.9676
				if DL < hb + 2.6:
					DL = hb + 2.6
				TFS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
				TMS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
				TRS = ((North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West))
				h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 6, 7)
				if h:
					own(TFS, TMS, TRS, 0, 5, DL)
				else:
					fsSW_NE()
					move(East)
					move(South)
					h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 6, 7)
					if h:
						own(TFS, TMS, TRS, 1, 5, DL)
					else:
						fSW_NE()
						move(East)
						move(South)
						h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 6, 7)
						if h:
							own(TFS, TMS, TRS, 2, 5, DL)
						else:
							fSW_NE()
							move(East)
							move(South)
							h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 7)
							if h:
								own(TFS, TMS, TRS, 3, 6, DL)
							else:
								fSW_NE()
								move(East)
								move(South)
								h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 7, 7)
								if h:
									own(TFS, TMS, TRS, 4, 6, DL)
								else:
									fSW_NE()
									move(East)
									move(South)
									h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 7, 7)
									if h:
										own(TFS, TMS, TRS, 5, 6, DL)
									else:
										fSW_NE()
										move(East)
										move(South)
										fSW_NE()
										move(East)
										move(South)
										fsSW_NE()
				if tl + 0.9676 > hb + 2.6:
					wuT = tl + 0.9676
					while get_time() < wuT:
						pass
			spawn_drone(w15)
			move(West)
			move(West)
			move(North)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			move(West)
			till()
			plant(Entities.Cactus)
			move(West)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			if measure() < measure(South):
				swap(South)
			move(West)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			tl = get_time()
			move(West)
			fsSW_NE()
			move(East)
			move(South)
			fsSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fsW_NE()
			move(East)
			move(East)
			move(East)
			wk = [3, 2, 1, 0]
			cur = 3
			qi = 0
			qn = 4
			q3 = True
			q2 = True
			q1 = True
			q0 = True
			q3 = False
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q2 = False
			move(East)
			move(South)
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
				break
			q1 = False
			move(West)
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				else:
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					else:
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
				break
			q0 = False
			move(West)
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
				break
			cur = 0
			qi = 4
			while qi < qn:
				cx = wk[qi]
				qi += 1
				if cx == 0:
					q0 = False
					if cur == 1:
						move(West)
					elif cur == 2:
						move(West)
						move(West)
					elif cur == 3:
						move(West)
						move(South)
					cur = 0
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
				elif cx == 1:
					q1 = False
					if cur == 0:
						move(East)
					elif cur == 2:
						move(West)
					elif cur == 3:
						move(South)
					cur = 1
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
						else:
							swap(North)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
				elif cx == 2:
					q2 = False
					if cur == 0:
						move(East)
						move(East)
					elif cur == 1:
						move(East)
					elif cur == 3:
						move(East)
						move(South)
					cur = 2
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
				else:
					q3 = False
					if cur == 0:
						move(East)
						move(North)
					elif cur == 1:
						move(North)
					elif cur == 2:
						move(West)
						move(North)
					cur = 3
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
			c = cur
			e = tl + 0.9345
			P = []
			if c == 0:
				if get_time() < e:
					move(East)
					if get_time() < e:
						move(East)
						if get_time() < e:
							move(South)
							if get_time() < e:
								move(South)
							else:
								P.append((South,))
						else:
							P.append((South, South,))
					else:
						P.append((East, South, South,))
				else:
					P.append((East, East, South, South,))
			elif c == 1:
				if get_time() < e:
					move(East)
					if get_time() < e:
						move(South)
						if get_time() < e:
							move(South)
						else:
							P.append((South,))
					else:
						P.append((South, South,))
				else:
					P.append((East, South, South,))
			elif c == 2:
				if get_time() < e:
					move(South)
					if get_time() < e:
						move(South)
					else:
						P.append((South,))
				else:
					P.append((South, South,))
			elif c == 3:
				if get_time() < e:
					move(East)
					if get_time() < e:
						move(South)
						if get_time() < e:
							move(South)
							if get_time() < e:
								move(South)
							else:
								P.append((South,))
						else:
							P.append((South, South,))
					else:
						P.append((South, South, South,))
				else:
					P.append((East, South, South, South,))
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
			if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
				if get_entity_type() == Entities.Cactus:
					harvest()
				else:
					use_item(Items.Water)
			else:
				use_item(Items.Water)
			for q in P:
				for d in q:
					move(d)
			hb = 0
			while num_items(Items.Cactus) <= 0:
				hb = get_time()
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			if measure() < measure(South):
				swap(South)
			move(West)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			swap(West)
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			move(East)
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			move(East)
			plant(Entities.Cactus)
			if measure() < measure(West):
				swap(West)
			move(South)
			plant(Entities.Cactus)
			if measure() > measure(North):
				swap(North)
			move(East)
			plant(Entities.Cactus)
			if measure() < measure(West):
				swap(West)
			move(South)
			plant(Entities.Cactus)
			swap(South)
			plant(Entities.Cactus)
			move(South)
			move(South)
			plant(Entities.Cactus)
			swap(South)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			move(West)
			tw = 0
			if get_time() > 6.0:
				if use_item(Items.Water, 4):
					tw = 1
			plant(Entities.Cactus)
			tl = get_time()
			if tw:
				tl = tl - 0.0988
			xcas(North, 1)
			move(East)
			wk = [0, 1, 2, 3]
			cur = 0
			qi = 0
			qn = 4
			q0 = True
			q1 = True
			q2 = True
			q3 = True
			q0 = False
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						v = measure()
					else:
						swap(South)
						v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				break
			q1 = False
			move(East)
			move(South)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						v = measure()
					else:
						swap(South)
						v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				break
			q2 = False
			move(North)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					else:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						else:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				break
			q3 = False
			move(North)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
				break
			cur = 3
			qi = 4
			while qi < qn:
				cx = wk[qi]
				qi += 1
				if cx == 0:
					q0 = False
					if cur == 1:
						move(West)
						move(North)
					elif cur == 2:
						move(West)
					elif cur == 3:
						move(West)
						move(South)
					cur = 0
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				elif cx == 1:
					q1 = False
					if cur == 0:
						move(East)
						move(South)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(South)
						move(South)
					cur = 1
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				elif cx == 2:
					q2 = False
					if cur == 0:
						move(East)
					elif cur == 1:
						move(North)
					elif cur == 3:
						move(South)
					cur = 2
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
							else:
								swap(South)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
				else:
					q3 = False
					if cur == 0:
						move(East)
						move(North)
					elif cur == 1:
						move(North)
						move(North)
					elif cur == 2:
						move(North)
					cur = 3
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
			if cur == 1:
				move(West)
				move(West)
				move(North)
				move(North)
				move(North)
				move(North)
				move(North)
			elif cur == 2:
				move(West)
				move(West)
				move(North)
				move(North)
				move(North)
				move(North)
			elif cur == 3:
				move(West)
				move(West)
				move(North)
				move(North)
				move(North)
			else:
				move(West)
				move(North)
				move(North)
				move(North)
				move(North)
			wk = [0, 1, 2, 3]
			cur = 0
			qi = 0
			qn = 4
			q0 = True
			q1 = True
			q2 = True
			q3 = True
			q0 = False
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						v = measure()
					else:
						swap(South)
						v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				break
			q1 = False
			move(West)
			move(North)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						v = measure()
					else:
						swap(South)
						v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							v = measure()
						else:
							swap(South)
							v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				break
			q2 = False
			move(East)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				jb = measure(West)
				while jb == None:
					jb = measure(West)
				if not ja <= v >= jb:
					if jb > ja:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					else:
						swap(South)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
				while True:
					v = measure()
					ja = measure(South)
					jb = measure(West)
					if not ja <= v >= jb:
						if jb > ja:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						else:
							swap(South)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				break
			q3 = False
			move(East)
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
					v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
						v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
				break
			cur = 3
			qi = 4
			while qi < qn:
				cx = wk[qi]
				qi += 1
				if cx == 0:
					q0 = False
					if cur == 1:
						move(East)
						move(South)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(West)
						move(South)
					cur = 0
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				elif cx == 1:
					q1 = False
					if cur == 0:
						move(West)
						move(North)
					elif cur == 2:
						move(West)
					elif cur == 3:
						move(West)
						move(West)
					cur = 1
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								v = measure()
							else:
								swap(South)
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				elif cx == 2:
					q2 = False
					if cur == 0:
						move(North)
					elif cur == 1:
						move(East)
					elif cur == 3:
						move(West)
					cur = 2
					while True:
						v = measure()
						ja = measure(South)
						jb = measure(West)
						if not ja <= v >= jb:
							if jb > ja:
								swap(West)
								if not q1:
									wk.append(1)
									qn += 1
									q1 = True
								v = measure()
							else:
								swap(South)
								if not q0:
									wk.append(0)
									qn += 1
									q0 = True
								v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
				else:
					q3 = False
					if cur == 0:
						move(East)
						move(North)
					elif cur == 1:
						move(East)
						move(East)
					elif cur == 2:
						move(East)
					cur = 3
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
							v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
			if tl + 0.9676 > hb + 2.6:
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
		spawn_drone(w14)
		def w13():
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			tl = get_time()
			move(South)
			fsSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fsSW_NE()
			e = tl + 0.9345
			P = []
			if get_time() < e:
				move(East)
				if get_time() < e:
					move(East)
					if get_time() < e:
						move(South)
						if get_time() < e:
							move(South)
						else:
							P.append((South,))
					else:
						P.append((South, South,))
				else:
					P.append((East, South, South,))
			else:
				P.append((East, East, South, South,))
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
			if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
				if get_entity_type() == Entities.Cactus:
					harvest()
				else:
					use_item(Items.Water)
			else:
				use_item(Items.Water)
			for q in P:
				for d in q:
					move(d)
			hb = 0
			while num_items(Items.Cactus) <= 0:
				hb = get_time()
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			swap(South)
			pkB(None)
			pkB(East)
			pkB(East)
			pkB(East)
			pkB(East)
			pkB(East)
			pkA(East, North)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			tl = get_time()
			if use_item(Items.Fertilizer):
				tl = get_time() - 0.0988
			DL = tl + 0.9676
			if DL < hb + 2.6:
				DL = hb + 2.6
			TFS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
			TMS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
			TRS = ((North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West))
			h = get_time() + 0.8100 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 7, 8)
			if h:
				own(TFS, TMS, TRS, 0, 6, DL)
			else:
				fsSW_NE()
				move(East)
				move(South)
				h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 7, 8)
				if h:
					own(TFS, TMS, TRS, 1, 6, DL)
				else:
					fSW_NE()
					move(East)
					move(South)
					h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 7, 8)
					if h:
						own(TFS, TMS, TRS, 2, 6, DL)
					else:
						fSW_NE()
						move(East)
						move(South)
						h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 8)
						if h:
							own(TFS, TMS, TRS, 3, 6, DL)
						else:
							fSW_NE()
							move(East)
							move(South)
							h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 8, 8)
							if h:
								own(TFS, TMS, TRS, 4, 7, DL)
							else:
								fSW_NE()
								move(East)
								move(South)
								h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 8, 8)
								if h:
									own(TFS, TMS, TRS, 5, 7, DL)
								else:
									fSW_NE()
									move(East)
									move(South)
									h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 6, 8, 8)
									if h:
										own(TFS, TMS, TRS, 6, 7, DL)
									else:
										fSW_NE()
										move(East)
										move(South)
										fSW_NE()
										move(East)
										move(South)
										fsSW_NE()
			if tl + 0.9676 > hb + 2.6:
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
		spawn_drone(w13)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		tl = get_time()
		move(North)
		till()
		wA = use_item(Items.Water, 4)
		plant(Entities.Cactus)
		move(South)
		fsSW_NE()
		move(East)
		move(South)
		fSW_NE()
		move(East)
		move(South)
		fSW_NE()
		move(East)
		move(South)
		fSW_NE()
		move(East)
		move(South)
		fSW_NE()
		move(East)
		move(South)
		fSW_NE()
		move(East)
		move(South)
		fsSW_NE()
		e = tl + 0.9345
		P = []
		if get_time() < e:
			move(East)
			if get_time() < e:
				move(East)
				if get_time() < e:
					move(South)
				else:
					P.append((South,))
			else:
				P.append((East, South,))
		else:
			P.append((East, East, South,))
		wuT = tl + 0.9676
		while get_time() < wuT:
			pass
		if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
			if get_entity_type() == Entities.Cactus:
				harvest()
			else:
				use_item(Items.Water)
		else:
			use_item(Items.Water)
		for q in P:
			for d in q:
				move(d)
		hb = 0
		while num_items(Items.Cactus) <= 0:
			hb = get_time()
		plant(Entities.Cactus)
		move(West)
		plant(Entities.Cactus)
		swap(South)
		pkB(None)
		pkB(East)
		pkB(East)
		pkB(East)
		pkB(East)
		pkB(East)
		pkB(East)
		tq = pkq()
		tl = get_time()
		if use_item(Items.Water, 4):
			tl = get_time() - 0.0988
			if wA:
				tl = tq
		DL = tl + 0.9676
		if DL < hb + 2.6:
			DL = hb + 2.6
		TFS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		TMS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
		TRS = ((North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West))
		h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 6, 7)
		if h:
			own(TFS, TMS, TRS, 0, 5, DL)
		else:
			fsSW_NE()
			move(East)
			move(South)
			h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 6, 7)
			if h:
				own(TFS, TMS, TRS, 1, 5, DL)
			else:
				fSW_NE()
				move(East)
				move(South)
				h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 6, 7)
				if h:
					own(TFS, TMS, TRS, 2, 5, DL)
				else:
					fSW_NE()
					move(East)
					move(South)
					h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 7)
					if h:
						own(TFS, TMS, TRS, 3, 6, DL)
					else:
						fSW_NE()
						move(East)
						move(South)
						h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 7, 7)
						if h:
							own(TFS, TMS, TRS, 4, 6, DL)
						else:
							fSW_NE()
							move(East)
							move(South)
							h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 7, 7)
							if h:
								own(TFS, TMS, TRS, 5, 6, DL)
							else:
								fSW_NE()
								move(East)
								move(South)
								fSW_NE()
								move(East)
								move(South)
								fsSW_NE()
		if tl + 0.9676 > hb + 2.6:
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
	spawn_drone(w12)
	def w9():
		def w11():
			move(East)
			move(East)
			move(East)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(East)
			move(East)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			if measure() < measure(South):
				swap(South)
			move(West)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			move(South)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			till()
			plant(Entities.Cactus)
			if measure() < measure(West):
				swap(West)
			move(South)
			till()
			plant(Entities.Cactus)
			tl = get_time()
			fsS_NE()
			move(North)
			move(North)
			move(North)
			wk = [3, 2, 1, 0]
			cur = 3
			qi = 0
			qn = 4
			q3 = True
			q2 = True
			q1 = True
			q0 = True
			q3 = False
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q2 = False
			move(West)
			move(North)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q1 = False
			move(South)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				else:
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					else:
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				break
			q0 = False
			move(South)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
				break
			cur = 0
			qi = 4
			while qi < qn:
				cx = wk[qi]
				qi += 1
				if cx == 0:
					q0 = False
					if cur == 1:
						move(South)
					elif cur == 2:
						move(South)
						move(South)
					elif cur == 3:
						move(West)
						move(South)
					cur = 0
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
				elif cx == 1:
					q1 = False
					if cur == 0:
						move(North)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(West)
					cur = 1
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
						else:
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
				elif cx == 2:
					q2 = False
					if cur == 0:
						move(North)
						move(North)
					elif cur == 1:
						move(North)
					elif cur == 3:
						move(West)
						move(North)
					cur = 2
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
				else:
					q3 = False
					if cur == 0:
						move(East)
						move(North)
					elif cur == 1:
						move(East)
					elif cur == 2:
						move(East)
						move(South)
					cur = 3
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
			if cur == 0:
				move(East)
				move(East)
				move(East)
			elif cur == 1:
				move(East)
				move(East)
				move(East)
				move(South)
			elif cur == 2:
				move(East)
				move(East)
				move(East)
				move(South)
				move(South)
			else:
				move(East)
				move(East)
				move(South)
			i_v = measure()
			i_s = measure(South)
			i_w = measure(West)
			if not i_s <= i_v >= i_w:
				if i_w > i_s:
					swap(West)
					i_q = i_w
					i_w = i_v
					i_v = i_q
				else:
					swap(South)
					i_q = i_s
					i_s = i_v
					i_v = i_q
			i_a = measure(East)
			while i_a < i_v:
				swap(East)
				i_q = i_a
				i_a = i_v
				i_v = i_q
				if not i_s <= i_v >= i_w:
					if i_w > i_s:
						swap(West)
						i_q = i_w
						i_w = i_v
						i_v = i_q
					else:
						swap(South)
						i_q = i_s
						i_s = i_v
						i_v = i_q
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fsSW_NE()
			e = tl + 0.9345
			P = []
			if get_time() < e:
				move(South)
			else:
				P.append((South,))
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
			if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
				if get_entity_type() == Entities.Cactus:
					harvest()
				else:
					use_item(Items.Water)
			else:
				use_item(Items.Water)
			for q in P:
				for d in q:
					move(d)
			hb = 0
			while num_items(Items.Cactus) <= 0:
				hb = get_time()
			plant(Entities.Cactus)
			move(North)
			pkB(None)
			pkB(East)
			pkA(East, North)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			if measure() < measure(South):
				swap(South)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			swap(North)
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			swap(South)
			plant(Entities.Cactus)
			tl = get_time()
			if tl > 6.0:
				if use_item(Items.Water, 4):
					tl = get_time() - 0.0988
			move(South)
			xcas(East, 1)
			move(North)
			move(East)
			move(North)
			wk = [3, 2, 1, 0]
			cur = 3
			qi = 0
			qn = 4
			q3 = True
			q2 = True
			q1 = True
			q0 = True
			q3 = False
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q2 = False
			move(West)
			move(North)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q1 = False
			move(South)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				else:
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					else:
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				break
			q0 = False
			move(South)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
				break
			cur = 0
			qi = 4
			while qi < qn:
				cx = wk[qi]
				qi += 1
				if cx == 0:
					q0 = False
					if cur == 1:
						move(South)
					elif cur == 2:
						move(South)
						move(South)
					elif cur == 3:
						move(West)
						move(South)
					cur = 0
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
				elif cx == 1:
					q1 = False
					if cur == 0:
						move(North)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(West)
					cur = 1
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
						else:
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
				elif cx == 2:
					q2 = False
					if cur == 0:
						move(North)
						move(North)
					elif cur == 1:
						move(North)
					elif cur == 3:
						move(West)
						move(North)
					cur = 2
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
				else:
					q3 = False
					if cur == 0:
						move(East)
						move(North)
					elif cur == 1:
						move(East)
					elif cur == 2:
						move(East)
						move(South)
					cur = 3
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
			if cur == 0:
				move(East)
				move(East)
				move(East)
			elif cur == 1:
				move(East)
				move(East)
				move(East)
				move(South)
			elif cur == 2:
				move(East)
				move(East)
				move(East)
				move(South)
				move(South)
			else:
				move(East)
				move(East)
				move(South)
			fsSW_E()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fsSW_NE()
			if tl + 0.9676 > hb + 2.6:
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
		spawn_drone(w11)
		def w10():
			move(East)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			tl = get_time()
			move(West)
			fsSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fsSW_NE()
			e = tl + 0.9345
			P = []
			if get_time() < e:
				move(West)
				if get_time() < e:
					move(North)
					if get_time() < e:
						move(North)
					else:
						P.append((North,))
				else:
					P.append((North, North,))
			else:
				P.append((West, North, North,))
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
			if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
				if get_entity_type() == Entities.Cactus:
					harvest()
				else:
					use_item(Items.Water)
			else:
				use_item(Items.Water)
			for q in P:
				for d in q:
					move(d)
			hb = 0
			while num_items(Items.Cactus) <= 0:
				hb = get_time()
			plant(Entities.Cactus)
			move(South)
			pkC(None)
			pkC(West)
			pkC(West)
			pkC(West)
			pkC(West)
			pkC(West)
			pkC(West)
			pkA(West, South)
			move(East)
			plant(Entities.Cactus)
			tl = get_time()
			if use_item(Items.Fertilizer):
				tl = get_time() - 0.0988
			move(West)
			DL = tl + 0.9676
			if DL < hb + 2.6:
				DL = hb + 2.6
			TFS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsS_NE)
			TMS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
			TRS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
			h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 6, 7)
			if h:
				own(TFS, TMS, TRS, 0, 5, DL)
			else:
				fsSW_NE()
				move(West)
				move(North)
				h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 6, 7)
				if h:
					own(TFS, TMS, TRS, 1, 5, DL)
				else:
					fSW_NE()
					move(West)
					move(North)
					h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 6, 7)
					if h:
						own(TFS, TMS, TRS, 2, 5, DL)
					else:
						fSW_NE()
						move(West)
						move(North)
						h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 7)
						if h:
							own(TFS, TMS, TRS, 3, 6, DL)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 7, 7)
							if h:
								own(TFS, TMS, TRS, 4, 6, DL)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 7, 7)
								if h:
									own(TFS, TMS, TRS, 5, 6, DL)
								else:
									fSW_NE()
									move(West)
									move(North)
									fSW_NE()
									move(West)
									move(North)
									fsS_NE()
			if tl + 0.9676 > hb + 2.6:
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
		spawn_drone(w10)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		till()
		move(East)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		tl = get_time()
		fsSW_NE()
		move(West)
		move(North)
		fSW_NE()
		move(West)
		move(North)
		fSW_NE()
		move(West)
		move(North)
		fSW_NE()
		move(West)
		move(North)
		fSW_NE()
		move(West)
		move(North)
		fSW_NE()
		move(West)
		move(North)
		fSW_NE()
		move(West)
		move(North)
		fsSW_NE()
		e = tl + 0.9345
		P = []
		if get_time() < e:
			move(West)
			if get_time() < e:
				move(North)
			else:
				P.append((North,))
		else:
			P.append((West, North,))
		wuT = tl + 0.9676
		while get_time() < wuT:
			pass
		if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
			if get_entity_type() == Entities.Cactus:
				harvest()
			else:
				use_item(Items.Water)
		else:
			use_item(Items.Water)
		for q in P:
			for d in q:
				move(d)
		hb = 0
		while num_items(Items.Cactus) <= 0:
			hb = get_time()
		plant(Entities.Cactus)
		move(South)
		plant(Entities.Cactus)
		move(East)
		plant(Entities.Cactus)
		swap(North)
		pkC(None)
		pkC(West)
		pkC(West)
		pkC(West)
		pkC(West)
		pkC(West)
		pkA(West, South)
		move(East)
		plant(Entities.Cactus)
		move(South)
		tw = 0
		if get_time() > 6.0:
			if use_item(Items.Water, 4):
				tw = 1
		plant(Entities.Cactus)
		tl = get_time()
		if tw:
			tl = tl - 0.0988
		DL = tl + 0.9676
		if DL < hb + 2.6:
			DL = hb + 2.6
		TFS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		TMS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
		TRS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
		h = get_time() + 0.8100 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 7, 8)
		if h:
			own(TFS, TMS, TRS, 0, 6, DL)
		else:
			fsSW_NE()
			move(West)
			move(North)
			h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 7, 8)
			if h:
				own(TFS, TMS, TRS, 1, 6, DL)
			else:
				fSW_NE()
				move(West)
				move(North)
				h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 7, 8)
				if h:
					own(TFS, TMS, TRS, 2, 6, DL)
				else:
					fSW_NE()
					move(West)
					move(North)
					h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 8)
					if h:
						own(TFS, TMS, TRS, 3, 6, DL)
					else:
						fSW_NE()
						move(West)
						move(North)
						h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 8, 8)
						if h:
							own(TFS, TMS, TRS, 4, 7, DL)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 8, 8)
							if h:
								own(TFS, TMS, TRS, 5, 7, DL)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 6, 8, 8)
								if h:
									own(TFS, TMS, TRS, 6, 7, DL)
								else:
									fSW_NE()
									move(West)
									move(North)
									fSW_NE()
									move(West)
									move(North)
									fsSW_NE()
		if tl + 0.9676 > hb + 2.6:
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
	spawn_drone(w9)
	def w6():
		def w8():
			move(West)
			move(West)
			move(West)
			move(North)
			move(North)
			till()
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			till()
			plant(Entities.Cactus)
			move(North)
			move(North)
			move(North)
			move(North)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			till()
			plant(Entities.Cactus)
			if measure() < measure(West):
				swap(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(West)
			till()
			plant(Entities.Cactus)
			move(West)
			till()
			plant(Entities.Cactus)
			move(West)
			till()
			plant(Entities.Cactus)
			tl = get_time()
			xcas(North, 1)
			move(East)
			move(East)
			move(North)
			wk = [3, 2, 1, 0]
			cur = 3
			qi = 0
			qn = 4
			q3 = True
			q2 = True
			q1 = True
			q0 = True
			q3 = False
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q2 = False
			move(East)
			move(South)
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q1 = False
			move(West)
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				else:
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					else:
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
				break
			q0 = False
			move(West)
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
				break
			cur = 0
			qi = 4
			while qi < qn:
				cx = wk[qi]
				qi += 1
				if cx == 0:
					q0 = False
					if cur == 1:
						move(West)
					elif cur == 2:
						move(West)
						move(West)
					elif cur == 3:
						move(West)
						move(South)
					cur = 0
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
				elif cx == 1:
					q1 = False
					if cur == 0:
						move(East)
					elif cur == 2:
						move(West)
					elif cur == 3:
						move(South)
					cur = 1
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
						else:
							swap(North)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
				elif cx == 2:
					q2 = False
					if cur == 0:
						move(East)
						move(East)
					elif cur == 1:
						move(East)
					elif cur == 3:
						move(East)
						move(South)
					cur = 2
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
				else:
					q3 = False
					if cur == 0:
						move(East)
						move(North)
					elif cur == 1:
						move(North)
					elif cur == 2:
						move(West)
						move(North)
					cur = 3
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
			if cur == 0:
				move(North)
				move(North)
				move(North)
			elif cur == 1:
				move(West)
				move(North)
				move(North)
				move(North)
			elif cur == 2:
				move(West)
				move(West)
				move(North)
				move(North)
				move(North)
			else:
				move(West)
				move(North)
				move(North)
			fsSW_N()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fsSW_NE()
			e = tl + 0.9345
			P = []
			if get_time() < e:
				move(West)
			else:
				P.append((West,))
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
			if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
				if get_entity_type() == Entities.Cactus:
					harvest()
				else:
					use_item(Items.Water)
			else:
				use_item(Items.Water)
			for q in P:
				for d in q:
					move(d)
			hb = 0
			while num_items(Items.Cactus) <= 0:
				hb = get_time()
			plant(Entities.Cactus)
			move(East)
			plant(Entities.Cactus)
			swap(North)
			pkC(None)
			pkC(West)
			pkC(West)
			pkA(West, South)
			move(East)
			move(South)
			plant(Entities.Cactus)
			if measure() < measure(West):
				swap(West)
			move(South)
			plant(Entities.Cactus)
			move(East)
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			swap(East)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			move(West)
			tw = 0
			if get_time() > 6.0:
				if use_item(Items.Water, 4):
					tw = 1
			plant(Entities.Cactus)
			tl = get_time()
			if tw:
				tl = tl - 0.0988
			xcas(North, 1)
			move(East)
			move(East)
			move(North)
			wk = [3, 2, 1, 0]
			cur = 3
			qi = 0
			qn = 4
			q3 = True
			q2 = True
			q1 = True
			q0 = True
			q3 = False
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q2 = False
			move(East)
			move(South)
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q1 = False
			move(West)
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				else:
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					else:
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
				break
			q0 = False
			move(West)
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					v = measure()
				ja = measure(East)
				while ja == None:
					ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
				break
			cur = 0
			qi = 4
			while qi < qn:
				cx = wk[qi]
				qi += 1
				if cx == 0:
					q0 = False
					if cur == 1:
						move(West)
					elif cur == 2:
						move(West)
						move(West)
					elif cur == 3:
						move(West)
						move(South)
					cur = 0
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							v = measure()
						ja = measure(East)
						if ja >= v:
							break
						swap(East)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
				elif cx == 1:
					q1 = False
					if cur == 0:
						move(East)
					elif cur == 2:
						move(West)
					elif cur == 3:
						move(South)
					cur = 1
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
						else:
							swap(North)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
				elif cx == 2:
					q2 = False
					if cur == 0:
						move(East)
						move(East)
					elif cur == 1:
						move(East)
					elif cur == 3:
						move(East)
						move(South)
					cur = 2
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
				else:
					q3 = False
					if cur == 0:
						move(East)
						move(North)
					elif cur == 1:
						move(North)
					elif cur == 2:
						move(West)
						move(North)
					cur = 3
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
			if cur == 0:
				move(North)
				move(North)
				move(North)
			elif cur == 1:
				move(West)
				move(North)
				move(North)
				move(North)
			elif cur == 2:
				move(West)
				move(West)
				move(North)
				move(North)
				move(North)
			else:
				move(West)
				move(North)
				move(North)
			fsSW_N()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fsSW_NE()
			if tl + 0.9676 > hb + 2.6:
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
		spawn_drone(w8)
		def w7():
			move(West)
			move(North)
			till()
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			till()
			move(West)
			move(West)
			move(West)
			till()
			plant(Entities.Cactus)
			move(West)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			tl = get_time()
			move(South)
			fsSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fsW_NE()
			e = tl + 0.9345
			P = []
			if get_time() < e:
				move(East)
			else:
				P.append((East,))
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
			if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
				if get_entity_type() == Entities.Cactus:
					harvest()
				else:
					use_item(Items.Water)
			else:
				use_item(Items.Water)
			for q in P:
				for d in q:
					move(d)
			hb = 0
			while num_items(Items.Cactus) <= 0:
				hb = get_time()
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			swap(South)
			pkB(None)
			pkB(East)
			pkB(East)
			pkB(East)
			pkB(East)
			pkB(East)
			pkA(East, North)
			move(West)
			plant(Entities.Cactus)
			tl = get_time()
			move(East)
			DL = tl + 0.9676
			if DL < hb + 2.6:
				DL = hb + 2.6
			TFS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsW_NE)
			TMS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
			TRS = ((North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West))
			h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 6, 7)
			if h:
				own(TFS, TMS, TRS, 0, 5, DL)
			else:
				fsSW_NE()
				move(East)
				move(South)
				h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 6, 7)
				if h:
					own(TFS, TMS, TRS, 1, 5, DL)
				else:
					fSW_NE()
					move(East)
					move(South)
					h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 6, 7)
					if h:
						own(TFS, TMS, TRS, 2, 5, DL)
					else:
						fSW_NE()
						move(East)
						move(South)
						h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 7)
						if h:
							own(TFS, TMS, TRS, 3, 6, DL)
						else:
							fSW_NE()
							move(East)
							move(South)
							h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 7, 7)
							if h:
								own(TFS, TMS, TRS, 4, 6, DL)
							else:
								fSW_NE()
								move(East)
								move(South)
								h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 7, 7)
								if h:
									own(TFS, TMS, TRS, 5, 6, DL)
								else:
									fSW_NE()
									move(East)
									move(South)
									fSW_NE()
									move(East)
									move(South)
									fsW_NE()
			if tl + 0.9676 > hb + 2.6:
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
		spawn_drone(w7)
		move(East)
		move(East)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		till()
		move(East)
		move(East)
		move(North)
		till()
		move(East)
		till()
		move(East)
		move(East)
		till()
		move(East)
		move(East)
		move(East)
		move(East)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		tl = get_time()
		move(South)
		fsSW_NE()
		move(East)
		move(South)
		fSW_NE()
		move(East)
		move(South)
		fSW_NE()
		move(East)
		move(South)
		fSW_NE()
		move(East)
		move(South)
		fSW_NE()
		move(East)
		move(South)
		fSW_NE()
		move(East)
		move(South)
		fsSW_NE()
		wuT = tl + 0.9676
		while get_time() < wuT:
			pass
		if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
			if get_entity_type() == Entities.Cactus:
				harvest()
			else:
				use_item(Items.Water)
		else:
			use_item(Items.Water)
		hb = 0
		while num_items(Items.Cactus) <= 0:
			hb = get_time()
		plant(Entities.Cactus)
		move(North)
		plant(Entities.Cactus)
		move(West)
		plant(Entities.Cactus)
		swap(South)
		pkB(None)
		pkB(East)
		pkB(East)
		pkB(East)
		pkB(East)
		pkB(East)
		pkA(East, North)
		move(West)
		plant(Entities.Cactus)
		move(North)
		tw = 0
		if get_time() > 6.0:
			if use_item(Items.Water, 4):
				tw = 1
		plant(Entities.Cactus)
		tl = get_time()
		if tw:
			tl = tl - 0.0988
		DL = tl + 0.9676
		if DL < hb + 2.6:
			DL = hb + 2.6
		TFS = (fsSW_E, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		TMS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
		TRS = ((North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West))
		h = get_time() + 0.8100 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 7, 8)
		if h:
			own(TFS, TMS, TRS, 0, 6, DL)
		else:
			fsSW_E()
			move(East)
			move(South)
			h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 7, 8)
			if h:
				own(TFS, TMS, TRS, 1, 6, DL)
			else:
				fSW_NE()
				move(East)
				move(South)
				h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 7, 8)
				if h:
					own(TFS, TMS, TRS, 2, 6, DL)
				else:
					fSW_NE()
					move(East)
					move(South)
					h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 8)
					if h:
						own(TFS, TMS, TRS, 3, 6, DL)
					else:
						fSW_NE()
						move(East)
						move(South)
						h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 8, 8)
						if h:
							own(TFS, TMS, TRS, 4, 7, DL)
						else:
							fSW_NE()
							move(East)
							move(South)
							h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 8, 8)
							if h:
								own(TFS, TMS, TRS, 5, 7, DL)
							else:
								fSW_NE()
								move(East)
								move(South)
								h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 6, 8, 8)
								if h:
									own(TFS, TMS, TRS, 6, 7, DL)
								else:
									fSW_NE()
									move(East)
									move(South)
									fSW_NE()
									move(East)
									move(South)
									fsSW_NE()
		if tl + 0.9676 > hb + 2.6:
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
	spawn_drone(w6)
	def w3():
		def w5():
			move(East)
			move(East)
			move(East)
			move(East)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			if measure() < measure(South):
				swap(South)
			move(West)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(West)
			till()
			plant(Entities.Cactus)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			till()
			plant(Entities.Cactus)
			if measure() < measure(West):
				swap(West)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			tl = get_time()
			move(North)
			fsSW_NE()
			move(West)
			move(North)
			i_v = measure()
			i_s = measure(South)
			if i_s > i_v:
				swap(South)
				i_q = i_s
				i_s = i_v
				i_v = i_q
			i_a = measure(North)
			i_b = measure(East)
			while not i_a >= i_v <= i_b:
				if i_b < i_a:
					swap(East)
					i_q = i_b
					i_b = i_v
					i_v = i_q
				else:
					swap(North)
					i_q = i_a
					i_a = i_v
					i_v = i_q
				if i_s > i_v:
					swap(South)
					i_q = i_s
					i_s = i_v
					i_v = i_q
			move(North)
			move(North)
			move(North)
			wk = [3, 2, 1, 0]
			cur = 3
			qi = 0
			qn = 4
			q3 = True
			q2 = True
			q1 = True
			q0 = True
			q3 = False
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q2 = False
			move(West)
			move(North)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q1 = False
			move(South)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				else:
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					else:
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				break
			q0 = False
			move(South)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
				break
			cur = 0
			qi = 4
			while qi < qn:
				cx = wk[qi]
				qi += 1
				if cx == 0:
					q0 = False
					if cur == 1:
						move(South)
					elif cur == 2:
						move(South)
						move(South)
					elif cur == 3:
						move(West)
						move(South)
					cur = 0
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
				elif cx == 1:
					q1 = False
					if cur == 0:
						move(North)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(West)
					cur = 1
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
						else:
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
				elif cx == 2:
					q2 = False
					if cur == 0:
						move(North)
						move(North)
					elif cur == 1:
						move(North)
					elif cur == 3:
						move(West)
						move(North)
					cur = 2
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
				else:
					q3 = False
					if cur == 0:
						move(East)
						move(North)
					elif cur == 1:
						move(East)
					elif cur == 2:
						move(East)
						move(South)
					cur = 3
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
			if cur == 0:
				move(East)
				move(East)
				move(East)
			elif cur == 1:
				move(East)
				move(East)
				move(East)
				move(South)
			elif cur == 2:
				move(East)
				move(East)
				move(East)
				move(South)
				move(South)
			else:
				move(East)
				move(East)
				move(South)
			i_v = measure()
			i_s = measure(South)
			i_w = measure(West)
			if not i_s <= i_v >= i_w:
				if i_w > i_s:
					swap(West)
					i_q = i_w
					i_w = i_v
					i_v = i_q
				else:
					swap(South)
					i_q = i_s
					i_s = i_v
					i_v = i_q
			i_a = measure(East)
			while i_a < i_v:
				swap(East)
				i_q = i_a
				i_a = i_v
				i_v = i_q
				if not i_s <= i_v >= i_w:
					if i_w > i_s:
						swap(West)
						i_q = i_w
						i_w = i_v
						i_v = i_q
					else:
						swap(South)
						i_q = i_s
						i_s = i_v
						i_v = i_q
			move(East)
			move(South)
			fsSW_NE()
			e = tl + 0.9345
			P = []
			if get_time() < e:
				move(West)
				if get_time() < e:
					move(West)
					if get_time() < e:
						move(North)
					else:
						P.append((North,))
				else:
					P.append((West, North,))
			else:
				P.append((West, West, North,))
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
			if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
				if get_entity_type() == Entities.Cactus:
					harvest()
				else:
					use_item(Items.Water)
			else:
				use_item(Items.Water)
			for q in P:
				for d in q:
					move(d)
			hb = 0
			while num_items(Items.Cactus) <= 0:
				hb = get_time()
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			if measure() < measure(South):
				swap(South)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			swap(North)
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			swap(South)
			plant(Entities.Cactus)
			move(East)
			move(South)
			plant(Entities.Cactus)
			if measure() < measure(West):
				swap(West)
			move(South)
			plant(Entities.Cactus)
			swap(South)
			plant(Entities.Cactus)
			move(East)
			plant(Entities.Cactus)
			move(South)
			pkC(None)
			pkC(West)
			pkA(West, South)
			tl = get_time()
			fsSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fsS_NE()
			move(North)
			move(North)
			move(North)
			wk = [3, 2, 1, 0]
			cur = 3
			qi = 0
			qn = 4
			q3 = True
			q2 = True
			q1 = True
			q0 = True
			q3 = False
			while True:
				v = measure()
				ja = measure(West)
				while ja == None:
					ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q2 = False
			move(West)
			move(North)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
				break
			q1 = False
			move(South)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				jb = measure(East)
				while jb == None:
					jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				else:
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					else:
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
				break
			q0 = False
			move(South)
			while True:
				v = measure()
				ja = measure(South)
				while ja == None:
					ja = measure(South)
				if ja > v:
					swap(South)
					v = measure()
				ja = measure(North)
				while ja == None:
					ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
				break
			cur = 0
			qi = 4
			while qi < qn:
				cx = wk[qi]
				qi += 1
				if cx == 0:
					q0 = False
					if cur == 1:
						move(South)
					elif cur == 2:
						move(South)
						move(South)
					elif cur == 3:
						move(West)
						move(South)
					cur = 0
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							v = measure()
						ja = measure(North)
						if ja >= v:
							break
						swap(North)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
				elif cx == 1:
					q1 = False
					if cur == 0:
						move(North)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(West)
					cur = 1
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q0:
								wk.append(0)
								qn += 1
								q0 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
							if not q3:
								wk.append(3)
								qn += 1
								q3 = True
						else:
							swap(North)
							if not q2:
								wk.append(2)
								qn += 1
								q2 = True
				elif cx == 2:
					q2 = False
					if cur == 0:
						move(North)
						move(North)
					elif cur == 1:
						move(North)
					elif cur == 3:
						move(West)
						move(North)
					cur = 2
					while True:
						v = measure()
						ja = measure(South)
						if ja > v:
							swap(South)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
				else:
					q3 = False
					if cur == 0:
						move(East)
						move(North)
					elif cur == 1:
						move(East)
					elif cur == 2:
						move(East)
						move(South)
					cur = 3
					while True:
						v = measure()
						ja = measure(West)
						if ja > v:
							swap(West)
							if not q1:
								wk.append(1)
								qn += 1
								q1 = True
							v = measure()
						ja = measure(North)
						jb = measure(East)
						if ja >= v <= jb:
							break
						if jb < ja:
							swap(East)
						else:
							swap(North)
			if tl + 0.9676 > hb + 2.6:
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
		spawn_drone(w5)
		def w4():
			move(East)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			move(North)
			till()
			move(East)
			move(East)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			move(East)
			move(North)
			till()
			plant(Entities.Cactus)
			move(South)
			till()
			plant(Entities.Cactus)
			tl = get_time()
			fsSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fSW_NE()
			move(West)
			move(North)
			fsSW_NE()
			e = tl + 0.9345
			P = []
			if get_time() < e:
				move(East)
				if get_time() < e:
					move(East)
					if get_time() < e:
						move(South)
					else:
						P.append((South,))
				else:
					P.append((East, South,))
			else:
				P.append((East, East, South,))
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
			if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
				if get_entity_type() == Entities.Cactus:
					harvest()
				else:
					use_item(Items.Water)
			else:
				use_item(Items.Water)
			for q in P:
				for d in q:
					move(d)
			hb = 0
			while num_items(Items.Cactus) <= 0:
				hb = get_time()
			plant(Entities.Cactus)
			move(South)
			pkC(None)
			pkC(West)
			pkC(West)
			pkC(West)
			pkC(West)
			pkC(West)
			pkC(West)
			pkA(West, South)
			move(East)
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			tl = get_time()
			if use_item(Items.Fertilizer):
				tl = get_time() - 0.0988
			DL = tl + 0.9676
			if DL < hb + 2.6:
				DL = hb + 2.6
			TFS = (fsSW_N, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
			TMS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
			TRS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
			h = get_time() + 0.8100 > DL and spawn_drone(hlp, TFS, TMS, TRS, 0, 7, 8)
			if h:
				own(TFS, TMS, TRS, 0, 6, DL)
			else:
				fsSW_N()
				move(West)
				move(North)
				h = get_time() + 0.7200 > DL and spawn_drone(hlp, TFS, TMS, TRS, 1, 7, 8)
				if h:
					own(TFS, TMS, TRS, 1, 6, DL)
				else:
					fSW_NE()
					move(West)
					move(North)
					h = get_time() + 0.6300 > DL and spawn_drone(hlp, TFS, TMS, TRS, 2, 7, 8)
					if h:
						own(TFS, TMS, TRS, 2, 6, DL)
					else:
						fSW_NE()
						move(West)
						move(North)
						h = get_time() + 0.5400 > DL and spawn_drone(hlp, TFS, TMS, TRS, 3, 7, 8)
						if h:
							own(TFS, TMS, TRS, 3, 6, DL)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = get_time() + 0.4500 > DL and spawn_drone(hlp, TFS, TMS, TRS, 4, 8, 8)
							if h:
								own(TFS, TMS, TRS, 4, 7, DL)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = get_time() + 0.3600 > DL and spawn_drone(hlp, TFS, TMS, TRS, 5, 8, 8)
								if h:
									own(TFS, TMS, TRS, 5, 7, DL)
								else:
									fSW_NE()
									move(West)
									move(North)
									h = get_time() + 0.2700 > DL and spawn_drone(hlp, TFS, TMS, TRS, 6, 8, 8)
									if h:
										own(TFS, TMS, TRS, 6, 7, DL)
									else:
										fSW_NE()
										move(West)
										move(North)
										fSW_NE()
										move(West)
										move(North)
										fsSW_NE()
			if tl + 0.9676 > hb + 2.6:
				wuT = tl + 0.9676
				while get_time() < wuT:
					pass
		spawn_drone(w4)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		till()
		move(East)
		move(East)
		move(East)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		till()
		plant(Entities.Cactus)
		if measure() < measure(West):
			swap(West)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(West)
		till()
		plant(Entities.Cactus)
		move(West)
		till()
		plant(Entities.Cactus)
		move(West)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		till()
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		till()
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		tl = get_time()
		xcas(West, 0)
		move(East)
		move(East)
		move(East)
		move(South)
		wk = [3, 2, 1, 0]
		cur = 3
		qi = 0
		qn = 4
		q3 = True
		q2 = True
		q1 = True
		q0 = True
		q3 = False
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q2 = False
		move(East)
		move(South)
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q1 = False
		move(West)
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				if not q0:
					wk.append(0)
					qn += 1
					q0 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
			else:
				swap(North)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				else:
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
			break
		q0 = False
		move(West)
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				v = measure()
			ja = measure(East)
			while ja == None:
				ja = measure(East)
			if ja >= v:
				break
			swap(East)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					v = measure()
				ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
			break
		cur = 0
		qi = 4
		while qi < qn:
			cx = wk[qi]
			qi += 1
			if cx == 0:
				q0 = False
				if cur == 1:
					move(West)
				elif cur == 2:
					move(West)
					move(West)
				elif cur == 3:
					move(West)
					move(South)
				cur = 0
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
			elif cx == 1:
				q1 = False
				if cur == 0:
					move(East)
				elif cur == 2:
					move(West)
				elif cur == 3:
					move(South)
				cur = 1
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					else:
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
			elif cx == 2:
				q2 = False
				if cur == 0:
					move(East)
					move(East)
				elif cur == 1:
					move(East)
				elif cur == 3:
					move(East)
					move(South)
				cur = 2
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
			else:
				q3 = False
				if cur == 0:
					move(East)
					move(North)
				elif cur == 1:
					move(North)
				elif cur == 2:
					move(West)
					move(North)
				cur = 3
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
		if cur == 0:
			move(North)
			move(North)
			move(North)
		elif cur == 1:
			move(West)
			move(North)
			move(North)
			move(North)
		elif cur == 2:
			move(West)
			move(West)
			move(North)
			move(North)
			move(North)
		else:
			move(West)
			move(North)
			move(North)
		fsSW_N()
		move(West)
		move(North)
		fSW_NE()
		move(West)
		move(North)
		fsSW_NE()
		e = tl + 0.9345
		P = []
		if get_time() < e:
			move(East)
			if get_time() < e:
				move(East)
				if get_time() < e:
					move(South)
					if get_time() < e:
						move(South)
						if get_time() < e:
							move(South)
						else:
							P.append((South,))
					else:
						P.append((South, South,))
				else:
					P.append((South, South, South,))
			else:
				P.append((East, South, South, South,))
		else:
			P.append((East, East, South, South, South,))
		wuT = tl + 0.9676
		while get_time() < wuT:
			pass
		if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
			if get_entity_type() == Entities.Cactus:
				harvest()
			else:
				use_item(Items.Water)
		else:
			use_item(Items.Water)
		for q in P:
			for d in q:
				move(d)
		hb = 0
		while num_items(Items.Cactus) <= 0:
			hb = get_time()
		plant(Entities.Cactus)
		move(East)
		plant(Entities.Cactus)
		if measure() < measure(West):
			swap(West)
		move(South)
		plant(Entities.Cactus)
		move(East)
		plant(Entities.Cactus)
		move(South)
		plant(Entities.Cactus)
		swap(East)
		plant(Entities.Cactus)
		move(West)
		plant(Entities.Cactus)
		move(West)
		plant(Entities.Cactus)
		move(West)
		plant(Entities.Cactus)
		move(North)
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		tl = get_time()
		xcas(North, 1)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(South)
		move(South)
		move(South)
		move(South)
		move(South)
		wk = [3, 2, 1, 0]
		cur = 3
		qi = 0
		qn = 4
		q3 = True
		q2 = True
		q1 = True
		q0 = True
		q3 = False
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q2 = False
		move(East)
		move(South)
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q1 = False
		move(West)
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				if not q0:
					wk.append(0)
					qn += 1
					q0 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
			else:
				swap(North)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				else:
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
			break
		q0 = False
		move(West)
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				v = measure()
			ja = measure(East)
			while ja == None:
				ja = measure(East)
			if ja >= v:
				break
			swap(East)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					v = measure()
				ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
			break
		cur = 0
		qi = 4
		while qi < qn:
			cx = wk[qi]
			qi += 1
			if cx == 0:
				q0 = False
				if cur == 1:
					move(West)
				elif cur == 2:
					move(West)
					move(West)
				elif cur == 3:
					move(West)
					move(South)
				cur = 0
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
			elif cx == 1:
				q1 = False
				if cur == 0:
					move(East)
				elif cur == 2:
					move(West)
				elif cur == 3:
					move(South)
				cur = 1
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					else:
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
			elif cx == 2:
				q2 = False
				if cur == 0:
					move(East)
					move(East)
				elif cur == 1:
					move(East)
				elif cur == 3:
					move(East)
					move(South)
				cur = 2
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
			else:
				q3 = False
				if cur == 0:
					move(East)
					move(North)
				elif cur == 1:
					move(North)
				elif cur == 2:
					move(West)
					move(North)
				cur = 3
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
		if tl + 0.9676 > hb + 2.6:
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
	spawn_drone(w3)
	def w2():
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		move(North)
		move(North)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		till()
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		till()
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		till()
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		till()
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		till()
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		till()
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		till()
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		till()
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(South)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		till()
		plant(Entities.Cactus)
		tl = get_time()
		if measure() < measure(West):
			swap(West)
		xcas(South, 0)
		move(North)
		move(North)
		wk = [3, 2, 1, 0]
		cur = 3
		qi = 0
		qn = 4
		q3 = True
		q2 = True
		q1 = True
		q0 = True
		q3 = False
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q2 = False
		move(West)
		move(North)
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q1 = False
		move(South)
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				if not q0:
					wk.append(0)
					qn += 1
					q0 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
			else:
				swap(North)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				else:
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
			break
		q0 = False
		move(South)
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			if ja >= v:
				break
			swap(North)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					v = measure()
				ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
			break
		cur = 0
		qi = 4
		while qi < qn:
			cx = wk[qi]
			qi += 1
			if cx == 0:
				q0 = False
				if cur == 1:
					move(South)
				elif cur == 2:
					move(South)
					move(South)
				elif cur == 3:
					move(West)
					move(South)
				cur = 0
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
			elif cx == 1:
				q1 = False
				if cur == 0:
					move(North)
				elif cur == 2:
					move(South)
				elif cur == 3:
					move(West)
				cur = 1
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					else:
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
			elif cx == 2:
				q2 = False
				if cur == 0:
					move(North)
					move(North)
				elif cur == 1:
					move(North)
				elif cur == 3:
					move(West)
					move(North)
				cur = 2
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
			else:
				q3 = False
				if cur == 0:
					move(East)
					move(North)
				elif cur == 1:
					move(East)
				elif cur == 2:
					move(East)
					move(South)
				cur = 3
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
		if cur == 0:
			move(East)
			move(North)
		elif cur == 1:
			move(East)
		elif cur == 2:
			move(East)
			move(South)
		move(East)
		if measure() < measure(South):
			swap(South)
		move(South)
		if measure() > measure(East):
			swap(East)
		move(East)
		if measure() < measure(South):
			swap(South)
		move(South)
		if measure() > measure(East):
			swap(East)
		move(East)
		if measure() < measure(South):
			swap(South)
		e = tl + 0.9345
		P = []
		if get_time() < e:
			move(East)
			if get_time() < e:
				move(East)
				if get_time() < e:
					move(South)
					if get_time() < e:
						move(South)
					else:
						P.append((South,))
				else:
					P.append((South, South,))
			else:
				P.append((East, South, South,))
		else:
			P.append((East, East, South, South,))
		wuT = tl + 0.9676
		while get_time() < wuT:
			pass
		if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
			if get_entity_type() == Entities.Cactus:
				harvest()
			else:
				use_item(Items.Water)
		else:
			use_item(Items.Water)
		for q in P:
			for d in q:
				move(d)
		hb = 0
		while num_items(Items.Cactus) <= 0:
			hb = get_time()
		plant(Entities.Cactus)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		move(North)
		plant(Entities.Cactus)
		move(West)
		plant(Entities.Cactus)
		swap(North)
		plant(Entities.Cactus)
		move(South)
		plant(Entities.Cactus)
		move(South)
		plant(Entities.Cactus)
		swap(South)
		plant(Entities.Cactus)
		move(East)
		move(South)
		plant(Entities.Cactus)
		if measure() < measure(West):
			swap(West)
		move(South)
		plant(Entities.Cactus)
		if measure() > measure(North):
			swap(North)
		move(East)
		plant(Entities.Cactus)
		move(South)
		plant(Entities.Cactus)
		move(East)
		plant(Entities.Cactus)
		move(South)
		plant(Entities.Cactus)
		move(East)
		if use_item(Items.Water, 4):
			plant(Entities.Cactus)
			tw = get_time() - 0.0988
		else:
			plant(Entities.Cactus)
			tw = 0
		if measure() < measure(West):
			swap(West)
		tl = get_time()
		if tw:
			tl = tw
		move(West)
		if measure() > measure(North):
			swap(North)
		move(North)
		if measure() < measure(West):
			swap(West)
		move(West)
		if measure() > measure(North):
			swap(North)
		move(North)
		if measure() < measure(West):
			swap(West)
		move(West)
		move(North)
		move(North)
		move(North)
		wk = [3, 2, 1, 0]
		cur = 3
		qi = 0
		qn = 4
		q3 = True
		q2 = True
		q1 = True
		q0 = True
		q3 = False
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q2 = False
		move(West)
		move(North)
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q1 = False
		move(South)
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				if not q0:
					wk.append(0)
					qn += 1
					q0 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
			else:
				swap(North)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				else:
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
			break
		q0 = False
		move(South)
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			if ja >= v:
				break
			swap(North)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					v = measure()
				ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
			break
		cur = 0
		qi = 4
		while qi < qn:
			cx = wk[qi]
			qi += 1
			if cx == 0:
				q0 = False
				if cur == 1:
					move(South)
				elif cur == 2:
					move(South)
					move(South)
				elif cur == 3:
					move(West)
					move(South)
				cur = 0
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
			elif cx == 1:
				q1 = False
				if cur == 0:
					move(North)
				elif cur == 2:
					move(South)
				elif cur == 3:
					move(West)
				cur = 1
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					else:
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
			elif cx == 2:
				q2 = False
				if cur == 0:
					move(North)
					move(North)
				elif cur == 1:
					move(North)
				elif cur == 3:
					move(West)
					move(North)
				cur = 2
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
			else:
				q3 = False
				if cur == 0:
					move(East)
					move(North)
				elif cur == 1:
					move(East)
				elif cur == 2:
					move(East)
					move(South)
				cur = 3
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
		if tl + 0.9676 > hb + 2.6:
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
	spawn_drone(w2)
	def w1():
		move(East)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
		till()
		plant(Entities.Cactus)
		move(East)
		till()
		plant(Entities.Cactus)
		if measure() < measure(West):
			swap(West)
		move(South)
		plant(Entities.Cactus)
		if measure() > measure(North):
			swap(North)
		move(East)
		till()
		plant(Entities.Cactus)
		if measure() < measure(West):
			swap(West)
		move(South)
		till()
		plant(Entities.Cactus)
		if measure() > measure(North):
			swap(North)
		move(East)
		till()
		plant(Entities.Cactus)
		if measure() < measure(West):
			swap(West)
		move(South)
		till()
		plant(Entities.Cactus)
		if measure() > measure(North):
			swap(North)
		move(East)
		till()
		plant(Entities.Cactus)
		if measure() < measure(West):
			swap(West)
		move(South)
		till()
		plant(Entities.Cactus)
		if measure() > measure(North):
			swap(North)
		move(East)
		till()
		plant(Entities.Cactus)
		if measure() < measure(West):
			swap(West)
		move(South)
		till()
		plant(Entities.Cactus)
		if measure() > measure(North):
			swap(North)
		move(East)
		till()
		plant(Entities.Cactus)
		if measure() < measure(West):
			swap(West)
		move(South)
		till()
		plant(Entities.Cactus)
		if measure() > measure(North):
			swap(North)
		move(East)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(West)
		till()
		plant(Entities.Cactus)
		move(West)
		till()
		plant(Entities.Cactus)
		move(West)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		move(West)
		till()
		plant(Entities.Cactus)
		move(North)
		till()
		plant(Entities.Cactus)
		tl = get_time()
		if measure() < measure(South):
			swap(South)
		xcas(West, 0)
		move(South)
		if measure() > measure(East):
			swap(East)
		move(East)
		if measure() < measure(South):
			swap(South)
		move(South)
		if measure() > measure(East):
			swap(East)
		move(East)
		if measure() < measure(South):
			swap(South)
		move(East)
		move(East)
		wk = [3, 2, 1, 0]
		cur = 3
		qi = 0
		qn = 4
		q3 = True
		q2 = True
		q1 = True
		q0 = True
		q3 = False
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q2 = False
		move(East)
		move(South)
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q1 = False
		move(West)
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				if not q0:
					wk.append(0)
					qn += 1
					q0 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
			else:
				swap(North)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				else:
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
			break
		q0 = False
		move(West)
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				v = measure()
			ja = measure(East)
			while ja == None:
				ja = measure(East)
			if ja >= v:
				break
			swap(East)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					v = measure()
				ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
			break
		cur = 0
		qi = 4
		while qi < qn:
			cx = wk[qi]
			qi += 1
			if cx == 0:
				q0 = False
				if cur == 1:
					move(West)
				elif cur == 2:
					move(West)
					move(West)
				elif cur == 3:
					move(West)
					move(South)
				cur = 0
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
			elif cx == 1:
				q1 = False
				if cur == 0:
					move(East)
				elif cur == 2:
					move(West)
				elif cur == 3:
					move(South)
				cur = 1
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					else:
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
			elif cx == 2:
				q2 = False
				if cur == 0:
					move(East)
					move(East)
				elif cur == 1:
					move(East)
				elif cur == 3:
					move(East)
					move(South)
				cur = 2
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
			else:
				q3 = False
				if cur == 0:
					move(East)
					move(North)
				elif cur == 1:
					move(North)
				elif cur == 2:
					move(West)
					move(North)
				cur = 3
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
		if cur == 0:
			move(East)
			move(North)
		elif cur == 1:
			move(North)
		elif cur == 2:
			move(West)
			move(North)
		move(North)
		if measure() < measure(West):
			swap(West)
		e = tl + 0.9345
		P = []
		if get_time() < e:
			move(West)
			if get_time() < e:
				move(West)
				if get_time() < e:
					move(West)
					if get_time() < e:
						move(West)
						if get_time() < e:
							move(West)
							if get_time() < e:
								move(West)
								if get_time() < e:
									move(West)
									if get_time() < e:
										move(West)
										if get_time() < e:
											move(South)
										else:
											P.append((South,))
									else:
										P.append((West, South,))
								else:
									P.append((West, West, South,))
							else:
								P.append((West, West, West, South,))
						else:
							P.append((West, West, West, West, South,))
					else:
						P.append((West, West, West, West, West, South,))
				else:
					P.append((West, West, West, West, West, West, South,))
			else:
				P.append((West, West, West, West, West, West, West, South,))
		else:
			P.append((West, West, West, West, West, West, West, West, South,))
		wuT = tl + 0.9676
		while get_time() < wuT:
			pass
		if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
			if get_entity_type() == Entities.Cactus:
				harvest()
			else:
				use_item(Items.Water)
		else:
			use_item(Items.Water)
		for q in P:
			for d in q:
				move(d)
		hb = 0
		while num_items(Items.Cactus) <= 0:
			hb = get_time()
		plant(Entities.Cactus)
		move(South)
		plant(Entities.Cactus)
		if measure() > measure(North):
			swap(North)
		move(East)
		plant(Entities.Cactus)
		move(East)
		plant(Entities.Cactus)
		move(East)
		plant(Entities.Cactus)
		swap(East)
		plant(Entities.Cactus)
		move(North)
		plant(Entities.Cactus)
		move(West)
		plant(Entities.Cactus)
		move(North)
		plant(Entities.Cactus)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		plant(Entities.Cactus)
		if measure() < measure(South):
			swap(South)
		move(West)
		plant(Entities.Cactus)
		if measure() > measure(East):
			swap(East)
		move(North)
		plant(Entities.Cactus)
		swap(North)
		plant(Entities.Cactus)
		move(North)
		move(North)
		plant(Entities.Cactus)
		swap(North)
		plant(Entities.Cactus)
		move(East)
		plant(Entities.Cactus)
		move(South)
		plant(Entities.Cactus)
		move(East)
		tw = 0
		if get_time() > 6.0:
			if use_item(Items.Water, 4):
				tw = 1
		plant(Entities.Cactus)
		tl = get_time()
		if tw:
			tl = tl - 0.0988
		xcas(South, 0)
		move(West)
		wk = [3, 2, 1, 0]
		cur = 3
		qi = 0
		qn = 4
		q3 = True
		q2 = True
		q1 = True
		q0 = True
		q3 = False
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q2 = False
		move(West)
		move(North)
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q1 = False
		move(South)
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				if not q0:
					wk.append(0)
					qn += 1
					q0 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
			else:
				swap(North)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				else:
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
			break
		q0 = False
		move(South)
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			if ja >= v:
				break
			swap(North)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					v = measure()
				ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
			break
		cur = 0
		qi = 4
		while qi < qn:
			cx = wk[qi]
			qi += 1
			if cx == 0:
				q0 = False
				if cur == 1:
					move(South)
				elif cur == 2:
					move(South)
					move(South)
				elif cur == 3:
					move(West)
					move(South)
				cur = 0
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						v = measure()
					ja = measure(North)
					if ja >= v:
						break
					swap(North)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
			elif cx == 1:
				q1 = False
				if cur == 0:
					move(North)
				elif cur == 2:
					move(South)
				elif cur == 3:
					move(West)
				cur = 1
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
					else:
						swap(North)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
			elif cx == 2:
				q2 = False
				if cur == 0:
					move(North)
					move(North)
				elif cur == 1:
					move(North)
				elif cur == 3:
					move(West)
					move(North)
				cur = 2
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
			else:
				q3 = False
				if cur == 0:
					move(East)
					move(North)
				elif cur == 1:
					move(East)
				elif cur == 2:
					move(East)
					move(South)
				cur = 3
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
		if cur == 0:
			move(East)
			move(East)
			move(South)
			move(South)
			move(South)
		elif cur == 1:
			move(East)
			move(East)
			move(South)
			move(South)
			move(South)
			move(South)
		elif cur == 2:
			move(East)
			move(East)
			move(South)
			move(South)
			move(South)
			move(South)
			move(South)
		else:
			move(East)
			move(South)
			move(South)
			move(South)
			move(South)
		wk = [3, 2, 1, 0]
		cur = 3
		qi = 0
		qn = 4
		q3 = True
		q2 = True
		q1 = True
		q0 = True
		q3 = False
		while True:
			v = measure()
			ja = measure(South)
			while ja == None:
				ja = measure(South)
			if ja > v:
				swap(South)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q2 = False
		move(East)
		move(South)
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
			break
		q1 = False
		move(West)
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				if not q0:
					wk.append(0)
					qn += 1
					q0 = True
				v = measure()
			ja = measure(North)
			while ja == None:
				ja = measure(North)
			jb = measure(East)
			while jb == None:
				jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
			else:
				swap(North)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				else:
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
			break
		q0 = False
		move(West)
		while True:
			v = measure()
			ja = measure(West)
			while ja == None:
				ja = measure(West)
			if ja > v:
				swap(West)
				v = measure()
			ja = measure(East)
			while ja == None:
				ja = measure(East)
			if ja >= v:
				break
			swap(East)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					v = measure()
				ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
			break
		cur = 0
		qi = 4
		while qi < qn:
			cx = wk[qi]
			qi += 1
			if cx == 0:
				q0 = False
				if cur == 1:
					move(West)
				elif cur == 2:
					move(West)
					move(West)
				elif cur == 3:
					move(West)
					move(South)
				cur = 0
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						v = measure()
					ja = measure(East)
					if ja >= v:
						break
					swap(East)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
			elif cx == 1:
				q1 = False
				if cur == 0:
					move(East)
				elif cur == 2:
					move(West)
				elif cur == 3:
					move(South)
				cur = 1
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q0:
							wk.append(0)
							qn += 1
							q0 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
						if not q2:
							wk.append(2)
							qn += 1
							q2 = True
					else:
						swap(North)
						if not q3:
							wk.append(3)
							qn += 1
							q3 = True
			elif cx == 2:
				q2 = False
				if cur == 0:
					move(East)
					move(East)
				elif cur == 1:
					move(East)
				elif cur == 3:
					move(East)
					move(South)
				cur = 2
				while True:
					v = measure()
					ja = measure(West)
					if ja > v:
						swap(West)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
			else:
				q3 = False
				if cur == 0:
					move(East)
					move(North)
				elif cur == 1:
					move(North)
				elif cur == 2:
					move(West)
					move(North)
				cur = 3
				while True:
					v = measure()
					ja = measure(South)
					if ja > v:
						swap(South)
						if not q1:
							wk.append(1)
							qn += 1
							q1 = True
						v = measure()
					ja = measure(North)
					jb = measure(East)
					if ja >= v <= jb:
						break
					if jb < ja:
						swap(East)
					else:
						swap(North)
		if tl + 0.9676 > hb + 2.6:
			wuT = tl + 0.9676
			while get_time() < wuT:
				pass
	spawn_drone(w1)
	move(East)
	move(East)
	move(East)
	move(North)
	move(North)
	move(North)
	till()
	plant(Entities.Cactus)
	move(North)
	till()
	plant(Entities.Cactus)
	if measure() < measure(South):
		swap(South)
	move(West)
	till()
	plant(Entities.Cactus)
	if measure() > measure(East):
		swap(East)
	move(North)
	till()
	plant(Entities.Cactus)
	if measure() < measure(South):
		swap(South)
	move(West)
	till()
	plant(Entities.Cactus)
	move(North)
	till()
	plant(Entities.Cactus)
	move(West)
	till()
	plant(Entities.Cactus)
	move(North)
	till()
	plant(Entities.Cactus)
	move(South)
	move(South)
	till()
	plant(Entities.Cactus)
	move(South)
	till()
	plant(Entities.Cactus)
	move(South)
	till()
	plant(Entities.Cactus)
	move(East)
	till()
	plant(Entities.Cactus)
	if measure() < measure(West):
		swap(West)
	move(South)
	till()
	plant(Entities.Cactus)
	if measure() > measure(North):
		swap(North)
	move(East)
	till()
	plant(Entities.Cactus)
	if measure() < measure(West):
		swap(West)
	move(South)
	till()
	plant(Entities.Cactus)
	move(East)
	till()
	plant(Entities.Cactus)
	move(South)
	till()
	plant(Entities.Cactus)
	move(West)
	till()
	plant(Entities.Cactus)
	move(West)
	till()
	plant(Entities.Cactus)
	move(West)
	till()
	plant(Entities.Cactus)
	move(North)
	till()
	plant(Entities.Cactus)
	if measure() < measure(South):
		swap(South)
	tl = get_time()
	move(East)
	move(East)
	wk = [3, 2, 1, 0]
	cur = 3
	qi = 0
	qn = 4
	q3 = True
	q2 = True
	q1 = True
	q0 = True
	q3 = False
	while True:
		v = measure()
		ja = measure(South)
		while ja == None:
			ja = measure(South)
		if ja > v:
			swap(South)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			v = measure()
		ja = measure(North)
		while ja == None:
			ja = measure(North)
		jb = measure(East)
		while jb == None:
			jb = measure(East)
		if ja >= v <= jb:
			break
		if jb < ja:
			swap(East)
		else:
			swap(North)
		while True:
			v = measure()
			ja = measure(South)
			if ja > v:
				swap(South)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
		break
	q2 = False
	move(East)
	move(South)
	while True:
		v = measure()
		ja = measure(West)
		while ja == None:
			ja = measure(West)
		if ja > v:
			swap(West)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			v = measure()
		ja = measure(North)
		while ja == None:
			ja = measure(North)
		jb = measure(East)
		while jb == None:
			jb = measure(East)
		if ja >= v <= jb:
			break
		if jb < ja:
			swap(East)
		else:
			swap(North)
		while True:
			v = measure()
			ja = measure(West)
			if ja > v:
				swap(West)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
		break
	q1 = False
	move(West)
	while True:
		v = measure()
		ja = measure(West)
		while ja == None:
			ja = measure(West)
		if ja > v:
			swap(West)
			if not q0:
				wk.append(0)
				qn += 1
				q0 = True
			v = measure()
		ja = measure(North)
		while ja == None:
			ja = measure(North)
		jb = measure(East)
		while jb == None:
			jb = measure(East)
		if ja >= v <= jb:
			break
		if jb < ja:
			swap(East)
			if not q2:
				wk.append(2)
				qn += 1
				q2 = True
		else:
			swap(North)
			if not q3:
				wk.append(3)
				qn += 1
				q3 = True
		while True:
			v = measure()
			ja = measure(West)
			if ja > v:
				swap(West)
				if not q0:
					wk.append(0)
					qn += 1
					q0 = True
				v = measure()
			ja = measure(North)
			jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
			else:
				swap(North)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
		break
	q0 = False
	move(West)
	while True:
		v = measure()
		ja = measure(West)
		while ja == None:
			ja = measure(West)
		if ja > v:
			swap(West)
			v = measure()
		ja = measure(East)
		while ja == None:
			ja = measure(East)
		if ja >= v:
			break
		swap(East)
		if not q1:
			wk.append(1)
			qn += 1
			q1 = True
		while True:
			v = measure()
			ja = measure(West)
			if ja > v:
				swap(West)
				v = measure()
			ja = measure(East)
			if ja >= v:
				break
			swap(East)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
		break
	cur = 0
	qi = 4
	while qi < qn:
		cx = wk[qi]
		qi += 1
		if cx == 0:
			q0 = False
			if cur == 1:
				move(West)
			elif cur == 2:
				move(West)
				move(West)
			elif cur == 3:
				move(West)
				move(South)
			cur = 0
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					v = measure()
				ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
		elif cx == 1:
			q1 = False
			if cur == 0:
				move(East)
			elif cur == 2:
				move(West)
			elif cur == 3:
				move(South)
			cur = 1
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				else:
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
		elif cx == 2:
			q2 = False
			if cur == 0:
				move(East)
				move(East)
			elif cur == 1:
				move(East)
			elif cur == 3:
				move(East)
				move(South)
			cur = 2
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
		else:
			q3 = False
			if cur == 0:
				move(East)
				move(North)
			elif cur == 1:
				move(North)
			elif cur == 2:
				move(West)
				move(North)
			cur = 3
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
	if cur == 0:
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
	elif cur == 1:
		move(West)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
	elif cur == 2:
		move(West)
		move(West)
		move(North)
		move(North)
		move(North)
		move(North)
		move(North)
	else:
		move(West)
		move(North)
		move(North)
		move(North)
		move(North)
	wk = [3, 2, 1, 0]
	cur = 3
	qi = 0
	qn = 4
	q3 = True
	q2 = True
	q1 = True
	q0 = True
	q3 = False
	while True:
		v = measure()
		ja = measure(West)
		while ja == None:
			ja = measure(West)
		if ja > v:
			swap(West)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			v = measure()
		ja = measure(North)
		while ja == None:
			ja = measure(North)
		jb = measure(East)
		while jb == None:
			jb = measure(East)
		if ja >= v <= jb:
			break
		if jb < ja:
			swap(East)
		else:
			swap(North)
		while True:
			v = measure()
			ja = measure(West)
			if ja > v:
				swap(West)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
		break
	q2 = False
	move(West)
	move(North)
	while True:
		v = measure()
		ja = measure(South)
		while ja == None:
			ja = measure(South)
		if ja > v:
			swap(South)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			v = measure()
		ja = measure(North)
		while ja == None:
			ja = measure(North)
		jb = measure(East)
		while jb == None:
			jb = measure(East)
		if ja >= v <= jb:
			break
		if jb < ja:
			swap(East)
		else:
			swap(North)
		while True:
			v = measure()
			ja = measure(South)
			if ja > v:
				swap(South)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
		break
	q1 = False
	move(South)
	while True:
		v = measure()
		ja = measure(South)
		while ja == None:
			ja = measure(South)
		if ja > v:
			swap(South)
			if not q0:
				wk.append(0)
				qn += 1
				q0 = True
			v = measure()
		ja = measure(North)
		while ja == None:
			ja = measure(North)
		jb = measure(East)
		while jb == None:
			jb = measure(East)
		if ja >= v <= jb:
			break
		if jb < ja:
			swap(East)
			if not q3:
				wk.append(3)
				qn += 1
				q3 = True
		else:
			swap(North)
			if not q2:
				wk.append(2)
				qn += 1
				q2 = True
		while True:
			v = measure()
			ja = measure(South)
			if ja > v:
				swap(South)
				if not q0:
					wk.append(0)
					qn += 1
					q0 = True
				v = measure()
			ja = measure(North)
			jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
			else:
				swap(North)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
		break
	q0 = False
	move(South)
	while True:
		v = measure()
		ja = measure(South)
		while ja == None:
			ja = measure(South)
		if ja > v:
			swap(South)
			v = measure()
		ja = measure(North)
		while ja == None:
			ja = measure(North)
		if ja >= v:
			break
		swap(North)
		if not q1:
			wk.append(1)
			qn += 1
			q1 = True
		while True:
			v = measure()
			ja = measure(South)
			if ja > v:
				swap(South)
				v = measure()
			ja = measure(North)
			if ja >= v:
				break
			swap(North)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
		break
	cur = 0
	qi = 4
	while qi < qn:
		cx = wk[qi]
		qi += 1
		if cx == 0:
			q0 = False
			if cur == 1:
				move(South)
			elif cur == 2:
				move(South)
				move(South)
			elif cur == 3:
				move(West)
				move(South)
			cur = 0
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					v = measure()
				ja = measure(North)
				if ja >= v:
					break
				swap(North)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
		elif cx == 1:
			q1 = False
			if cur == 0:
				move(North)
			elif cur == 2:
				move(South)
			elif cur == 3:
				move(West)
			cur = 1
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
				else:
					swap(North)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
		elif cx == 2:
			q2 = False
			if cur == 0:
				move(North)
				move(North)
			elif cur == 1:
				move(North)
			elif cur == 3:
				move(West)
				move(North)
			cur = 2
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
		else:
			q3 = False
			if cur == 0:
				move(East)
				move(North)
			elif cur == 1:
				move(East)
			elif cur == 2:
				move(East)
				move(South)
			cur = 3
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
	c = cur
	e = tl + 0.9345
	P = []
	if c == 0:
		if get_time() < e:
			move(East)
			if get_time() < e:
				move(East)
			else:
				P.append((East,))
		else:
			P.append((East, East,))
	elif c == 1:
		if get_time() < e:
			move(East)
			if get_time() < e:
				move(East)
				if get_time() < e:
					move(South)
				else:
					P.append((South,))
			else:
				P.append((East, South,))
		else:
			P.append((East, East, South,))
	elif c == 2:
		if get_time() < e:
			move(East)
			if get_time() < e:
				move(East)
				if get_time() < e:
					move(South)
					if get_time() < e:
						move(South)
					else:
						P.append((South,))
				else:
					P.append((South, South,))
			else:
				P.append((East, South, South,))
		else:
			P.append((East, East, South, South,))
	elif c == 3:
		if get_time() < e:
			move(East)
			if get_time() < e:
				move(South)
			else:
				P.append((South,))
		else:
			P.append((East, South,))
	wuT = tl + 0.9676
	while get_time() < wuT:
		pass
	if (get_time() // WDT) - num_items(Items.Water) >= NSIG:
		if get_entity_type() == Entities.Cactus:
			harvest()
		else:
			use_item(Items.Water)
	else:
		use_item(Items.Water)
	for q in P:
		for d in q:
			move(d)
	while num_items(Items.Cactus) <= 0:
		pass
	hm = get_time()
	plant(Entities.Cactus)
	move(East)
	plant(Entities.Cactus)
	if measure() < measure(West):
		swap(West)
	move(South)
	plant(Entities.Cactus)
	if measure() > measure(North):
		swap(North)
	move(East)
	plant(Entities.Cactus)
	if measure() < measure(West):
		swap(West)
	move(South)
	plant(Entities.Cactus)
	if measure() > measure(North):
		swap(North)
	move(East)
	plant(Entities.Cactus)
	if measure() < measure(West):
		swap(West)
	move(South)
	plant(Entities.Cactus)
	if measure() > measure(North):
		swap(North)
	move(East)
	plant(Entities.Cactus)
	if measure() < measure(West):
		swap(West)
	move(South)
	plant(Entities.Cactus)
	if measure() > measure(North):
		swap(North)
	move(East)
	plant(Entities.Cactus)
	move(East)
	plant(Entities.Cactus)
	move(East)
	plant(Entities.Cactus)
	move(North)
	plant(Entities.Cactus)
	move(West)
	plant(Entities.Cactus)
	move(North)
	plant(Entities.Cactus)
	move(West)
	plant(Entities.Cactus)
	move(North)
	plant(Entities.Cactus)
	move(West)
	plant(Entities.Cactus)
	move(North)
	plant(Entities.Cactus)
	move(West)
	plant(Entities.Cactus)
	move(North)
	plant(Entities.Cactus)
	move(West)
	plant(Entities.Cactus)
	tl = get_time()
	if measure() > measure(East):
		swap(East)
	xcasq(North, 1)
	move(East)
	if measure() < measure(South):
		swap(South)
	move(South)
	if measure() > measure(East):
		swap(East)
	move(East)
	if measure() < measure(South):
		swap(South)
	move(South)
	if measure() > measure(East):
		swap(East)
	move(East)
	if measure() < measure(South):
		swap(South)
	move(South)
	if measure() > measure(East):
		swap(East)
	move(East)
	move(South)
	wk = [3, 2, 1, 0]
	cur = 3
	qi = 0
	qn = 4
	q3 = True
	q2 = True
	q1 = True
	q0 = True
	q3 = False
	while True:
		v = measure()
		ja = measure(South)
		while ja == None:
			ja = measure(South)
		if ja > v:
			swap(South)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			v = measure()
		ja = measure(North)
		while ja == None:
			ja = measure(North)
		jb = measure(East)
		while jb == None:
			jb = measure(East)
		if ja >= v <= jb:
			break
		if jb < ja:
			swap(East)
		else:
			swap(North)
		while True:
			v = measure()
			ja = measure(South)
			if ja > v:
				swap(South)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
			else:
				swap(North)
		break
	q2 = False
	move(East)
	move(South)
	while True:
		v = measure()
		ja = measure(West)
		while ja == None:
			ja = measure(West)
		if ja > v:
			swap(West)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
			v = measure()
		ja = measure(North)
		while ja == None:
			ja = measure(North)
		if ja >= v:
			break
		swap(North)
		while True:
			v = measure()
			ja = measure(West)
			if ja > v:
				swap(West)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
				v = measure()
			ja = measure(North)
			if ja >= v:
				break
			swap(North)
		break
	q1 = False
	move(West)
	while True:
		v = measure()
		ja = measure(West)
		while ja == None:
			ja = measure(West)
		if ja > v:
			swap(West)
			if not q0:
				wk.append(0)
				qn += 1
				q0 = True
			v = measure()
		ja = measure(North)
		while ja == None:
			ja = measure(North)
		jb = measure(East)
		while jb == None:
			jb = measure(East)
		if ja >= v <= jb:
			break
		if jb < ja:
			swap(East)
			if not q2:
				wk.append(2)
				qn += 1
				q2 = True
		else:
			swap(North)
			if not q3:
				wk.append(3)
				qn += 1
				q3 = True
		while True:
			v = measure()
			ja = measure(West)
			if ja > v:
				swap(West)
				if not q0:
					wk.append(0)
					qn += 1
					q0 = True
				v = measure()
			ja = measure(North)
			jb = measure(East)
			if ja >= v <= jb:
				break
			if jb < ja:
				swap(East)
				if not q2:
					wk.append(2)
					qn += 1
					q2 = True
			else:
				swap(North)
				if not q3:
					wk.append(3)
					qn += 1
					q3 = True
		break
	q0 = False
	move(West)
	while True:
		v = measure()
		ja = measure(West)
		while ja == None:
			ja = measure(West)
		if ja > v:
			swap(West)
			v = measure()
		ja = measure(East)
		while ja == None:
			ja = measure(East)
		if ja >= v:
			break
		swap(East)
		if not q1:
			wk.append(1)
			qn += 1
			q1 = True
		while True:
			v = measure()
			ja = measure(West)
			if ja > v:
				swap(West)
				v = measure()
			ja = measure(East)
			if ja >= v:
				break
			swap(East)
			if not q1:
				wk.append(1)
				qn += 1
				q1 = True
		break
	cur = 0
	qi = 4
	while qi < qn:
		cx = wk[qi]
		qi += 1
		if cx == 0:
			q0 = False
			if cur == 1:
				move(West)
			elif cur == 2:
				move(West)
				move(West)
			elif cur == 3:
				move(West)
				move(South)
			cur = 0
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					v = measure()
				ja = measure(East)
				if ja >= v:
					break
				swap(East)
				if not q1:
					wk.append(1)
					qn += 1
					q1 = True
		elif cx == 1:
			q1 = False
			if cur == 0:
				move(East)
			elif cur == 2:
				move(West)
			elif cur == 3:
				move(South)
			cur = 1
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q0:
						wk.append(0)
						qn += 1
						q0 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
					if not q2:
						wk.append(2)
						qn += 1
						q2 = True
				else:
					swap(North)
					if not q3:
						wk.append(3)
						qn += 1
						q3 = True
		elif cx == 2:
			q2 = False
			if cur == 0:
				move(East)
				move(East)
			elif cur == 1:
				move(East)
			elif cur == 3:
				move(East)
				move(South)
			cur = 2
			while True:
				v = measure()
				ja = measure(West)
				if ja > v:
					swap(West)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				if ja >= v:
					break
				swap(North)
		else:
			q3 = False
			if cur == 0:
				move(East)
				move(North)
			elif cur == 1:
				move(North)
			elif cur == 2:
				move(West)
				move(North)
			cur = 3
			while True:
				v = measure()
				ja = measure(South)
				if ja > v:
					swap(South)
					if not q1:
						wk.append(1)
						qn += 1
						q1 = True
					v = measure()
				ja = measure(North)
				jb = measure(East)
				if ja >= v <= jb:
					break
				if jb < ja:
					swap(East)
				else:
					swap(North)
	wuT = tl + 0.9676
	while get_time() < wuT:
		pass
	wuT = hm + 2.6
	while get_time() < wuT:
		pass
	while num_drones() > 1:
		pass
	harvest()

w0()
