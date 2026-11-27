# layout_7: diagonal bands on the 6x6 farm, sunflower power.
# Cells on one diagonal d = (x - y) % 6 mostly hold one crop. Moving East goes to diagonal d + 1,
# North to d - 1, so two neighbouring diagonals form a band the drone walks as a staircase
# (E, N, E, N, ...): every move lands on a cell to tend, and a band's 12 cells come round in 12
# moves. A crop on a two-wide band has most cells within companion reach holding other crops.
# Sunflowers (10 on the field, the one with most petals cut when power runs low: 8 power) double
# the drone's speed.

LAYS = {
	# carrots on diagonals 0, 1; grass 2, 4; trees 3, 5
	'D': ['CGTGTC', 'GTGTCC', 'TGTCCG', 'GTCCGT', 'TCCGTG', 'CCGTGT'],
	# grass on diagonals 0, 1; the rest trees, carrots and sunflowers
	'E': ['GSTCSG', 'STCSGG', 'TCCGGS', 'CSGGST', 'SGGSTC', 'GGSTCC'],
}
MEST = 1.9
PW_LO = 6
EX_GAP = 6.5
DBG = False

NW = 0
NH = 0
NC = 0
CC = 1
CY = 1.0
CYL = 1.0
PENDC = 0
HW = True
HH = True
HC = True
HS = True
TY = []
SUN = {}


def state():
	n = get_world_size()
	if n == 3:
		return 'A'
	if n == 4:
		if num_unlocked(Unlocks.Trees) > 0:
			return 'C'
		return 'B'
	if num_unlocked(Unlocks.Fertilizer) > 0:
		return 'E'
	return 'D'


def flags():
	# what is still needed, worked out once a band
	global HW
	global HH
	global HC
	w = num_items(Items.Wood)
	h = num_items(Items.Hay)
	c = num_items(Items.Carrot)
	left = NC - c - PENDC
	seeds = 0
	if left > 0:
		seeds = (left + CYL - 1) // CYL
	HW = NW + seeds * CC > w
	HH = NH + seeds * CC > h
	HC = left > 0
	if DBG:
		quick_print(get_time(), w, h, c, PENDC, num_items(Items.Power), len(SUN))


def done():
	return num_items(Items.Wood) >= NW and num_items(Items.Hay) >= NH and num_items(Items.Carrot) >= NC


def tend():
	global PENDC
	x = get_pos_x()
	y = get_pos_y()
	t = TY[x * 6 + y]
	e = get_entity_type()
	if t == 'G':
		if e == Entities.Grass:
			if HH and can_harvest():
				harvest()
		elif e == None or can_harvest():
			if e != None:
				harvest()
			if get_ground_type() == Grounds.Soil:
				till()
	elif t == 'C':
		if e == Entities.Carrot:
			if can_harvest():
				harvest()
				PENDC -= CYL
				if HC and plant(Entities.Carrot):
					PENDC += CYL
		elif e == None:
			if HC and plant(Entities.Carrot):
				PENDC += CYL
		elif e == Entities.Grass or can_harvest():
			if HH and can_harvest():
				harvest()
			if HC and num_items(Items.Wood) >= CC and num_items(Items.Hay) >= CC:
				till()
				if plant(Entities.Carrot):
					PENDC += CYL
	elif t == 'T':
		if e == Entities.Tree:
			if HW and can_harvest():
				harvest()
				plant(Entities.Tree)
		elif e == Entities.Grass or e == None or can_harvest():
			if e != None and HH and can_harvest():
				harvest()
			plant(Entities.Tree)
	elif t == 'S':
		if e == Entities.Sunflower:
			if len(SUN) >= 10 and num_items(Items.Power) < PW_LO and can_harvest():
				p = SUN[(x, y)]
				for q in SUN:
					if SUN[q] > p:
						return
				harvest()
				SUN.pop((x, y))
				if plant(Entities.Sunflower):
					SUN[(x, y)] = measure()
		elif HS and num_items(Items.Carrot) >= 1:
			if e == Entities.Grass:
				if HH and can_harvest():
					harvest()
			if e != None or get_ground_type() != Grounds.Soil:
				till()
			if plant(Entities.Sunflower):
				SUN[(x, y)] = measure()
		elif e == Entities.Grass and HH and can_harvest():
			harvest()


def band(k, last):
	# k moves along the band from here (tending each cell reached), then `last` (East / North / None)
	ev = (get_pos_x() - get_pos_y()) % 2 == 0
	for j in range(k):
		if ev:
			move(East)
		else:
			move(North)
		ev = not ev
		if done():
			return True
		tend()
	if last != None:
		move(last)
		if done():
			return True
		tend()
	return False


def setup(need):
	global NW
	global NH
	global NC
	global CC
	global CY
	global CYL
	global PENDC
	global TY
	global HS
	st = state()
	if Items.Wood in need:
		NW = need[Items.Wood]
	if Items.Hay in need:
		NH = need[Items.Hay]
	if Items.Carrot in need:
		NC = need[Items.Carrot]
	lc = 2 ** (num_unlocked(Unlocks.Carrots) - 1)
	CC = lc
	CY = lc * MEST
	CYL = lc * CYL_F
	PENDC = 0
	L = LAYS[st]
	TY = []
	for x in range(6):
		for y in range(6):
			TY.append(L[5 - y][x])
	HS = num_unlocked(Unlocks.Sunflowers) > 0
	return st


CYL_F = 1.2


def run_farm(need):
	st = setup(need)
	while get_pos_x() != 0:
		move(East)
	while get_pos_y() != 0:
		move(North)
	flags()
	tend()
	if st == 'D':
		# start: trees on band 4-5 (in via North), the carrot band (grass for hay), trees on band
		# 2-3, then band 4-5 again (its trees ripe: wood) and into the carrot band
		move(North)
		tend()
		if band(12, East):
			return
		flags()
		if band(11, East):
			return
		if band(11, East):
			return
		if band(11, East):
			return
		while True:
			# carrot band up, side band 2-3 round, carrot band down, side band 4-5 round
			flags()
			if band(11, East):
				return
			flags()
			if band(12, North):
				return
			flags()
			if band(11, North):
				return
			flags()
			if band(12, East):
				return
	else:
		# grass band (diagonals 0, 1) round after round; every EX_GAP seconds the rest of the field
		last = -100
		while True:
			flags()
			if get_time() - last >= EX_GAP:
				last = get_time()
				if band(11, East):
					return
				if band(11, East):
					return
				if band(11, East):
					return
			elif band(12, None):
				return
