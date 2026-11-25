TARGET = 1000000  # stop once you have this many carrots


def hop(dx, dy):
	for i in range(abs(dx)):
		if dx > 0:
			move(East)
		else:
			move(West)
	for i in range(abs(dy)):
		if dy > 0:
			move(North)
		else:
			move(South)


def place_companion(kind, px, py):
	# Fly to the companion tile, put the requested plant there, and fly back.
	dx = px - get_pos_x()
	dy = py - get_pos_y()
	hop(dx, dy)
	if get_entity_type() != kind:
		harvest()
		plant(kind)
	hop(-dx, -dy)


def tend():
	# Carrots only go on one colour of the checkerboard; the other colour is for companions.
	if (get_pos_x() + get_pos_y()) % 2 == 1:
		return
	if can_harvest():
		harvest()
	if get_ground_type() != Grounds.Soil:
		till()
	if get_entity_type() == None:
		if plant(Entities.Carrot):
			companion = get_companion()
			if companion != None:
				kind = companion[0]
				px = companion[1][0]
				py = companion[1][1]
				if (px + py) % 2 == 1:
					place_companion(kind, px, py)
	if get_water() < 0.75:
		use_item(Items.Water)


def farm():
	# Work one column bottom to top, then jump sideways past the other drones' columns.
	n = get_world_size()
	while num_items(Items.Carrot) < TARGET:
		for i in range(n):
			tend()
			move(North)
		for i in range(max_drones()):
			move(East)


clear()
while get_pos_x() > 0:
	move(West)
while get_pos_y() > 0:
	move(South)

crew = []
for i in range(max_drones() - 1):
	crew.append(spawn_drone(farm))
	move(East)
farm()
for drone in crew:
	if drone != None:
		wait_for(drone)
