clear()

def make_maze():
	plant(Entities.Bush)
	N = get_world_size()
	use_item(Items.Weird_Substance, N)

def drone():
	while True:
		if get_entity_type() == Entities.Treasure:
			harvest()
			make_maze()

		move([North, East, South, West][random() * 4 // 1])

make_maze()
spawn_drone(drone)
drone()