# sched_20: the narrow start phase lasts until the boosted sunflower cut is done.
# sched_19: sched_17, and on the 6x6 carrot field tree cells also take sunflowers (burst sooner).
# sched_17: route-and-timing farm for one drone (a rewrite of sched_16 with plain globals, which
# cost fewer interpreter ticks than list cells).
#
# Each field has a fixed layout of roles; the drone walks a fixed cycle (the torus column walk,
# or on 6x6 a snake over the first K columns while the farm starts up) and tends each cell as it
# passes: a ripe crop is cut and replanted, an unripe one is skipped (or, while power is on,
# waited for if it is due soon). What gets planted follows what is still short, counting the
# crops already growing. On 6x6 with sunflowers, the first NSUN freed carrot cells get
# sunflowers; once all stand, only the highest-petal one is cut while 10 or more stand (8 power
# each, twice the drone's speed for 48000 ticks), then the rest are cut and become carrots again.
# roles: G grass, C carrot (sunflower in the burst; bush once carrots are done), T tree or grass,
# B bush or grass

LAY3 = ['CBC', 'BGB', 'CBC']
LAY4B = ['BCBC', 'CGCB', 'BCBC', 'CBCG']
LAY4C = ['TGTG', 'GTGT', 'TGTG', 'GTGT']
LAY6D = ['TCTCTC', 'CTCTCT', 'TCTCTC', 'CTCTCT', 'TCTCTC', 'CTCTCT']
LAY6E = ['GTGCGC', 'CGCGTG', 'GCGTGC', 'TGCGCG', 'GCGCGT', 'CGTGCG']
MC = 1.5  # expected companion multiplier of a carrot, for planning seeds
MCP = 1.3  # growing carrots counted at this multiplier when deciding to plant another
MT = 1.4  # likewise for trees and bushes
WLO = 0.15  # a tree planted on soil drier than this gets one water
NSUNE = 12  # sunflowers in the burst (6x6 mixed)
NSUND = 10  # (6x6 carrots)
PH6 = [(6, 9999)]  # route phases: (columns walked, until game time)
PH6D = [(2, 18), (6, 9999)]
CW = 5.0  # with power on, wait at a carrot planted at least this long ago
SUNMAX = 120
SUNTD = True  # 6x6 carrots: tree cells take sunflowers too
SUNTE = False  # (6x6 mixed)
SUNT = False
STAYB = True  # stay on the narrow route until the boosted cuts are done  # give up planting sunflowers after this long (safety)

NEEDL = []
NDC = 0
NDW = 0
NDH = 0
PC = 0
PT = 0
PB = 0
FC = True
FW = True
HTG = 0
CCOST = 1
YTR = 5
YBU = 1
KCF = 1
MCPY = 1
POW = False
NSUN = 0
SPL = 0  # sunflowers planted so far
SST = 0  # sunflowers standing
SMX = 0  # their highest petal count
SUN = {}
RT = []


def lvl(u):
	n = num_unlocked(u)
	if n <= 1:
		return 1
	return 2 ** (n - 1)


def upd():
	global FC
	global FW
	global HTG
	r = NDC - num_items(Items.Carrot)
	FC = r > PC * MCPY
	k = r * KCF - PC
	if k < 0:
		k = 0
	k = k * CCOST
	FW = NDW + k > num_items(Items.Wood) + PT * YTR + PB * YBU
	HTG = NDH + k


def done():
	for p in NEEDL:
		if num_items(p[0]) < p[1]:
			return False
	return True


def smax():
	global SMX
	m = 0
	for k in SUN:
		if SUN[k] > m:
			m = SUN[k]
	SMX = m


def tg(c):
	if num_items(Items.Hay) < HTG and can_harvest():
		harvest()
		return True
	return False


def tc(c):
	global PC
	global PB
	global SPL
	global SST
	e = get_entity_type()
	r = False
	if e == Entities.Carrot:
		if not can_harvest():
			if not POW or get_time() < RT[c] or num_items(Items.Power) == 0:
				return False
			while not can_harvest():
				pass
		harvest()
		PC -= 1
		r = True
	elif e == Entities.Bush:
		if not can_harvest():
			return False
		harvest()
		PB -= 1
		r = True
	elif e == Entities.Sunflower:
		if not can_harvest():
			return False
		if SPL < NSUN or (SST >= 10 and SUN[c] < SMX):
			return False
		harvest()
		SUN.pop(c)
		SST -= 1
		smax()
	elif get_ground_type() != Grounds.Soil:
		if e == Entities.Grass and num_items(Items.Hay) < HTG:
			harvest()
			r = True
		till()
	if SPL < NSUN and num_items(Items.Carrot) >= 1:
		if plant(Entities.Sunflower):
			SUN[c] = measure()
			SPL += 1
			SST += 1
			smax()
			upd()
			return r
	upd()
	if FC:
		if plant(Entities.Carrot):
			PC += 1
			RT[c] = get_time() + CW
			upd()
	elif FW:
		if plant(Entities.Bush):
			PB += 1
			upd()
	return r


