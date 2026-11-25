clear()

N = get_world_size()

def drone():
	while True:
		harvest()
		
		move([North, East, South, West][random() * 4 // 1])

spawn_drone(drone)
drone()