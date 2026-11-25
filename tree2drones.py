clear()

N = get_world_size()

def drone():
	while True:
		if (get_pos_x() % 2 == 0 and get_pos_y() % 2 == 0) or (get_pos_x() % 2 == 1 and get_pos_y() % 2 == 1):
			plant(Entities.Tree)
			if can_harvest():
				harvest()
		
		move([North, East, South, West][random() * 4 // 1])

spawn_drone(drone)
drone()