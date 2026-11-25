clear()

N = get_world_size()
D = min(max_drones(), N)
CACTUS_LEVEL = 5


def goto(x, y):
	while get_pos_x() < x:
		move(East)
	while get_pos_x() > x:
		move(West)
	while get_pos_y() < y:
		move(North)
	while get_pos_y() > y:
		move(South)


def worker():
	# Work out which strip this drone owns from where it was spawned
	x0 = get_pos_x()
	x1 = N
	for k in range(D):
		if k * N // D == x0:
			x1 = (k + 1) * N // D

	# Pass 1: serpentine over the strip, plant everything
	pending = []
	for x in range(x0, x1):
		for j in range(N):
			y = j
			if (x - x0) % 2 == 1:
				y = N - 1 - j
			goto(x, y)
			if get_ground_type() != Grounds.Soil:
				till()
			plant(Entities.Pumpkin)
			pending.append((x, y))

	# Later passes: only revisit unconfirmed tiles.
	# Walking the list backwards each time means the drone
	# retraces its path instead of flying back to the start.
	while len(pending) > 0:
		nxt = []
		for i in range(len(pending) - 1, -1, -1):
			x, y = pending[i]
			goto(x, y)
			if can_harvest():
				continue
			if get_entity_type() != Entities.Pumpkin:
				plant(Entities.Pumpkin)
			if get_water() < 0.75 and num_items(Items.Water) > 0:
				use_item(Items.Water)
			nxt.append((x, y))
		pending = nxt


while True:
	drones = []
	for k in range(D - 1):
		goto(k * N // D, 0)
		drones.append(spawn_drone(worker))
	goto((D - 1) * N // D, 0)
	worker()
	for d in drones:
		wait_for(d)
	harvest()

	# Buy cactus level 5 (doubles every cactus harvest) as soon as the pumpkins are there.
	# unlock() does nothing when it is too expensive.
	if num_unlocked(Unlocks.Cactus) < CACTUS_LEVEL:
		if unlock(Unlocks.Cactus):
			quick_print("Bought cactus level", num_unlocked(Unlocks.Cactus))
