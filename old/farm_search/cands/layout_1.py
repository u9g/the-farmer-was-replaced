# layout_1: fixed crop per cell, one torus walk, harvest what is ripe and replant.

G = 0
B = 1
T = 2
C = 3


def lay(n):
	L = {}
	for x in range(n):
		for y in range(n):
			if n == 3:
				r = [C, B, G]
				L[(x, y)] = r[y]
			elif num_unlocked(Unlocks.Trees) > 0:
				if (x + y) % 2 == 0:
					L[(x, y)] = T
				else:
					L[(x, y)] = C
			else:
				if (x + y) % 2 == 0:
					L[(x, y)] = B
				else:
					L[(x, y)] = C
	return L


def done(need):
	for it in need:
		if num_items(it) < need[it]:
			return False
	return True


ENT = [Entities.Grass, Entities.Bush, Entities.Tree, Entities.Carrot]


def cell(c):
	e = get_entity_type()
	if c == G:
		if e == Entities.Grass:
			if can_harvest():
				harvest()
			return
		if e != None:
			if not can_harvest():
				return
			harvest()
		if get_ground_type() == Grounds.Soil:
			till()
		return
	want = ENT[c]
	if e == want:
		if not can_harvest():
			return
		harvest()
	elif e == Entities.Grass:
		if can_harvest():
			harvest()
	elif e != None:
		if not can_harvest():
			return
		harvest()
	if c == C:
		if get_ground_type() != Grounds.Soil:
			till()
	plant(want)


def run_farm(need):
	n = get_world_size()
	L = lay(n)
	k = 0
	while not done(need):
		cell(L[(get_pos_x(), get_pos_y())])
		k += 1
		if k % n == 0:
			move(East)
		else:
			move(North)
