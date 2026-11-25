clear()

N = get_world_size()


def plant_and_sort_row():
	for k in range(N):
		if get_ground_type() != Grounds.Soil:
			till()
		plant(Entities.Cactus)
		steps = 0
		while steps < k and measure(West) > measure():
			swap(West)
			move(West)
			steps += 1
		for _ in range(steps):
			move(East)
		move(East)  # after the last tile this wraps back to the start


def sort_column():
	for k in range(1, N):
		move(North)
		steps = 0
		while steps < k and measure(South) > measure():
			swap(South)
			move(South)
			steps += 1
		for _ in range(steps):
			move(North)
	move(North)  # wraps back to the start of the column


def on_each_line(fn, step):
	drones = []
	for k in range(N):
		drone = None
		if k < N - 1:
			drone = spawn_drone(fn)
		if drone:
			drones.append(drone)
		else:
			fn()
		move(step)
	for drone in drones:
		wait_for(drone)


while True:
	on_each_line(plant_and_sort_row, North)
	on_each_line(sort_column, East)
	while not can_harvest():
		pass
	harvest()
