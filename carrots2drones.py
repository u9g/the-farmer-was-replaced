clear()

N = get_world_size()

def drone():
	while True:
		if can_harvest():
			harvest()
			plant(Entities.Carrot)
		
		move([North, East, South, West][random() * 4 // 1])

spawn_drone(drone)


for i in range(N):
	for j in range(N):
		harvest()
		till()
		plant(Entities.Carrot)
		
		if j != N - 1:
			if i % 2 == 0:
				move(North)
			else:
				move(South)
	move(East)

while True:
	for i in range(N):
		for j in range(N):
			harvest()
			#till()
			plant(Entities.Carrot)
			
			if j != N - 1:
				if i % 2 == 0:
					move(North)
				else:
					move(South)
		move(East)