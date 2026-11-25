# Polyculture weird trees: trees on the black squares of a checkerboard, grass on the white.
# A tree is replanted until its companion is grass on a white square, then made weird with one
# toggle. A weird tree with its companion yields 0.5 * 5 * 64 * 160 = 25,600 weird substance.

idx = 0


def goto(tx, ty):
	n = get_world_size()
	dx = (tx - get_pos_x()) % n
	if dx <= n // 2:
		for i in range(dx):
			move(East)
	else:
		for i in range(n - dx):
			move(West)
	dy = (ty - get_pos_y()) % n
	if dy <= n // 2:
		for i in range(dy):
			move(North)
	else:
		for i in range(n - dy):
			move(South)


def replant():
	plant(Entities.Tree)
	c = get_companion()
	while c[0] != Entities.Grass or (c[1][0] + c[1][1]) % 2 == 0:
		harvest()
		plant(Entities.Tree)
		c = get_companion()
	use_item(Items.Weird_Substance)


def work():
	x0 = (idx % 8) * 2
	y0 = (idx // 8) * 4
	goto(x0, y0)
	ring = [North, North, North, East, South, South, South, West]
	# plant the four trees once
	for d in ring:
		if (get_pos_x() + get_pos_y()) % 2 == 0:
			replant()
		move(d)
	while True:
		for d in ring:
			if (get_pos_x() + get_pos_y()) % 2 == 0 and can_harvest():
				harvest()
				replant()
			move(d)


clear()
for i in range(max_drones() - 1):
	idx = i + 1
	spawn_drone(work)
idx = 0
work()
