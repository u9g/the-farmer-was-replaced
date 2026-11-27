WDT = 0.0390625
NSIG = 31

def wait_until(e):
	while get_time() < e:
		pass


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


KA = 3
KB = 6
KP = 6
PD = False


def pk2(dp, df, de, lo, nx):
	global PD
	plant(Entities.Cactus)
	f = 0
	if PD:
		if nx:
			v = measure()
			if not lo:
				v = 9 - v
			if v >= KP:
				swap(de)
				plant(Entities.Cactus)
				f = 2
		swap(dp)
		plant(Entities.Cactus)
		PD = False
	if not nx:
		swap(df)
		plant(Entities.Cactus)
		return
	if f == 0:
		v = measure()
		if not lo:
			v = 9 - v
		if v <= KA:
			swap(df)
			plant(Entities.Cactus)
			f = 1
		elif v >= KB:
			swap(de)
			plant(Entities.Cactus)
			f = 2
	if f == 2:
		move(df)
		plant(Entities.Cactus)
		move(de)
	else:
		move(de)
		plant(Entities.Cactus)
		move(df)
		if f == 0:
			PD = True


def hlp(K, j, lo, e):
	if K == 5:
		FS = (fsSW_N, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
		RS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
	elif K == 13:
		FS = (fsSW_E, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
		RS = ((North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West))
	elif K == 15:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsW_NE)
		MS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
		RS = ((North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West))
	elif K == 19:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
		RS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
	elif K == 21:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsS_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
		RS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
	elif K == 25:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
		RS = ((North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West))
	elif K == 27:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
		RS = ((North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West))
	elif K == 31:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
		RS = ((North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West))
	elif K == 33:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
		RS = ((North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West), (North, West))
	elif K == 37:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsS_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
		RS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
	elif K == 39:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
		RS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
	elif K == 41:
		FS = (fsSW_N, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
		RS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
	elif K == 47:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
		RS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
	elif K == 49:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
		RS = ((South, East), (South, East), (South, East), (South, East), (South, East), (South, East), (South, East))
	while j < e:
		for d in MS[j]:
			move(d)
		j += 1
	while j >= lo:
		FS[j]()
		if j > lo:
			for d in RS[j - 1]:
				move(d)
		j -= 1


def own(K, j, e):
	if K == 5:
		FS = (fsSW_N, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
	elif K == 13:
		FS = (fsSW_E, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
	elif K == 15:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsW_NE)
		MS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
	elif K == 19:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
	elif K == 21:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsS_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
	elif K == 25:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
	elif K == 27:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
	elif K == 31:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
	elif K == 33:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South), (East, South))
	elif K == 37:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsS_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
	elif K == 39:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
	elif K == 41:
		FS = (fsSW_N, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
	elif K == 47:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
	elif K == 49:
		FS = (fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE, fsSW_NE)
		MS = ((West, North), (West, North), (West, North), (West, North), (West, North), (West, North), (West, North))
	SP = [0, 0, 0, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10, 10, 11, 12, 13, 13, 14, 15, 16, 16, 17, 18, 19, 20, 20, 21, 22]
	while j <= e:
		if e - j >= 2:
			a = SP[e - j + 1]
			h = spawn_drone(hlp, K, j, j + a, e)
			if h != None:
				e = j + a - 1
		FS[j]()
		if j < e:
			for d in MS[j]:
				move(d)
		j += 1


def fS_NE():
	while True:
		v = measure()
		a = measure(South)
		if a > v:
			swap(South)
		else:
			a = measure(North)
			b = measure(East)
			if a < v:
				if b < a:
					swap(East)
				else:
					swap(North)
			elif b < v:
				swap(East)
			else:
				return


def fsS_NE():
	while True:
		v = measure()
		a = measure(South)
		if a == None:
			continue
		if a > v:
			swap(South)
		else:
			a = measure(North)
			b = measure(East)
			if a == None or b == None:
				continue
			if a < v:
				if b < a:
					swap(East)
				else:
					swap(North)
			elif b < v:
				swap(East)
			else:
				return


def fSW_E():
	while True:
		v = measure()
		a = measure(South)
		b = measure(West)
		if a > v:
			if b > a:
				swap(West)
			else:
				swap(South)
		elif b > v:
			swap(West)
		else:
			a = measure(East)
			if a < v:
				swap(East)
			else:
				return


def fsSW_E():
	while True:
		v = measure()
		a = measure(South)
		b = measure(West)
		if a == None or b == None:
			continue
		if a > v:
			if b > a:
				swap(West)
			else:
				swap(South)
		elif b > v:
			swap(West)
		else:
			a = measure(East)
			if a == None:
				continue
			if a < v:
				swap(East)
			else:
				return


def fsSW_N():
	while True:
		v = measure()
		a = measure(South)
		b = measure(West)
		if a == None or b == None:
			continue
		if a > v:
			if b > a:
				swap(West)
			else:
				swap(South)
		elif b > v:
			swap(West)
		else:
			a = measure(North)
			if a == None:
				continue
			if a < v:
				swap(North)
			else:
				return


def fSW_NE():
	while True:
		v = measure()
		a = measure(South)
		b = measure(West)
		if a > v:
			if b > a:
				swap(West)
			else:
				swap(South)
		elif b > v:
			swap(West)
		else:
			a = measure(North)
			b = measure(East)
			if a < v:
				if b < a:
					swap(East)
				else:
					swap(North)
			elif b < v:
				swap(East)
			else:
				return


def fsSW_NE():
	while True:
		v = measure()
		a = measure(South)
		b = measure(West)
		if a == None or b == None:
			continue
		if a > v:
			if b > a:
				swap(West)
			else:
				swap(South)
		elif b > v:
			swap(West)
		else:
			a = measure(North)
			b = measure(East)
			if a == None or b == None:
				continue
			if a < v:
				if b < a:
					swap(East)
				else:
					swap(North)
			elif b < v:
				swap(East)
			else:
				return


def fsW_NE():
	while True:
		v = measure()
		a = measure(West)
		if a == None:
			continue
		if a > v:
			swap(West)
		else:
			a = measure(North)
			b = measure(East)
			if a == None or b == None:
				continue
			if a < v:
				if b < a:
					swap(East)
				else:
					swap(North)
			elif b < v:
				swap(East)
			else:
				return


def w0():
	def w14():
		def w21():
			def w26():
				def w28():
					move(West)
					move(South)
					move(South)
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
							while len(wk) > 0:
								cx = wk.pop(0)
								if cx == 0:
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
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 1
										if bi == 0:
											swap(South)
										elif bi == 1:
											swap(West)
										else:
											ti = -1
											tv = v
											w = measure(East)
											while w == None:
												w = measure(East)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(East)
												if not (2 in wk):
													wk.append(2)
											else:
												break
								elif cx == 1:
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
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 1
										if bi == 0:
											swap(South)
										elif bi == 1:
											swap(West)
										else:
											ti = -1
											tv = v
											w = measure(North)
											while w == None:
												w = measure(North)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(North)
												if not (2 in wk):
													wk.append(2)
											else:
												break
								elif cx == 2:
									if cur == 0:
										move(East)
									elif cur == 1:
										move(North)
									elif cur == 3:
										move(South)
									cur = 2
									while True:
										v = measure()
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 1
										if bi == 0:
											swap(South)
											if not (1 in wk):
												wk.append(1)
										elif bi == 1:
											swap(West)
											if not (0 in wk):
												wk.append(0)
										else:
											ti = -1
											tv = v
											w = measure(North)
											while w == None:
												w = measure(North)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(North)
												if not (3 in wk):
													wk.append(3)
											else:
												break
								elif cx == 3:
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
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										if bi == 0:
											swap(South)
											if not (2 in wk):
												wk.append(2)
										else:
											ti = -1
											tv = v
											w = measure(North)
											while w == None:
												w = measure(North)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(North)
											else:
												break
							if cur == 1:
								move(West)
								move(North)
							elif cur == 2:
								move(West)
							elif cur == 3:
								move(West)
								move(South)
							move(West)
							move(North)
							move(North)
							move(North)
							move(North)
							wk = [0, 1, 2, 3]
							cur = 0
							while len(wk) > 0:
								cx = wk.pop(0)
								if cx == 0:
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
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 1
										if bi == 0:
											swap(South)
										elif bi == 1:
											swap(West)
										else:
											ti = -1
											tv = v
											w = measure(North)
											while w == None:
												w = measure(North)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(North)
												if not (2 in wk):
													wk.append(2)
											else:
												break
								elif cx == 1:
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
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 1
										if bi == 0:
											swap(South)
										elif bi == 1:
											swap(West)
										else:
											ti = -1
											tv = v
											w = measure(East)
											while w == None:
												w = measure(East)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(East)
												if not (2 in wk):
													wk.append(2)
											else:
												break
								elif cx == 2:
									if cur == 0:
										move(North)
									elif cur == 1:
										move(East)
									elif cur == 3:
										move(West)
									cur = 2
									while True:
										v = measure()
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 1
										if bi == 0:
											swap(South)
											if not (0 in wk):
												wk.append(0)
										elif bi == 1:
											swap(West)
											if not (1 in wk):
												wk.append(1)
										else:
											ti = -1
											tv = v
											w = measure(East)
											while w == None:
												w = measure(East)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(East)
												if not (3 in wk):
													wk.append(3)
											else:
												break
								elif cx == 3:
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
										bi = -1
										bv = v
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 0
										if bi == 0:
											swap(West)
											if not (2 in wk):
												wk.append(2)
										else:
											ti = -1
											tv = v
											w = measure(East)
											while w == None:
												w = measure(East)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(East)
											else:
												break
							c = cur
							wait_until(tl + 0.9676)
							use_item(Items.Water)
							if c == 0:
								move(East)
								move(East)
							elif c == 1:
								move(East)
								move(East)
								move(East)
								move(South)
							elif c == 2:
								move(East)
								move(East)
								move(South)
							elif c == 3:
								move(East)
								move(South)
							while num_items(Items.Cactus) <= 0:
								pass
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
							plant(Entities.Cactus)
							tl = get_time()
							xcas(North, 1)
							move(East)
							wk = [0, 1, 2, 3]
							cur = 0
							while len(wk) > 0:
								cx = wk.pop(0)
								if cx == 0:
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
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 1
										if bi == 0:
											swap(South)
										elif bi == 1:
											swap(West)
										else:
											ti = -1
											tv = v
											w = measure(East)
											while w == None:
												w = measure(East)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(East)
												if not (2 in wk):
													wk.append(2)
											else:
												break
								elif cx == 1:
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
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 1
										if bi == 0:
											swap(South)
										elif bi == 1:
											swap(West)
										else:
											ti = -1
											tv = v
											w = measure(North)
											while w == None:
												w = measure(North)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(North)
												if not (2 in wk):
													wk.append(2)
											else:
												break
								elif cx == 2:
									if cur == 0:
										move(East)
									elif cur == 1:
										move(North)
									elif cur == 3:
										move(South)
									cur = 2
									while True:
										v = measure()
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 1
										if bi == 0:
											swap(South)
											if not (1 in wk):
												wk.append(1)
										elif bi == 1:
											swap(West)
											if not (0 in wk):
												wk.append(0)
										else:
											ti = -1
											tv = v
											w = measure(North)
											while w == None:
												w = measure(North)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(North)
												if not (3 in wk):
													wk.append(3)
											else:
												break
								elif cx == 3:
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
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										if bi == 0:
											swap(South)
											if not (2 in wk):
												wk.append(2)
										else:
											ti = -1
											tv = v
											w = measure(North)
											while w == None:
												w = measure(North)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(North)
											else:
												break
							if cur == 1:
								move(West)
								move(North)
							elif cur == 2:
								move(West)
							elif cur == 3:
								move(West)
								move(South)
							move(West)
							move(North)
							move(North)
							move(North)
							move(North)
							wk = [0, 1, 2, 3]
							cur = 0
							while len(wk) > 0:
								cx = wk.pop(0)
								if cx == 0:
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
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 1
										if bi == 0:
											swap(South)
										elif bi == 1:
											swap(West)
										else:
											ti = -1
											tv = v
											w = measure(North)
											while w == None:
												w = measure(North)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(North)
												if not (2 in wk):
													wk.append(2)
											else:
												break
								elif cx == 1:
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
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 1
										if bi == 0:
											swap(South)
										elif bi == 1:
											swap(West)
										else:
											ti = -1
											tv = v
											w = measure(East)
											while w == None:
												w = measure(East)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(East)
												if not (2 in wk):
													wk.append(2)
											else:
												break
								elif cx == 2:
									if cur == 0:
										move(North)
									elif cur == 1:
										move(East)
									elif cur == 3:
										move(West)
									cur = 2
									while True:
										v = measure()
										bi = -1
										bv = v
										w = measure(South)
										while w == None:
											w = measure(South)
										if w > bv:
											bv = w
											bi = 0
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 1
										if bi == 0:
											swap(South)
											if not (0 in wk):
												wk.append(0)
										elif bi == 1:
											swap(West)
											if not (1 in wk):
												wk.append(1)
										else:
											ti = -1
											tv = v
											w = measure(East)
											while w == None:
												w = measure(East)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(East)
												if not (3 in wk):
													wk.append(3)
											else:
												break
								elif cx == 3:
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
										bi = -1
										bv = v
										w = measure(West)
										while w == None:
											w = measure(West)
										if w > bv:
											bv = w
											bi = 0
										if bi == 0:
											swap(West)
											if not (2 in wk):
												wk.append(2)
										else:
											ti = -1
											tv = v
											w = measure(East)
											while w == None:
												w = measure(East)
											if w < tv:
												tv = w
												ti = 0
											if ti == 0:
												swap(East)
											else:
												break
							wait_until(tl + 0.9676)
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
						xcas(East, 1)
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
						while len(wk) > 0:
							cx = wk.pop(0)
							if cx == 0:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
									elif bi == 1:
										swap(West)
									else:
										ti = -1
										tv = v
										w = measure(North)
										while w == None:
											w = measure(North)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(North)
											if not (2 in wk):
												wk.append(2)
										else:
											break
							elif cx == 1:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
									elif bi == 1:
										swap(West)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
											if not (2 in wk):
												wk.append(2)
										else:
											break
							elif cx == 2:
								if cur == 0:
									move(North)
								elif cur == 1:
									move(East)
								elif cur == 3:
									move(West)
								cur = 2
								while True:
									v = measure()
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
										if not (0 in wk):
											wk.append(0)
									elif bi == 1:
										swap(West)
										if not (1 in wk):
											wk.append(1)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
											if not (3 in wk):
												wk.append(3)
										else:
											break
							elif cx == 3:
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
									bi = -1
									bv = v
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 0
									if bi == 0:
										swap(West)
										if not (2 in wk):
											wk.append(2)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
										else:
											break
						c = cur
						wait_until(tl + 0.9676)
						use_item(Items.Water)
						if c == 0:
							move(East)
							move(East)
							move(South)
							move(South)
							move(South)
							move(South)
							move(South)
							move(South)
						elif c == 1:
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
						elif c == 2:
							move(East)
							move(East)
							move(South)
							move(South)
							move(South)
							move(South)
							move(South)
							move(South)
							move(South)
						elif c == 3:
							move(East)
							move(South)
							move(South)
							move(South)
							move(South)
							move(South)
							move(South)
							move(South)
						while num_items(Items.Cactus) <= 0:
							pass
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
						plant(Entities.Cactus)
						tl = get_time()
						xcas(East, 1)
						move(North)
						wk = [0, 1, 2, 3]
						cur = 0
						while len(wk) > 0:
							cx = wk.pop(0)
							if cx == 0:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
									elif bi == 1:
										swap(West)
									else:
										ti = -1
										tv = v
										w = measure(North)
										while w == None:
											w = measure(North)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(North)
											if not (2 in wk):
												wk.append(2)
										else:
											break
							elif cx == 1:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
									elif bi == 1:
										swap(West)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
											if not (2 in wk):
												wk.append(2)
										else:
											break
							elif cx == 2:
								if cur == 0:
									move(North)
								elif cur == 1:
									move(East)
								elif cur == 3:
									move(West)
								cur = 2
								while True:
									v = measure()
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
										if not (0 in wk):
											wk.append(0)
									elif bi == 1:
										swap(West)
										if not (1 in wk):
											wk.append(1)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
											if not (3 in wk):
												wk.append(3)
										else:
											break
							elif cx == 3:
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
									bi = -1
									bv = v
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 0
									if bi == 0:
										swap(West)
										if not (2 in wk):
											wk.append(2)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
										else:
											break
						if cur == 1:
							move(East)
							move(South)
						elif cur == 2:
							move(South)
						elif cur == 3:
							move(West)
							move(South)
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
						wait_until(tl + 0.9676)
					spawn_drone(w30)
					def w29():
						move(West)
						move(South)
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
						move(South)
						move(South)
						wk = [0, 1, 2, 3]
						cur = 0
						while len(wk) > 0:
							cx = wk.pop(0)
							if cx == 0:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
									elif bi == 1:
										swap(West)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
											if not (2 in wk):
												wk.append(2)
										else:
											break
							elif cx == 1:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
									elif bi == 1:
										swap(West)
									else:
										ti = -1
										tv = v
										w = measure(North)
										while w == None:
											w = measure(North)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(North)
											if not (2 in wk):
												wk.append(2)
										else:
											break
							elif cx == 2:
								if cur == 0:
									move(East)
								elif cur == 1:
									move(North)
								elif cur == 3:
									move(South)
								cur = 2
								while True:
									v = measure()
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
										if not (1 in wk):
											wk.append(1)
									elif bi == 1:
										swap(West)
										if not (0 in wk):
											wk.append(0)
									else:
										ti = -1
										tv = v
										w = measure(North)
										while w == None:
											w = measure(North)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(North)
											if not (3 in wk):
												wk.append(3)
										else:
											break
							elif cx == 3:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									if bi == 0:
										swap(South)
										if not (2 in wk):
											wk.append(2)
									else:
										ti = -1
										tv = v
										w = measure(North)
										while w == None:
											w = measure(North)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(North)
										else:
											break
						c = cur
						wait_until(tl + 0.9676)
						use_item(Items.Water)
						if c == 0:
							move(West)
							move(North)
							move(North)
							move(North)
							move(North)
							move(North)
							move(North)
							move(North)
						elif c == 1:
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
						elif c == 2:
							move(West)
							move(West)
							move(North)
							move(North)
							move(North)
							move(North)
							move(North)
							move(North)
							move(North)
						elif c == 3:
							move(West)
							move(West)
							move(North)
							move(North)
							move(North)
							move(North)
							move(North)
							move(North)
						while num_items(Items.Cactus) <= 0:
							pass
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
						while len(wk) > 0:
							cx = wk.pop(0)
							if cx == 0:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
									elif bi == 1:
										swap(West)
									else:
										ti = -1
										tv = v
										w = measure(North)
										while w == None:
											w = measure(North)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(North)
											if not (2 in wk):
												wk.append(2)
										else:
											break
							elif cx == 1:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
									elif bi == 1:
										swap(West)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
											if not (2 in wk):
												wk.append(2)
										else:
											break
							elif cx == 2:
								if cur == 0:
									move(North)
								elif cur == 1:
									move(East)
								elif cur == 3:
									move(West)
								cur = 2
								while True:
									v = measure()
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
										if not (0 in wk):
											wk.append(0)
									elif bi == 1:
										swap(West)
										if not (1 in wk):
											wk.append(1)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
											if not (3 in wk):
												wk.append(3)
										else:
											break
							elif cx == 3:
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
									bi = -1
									bv = v
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 0
									if bi == 0:
										swap(West)
										if not (2 in wk):
											wk.append(2)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
										else:
											break
						wait_until(tl + 0.9676)
					spawn_drone(w29)
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
					while len(wk) > 0:
						cx = wk.pop(0)
						if cx == 0:
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
								bi = -1
								bv = v
								w = measure(South)
								while w == None:
									w = measure(South)
								if w > bv:
									bv = w
									bi = 0
								w = measure(West)
								while w == None:
									w = measure(West)
								if w > bv:
									bv = w
									bi = 1
								if bi == 0:
									swap(South)
								elif bi == 1:
									swap(West)
								else:
									ti = -1
									tv = v
									w = measure(North)
									while w == None:
										w = measure(North)
									if w < tv:
										tv = w
										ti = 0
									if ti == 0:
										swap(North)
										if not (2 in wk):
											wk.append(2)
									else:
										break
						elif cx == 1:
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
								bi = -1
								bv = v
								w = measure(South)
								while w == None:
									w = measure(South)
								if w > bv:
									bv = w
									bi = 0
								w = measure(West)
								while w == None:
									w = measure(West)
								if w > bv:
									bv = w
									bi = 1
								if bi == 0:
									swap(South)
								elif bi == 1:
									swap(West)
								else:
									ti = -1
									tv = v
									w = measure(East)
									while w == None:
										w = measure(East)
									if w < tv:
										tv = w
										ti = 0
									if ti == 0:
										swap(East)
										if not (2 in wk):
											wk.append(2)
									else:
										break
						elif cx == 2:
							if cur == 0:
								move(North)
							elif cur == 1:
								move(East)
							elif cur == 3:
								move(West)
							cur = 2
							while True:
								v = measure()
								bi = -1
								bv = v
								w = measure(South)
								while w == None:
									w = measure(South)
								if w > bv:
									bv = w
									bi = 0
								w = measure(West)
								while w == None:
									w = measure(West)
								if w > bv:
									bv = w
									bi = 1
								if bi == 0:
									swap(South)
									if not (0 in wk):
										wk.append(0)
								elif bi == 1:
									swap(West)
									if not (1 in wk):
										wk.append(1)
								else:
									ti = -1
									tv = v
									w = measure(East)
									while w == None:
										w = measure(East)
									if w < tv:
										tv = w
										ti = 0
									if ti == 0:
										swap(East)
										if not (3 in wk):
											wk.append(3)
									else:
										break
						elif cx == 3:
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
								bi = -1
								bv = v
								w = measure(West)
								while w == None:
									w = measure(West)
								if w > bv:
									bv = w
									bi = 0
								if bi == 0:
									swap(West)
									if not (2 in wk):
										wk.append(2)
								else:
									ti = -1
									tv = v
									w = measure(East)
									while w == None:
										w = measure(East)
									if w < tv:
										tv = w
										ti = 0
									if ti == 0:
										swap(East)
									else:
										break
					c = cur
					wait_until(tl + 0.9676)
					use_item(Items.Water)
					if c == 0:
						move(East)
						move(South)
					elif c == 1:
						move(East)
						move(East)
						move(South)
						move(South)
					elif c == 2:
						move(East)
						move(South)
						move(South)
					elif c == 3:
						move(South)
						move(South)
					while num_items(Items.Cactus) <= 0:
						pass
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
					wait_until(tl + 0.9676)
				spawn_drone(w28)
				def w27():
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
					while len(wk) > 0:
						cx = wk.pop(0)
						if cx == 0:
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
								bi = -1
								bv = v
								w = measure(South)
								while w == None:
									w = measure(South)
								if w > bv:
									bv = w
									bi = 0
								w = measure(West)
								while w == None:
									w = measure(West)
								if w > bv:
									bv = w
									bi = 1
								if bi == 0:
									swap(South)
								elif bi == 1:
									swap(West)
								else:
									ti = -1
									tv = v
									w = measure(East)
									while w == None:
										w = measure(East)
									if w < tv:
										tv = w
										ti = 0
									if ti == 0:
										swap(East)
										if not (2 in wk):
											wk.append(2)
									else:
										break
						elif cx == 1:
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
								bi = -1
								bv = v
								w = measure(South)
								while w == None:
									w = measure(South)
								if w > bv:
									bv = w
									bi = 0
								w = measure(West)
								while w == None:
									w = measure(West)
								if w > bv:
									bv = w
									bi = 1
								if bi == 0:
									swap(South)
								elif bi == 1:
									swap(West)
								else:
									ti = -1
									tv = v
									w = measure(North)
									while w == None:
										w = measure(North)
									if w < tv:
										tv = w
										ti = 0
									if ti == 0:
										swap(North)
										if not (2 in wk):
											wk.append(2)
									else:
										break
						elif cx == 2:
							if cur == 0:
								move(East)
							elif cur == 1:
								move(North)
							elif cur == 3:
								move(South)
							cur = 2
							while True:
								v = measure()
								bi = -1
								bv = v
								w = measure(South)
								while w == None:
									w = measure(South)
								if w > bv:
									bv = w
									bi = 0
								w = measure(West)
								while w == None:
									w = measure(West)
								if w > bv:
									bv = w
									bi = 1
								if bi == 0:
									swap(South)
									if not (1 in wk):
										wk.append(1)
								elif bi == 1:
									swap(West)
									if not (0 in wk):
										wk.append(0)
								else:
									ti = -1
									tv = v
									w = measure(North)
									while w == None:
										w = measure(North)
									if w < tv:
										tv = w
										ti = 0
									if ti == 0:
										swap(North)
										if not (3 in wk):
											wk.append(3)
									else:
										break
						elif cx == 3:
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
								bi = -1
								bv = v
								w = measure(South)
								while w == None:
									w = measure(South)
								if w > bv:
									bv = w
									bi = 0
								if bi == 0:
									swap(South)
									if not (2 in wk):
										wk.append(2)
								else:
									ti = -1
									tv = v
									w = measure(North)
									while w == None:
										w = measure(North)
									if w < tv:
										tv = w
										ti = 0
									if ti == 0:
										swap(North)
									else:
										break
					if cur == 1:
						move(West)
						move(North)
					elif cur == 2:
						move(West)
					elif cur == 3:
						move(West)
						move(South)
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
					wait_until(tl + 0.9676)
					use_item(Items.Water)
					move(West)
					move(North)
					move(North)
					move(North)
					move(North)
					move(North)
					move(North)
					move(North)
					while num_items(Items.Cactus) <= 0:
						pass
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
					move(East)
					move(South)
					wk = [0, 1, 2, 3]
					cur = 0
					while len(wk) > 0:
						cx = wk.pop(0)
						if cx == 0:
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
								bi = -1
								bv = v
								w = measure(South)
								while w == None:
									w = measure(South)
								if w > bv:
									bv = w
									bi = 0
								w = measure(West)
								while w == None:
									w = measure(West)
								if w > bv:
									bv = w
									bi = 1
								if bi == 0:
									swap(South)
								elif bi == 1:
									swap(West)
								else:
									ti = -1
									tv = v
									w = measure(East)
									while w == None:
										w = measure(East)
									if w < tv:
										tv = w
										ti = 0
									if ti == 0:
										swap(East)
										if not (2 in wk):
											wk.append(2)
									else:
										break
						elif cx == 1:
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
								bi = -1
								bv = v
								w = measure(South)
								while w == None:
									w = measure(South)
								if w > bv:
									bv = w
									bi = 0
								w = measure(West)
								while w == None:
									w = measure(West)
								if w > bv:
									bv = w
									bi = 1
								if bi == 0:
									swap(South)
								elif bi == 1:
									swap(West)
								else:
									ti = -1
									tv = v
									w = measure(North)
									while w == None:
										w = measure(North)
									if w < tv:
										tv = w
										ti = 0
									if ti == 0:
										swap(North)
										if not (2 in wk):
											wk.append(2)
									else:
										break
						elif cx == 2:
							if cur == 0:
								move(East)
							elif cur == 1:
								move(North)
							elif cur == 3:
								move(South)
							cur = 2
							while True:
								v = measure()
								bi = -1
								bv = v
								w = measure(South)
								while w == None:
									w = measure(South)
								if w > bv:
									bv = w
									bi = 0
								w = measure(West)
								while w == None:
									w = measure(West)
								if w > bv:
									bv = w
									bi = 1
								if bi == 0:
									swap(South)
									if not (1 in wk):
										wk.append(1)
								elif bi == 1:
									swap(West)
									if not (0 in wk):
										wk.append(0)
								else:
									ti = -1
									tv = v
									w = measure(North)
									while w == None:
										w = measure(North)
									if w < tv:
										tv = w
										ti = 0
									if ti == 0:
										swap(North)
										if not (3 in wk):
											wk.append(3)
									else:
										break
						elif cx == 3:
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
								bi = -1
								bv = v
								w = measure(South)
								while w == None:
									w = measure(South)
								if w > bv:
									bv = w
									bi = 0
								if bi == 0:
									swap(South)
									if not (2 in wk):
										wk.append(2)
								else:
									ti = -1
									tv = v
									w = measure(North)
									while w == None:
										w = measure(North)
									if w < tv:
										tv = w
										ti = 0
									if ti == 0:
										swap(North)
									else:
										break
					wait_until(tl + 0.9676)
				spawn_drone(w27)
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
				wait_until(tl + 0.9676)
				use_item(Items.Water)
				move(West)
				move(West)
				move(West)
				move(North)
				move(North)
				move(North)
				while num_items(Items.Cactus) <= 0:
					pass
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
				plant(Entities.Cactus)
				tl = get_time()
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
				wait_until(tl + 0.9676)
			spawn_drone(w26)
			def w23():
				def w24():
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
						while len(wk) > 0:
							cx = wk.pop(0)
							if cx == 0:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
									elif bi == 1:
										swap(West)
									else:
										ti = -1
										tv = v
										w = measure(North)
										while w == None:
											w = measure(North)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(North)
											if not (2 in wk):
												wk.append(2)
										else:
											break
							elif cx == 1:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
									elif bi == 1:
										swap(West)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
											if not (2 in wk):
												wk.append(2)
										else:
											break
							elif cx == 2:
								if cur == 0:
									move(North)
								elif cur == 1:
									move(East)
								elif cur == 3:
									move(West)
								cur = 2
								while True:
									v = measure()
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
										if not (0 in wk):
											wk.append(0)
									elif bi == 1:
										swap(West)
										if not (1 in wk):
											wk.append(1)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
											if not (3 in wk):
												wk.append(3)
										else:
											break
							elif cx == 3:
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
									bi = -1
									bv = v
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 0
									if bi == 0:
										swap(West)
										if not (2 in wk):
											wk.append(2)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
										else:
											break
						c = cur
						wait_until(tl + 0.9676)
						use_item(Items.Water)
						if c == 0:
							move(East)
							move(East)
							move(East)
						elif c == 1:
							move(East)
							move(East)
							move(East)
							move(East)
							move(South)
						elif c == 2:
							move(East)
							move(East)
							move(East)
							move(South)
						elif c == 3:
							move(East)
							move(East)
							move(South)
						while num_items(Items.Cactus) <= 0:
							pass
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
						pk2(None, South, East, 1, 1)
						pk2(West, South, None, 1, 0)
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
						while len(wk) > 0:
							cx = wk.pop(0)
							if cx == 0:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
									elif bi == 1:
										swap(West)
									else:
										ti = -1
										tv = v
										w = measure(North)
										while w == None:
											w = measure(North)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(North)
											if not (2 in wk):
												wk.append(2)
										else:
											break
							elif cx == 1:
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
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
									elif bi == 1:
										swap(West)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
											if not (2 in wk):
												wk.append(2)
										else:
											break
							elif cx == 2:
								if cur == 0:
									move(North)
								elif cur == 1:
									move(East)
								elif cur == 3:
									move(West)
								cur = 2
								while True:
									v = measure()
									bi = -1
									bv = v
									w = measure(South)
									while w == None:
										w = measure(South)
									if w > bv:
										bv = w
										bi = 0
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 1
									if bi == 0:
										swap(South)
										if not (0 in wk):
											wk.append(0)
									elif bi == 1:
										swap(West)
										if not (1 in wk):
											wk.append(1)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
											if not (3 in wk):
												wk.append(3)
										else:
											break
							elif cx == 3:
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
									bi = -1
									bv = v
									w = measure(West)
									while w == None:
										w = measure(West)
									if w > bv:
										bv = w
										bi = 0
									if bi == 0:
										swap(West)
										if not (2 in wk):
											wk.append(2)
									else:
										ti = -1
										tv = v
										w = measure(East)
										while w == None:
											w = measure(East)
										if w < tv:
											tv = w
											ti = 0
										if ti == 0:
											swap(East)
										else:
											break
						wait_until(tl + 0.9676)
					spawn_drone(w25)
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
					wait_until(tl + 0.9676)
					use_item(Items.Water)
					move(East)
					move(South)
					while num_items(Items.Cactus) <= 0:
						pass
					plant(Entities.Cactus)
					move(South)
					plant(Entities.Cactus)
					move(East)
					plant(Entities.Cactus)
					swap(North)
					pk2(None, South, East, 1, 1)
					pk2(West, South, East, 1, 1)
					pk2(West, South, East, 1, 1)
					pk2(West, South, East, 1, 1)
					pk2(West, South, East, 1, 1)
					pk2(West, South, East, 1, 1)
					pk2(West, South, None, 1, 0)
					tl = get_time()
					h = spawn_drone(hlp, 49, 0, 6, 7)
					if h != None:
						own(49, 0, 5)
					else:
						fsSW_NE()
						move(West)
						move(North)
						h = spawn_drone(hlp, 49, 1, 6, 7)
						if h != None:
							own(49, 1, 5)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = spawn_drone(hlp, 49, 2, 6, 7)
							if h != None:
								own(49, 2, 5)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = spawn_drone(hlp, 49, 3, 7, 7)
								if h != None:
									own(49, 3, 6)
								else:
									fSW_NE()
									move(West)
									move(North)
									h = spawn_drone(hlp, 49, 4, 7, 7)
									if h != None:
										own(49, 4, 6)
									else:
										fSW_NE()
										move(West)
										move(North)
										h = spawn_drone(hlp, 49, 5, 7, 7)
										if h != None:
											own(49, 5, 6)
										else:
											fSW_NE()
											move(West)
											move(North)
											fSW_NE()
											move(West)
											move(North)
											fsSW_NE()
					wait_until(tl + 0.9676)
				spawn_drone(w24)
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
				fsSW_NE()
				wait_until(tl + 0.9676)
				use_item(Items.Water)
				move(East)
				while num_items(Items.Cactus) <= 0:
					pass
				plant(Entities.Cactus)
				move(South)
				pk2(None, South, East, 1, 1)
				pk2(West, South, East, 1, 1)
				pk2(West, South, East, 1, 1)
				pk2(West, South, East, 1, 1)
				pk2(West, South, East, 1, 1)
				pk2(West, South, East, 1, 1)
				pk2(West, South, None, 1, 0)
				move(East)
				plant(Entities.Cactus)
				move(South)
				plant(Entities.Cactus)
				tl = get_time()
				h = spawn_drone(hlp, 47, 0, 6, 7)
				if h != None:
					own(47, 0, 5)
				else:
					fsSW_NE()
					move(West)
					move(North)
					h = spawn_drone(hlp, 47, 1, 6, 7)
					if h != None:
						own(47, 1, 5)
					else:
						fSW_NE()
						move(West)
						move(North)
						h = spawn_drone(hlp, 47, 2, 6, 7)
						if h != None:
							own(47, 2, 5)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = spawn_drone(hlp, 47, 3, 7, 7)
							if h != None:
								own(47, 3, 6)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = spawn_drone(hlp, 47, 4, 7, 7)
								if h != None:
									own(47, 4, 6)
								else:
									fSW_NE()
									move(West)
									move(North)
									h = spawn_drone(hlp, 47, 5, 7, 7)
									if h != None:
										own(47, 5, 6)
									else:
										fSW_NE()
										move(West)
										move(North)
										fSW_NE()
										move(West)
										move(North)
										fsSW_NE()
				wait_until(tl + 0.9676)
			spawn_drone(w23)
			def w22():
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
				while len(wk) > 0:
					cx = wk.pop(0)
					if cx == 0:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 1
							if bi == 0:
								swap(South)
							elif bi == 1:
								swap(West)
							else:
								ti = -1
								tv = v
								w = measure(East)
								while w == None:
									w = measure(East)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(East)
									if not (2 in wk):
										wk.append(2)
								else:
									break
					elif cx == 1:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 1
							if bi == 0:
								swap(South)
							elif bi == 1:
								swap(West)
							else:
								ti = -1
								tv = v
								w = measure(North)
								while w == None:
									w = measure(North)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(North)
									if not (2 in wk):
										wk.append(2)
								else:
									break
					elif cx == 2:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 1
							if bi == 0:
								swap(South)
								if not (1 in wk):
									wk.append(1)
							elif bi == 1:
								swap(West)
								if not (0 in wk):
									wk.append(0)
							else:
								ti = -1
								tv = v
								w = measure(North)
								while w == None:
									w = measure(North)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(North)
									if not (3 in wk):
										wk.append(3)
								else:
									break
					elif cx == 3:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							if bi == 0:
								swap(South)
								if not (2 in wk):
									wk.append(2)
							else:
								ti = -1
								tv = v
								w = measure(North)
								while w == None:
									w = measure(North)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(North)
									if not (4 in wk):
										wk.append(4)
								else:
									break
					elif cx == 4:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 1
							if bi == 0:
								swap(South)
								if not (3 in wk):
									wk.append(3)
							elif bi == 1:
								swap(West)
							else:
								ti = -1
								tv = v
								w = measure(North)
								while w == None:
									w = measure(North)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(North)
								else:
									break
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
				move(North)
				move(North)
				move(North)
				fSW_NE()
				move(West)
				move(North)
				fsSW_NE()
				wait_until(tl + 0.9676)
				use_item(Items.Water)
				move(South)
				move(South)
				move(South)
				move(South)
				move(South)
				move(South)
				move(South)
				move(South)
				move(South)
				while num_items(Items.Cactus) <= 0:
					pass
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
				pk2(None, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, None, 0, 0)
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
				move(South)
				move(East)
				move(North)
				wk = [3, 2, 1, 0]
				cur = 3
				while len(wk) > 0:
					cx = wk.pop(0)
					if cx == 0:
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
							bi = -1
							bv = v
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 0
							if bi == 0:
								swap(West)
							else:
								ti = -1
								tv = v
								w = measure(East)
								while w == None:
									w = measure(East)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(East)
									if not (1 in wk):
										wk.append(1)
								else:
									break
					elif cx == 1:
						if cur == 0:
							move(East)
						elif cur == 2:
							move(West)
						elif cur == 3:
							move(South)
						cur = 1
						while True:
							v = measure()
							bi = -1
							bv = v
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 0
							if bi == 0:
								swap(West)
								if not (0 in wk):
									wk.append(0)
							else:
								ti = -1
								tv = v
								w = measure(North)
								while w == None:
									w = measure(North)
								if w < tv:
									tv = w
									ti = 0
								w = measure(East)
								while w == None:
									w = measure(East)
								if w < tv:
									tv = w
									ti = 1
								if ti == 0:
									swap(North)
									if not (3 in wk):
										wk.append(3)
								elif ti == 1:
									swap(East)
									if not (2 in wk):
										wk.append(2)
								else:
									break
					elif cx == 2:
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
							bi = -1
							bv = v
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 0
							if bi == 0:
								swap(West)
								if not (1 in wk):
									wk.append(1)
							else:
								ti = -1
								tv = v
								w = measure(North)
								while w == None:
									w = measure(North)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(North)
								else:
									break
					elif cx == 3:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							if bi == 0:
								swap(South)
								if not (1 in wk):
									wk.append(1)
							else:
								ti = -1
								tv = v
								w = measure(North)
								while w == None:
									w = measure(North)
								if w < tv:
									tv = w
									ti = 0
								w = measure(East)
								while w == None:
									w = measure(East)
								if w < tv:
									tv = w
									ti = 1
								if ti == 0:
									swap(North)
								elif ti == 1:
									swap(East)
								else:
									break
				wait_until(tl + 0.9676)
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
			wait_until(tl + 0.9676)
			use_item(Items.Water)
			move(East)
			move(East)
			move(East)
			while num_items(Items.Cactus) <= 0:
				pass
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
			pk2(None, North, West, 0, 1)
			pk2(East, North, None, 0, 0)
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
			while len(wk) > 0:
				cx = wk.pop(0)
				if cx == 0:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						w = measure(West)
						while w == None:
							w = measure(West)
						if w > bv:
							bv = w
							bi = 1
						if bi == 0:
							swap(South)
						elif bi == 1:
							swap(West)
						else:
							ti = -1
							tv = v
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(East)
								if not (2 in wk):
									wk.append(2)
							else:
								break
				elif cx == 1:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						w = measure(West)
						while w == None:
							w = measure(West)
						if w > bv:
							bv = w
							bi = 1
						if bi == 0:
							swap(South)
						elif bi == 1:
							swap(West)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(North)
								if not (2 in wk):
									wk.append(2)
							else:
								break
				elif cx == 2:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						w = measure(West)
						while w == None:
							w = measure(West)
						if w > bv:
							bv = w
							bi = 1
						if bi == 0:
							swap(South)
							if not (1 in wk):
								wk.append(1)
						elif bi == 1:
							swap(West)
							if not (0 in wk):
								wk.append(0)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(North)
								if not (3 in wk):
									wk.append(3)
							else:
								break
				elif cx == 3:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
							if not (2 in wk):
								wk.append(2)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(North)
								if not (4 in wk):
									wk.append(4)
							else:
								break
				elif cx == 4:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						w = measure(West)
						while w == None:
							w = measure(West)
						if w > bv:
							bv = w
							bi = 1
						if bi == 0:
							swap(South)
							if not (3 in wk):
								wk.append(3)
						elif bi == 1:
							swap(West)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(North)
							else:
								break
			wait_until(tl + 0.9676)
		spawn_drone(w21)
		def w16():
			def w18():
				def w19():
					def w20():
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
						wait_until(tl + 0.9676)
						use_item(Items.Water)
						move(East)
						move(East)
						move(South)
						move(South)
						move(South)
						move(South)
						move(South)
						while num_items(Items.Cactus) <= 0:
							pass
						plant(Entities.Cactus)
						move(South)
						pk2(None, South, East, 1, 1)
						pk2(West, South, East, 1, 1)
						pk2(West, South, East, 1, 1)
						pk2(West, South, East, 1, 1)
						pk2(West, South, East, 1, 1)
						pk2(West, South, East, 1, 1)
						pk2(West, South, East, 1, 1)
						pk2(West, South, None, 1, 0)
						move(East)
						plant(Entities.Cactus)
						move(South)
						plant(Entities.Cactus)
						tl = get_time()
						h = spawn_drone(hlp, 41, 0, 7, 8)
						if h != None:
							own(41, 0, 6)
						else:
							fsSW_N()
							move(West)
							move(North)
							h = spawn_drone(hlp, 41, 1, 7, 8)
							if h != None:
								own(41, 1, 6)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = spawn_drone(hlp, 41, 2, 7, 8)
								if h != None:
									own(41, 2, 6)
								else:
									fSW_NE()
									move(West)
									move(North)
									h = spawn_drone(hlp, 41, 3, 7, 8)
									if h != None:
										own(41, 3, 6)
									else:
										fSW_NE()
										move(West)
										move(North)
										h = spawn_drone(hlp, 41, 4, 8, 8)
										if h != None:
											own(41, 4, 7)
										else:
											fSW_NE()
											move(West)
											move(North)
											h = spawn_drone(hlp, 41, 5, 8, 8)
											if h != None:
												own(41, 5, 7)
											else:
												fSW_NE()
												move(West)
												move(North)
												h = spawn_drone(hlp, 41, 6, 8, 8)
												if h != None:
													own(41, 6, 7)
												else:
													fSW_NE()
													move(West)
													move(North)
													fSW_NE()
													move(West)
													move(North)
													fsSW_NE()
						wait_until(tl + 0.9676)
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
					wait_until(tl + 0.9676)
					use_item(Items.Water)
					move(South)
					move(South)
					move(South)
					move(South)
					move(South)
					while num_items(Items.Cactus) <= 0:
						pass
					plant(Entities.Cactus)
					move(East)
					plant(Entities.Cactus)
					swap(North)
					pk2(None, South, East, 1, 1)
					pk2(West, South, East, 1, 1)
					pk2(West, South, East, 1, 1)
					pk2(West, South, East, 1, 1)
					pk2(West, South, East, 1, 1)
					pk2(West, South, East, 1, 1)
					pk2(West, South, East, 1, 1)
					pk2(West, South, None, 1, 0)
					tl = get_time()
					h = spawn_drone(hlp, 39, 0, 6, 7)
					if h != None:
						own(39, 0, 5)
					else:
						fsSW_NE()
						move(West)
						move(North)
						h = spawn_drone(hlp, 39, 1, 6, 7)
						if h != None:
							own(39, 1, 5)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = spawn_drone(hlp, 39, 2, 6, 7)
							if h != None:
								own(39, 2, 5)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = spawn_drone(hlp, 39, 3, 7, 7)
								if h != None:
									own(39, 3, 6)
								else:
									fSW_NE()
									move(West)
									move(North)
									h = spawn_drone(hlp, 39, 4, 7, 7)
									if h != None:
										own(39, 4, 6)
									else:
										fSW_NE()
										move(West)
										move(North)
										h = spawn_drone(hlp, 39, 5, 7, 7)
										if h != None:
											own(39, 5, 6)
										else:
											fSW_NE()
											move(West)
											move(North)
											fSW_NE()
											move(West)
											move(North)
											fsSW_NE()
					wait_until(tl + 0.9676)
				spawn_drone(w19)
				move(East)
				move(East)
				move(East)
				move(East)
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
				while len(wk) > 0:
					cx = wk.pop(0)
					if cx == 0:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 1
							if bi == 0:
								swap(South)
							elif bi == 1:
								swap(West)
							else:
								ti = -1
								tv = v
								w = measure(North)
								while w == None:
									w = measure(North)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(North)
									if not (2 in wk):
										wk.append(2)
								else:
									break
					elif cx == 1:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 1
							if bi == 0:
								swap(South)
							elif bi == 1:
								swap(West)
							else:
								ti = -1
								tv = v
								w = measure(East)
								while w == None:
									w = measure(East)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(East)
									if not (2 in wk):
										wk.append(2)
								else:
									break
					elif cx == 2:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 1
							if bi == 0:
								swap(South)
								if not (0 in wk):
									wk.append(0)
							elif bi == 1:
								swap(West)
								if not (1 in wk):
									wk.append(1)
							else:
								ti = -1
								tv = v
								w = measure(East)
								while w == None:
									w = measure(East)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(East)
									if not (3 in wk):
										wk.append(3)
								else:
									break
					elif cx == 3:
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
							bi = -1
							bv = v
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 0
							if bi == 0:
								swap(West)
								if not (2 in wk):
									wk.append(2)
							else:
								ti = -1
								tv = v
								w = measure(East)
								while w == None:
									w = measure(East)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(East)
									if not (4 in wk):
										wk.append(4)
								else:
									break
					elif cx == 4:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 1
							if bi == 0:
								swap(South)
							elif bi == 1:
								swap(West)
								if not (3 in wk):
									wk.append(3)
							else:
								ti = -1
								tv = v
								w = measure(East)
								while w == None:
									w = measure(East)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(East)
								else:
									break
				c = cur
				wait_until(tl + 0.9676)
				use_item(Items.Water)
				if c == 0:
					move(East)
					move(South)
				elif c == 1:
					move(East)
					move(East)
					move(South)
					move(South)
				elif c == 2:
					move(East)
					move(South)
					move(South)
				elif c == 3:
					move(South)
					move(South)
				elif c == 4:
					move(West)
					move(South)
					move(South)
				while num_items(Items.Cactus) <= 0:
					pass
				plant(Entities.Cactus)
				move(South)
				pk2(None, South, East, 1, 1)
				pk2(West, South, East, 1, 1)
				pk2(West, South, East, 1, 1)
				pk2(West, South, East, 1, 1)
				pk2(West, South, East, 1, 1)
				pk2(West, South, East, 1, 1)
				pk2(West, South, East, 1, 1)
				pk2(West, South, None, 1, 0)
				move(East)
				plant(Entities.Cactus)
				move(South)
				plant(Entities.Cactus)
				tl = get_time()
				h = spawn_drone(hlp, 37, 0, 7, 8)
				if h != None:
					own(37, 0, 6)
				else:
					fsSW_NE()
					move(West)
					move(North)
					h = spawn_drone(hlp, 37, 1, 7, 8)
					if h != None:
						own(37, 1, 6)
					else:
						fSW_NE()
						move(West)
						move(North)
						h = spawn_drone(hlp, 37, 2, 7, 8)
						if h != None:
							own(37, 2, 6)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = spawn_drone(hlp, 37, 3, 7, 8)
							if h != None:
								own(37, 3, 6)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = spawn_drone(hlp, 37, 4, 8, 8)
								if h != None:
									own(37, 4, 7)
								else:
									fSW_NE()
									move(West)
									move(North)
									h = spawn_drone(hlp, 37, 5, 8, 8)
									if h != None:
										own(37, 5, 7)
									else:
										fSW_NE()
										move(West)
										move(North)
										h = spawn_drone(hlp, 37, 6, 8, 8)
										if h != None:
											own(37, 6, 7)
										else:
											fSW_NE()
											move(West)
											move(North)
											fSW_NE()
											move(West)
											move(North)
											fsS_NE()
				wait_until(tl + 0.9676)
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
				wait_until(tl + 0.9676)
				use_item(Items.Water)
				move(East)
				move(North)
				move(North)
				move(North)
				move(North)
				while num_items(Items.Cactus) <= 0:
					pass
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				swap(South)
				pk2(None, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, None, 0, 0)
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
				plant(Entities.Cactus)
				tl = get_time()
				xcas(East, 1)
				move(North)
				wk = [0, 1, 2, 3, 4]
				cur = 0
				while len(wk) > 0:
					cx = wk.pop(0)
					if cx == 0:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 1
							if bi == 0:
								swap(South)
							elif bi == 1:
								swap(West)
							else:
								ti = -1
								tv = v
								w = measure(North)
								while w == None:
									w = measure(North)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(North)
									if not (2 in wk):
										wk.append(2)
								else:
									break
					elif cx == 1:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 1
							if bi == 0:
								swap(South)
							elif bi == 1:
								swap(West)
							else:
								ti = -1
								tv = v
								w = measure(East)
								while w == None:
									w = measure(East)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(East)
									if not (2 in wk):
										wk.append(2)
								else:
									break
					elif cx == 2:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 1
							if bi == 0:
								swap(South)
								if not (0 in wk):
									wk.append(0)
							elif bi == 1:
								swap(West)
								if not (1 in wk):
									wk.append(1)
							else:
								ti = -1
								tv = v
								w = measure(East)
								while w == None:
									w = measure(East)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(East)
									if not (3 in wk):
										wk.append(3)
								else:
									break
					elif cx == 3:
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
							bi = -1
							bv = v
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 0
							if bi == 0:
								swap(West)
								if not (2 in wk):
									wk.append(2)
							else:
								ti = -1
								tv = v
								w = measure(East)
								while w == None:
									w = measure(East)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(East)
									if not (4 in wk):
										wk.append(4)
								else:
									break
					elif cx == 4:
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
							bi = -1
							bv = v
							w = measure(South)
							while w == None:
								w = measure(South)
							if w > bv:
								bv = w
								bi = 0
							w = measure(West)
							while w == None:
								w = measure(West)
							if w > bv:
								bv = w
								bi = 1
							if bi == 0:
								swap(South)
							elif bi == 1:
								swap(West)
								if not (3 in wk):
									wk.append(3)
							else:
								ti = -1
								tv = v
								w = measure(East)
								while w == None:
									w = measure(East)
								if w < tv:
									tv = w
									ti = 0
								if ti == 0:
									swap(East)
								else:
									break
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
				wait_until(tl + 0.9676)
			spawn_drone(w17)
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
			fsSW_NE()
			wait_until(tl + 0.9676)
			use_item(Items.Water)
			move(East)
			move(North)
			move(North)
			move(North)
			while num_items(Items.Cactus) <= 0:
				pass
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			swap(South)
			pk2(None, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, None, 0, 0)
			move(West)
			plant(Entities.Cactus)
			move(North)
			plant(Entities.Cactus)
			tl = get_time()
			h = spawn_drone(hlp, 33, 0, 7, 8)
			if h != None:
				own(33, 0, 6)
			else:
				fsSW_NE()
				move(East)
				move(South)
				h = spawn_drone(hlp, 33, 1, 7, 8)
				if h != None:
					own(33, 1, 6)
				else:
					fSW_NE()
					move(East)
					move(South)
					h = spawn_drone(hlp, 33, 2, 7, 8)
					if h != None:
						own(33, 2, 6)
					else:
						fSW_NE()
						move(East)
						move(South)
						h = spawn_drone(hlp, 33, 3, 7, 8)
						if h != None:
							own(33, 3, 6)
						else:
							fSW_NE()
							move(East)
							move(South)
							h = spawn_drone(hlp, 33, 4, 8, 8)
							if h != None:
								own(33, 4, 7)
							else:
								fSW_NE()
								move(East)
								move(South)
								h = spawn_drone(hlp, 33, 5, 8, 8)
								if h != None:
									own(33, 5, 7)
								else:
									fSW_NE()
									move(East)
									move(South)
									h = spawn_drone(hlp, 33, 6, 8, 8)
									if h != None:
										own(33, 6, 7)
									else:
										fSW_NE()
										move(East)
										move(South)
										fSW_NE()
										move(East)
										move(South)
										fsSW_NE()
			wait_until(tl + 0.9676)
		spawn_drone(w16)
		move(West)
		move(West)
		move(North)
		move(North)
		def w15():
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
			move(North)
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
			till()
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
			wait_until(tl + 0.9676)
			use_item(Items.Water)
			move(East)
			move(East)
			move(East)
			while num_items(Items.Cactus) <= 0:
				pass
			plant(Entities.Cactus)
			move(North)
			pk2(None, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, None, 0, 0)
			move(West)
			plant(Entities.Cactus)
			tl = get_time()
			move(East)
			h = spawn_drone(hlp, 31, 0, 6, 7)
			if h != None:
				own(31, 0, 5)
			else:
				fsSW_NE()
				move(East)
				move(South)
				h = spawn_drone(hlp, 31, 1, 6, 7)
				if h != None:
					own(31, 1, 5)
				else:
					fSW_NE()
					move(East)
					move(South)
					h = spawn_drone(hlp, 31, 2, 6, 7)
					if h != None:
						own(31, 2, 5)
					else:
						fSW_NE()
						move(East)
						move(South)
						h = spawn_drone(hlp, 31, 3, 7, 7)
						if h != None:
							own(31, 3, 6)
						else:
							fSW_NE()
							move(East)
							move(South)
							h = spawn_drone(hlp, 31, 4, 7, 7)
							if h != None:
								own(31, 4, 6)
							else:
								fSW_NE()
								move(East)
								move(South)
								h = spawn_drone(hlp, 31, 5, 7, 7)
								if h != None:
									own(31, 5, 6)
								else:
									fSW_NE()
									move(East)
									move(South)
									fSW_NE()
									move(East)
									move(South)
									fsSW_NE()
			wait_until(tl + 0.9676)
		spawn_drone(w15)
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
		move(South)
		move(East)
		move(North)
		wk = [3, 2, 1, 0]
		cur = 3
		while len(wk) > 0:
			cx = wk.pop(0)
			if cx == 0:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
					else:
						ti = -1
						tv = v
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 0
						if ti == 0:
							swap(East)
							if not (1 in wk):
								wk.append(1)
						else:
							break
			elif cx == 1:
				if cur == 0:
					move(East)
				elif cur == 2:
					move(West)
				elif cur == 3:
					move(South)
				cur = 1
				while True:
					v = measure()
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (0 in wk):
							wk.append(0)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
							if not (3 in wk):
								wk.append(3)
						elif ti == 1:
							swap(East)
							if not (2 in wk):
								wk.append(2)
						else:
							break
			elif cx == 2:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						if ti == 0:
							swap(North)
						else:
							break
			elif cx == 3:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
		c = cur
		wait_until(tl + 0.9676)
		use_item(Items.Water)
		if c == 0:
			move(East)
			move(East)
			move(East)
			move(North)
		elif c == 1:
			move(East)
			move(East)
			move(North)
		elif c == 2:
			move(East)
			move(North)
		elif c == 3:
			move(East)
			move(East)
		while num_items(Items.Cactus) <= 0:
			pass
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
		plant(Entities.Cactus)
		tl = get_time()
		xcas(South, 0)
		move(West)
		wk = [3, 2, 1, 0]
		cur = 3
		while len(wk) > 0:
			cx = wk.pop(0)
			if cx == 0:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						if ti == 0:
							swap(North)
							if not (1 in wk):
								wk.append(1)
						else:
							break
			elif cx == 1:
				if cur == 0:
					move(North)
				elif cur == 2:
					move(South)
				elif cur == 3:
					move(West)
				cur = 1
				while True:
					v = measure()
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (0 in wk):
							wk.append(0)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
							if not (2 in wk):
								wk.append(2)
						elif ti == 1:
							swap(East)
							if not (3 in wk):
								wk.append(3)
						else:
							break
			elif cx == 2:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
			elif cx == 3:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
		if cur == 0:
			move(East)
			move(North)
		elif cur == 1:
			move(East)
		elif cur == 2:
			move(East)
			move(South)
		move(East)
		move(South)
		move(South)
		move(South)
		move(South)
		wk = [3, 2, 1, 0]
		cur = 3
		while len(wk) > 0:
			cx = wk.pop(0)
			if cx == 0:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
					else:
						ti = -1
						tv = v
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 0
						if ti == 0:
							swap(East)
							if not (1 in wk):
								wk.append(1)
						else:
							break
			elif cx == 1:
				if cur == 0:
					move(East)
				elif cur == 2:
					move(West)
				elif cur == 3:
					move(South)
				cur = 1
				while True:
					v = measure()
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (0 in wk):
							wk.append(0)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
							if not (3 in wk):
								wk.append(3)
						elif ti == 1:
							swap(East)
							if not (2 in wk):
								wk.append(2)
						else:
							break
			elif cx == 2:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
			elif cx == 3:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
		wait_until(tl + 0.9676)
	spawn_drone(w14)
	def w10():
		def w12():
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
				wait_until(tl + 0.9676)
				use_item(Items.Water)
				move(East)
				move(East)
				move(South)
				move(South)
				while num_items(Items.Cactus) <= 0:
					pass
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				swap(South)
				pk2(None, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, None, 0, 0)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				tl = get_time()
				h = spawn_drone(hlp, 27, 0, 7, 8)
				if h != None:
					own(27, 0, 6)
				else:
					fsSW_NE()
					move(East)
					move(South)
					h = spawn_drone(hlp, 27, 1, 7, 8)
					if h != None:
						own(27, 1, 6)
					else:
						fSW_NE()
						move(East)
						move(South)
						h = spawn_drone(hlp, 27, 2, 7, 8)
						if h != None:
							own(27, 2, 6)
						else:
							fSW_NE()
							move(East)
							move(South)
							h = spawn_drone(hlp, 27, 3, 7, 8)
							if h != None:
								own(27, 3, 6)
							else:
								fSW_NE()
								move(East)
								move(South)
								h = spawn_drone(hlp, 27, 4, 8, 8)
								if h != None:
									own(27, 4, 7)
								else:
									fSW_NE()
									move(East)
									move(South)
									h = spawn_drone(hlp, 27, 5, 8, 8)
									if h != None:
										own(27, 5, 7)
									else:
										fSW_NE()
										move(East)
										move(South)
										h = spawn_drone(hlp, 27, 6, 8, 8)
										if h != None:
											own(27, 6, 7)
										else:
											fSW_NE()
											move(East)
											move(South)
											fSW_NE()
											move(East)
											move(South)
											fsSW_NE()
				wait_until(tl + 0.9676)
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
			wait_until(tl + 0.9676)
			use_item(Items.Water)
			move(East)
			move(East)
			move(South)
			while num_items(Items.Cactus) <= 0:
				pass
			plant(Entities.Cactus)
			move(West)
			plant(Entities.Cactus)
			swap(South)
			pk2(None, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, None, 0, 0)
			tl = get_time()
			h = spawn_drone(hlp, 25, 0, 6, 7)
			if h != None:
				own(25, 0, 5)
			else:
				fsSW_NE()
				move(East)
				move(South)
				h = spawn_drone(hlp, 25, 1, 6, 7)
				if h != None:
					own(25, 1, 5)
				else:
					fSW_NE()
					move(East)
					move(South)
					h = spawn_drone(hlp, 25, 2, 6, 7)
					if h != None:
						own(25, 2, 5)
					else:
						fSW_NE()
						move(East)
						move(South)
						h = spawn_drone(hlp, 25, 3, 7, 7)
						if h != None:
							own(25, 3, 6)
						else:
							fSW_NE()
							move(East)
							move(South)
							h = spawn_drone(hlp, 25, 4, 7, 7)
							if h != None:
								own(25, 4, 6)
							else:
								fSW_NE()
								move(East)
								move(South)
								h = spawn_drone(hlp, 25, 5, 7, 7)
								if h != None:
									own(25, 5, 6)
								else:
									fSW_NE()
									move(East)
									move(South)
									fSW_NE()
									move(East)
									move(South)
									fsSW_NE()
			wait_until(tl + 0.9676)
		spawn_drone(w12)
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
		def w11():
			move(East)
			move(East)
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
			tl = get_time()
			fsS_NE()
			move(West)
			move(North)
			move(North)
			move(East)
			move(North)
			wk = [3, 2, 1, 0]
			cur = 3
			while len(wk) > 0:
				cx = wk.pop(0)
				if cx == 0:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(North)
								if not (1 in wk):
									wk.append(1)
							else:
								break
				elif cx == 1:
					if cur == 0:
						move(North)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(West)
					cur = 1
					while True:
						v = measure()
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
							if not (0 in wk):
								wk.append(0)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 1
							if ti == 0:
								swap(North)
								if not (2 in wk):
									wk.append(2)
							elif ti == 1:
								swap(East)
								if not (3 in wk):
									wk.append(3)
							else:
								break
				elif cx == 2:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
							if not (1 in wk):
								wk.append(1)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 1
							if ti == 0:
								swap(North)
							elif ti == 1:
								swap(East)
							else:
								break
				elif cx == 3:
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
						bi = -1
						bv = v
						w = measure(West)
						while w == None:
							w = measure(West)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(West)
							if not (1 in wk):
								wk.append(1)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 1
							if ti == 0:
								swap(North)
							elif ti == 1:
								swap(East)
							else:
								break
			if cur == 0:
				move(East)
				move(North)
			elif cur == 1:
				move(East)
			elif cur == 2:
				move(East)
				move(South)
			move(East)
			move(East)
			move(South)
			fSW_E()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fSW_NE()
			move(East)
			move(South)
			fsSW_NE()
			wait_until(tl + 0.9676)
			use_item(Items.Water)
			move(South)
			while num_items(Items.Cactus) <= 0:
				pass
			plant(Entities.Cactus)
			move(North)
			pk2(None, North, West, 0, 1)
			pk2(East, North, West, 0, 1)
			pk2(East, North, None, 0, 0)
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
			move(South)
			xcas(East, 1)
			move(North)
			move(East)
			move(North)
			wk = [3, 2, 1, 0]
			cur = 3
			while len(wk) > 0:
				cx = wk.pop(0)
				if cx == 0:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(North)
								if not (1 in wk):
									wk.append(1)
							else:
								break
				elif cx == 1:
					if cur == 0:
						move(North)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(West)
					cur = 1
					while True:
						v = measure()
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
							if not (0 in wk):
								wk.append(0)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 1
							if ti == 0:
								swap(North)
								if not (2 in wk):
									wk.append(2)
							elif ti == 1:
								swap(East)
								if not (3 in wk):
									wk.append(3)
							else:
								break
				elif cx == 2:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
							if not (1 in wk):
								wk.append(1)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 1
							if ti == 0:
								swap(North)
							elif ti == 1:
								swap(East)
							else:
								break
				elif cx == 3:
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
						bi = -1
						bv = v
						w = measure(West)
						while w == None:
							w = measure(West)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(West)
							if not (1 in wk):
								wk.append(1)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 1
							if ti == 0:
								swap(North)
							elif ti == 1:
								swap(East)
							else:
								break
			if cur == 0:
				move(East)
				move(North)
			elif cur == 1:
				move(East)
			elif cur == 2:
				move(East)
				move(South)
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
			wait_until(tl + 0.9676)
		spawn_drone(w11)
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
		wait_until(tl + 0.9676)
		use_item(Items.Water)
		move(West)
		move(North)
		move(North)
		while num_items(Items.Cactus) <= 0:
			pass
		plant(Entities.Cactus)
		move(South)
		pk2(None, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, None, 1, 0)
		move(East)
		plant(Entities.Cactus)
		tl = get_time()
		move(West)
		h = spawn_drone(hlp, 21, 0, 6, 7)
		if h != None:
			own(21, 0, 5)
		else:
			fsSW_NE()
			move(West)
			move(North)
			h = spawn_drone(hlp, 21, 1, 6, 7)
			if h != None:
				own(21, 1, 5)
			else:
				fSW_NE()
				move(West)
				move(North)
				h = spawn_drone(hlp, 21, 2, 6, 7)
				if h != None:
					own(21, 2, 5)
				else:
					fSW_NE()
					move(West)
					move(North)
					h = spawn_drone(hlp, 21, 3, 7, 7)
					if h != None:
						own(21, 3, 6)
					else:
						fSW_NE()
						move(West)
						move(North)
						h = spawn_drone(hlp, 21, 4, 7, 7)
						if h != None:
							own(21, 4, 6)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = spawn_drone(hlp, 21, 5, 7, 7)
							if h != None:
								own(21, 5, 6)
							else:
								fSW_NE()
								move(West)
								move(North)
								fSW_NE()
								move(West)
								move(North)
								fsS_NE()
		wait_until(tl + 0.9676)
	spawn_drone(w10)
	def w8():
		def w9():
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
			move(North)
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
			wait_until(tl + 0.9676)
			use_item(Items.Water)
			move(West)
			move(North)
			while num_items(Items.Cactus) <= 0:
				pass
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			move(East)
			plant(Entities.Cactus)
			swap(North)
			pk2(None, South, East, 1, 1)
			pk2(West, South, East, 1, 1)
			pk2(West, South, East, 1, 1)
			pk2(West, South, East, 1, 1)
			pk2(West, South, East, 1, 1)
			pk2(West, South, East, 1, 1)
			pk2(West, South, None, 1, 0)
			move(East)
			plant(Entities.Cactus)
			move(South)
			plant(Entities.Cactus)
			tl = get_time()
			h = spawn_drone(hlp, 19, 0, 7, 8)
			if h != None:
				own(19, 0, 6)
			else:
				fsSW_NE()
				move(West)
				move(North)
				h = spawn_drone(hlp, 19, 1, 7, 8)
				if h != None:
					own(19, 1, 6)
				else:
					fSW_NE()
					move(West)
					move(North)
					h = spawn_drone(hlp, 19, 2, 7, 8)
					if h != None:
						own(19, 2, 6)
					else:
						fSW_NE()
						move(West)
						move(North)
						h = spawn_drone(hlp, 19, 3, 7, 8)
						if h != None:
							own(19, 3, 6)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = spawn_drone(hlp, 19, 4, 8, 8)
							if h != None:
								own(19, 4, 7)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = spawn_drone(hlp, 19, 5, 8, 8)
								if h != None:
									own(19, 5, 7)
								else:
									fSW_NE()
									move(West)
									move(North)
									h = spawn_drone(hlp, 19, 6, 8, 8)
									if h != None:
										own(19, 6, 7)
									else:
										fSW_NE()
										move(West)
										move(North)
										fSW_NE()
										move(West)
										move(North)
										fsSW_NE()
			wait_until(tl + 0.9676)
		spawn_drone(w9)
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
		till()
		plant(Entities.Cactus)
		move(South)
		till()
		plant(Entities.Cactus)
		move(East)
		till()
		plant(Entities.Cactus)
		move(West)
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
		while len(wk) > 0:
			cx = wk.pop(0)
			if cx == 0:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
					else:
						ti = -1
						tv = v
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 0
						if ti == 0:
							swap(East)
							if not (1 in wk):
								wk.append(1)
						else:
							break
			elif cx == 1:
				if cur == 0:
					move(East)
				elif cur == 2:
					move(West)
				elif cur == 3:
					move(South)
				cur = 1
				while True:
					v = measure()
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (0 in wk):
							wk.append(0)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
							if not (3 in wk):
								wk.append(3)
						elif ti == 1:
							swap(East)
							if not (2 in wk):
								wk.append(2)
						else:
							break
			elif cx == 2:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
			elif cx == 3:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
		if cur == 0:
			move(East)
			move(North)
		elif cur == 1:
			move(North)
		elif cur == 2:
			move(West)
			move(North)
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
		wait_until(tl + 0.9676)
		use_item(Items.Water)
		move(West)
		while num_items(Items.Cactus) <= 0:
			pass
		plant(Entities.Cactus)
		move(East)
		plant(Entities.Cactus)
		swap(North)
		pk2(None, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, None, 1, 0)
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
		plant(Entities.Cactus)
		tl = get_time()
		xcas(North, 1)
		move(East)
		move(East)
		move(North)
		wk = [3, 2, 1, 0]
		cur = 3
		while len(wk) > 0:
			cx = wk.pop(0)
			if cx == 0:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
					else:
						ti = -1
						tv = v
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 0
						if ti == 0:
							swap(East)
							if not (1 in wk):
								wk.append(1)
						else:
							break
			elif cx == 1:
				if cur == 0:
					move(East)
				elif cur == 2:
					move(West)
				elif cur == 3:
					move(South)
				cur = 1
				while True:
					v = measure()
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (0 in wk):
							wk.append(0)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
							if not (3 in wk):
								wk.append(3)
						elif ti == 1:
							swap(East)
							if not (2 in wk):
								wk.append(2)
						else:
							break
			elif cx == 2:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
			elif cx == 3:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
		if cur == 0:
			move(East)
			move(North)
		elif cur == 1:
			move(North)
		elif cur == 2:
			move(West)
			move(North)
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
		wait_until(tl + 0.9676)
	spawn_drone(w8)
	def w3():
		def w5():
			def w7():
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
				wait_until(tl + 0.9676)
				use_item(Items.Water)
				move(East)
				while num_items(Items.Cactus) <= 0:
					pass
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				swap(South)
				pk2(None, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, None, 0, 0)
				move(West)
				plant(Entities.Cactus)
				tl = get_time()
				move(East)
				h = spawn_drone(hlp, 15, 0, 6, 7)
				if h != None:
					own(15, 0, 5)
				else:
					fsSW_NE()
					move(East)
					move(South)
					h = spawn_drone(hlp, 15, 1, 6, 7)
					if h != None:
						own(15, 1, 5)
					else:
						fSW_NE()
						move(East)
						move(South)
						h = spawn_drone(hlp, 15, 2, 6, 7)
						if h != None:
							own(15, 2, 5)
						else:
							fSW_NE()
							move(East)
							move(South)
							h = spawn_drone(hlp, 15, 3, 7, 7)
							if h != None:
								own(15, 3, 6)
							else:
								fSW_NE()
								move(East)
								move(South)
								h = spawn_drone(hlp, 15, 4, 7, 7)
								if h != None:
									own(15, 4, 6)
								else:
									fSW_NE()
									move(East)
									move(South)
									h = spawn_drone(hlp, 15, 5, 7, 7)
									if h != None:
										own(15, 5, 6)
									else:
										fSW_NE()
										move(East)
										move(South)
										fSW_NE()
										move(East)
										move(South)
										fsW_NE()
				wait_until(tl + 0.9676)
			spawn_drone(w7)
			def w6():
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
				wait_until(tl + 0.9676)
				use_item(Items.Water)
				while num_items(Items.Cactus) <= 0:
					pass
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				move(West)
				plant(Entities.Cactus)
				swap(South)
				pk2(None, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, West, 0, 1)
				pk2(East, North, None, 0, 0)
				move(West)
				plant(Entities.Cactus)
				move(North)
				plant(Entities.Cactus)
				tl = get_time()
				h = spawn_drone(hlp, 13, 0, 7, 8)
				if h != None:
					own(13, 0, 6)
				else:
					fsSW_E()
					move(East)
					move(South)
					h = spawn_drone(hlp, 13, 1, 7, 8)
					if h != None:
						own(13, 1, 6)
					else:
						fSW_NE()
						move(East)
						move(South)
						h = spawn_drone(hlp, 13, 2, 7, 8)
						if h != None:
							own(13, 2, 6)
						else:
							fSW_NE()
							move(East)
							move(South)
							h = spawn_drone(hlp, 13, 3, 7, 8)
							if h != None:
								own(13, 3, 6)
							else:
								fSW_NE()
								move(East)
								move(South)
								h = spawn_drone(hlp, 13, 4, 8, 8)
								if h != None:
									own(13, 4, 7)
								else:
									fSW_NE()
									move(East)
									move(South)
									h = spawn_drone(hlp, 13, 5, 8, 8)
									if h != None:
										own(13, 5, 7)
									else:
										fSW_NE()
										move(East)
										move(South)
										h = spawn_drone(hlp, 13, 6, 8, 8)
										if h != None:
											own(13, 6, 7)
										else:
											fSW_NE()
											move(East)
											move(South)
											fSW_NE()
											move(East)
											move(South)
											fsSW_NE()
				wait_until(tl + 0.9676)
			spawn_drone(w6)
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
			fS_NE()
			move(West)
			move(North)
			move(North)
			move(East)
			move(North)
			wk = [3, 2, 1, 0]
			cur = 3
			while len(wk) > 0:
				cx = wk.pop(0)
				if cx == 0:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(North)
								if not (1 in wk):
									wk.append(1)
							else:
								break
				elif cx == 1:
					if cur == 0:
						move(North)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(West)
					cur = 1
					while True:
						v = measure()
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
							if not (0 in wk):
								wk.append(0)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 1
							if ti == 0:
								swap(North)
								if not (2 in wk):
									wk.append(2)
							elif ti == 1:
								swap(East)
								if not (3 in wk):
									wk.append(3)
							else:
								break
				elif cx == 2:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
							if not (1 in wk):
								wk.append(1)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 1
							if ti == 0:
								swap(North)
							elif ti == 1:
								swap(East)
							else:
								break
				elif cx == 3:
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
						bi = -1
						bv = v
						w = measure(West)
						while w == None:
							w = measure(West)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(West)
							if not (1 in wk):
								wk.append(1)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 1
							if ti == 0:
								swap(North)
							elif ti == 1:
								swap(East)
							else:
								break
			if cur == 0:
				move(East)
				move(North)
			elif cur == 1:
				move(East)
			elif cur == 2:
				move(East)
				move(South)
			move(East)
			move(East)
			move(South)
			fSW_E()
			move(East)
			move(South)
			fsSW_NE()
			wait_until(tl + 0.9676)
			use_item(Items.Water)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(West)
			move(North)
			while num_items(Items.Cactus) <= 0:
				pass
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
			plant(Entities.Cactus)
			tl = get_time()
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
			while len(wk) > 0:
				cx = wk.pop(0)
				if cx == 0:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						w = measure(West)
						while w == None:
							w = measure(West)
						if w > bv:
							bv = w
							bi = 1
						if bi == 0:
							swap(South)
						elif bi == 1:
							swap(West)
						else:
							ti = -1
							tv = v
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(East)
								if not (2 in wk):
									wk.append(2)
							else:
								break
				elif cx == 1:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						w = measure(West)
						while w == None:
							w = measure(West)
						if w > bv:
							bv = w
							bi = 1
						if bi == 0:
							swap(South)
						elif bi == 1:
							swap(West)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(North)
								if not (2 in wk):
									wk.append(2)
							else:
								break
				elif cx == 2:
					if cur == 0:
						move(East)
					elif cur == 1:
						move(North)
					elif cur == 3:
						move(South)
					cur = 2
					while True:
						v = measure()
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						w = measure(West)
						while w == None:
							w = measure(West)
						if w > bv:
							bv = w
							bi = 1
						if bi == 0:
							swap(South)
							if not (1 in wk):
								wk.append(1)
						elif bi == 1:
							swap(West)
							if not (0 in wk):
								wk.append(0)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(North)
								if not (3 in wk):
									wk.append(3)
							else:
								break
				elif cx == 3:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
							if not (2 in wk):
								wk.append(2)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(North)
							else:
								break
			wait_until(tl + 0.9676)
		spawn_drone(w5)
		def w4():
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
			wait_until(tl + 0.9676)
			use_item(Items.Water)
			move(West)
			move(North)
			move(North)
			move(North)
			move(North)
			while num_items(Items.Cactus) <= 0:
				pass
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
			pk2(None, South, East, 1, 1)
			pk2(West, South, East, 1, 1)
			pk2(West, South, None, 1, 0)
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
			move(West)
			move(North)
			move(North)
			move(East)
			move(North)
			wk = [3, 2, 1, 0]
			cur = 3
			while len(wk) > 0:
				cx = wk.pop(0)
				if cx == 0:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							if ti == 0:
								swap(North)
								if not (1 in wk):
									wk.append(1)
							else:
								break
				elif cx == 1:
					if cur == 0:
						move(North)
					elif cur == 2:
						move(South)
					elif cur == 3:
						move(West)
					cur = 1
					while True:
						v = measure()
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
							if not (0 in wk):
								wk.append(0)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 1
							if ti == 0:
								swap(North)
								if not (2 in wk):
									wk.append(2)
							elif ti == 1:
								swap(East)
								if not (3 in wk):
									wk.append(3)
							else:
								break
				elif cx == 2:
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
						bi = -1
						bv = v
						w = measure(South)
						while w == None:
							w = measure(South)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(South)
							if not (1 in wk):
								wk.append(1)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 1
							if ti == 0:
								swap(North)
							elif ti == 1:
								swap(East)
							else:
								break
				elif cx == 3:
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
						bi = -1
						bv = v
						w = measure(West)
						while w == None:
							w = measure(West)
						if w > bv:
							bv = w
							bi = 0
						if bi == 0:
							swap(West)
							if not (1 in wk):
								wk.append(1)
						else:
							ti = -1
							tv = v
							w = measure(North)
							while w == None:
								w = measure(North)
							if w < tv:
								tv = w
								ti = 0
							w = measure(East)
							while w == None:
								w = measure(East)
							if w < tv:
								tv = w
								ti = 1
							if ti == 0:
								swap(North)
							elif ti == 1:
								swap(East)
							else:
								break
			wait_until(tl + 0.9676)
		spawn_drone(w4)
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
		move(East)
		till()
		plant(Entities.Cactus)
		move(West)
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
		move(South)
		move(South)
		move(East)
		move(North)
		wk = [3, 2, 1, 0]
		cur = 3
		while len(wk) > 0:
			cx = wk.pop(0)
			if cx == 0:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
					else:
						ti = -1
						tv = v
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 0
						if ti == 0:
							swap(East)
							if not (1 in wk):
								wk.append(1)
						else:
							break
			elif cx == 1:
				if cur == 0:
					move(East)
				elif cur == 2:
					move(West)
				elif cur == 3:
					move(South)
				cur = 1
				while True:
					v = measure()
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (0 in wk):
							wk.append(0)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
							if not (3 in wk):
								wk.append(3)
						elif ti == 1:
							swap(East)
							if not (2 in wk):
								wk.append(2)
						else:
							break
			elif cx == 2:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
			elif cx == 3:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
		if cur == 0:
			move(East)
			move(North)
		elif cur == 1:
			move(North)
		elif cur == 2:
			move(West)
			move(North)
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
		wait_until(tl + 0.9676)
		use_item(Items.Water)
		move(West)
		move(West)
		move(West)
		move(West)
		move(West)
		move(North)
		move(North)
		while (get_time() // WDT) - num_items(Items.Water) < NSIG + 1:
			pass
		harvest()
		while num_items(Items.Cactus) <= 0:
			pass
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
		plant(Entities.Cactus)
		if measure() < measure(West):
			swap(West)
		tl = get_time()
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
		move(West)
		move(North)
		move(North)
		move(East)
		move(North)
		wk = [3, 2, 1, 0]
		cur = 3
		while len(wk) > 0:
			cx = wk.pop(0)
			if cx == 0:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						if ti == 0:
							swap(North)
							if not (1 in wk):
								wk.append(1)
						else:
							break
			elif cx == 1:
				if cur == 0:
					move(North)
				elif cur == 2:
					move(South)
				elif cur == 3:
					move(West)
				cur = 1
				while True:
					v = measure()
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (0 in wk):
							wk.append(0)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
							if not (2 in wk):
								wk.append(2)
						elif ti == 1:
							swap(East)
							if not (3 in wk):
								wk.append(3)
						else:
							break
			elif cx == 2:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
			elif cx == 3:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
		wait_until(tl + 0.9676)
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
		move(West)
		move(North)
		move(East)
		move(North)
		wk = [3, 2, 1, 0]
		cur = 3
		while len(wk) > 0:
			cx = wk.pop(0)
			if cx == 0:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						if ti == 0:
							swap(North)
							if not (1 in wk):
								wk.append(1)
						else:
							break
			elif cx == 1:
				if cur == 0:
					move(North)
				elif cur == 2:
					move(South)
				elif cur == 3:
					move(West)
				cur = 1
				while True:
					v = measure()
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (0 in wk):
							wk.append(0)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
							if not (2 in wk):
								wk.append(2)
						elif ti == 1:
							swap(East)
							if not (3 in wk):
								wk.append(3)
						else:
							break
			elif cx == 2:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
			elif cx == 3:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
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
		wait_until(tl + 0.9676)
		use_item(Items.Water)
		move(East)
		move(North)
		move(North)
		move(North)
		while num_items(Items.Cactus) <= 0:
			pass
		plant(Entities.Cactus)
		move(South)
		pk2(None, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, East, 1, 1)
		pk2(West, South, None, 1, 0)
		move(East)
		plant(Entities.Cactus)
		move(South)
		plant(Entities.Cactus)
		tl = get_time()
		h = spawn_drone(hlp, 5, 0, 7, 8)
		if h != None:
			own(5, 0, 6)
		else:
			fsSW_N()
			move(West)
			move(North)
			h = spawn_drone(hlp, 5, 1, 7, 8)
			if h != None:
				own(5, 1, 6)
			else:
				fSW_NE()
				move(West)
				move(North)
				h = spawn_drone(hlp, 5, 2, 7, 8)
				if h != None:
					own(5, 2, 6)
				else:
					fSW_NE()
					move(West)
					move(North)
					h = spawn_drone(hlp, 5, 3, 7, 8)
					if h != None:
						own(5, 3, 6)
					else:
						fSW_NE()
						move(West)
						move(North)
						h = spawn_drone(hlp, 5, 4, 8, 8)
						if h != None:
							own(5, 4, 7)
						else:
							fSW_NE()
							move(West)
							move(North)
							h = spawn_drone(hlp, 5, 5, 8, 8)
							if h != None:
								own(5, 5, 7)
							else:
								fSW_NE()
								move(West)
								move(North)
								h = spawn_drone(hlp, 5, 6, 8, 8)
								if h != None:
									own(5, 6, 7)
								else:
									fSW_NE()
									move(West)
									move(North)
									fSW_NE()
									move(West)
									move(North)
									fsSW_NE()
		wait_until(tl + 0.9676)
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
		move(East)
		till()
		plant(Entities.Cactus)
		move(West)
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
		move(South)
		move(East)
		move(North)
		wk = [3, 2, 1, 0]
		cur = 3
		while len(wk) > 0:
			cx = wk.pop(0)
			if cx == 0:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
					else:
						ti = -1
						tv = v
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 0
						if ti == 0:
							swap(East)
							if not (1 in wk):
								wk.append(1)
						else:
							break
			elif cx == 1:
				if cur == 0:
					move(East)
				elif cur == 2:
					move(West)
				elif cur == 3:
					move(South)
				cur = 1
				while True:
					v = measure()
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (0 in wk):
							wk.append(0)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
							if not (3 in wk):
								wk.append(3)
						elif ti == 1:
							swap(East)
							if not (2 in wk):
								wk.append(2)
						else:
							break
			elif cx == 2:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
			elif cx == 3:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
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
		wait_until(tl + 0.9676)
		use_item(Items.Water)
		move(East)
		move(East)
		move(East)
		move(East)
		move(East)
		while num_items(Items.Cactus) <= 0:
			pass
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
		move(South)
		move(South)
		move(South)
		move(South)
		move(South)
		move(South)
		move(East)
		move(North)
		wk = [3, 2, 1, 0]
		cur = 3
		while len(wk) > 0:
			cx = wk.pop(0)
			if cx == 0:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
					else:
						ti = -1
						tv = v
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 0
						if ti == 0:
							swap(East)
							if not (1 in wk):
								wk.append(1)
						else:
							break
			elif cx == 1:
				if cur == 0:
					move(East)
				elif cur == 2:
					move(West)
				elif cur == 3:
					move(South)
				cur = 1
				while True:
					v = measure()
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (0 in wk):
							wk.append(0)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
							if not (3 in wk):
								wk.append(3)
						elif ti == 1:
							swap(East)
							if not (2 in wk):
								wk.append(2)
						else:
							break
			elif cx == 2:
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
					bi = -1
					bv = v
					w = measure(West)
					while w == None:
						w = measure(West)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(West)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
			elif cx == 3:
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
					bi = -1
					bv = v
					w = measure(South)
					while w == None:
						w = measure(South)
					if w > bv:
						bv = w
						bi = 0
					if bi == 0:
						swap(South)
						if not (1 in wk):
							wk.append(1)
					else:
						ti = -1
						tv = v
						w = measure(North)
						while w == None:
							w = measure(North)
						if w < tv:
							tv = w
							ti = 0
						w = measure(East)
						while w == None:
							w = measure(East)
						if w < tv:
							tv = w
							ti = 1
						if ti == 0:
							swap(North)
						elif ti == 1:
							swap(East)
						else:
							break
		wait_until(tl + 0.9676)
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
	move(East)
	till()
	plant(Entities.Cactus)
	move(West)
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
	move(South)
	move(East)
	move(North)
	wk = [3, 2, 1, 0]
	cur = 3
	while len(wk) > 0:
		cx = wk.pop(0)
		if cx == 0:
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
				bi = -1
				bv = v
				w = measure(West)
				while w == None:
					w = measure(West)
				if w > bv:
					bv = w
					bi = 0
				if bi == 0:
					swap(West)
				else:
					ti = -1
					tv = v
					w = measure(East)
					while w == None:
						w = measure(East)
					if w < tv:
						tv = w
						ti = 0
					if ti == 0:
						swap(East)
						if not (1 in wk):
							wk.append(1)
					else:
						break
		elif cx == 1:
			if cur == 0:
				move(East)
			elif cur == 2:
				move(West)
			elif cur == 3:
				move(South)
			cur = 1
			while True:
				v = measure()
				bi = -1
				bv = v
				w = measure(West)
				while w == None:
					w = measure(West)
				if w > bv:
					bv = w
					bi = 0
				if bi == 0:
					swap(West)
					if not (0 in wk):
						wk.append(0)
				else:
					ti = -1
					tv = v
					w = measure(North)
					while w == None:
						w = measure(North)
					if w < tv:
						tv = w
						ti = 0
					w = measure(East)
					while w == None:
						w = measure(East)
					if w < tv:
						tv = w
						ti = 1
					if ti == 0:
						swap(North)
						if not (3 in wk):
							wk.append(3)
					elif ti == 1:
						swap(East)
						if not (2 in wk):
							wk.append(2)
					else:
						break
		elif cx == 2:
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
				bi = -1
				bv = v
				w = measure(West)
				while w == None:
					w = measure(West)
				if w > bv:
					bv = w
					bi = 0
				if bi == 0:
					swap(West)
					if not (1 in wk):
						wk.append(1)
				else:
					ti = -1
					tv = v
					w = measure(North)
					while w == None:
						w = measure(North)
					if w < tv:
						tv = w
						ti = 0
					w = measure(East)
					while w == None:
						w = measure(East)
					if w < tv:
						tv = w
						ti = 1
					if ti == 0:
						swap(North)
					elif ti == 1:
						swap(East)
					else:
						break
		elif cx == 3:
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
				bi = -1
				bv = v
				w = measure(South)
				while w == None:
					w = measure(South)
				if w > bv:
					bv = w
					bi = 0
				if bi == 0:
					swap(South)
					if not (1 in wk):
						wk.append(1)
				else:
					ti = -1
					tv = v
					w = measure(North)
					while w == None:
						w = measure(North)
					if w < tv:
						tv = w
						ti = 0
					w = measure(East)
					while w == None:
						w = measure(East)
					if w < tv:
						tv = w
						ti = 1
					if ti == 0:
						swap(North)
					elif ti == 1:
						swap(East)
					else:
						break
	if cur == 0:
		move(East)
		move(North)
	elif cur == 1:
		move(North)
	elif cur == 2:
		move(West)
		move(North)
	move(West)
	move(West)
	move(North)
	move(North)
	move(North)
	move(East)
	move(North)
	wk = [3, 2, 1, 0]
	cur = 3
	while len(wk) > 0:
		cx = wk.pop(0)
		if cx == 0:
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
				bi = -1
				bv = v
				w = measure(South)
				while w == None:
					w = measure(South)
				if w > bv:
					bv = w
					bi = 0
				if bi == 0:
					swap(South)
				else:
					ti = -1
					tv = v
					w = measure(North)
					while w == None:
						w = measure(North)
					if w < tv:
						tv = w
						ti = 0
					if ti == 0:
						swap(North)
						if not (1 in wk):
							wk.append(1)
					else:
						break
		elif cx == 1:
			if cur == 0:
				move(North)
			elif cur == 2:
				move(South)
			elif cur == 3:
				move(West)
			cur = 1
			while True:
				v = measure()
				bi = -1
				bv = v
				w = measure(South)
				while w == None:
					w = measure(South)
				if w > bv:
					bv = w
					bi = 0
				if bi == 0:
					swap(South)
					if not (0 in wk):
						wk.append(0)
				else:
					ti = -1
					tv = v
					w = measure(North)
					while w == None:
						w = measure(North)
					if w < tv:
						tv = w
						ti = 0
					w = measure(East)
					while w == None:
						w = measure(East)
					if w < tv:
						tv = w
						ti = 1
					if ti == 0:
						swap(North)
						if not (2 in wk):
							wk.append(2)
					elif ti == 1:
						swap(East)
						if not (3 in wk):
							wk.append(3)
					else:
						break
		elif cx == 2:
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
				bi = -1
				bv = v
				w = measure(South)
				while w == None:
					w = measure(South)
				if w > bv:
					bv = w
					bi = 0
				if bi == 0:
					swap(South)
					if not (1 in wk):
						wk.append(1)
				else:
					ti = -1
					tv = v
					w = measure(North)
					while w == None:
						w = measure(North)
					if w < tv:
						tv = w
						ti = 0
					w = measure(East)
					while w == None:
						w = measure(East)
					if w < tv:
						tv = w
						ti = 1
					if ti == 0:
						swap(North)
					elif ti == 1:
						swap(East)
					else:
						break
		elif cx == 3:
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
				bi = -1
				bv = v
				w = measure(West)
				while w == None:
					w = measure(West)
				if w > bv:
					bv = w
					bi = 0
				if bi == 0:
					swap(West)
					if not (1 in wk):
						wk.append(1)
				else:
					ti = -1
					tv = v
					w = measure(North)
					while w == None:
						w = measure(North)
					if w < tv:
						tv = w
						ti = 0
					w = measure(East)
					while w == None:
						w = measure(East)
					if w < tv:
						tv = w
						ti = 1
					if ti == 0:
						swap(North)
					elif ti == 1:
						swap(East)
					else:
						break
	c = cur
	wait_until(tl + 0.9676)
	use_item(Items.Water)
	if c == 0:
		move(East)
		move(East)
	elif c == 1:
		move(East)
		move(East)
		move(South)
	elif c == 2:
		move(East)
		move(East)
		move(South)
		move(South)
	elif c == 3:
		move(East)
		move(South)
	while num_items(Items.Cactus) <= 0:
		pass
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
	xcasw(North, 1)
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
	while len(wk) > 0:
		cx = wk.pop(0)
		if cx == 0:
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
				bi = -1
				bv = v
				w = measure(West)
				while w == None:
					w = measure(West)
				if w > bv:
					bv = w
					bi = 0
				if bi == 0:
					swap(West)
				else:
					ti = -1
					tv = v
					w = measure(East)
					while w == None:
						w = measure(East)
					if w < tv:
						tv = w
						ti = 0
					if ti == 0:
						swap(East)
						if not (1 in wk):
							wk.append(1)
					else:
						break
		elif cx == 1:
			if cur == 0:
				move(East)
			elif cur == 2:
				move(West)
			elif cur == 3:
				move(South)
			cur = 1
			while True:
				v = measure()
				bi = -1
				bv = v
				w = measure(West)
				while w == None:
					w = measure(West)
				if w > bv:
					bv = w
					bi = 0
				if bi == 0:
					swap(West)
					if not (0 in wk):
						wk.append(0)
				else:
					ti = -1
					tv = v
					w = measure(North)
					while w == None:
						w = measure(North)
					if w < tv:
						tv = w
						ti = 0
					w = measure(East)
					while w == None:
						w = measure(East)
					if w < tv:
						tv = w
						ti = 1
					if ti == 0:
						swap(North)
						if not (3 in wk):
							wk.append(3)
					elif ti == 1:
						swap(East)
						if not (2 in wk):
							wk.append(2)
					else:
						break
		elif cx == 2:
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
				bi = -1
				bv = v
				w = measure(West)
				while w == None:
					w = measure(West)
				if w > bv:
					bv = w
					bi = 0
				if bi == 0:
					swap(West)
					if not (1 in wk):
						wk.append(1)
				else:
					ti = -1
					tv = v
					w = measure(North)
					while w == None:
						w = measure(North)
					if w < tv:
						tv = w
						ti = 0
					w = measure(East)
					while w == None:
						w = measure(East)
					if w < tv:
						tv = w
						ti = 1
					if ti == 0:
						swap(North)
					elif ti == 1:
						swap(East)
					else:
						break
		elif cx == 3:
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
				bi = -1
				bv = v
				w = measure(South)
				while w == None:
					w = measure(South)
				if w > bv:
					bv = w
					bi = 0
				if bi == 0:
					swap(South)
					if not (1 in wk):
						wk.append(1)
				else:
					ti = -1
					tv = v
					w = measure(North)
					while w == None:
						w = measure(North)
					if w < tv:
						tv = w
						ti = 0
					w = measure(East)
					while w == None:
						w = measure(East)
					if w < tv:
						tv = w
						ti = 1
					if ti == 0:
						swap(North)
					elif ti == 1:
						swap(East)
					else:
						break
	wait_until(tl + 0.9676)
	while num_drones() > 1:
		pass
	harvest()

w0()
