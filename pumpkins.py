# Pumpkin farm: one giant pumpkin over the whole field, harvested the instant it forms.
#
# Every drone owns a small block and walks it as a loop, replanting whatever died. Nobody waits
# for anybody: all tiles of a merged pumpkin measure the same, so a drone on the west edge that
# measures the same number on the east edge (measure wraps around) knows the pumpkin spans the
# field and cuts it straight away. The other drones see their tile go empty and replant.
#
# The last few tiles to grow hold up the whole field, so water and fertilizer are spent only on
# those. Needs an even world size.

clear()

N = get_world_size()
CACTUS_LEVEL = 5

# Blocks are 2 wide and TALL high, the smallest height that gives every block its own drone.
TALL = N
for h in range(N, 0, -1):
	if N % h == 0 and (N // 2) * (N // h) <= max_drones():
		TALL = h
M = 2 * TALL

# Seconds into a harvest cycle after which a tile that is still not grown gets fertilizer or
# water. The early value applies while there is more fertilizer than FERTILIZER_KEEP.
BOOST_AFTER = 7
BOOST_AFTER_RICH = 2
FERTILIZER_KEEP = 1000

OPPOSITE = {North: South, South: North, East: West, West: East}

FORWARD = []
for _ in range(TALL - 1):
	FORWARD.append(North)
FORWARD.append(East)
for _ in range(TALL - 1):
	FORWARD.append(South)
FORWARD.append(West)


def boost(began):
	spent = get_time() - began
	if num_items(Items.Fertilizer) > FERTILIZER_KEEP:
		if spent > BOOST_AFTER_RICH:
			use_item(Items.Fertilizer, 2)
	elif spent > BOOST_AFTER:
		if num_items(Items.Fertilizer) >= 2:
			use_item(Items.Fertilizer, 2)
		elif num_items(Items.Water) >= 4:
			if get_water() < 0.5:
				use_item(Items.Water, 4)


def worker(x0, y0):
	for _ in range(x0):
		move(East)
	for _ in range(y0):
		move(North)

	# Which way to look across the world border from each tile of the loop, if it is on the border.
	across = []
	for k in range(M):
		x = x0
		y = y0 + k
		if k >= TALL:
			x = x0 + 1
			y = y0 + M - 1 - k
		look = None
		if x == 0:
			look = West
		elif x == N - 1:
			look = East
		elif y == 0:
			look = South
		elif y == N - 1:
			look = North
		across.append(look)
	post = 0
	for k in range(M):
		if across[k] != None:
			post = k
			break

	at = 0
	while True:
		began = get_time()

		# Plant the whole block: once around the loop.
		for k in range(M):
			if get_ground_type() != Grounds.Soil:
				till()
			plant(Entities.Pumpkin)
			move(FORWARD[k])
		waiting = list(range(M))

		# Revisit the tiles that are not grown yet and replant the dead ones. An empty tile means
		# the giant pumpkin was already cut (it can form and be cut between two looks), so the
		# whole block has to be planted again.
		cut = False
		while waiting and not cut:
			still = []
			alone = len(waiting) == 1
			for k in waiting:
				ahead = (k - at) % M
				if ahead <= TALL:
					for _ in range(ahead):
						move(FORWARD[at])
						at = (at + 1) % M
				else:
					for _ in range(M - ahead):
						at = (at - 1) % M
						move(OPPOSITE[FORWARD[at]])
				while True:
					if can_harvest():
						break
					kind = get_entity_type()
					if kind == None:
						cut = True
						break
					if kind == Entities.Dead_Pumpkin:
						plant(Entities.Pumpkin)
						boost(began)
					if not alone:
						still.append(k)
						break
				if cut:
					break
			waiting = still

		if not cut:
			# Stand on a border tile if the block has one and wait for the giant pumpkin.
			ahead = (post - at) % M
			if ahead <= TALL:
				for _ in range(ahead):
					move(FORWARD[at])
					at = (at + 1) % M
			else:
				for _ in range(M - ahead):
					at = (at - 1) % M
					move(OPPOSITE[FORWARD[at]])
			look = across[at]
			if look == None:
				while can_harvest():
					pass
			else:
				while can_harvest():
					if measure() == measure(look):
						harvest()
						# Buy cactus level 5 (doubles every cactus harvest) as soon as the
						# pumpkins are there. unlock() does nothing when it is too expensive.
						if num_unlocked(Unlocks.Cactus) < CACTUS_LEVEL:
							if unlock(Unlocks.Cactus):
								quick_print("Bought cactus level", num_unlocked(Unlocks.Cactus))

		# Back to the first tile of the loop.
		if at <= TALL:
			for _ in range(at):
				at -= 1
				move(OPPOSITE[FORWARD[at]])
		else:
			for _ in range(M - at):
				move(FORWARD[at])
				at += 1
			at = 0


for x0 in range(0, N, 2):
	for y0 in range(0, N, TALL):
		if x0 + y0 > 0:
			spawn_drone(worker, x0, y0)
worker(0, 0)
