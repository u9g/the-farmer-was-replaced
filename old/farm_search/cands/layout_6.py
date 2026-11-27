# layout_6: diagonal bands on the 6x6 farm.
# The crop of cell (x, y) depends only on its diagonal d = (x - y) % 6. Moving East goes to
# diagonal d + 1, North to d - 1, so two neighbouring diagonals form a band the drone walks as a
# staircase (E, N, E, N, ...): every move lands on a cell to tend. A band's 12 cells come round
# in 12 moves; 11 moves then East leaves for the next band up.
# Each crop's companion cell then holds one of the other types far more often than on a
# checkerboard (a crop band is two cells wide, so most cells within reach are other types).

DIAG = {'D': 'CCGTGT', 'E': 'GGTCCT'}
MEST = 1.9
DBG = False

NW = 0
NH = 0
NC = 0
CC = 1
CY = 1.0
PENDC = 0
HW = True
HH = True
HC = True


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
		seeds = (left + CY - 1) // CY
	HW = NW + seeds * CC > w
	HH = NH + seeds * CC > h
	HC = left > 0


def done():
	return num_items(Items.Wood) >= NW and num_items(Items.Hay) >= NH and num_items(Items.Carrot) >= NC


def tend(t):
	global PENDC
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
				PENDC -= CY
				if HC and plant(Entities.Carrot):
					PENDC += CY
		elif e == None:
			if HC and plant(Entities.Carrot):
				PENDC += CY
		elif e == Entities.Grass or can_harvest():
			if HH and can_harvest():
				harvest()
			if HC and num_items(Items.Wood) >= CC and num_items(Items.Hay) >= CC:
				till()
				if plant(Entities.Carrot):
					PENDC += CY
	elif t == 'T':
		if e == Entities.Tree:
			if HW and can_harvest():
				harvest()
				plant(Entities.Tree)
		elif e == Entities.Grass or e == None or can_harvest():
			if e != None and HH and can_harvest():
				harvest()
			plant(Entities.Tree)


def band(dg, k, last):
	# k moves along the band from here (tending each cell reached), then `last` (East / North / None)
	for j in range(k):
		if (get_pos_x() - get_pos_y()) % 6 % 2 == 0:
			move(East)
		else:
			move(North)
		if done():
			return True
		tend(dg[(get_pos_x() - get_pos_y()) % 6])
	if last != None:
		move(last)
		if done():
			return True
		tend(dg[(get_pos_x() - get_pos_y()) % 6])
	return False


def run_farm(need):
	global NW
	global NH
	global NC
	global CC
	global CY
	global PENDC
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
	PENDC = 0
	dg = DIAG[st]
	while get_pos_x() != 0:
		move(East)
	while get_pos_y() != 0:
		move(North)
	flags()
	tend(dg[0])
	if st == 'D':
		# carrots on diagonals 0, 1; grass 2, 4; trees 3, 5
		# start: plant the trees (bands 2-3 and 4-5), then alternate the carrot band with a side band
		move(East)
		move(East)
		tend(dg[2])
		if band(dg, 11, East):
			return
		if band(dg, 11, East):
			return
		while True:
			flags()
			if band(dg, 11, East):
				return
			flags()
			if band(dg, 11, East):
				return
			flags()
			if band(dg, 11, East):
				return
	else:
		# grass on diagonals 0, 1; trees 2, 5; carrots 3, 4
		while True:
			for r in range(GL):
				flags()
				if band(dg, 12, None):
					return
			flags()
			if band(dg, 11, East):
				return
			if band(dg, 11, East):
				return
			if band(dg, 11, East):
				return


GL = 2
