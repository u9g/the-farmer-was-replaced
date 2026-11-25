clear()

N = get_world_size()

def drone():
	while True:
		if get_entity_type() == None:
			plant(Entities.Pumpkin)
		if get_entity_type() == Entities.Dead_Pumpkin:
			harvest()
			plant(Entities.Pumpkin)
		
		move([North, East, South, West][random() * 4 // 1])

spawn_drone(drone)


for i in range(N):
	for j in range(N):
		till()
		plant(Entities.Pumpkin)
		
		if j != N - 1:
			if i % 2 == 0:
				move(North)
			else:
				move(South)
	move(East)

issues = 0
while True:
	issues = 0
	for i in range(N):
		for j in range(N):
			if get_entity_type() == None:
				plant(Entities.Pumpkin)
			if get_entity_type() == Entities.Dead_Pumpkin:
				issues += 1
				harvest()
				plant(Entities.Pumpkin)
			
			if j != N - 1:
				if i % 2 == 0:
					move(North)
				else:
					move(South)
		move(East)
	if issues == 0:
		harvest()