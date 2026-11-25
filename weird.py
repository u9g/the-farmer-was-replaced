TARGET = 1000000  # stop once you have this much Weird Substance


def tend():
	# Harvest what is ready, replant, and fertilize so the plant is infected.
	if can_harvest():
		harvest()
	kind = get_entity_type()
	if kind == None or kind == Entities.Grass:
		if (get_pos_x() + get_pos_y()) % 2 == 0:
			planted = plant(Entities.Tree)
		else:
			planted = plant(Entities.Bush)
		if planted:
			use_item(Items.Fertilizer)
			if can_harvest():
				harvest()


def farm():
	# Work one column bottom to top, then jump sideways past the other drones' columns.
	n = get_world_size()
	while num_items(Items.Weird_Substance) < TARGET:
		if num_items(Items.Fertilizer) == 0:
			return
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
