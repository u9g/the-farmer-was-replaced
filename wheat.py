TARGET = 100000000  # stop once you have this much hay


def tend():
	if get_ground_type() == Grounds.Soil:
		harvest()
		till()  # back to grassland so grass regrows by itself
	if can_harvest():
		harvest()


def farm():
	# Work one column bottom to top, then jump sideways past the other drones' columns.
	n = get_world_size()
	while num_items(Items.Hay) < TARGET:
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