def tt(c):
	global PT
	global SPL
	global SST
	e = get_entity_type()
	r = False
	if e == Entities.Tree:
		if not can_harvest():
			return False
		harvest()
		PT -= 1
		r = True
		upd()
	elif e == Entities.Grass:
		if num_items(Items.Hay) < HTG and can_harvest():
			harvest()
			r = True
	elif e == Entities.Sunflower:
		if not can_harvest():
			return False
		if SPL < NSUN or (SST >= 10 and SUN[c] < SMX):
			return False
		harvest()
		SUN.pop(c)
		SST -= 1
		smax()
		if get_ground_type() == Grounds.Soil:
			till()
	if SUNT and SPL < NSUN and num_items(Items.Carrot) >= 1:
		if get_ground_type() != Grounds.Soil:
			till()
		if plant(Entities.Sunflower):
			SUN[c] = measure()
			SPL += 1
			SST += 1
			smax()
			upd()
			return r
	if FW:
		if plant(Entities.Tree):
			PT += 1
			if get_water() < WLO and num_items(Items.Water) >= 1:
				use_item(Items.Water)
			upd()
	return r


def tb(c):
	global PB
	e = get_entity_type()
	r = False
	if e == Entities.Bush:
		if not can_harvest():
			return False
		harvest()
		PB -= 1
		r = True
		upd()
	elif e == Entities.Grass:
		if num_items(Items.Hay) < HTG and can_harvest():
			harvest()
			r = True
	if FW:
		if plant(Entities.Bush):
			PB += 1
			upd()
	return r


def route(n, K, lay, tr):
	# K == n: torus column walk (every cell once, n * n moves); K < n (even): a snake over
	# columns 0..K-1, then east along row 0 back to column 0
	fs = []
	ds = []
	cs = []
	x = 0
	y = 0
	if K == n:
		for c in range(n):
			for k in range(n):
				cs.append(x * n + y)
				if k < n - 1:
					ds.append(North)
					y = (y + 1) % n
				else:
					ds.append(East)
					x = (x + 1) % n
	else:
		for c in range(K):
			for k in range(n):
				cs.append(x * n + y)
				if k < n - 1:
					if c % 2 == 0:
						ds.append(North)
						y += 1
					else:
						ds.append(South)
						y -= 1
				else:
					ds.append(East)
					x += 1
		while x < n:
			cs.append(x * n + y)
			ds.append(East)
			x += 1
	for c in cs:
		ch = lay[c % n][c // n]
		if ch == 'T' and not tr:
			ch = 'B'
		if ch == 'G':
			fs.append(tg)
		elif ch == 'C':
			fs.append(tc)
		elif ch == 'T':
			fs.append(tt)
		else:
			fs.append(tb)
	return (fs, ds, cs)


def run_farm(need):
	global NEEDL
	global NDC
	global NDW
	global NDH
	global CCOST
	global YTR
	global YBU
	global KCF
	global MCPY
	global POW
	global NSUN
	global SUNT
	n = get_world_size()
	tr = num_unlocked(Unlocks.Trees) > 0
	ph = PH6
	NSUN = NSUNE
	SUNT = SUNTE
	if n == 3:
		lay = LAY3
	elif n == 4:
		if tr:
			lay = LAY4C
		else:
			lay = LAY4B
	elif Items.Hay in need:
		lay = LAY6E
	else:
		lay = LAY6D
		ph = PH6D
		NSUN = NSUND
		SUNT = SUNTD
	if n != 6:
		ph = [(n, 9999)]
	POW = num_unlocked(Unlocks.Sunflowers) > 0
	if not POW:
		NSUN = 0
	CCOST = lvl(Unlocks.Carrots)
	yc = lvl(Unlocks.Carrots)
	YTR = 5 * lvl(Unlocks.Trees) * MT
	YBU = lvl(Unlocks.Trees) * MT
	KCF = 1 / (yc * MC)
	MCPY = yc * MCP
	NEEDL = []
	for it in need:
		NEEDL.append((it, need[it]))
	if Items.Carrot in need:
		NDC = need[Items.Carrot]
	NDC += NSUN
	if Items.Wood in need:
		NDW = need[Items.Wood]
	if Items.Hay in need:
		NDH = need[Items.Hay]
	for c in range(n * n):
		RT.append(0)
	upd()
	for p in ph:
		K = p[0]
		r = route(n, K, lay, tr)
		fs = r[0]
		ds = r[1]
		cs = r[2]
		L = len(fs)
		until = p[1]
		while get_time() < until or (STAYB and K < n and NSUN > 0 and (SPL < NSUN or SST >= 10)):
			if SPL < NSUN and get_time() > SUNMAX:
				NSUN = SPL
			for i in range(L):
				f = fs[i]
				if f(cs[i]) and done():
					return
				move(ds[i])
