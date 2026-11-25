DIRS = [North, East, South, West]
DELTA = {North: (0, 1), South: (0, -1), East: (1, 0), West: (-1, 0)}
OPP = {North: South, South: North, East: West, West: East}
REUSES = 300

links = {}  # (x, y) -> list of directions you can walk from that cell
x = 0
y = 0

def scan():
	# Record the open directions of the current cell.
	open_dirs = []
	for d in DIRS:
		if can_move(d):
			open_dirs.append(d)
	links[(x, y)] = open_dirs

def step(d):
	global x
	global y
	move(d)
	dx, dy = DELTA[d]
	x += dx
	y += dy
	if not (x, y) in links:
		scan()

def ordered_dirs(tx, ty):
	# Directions that lead toward the treasure come first.
	if tx >= x:
		h = East
		h2 = West
	else:
		h = West
		h2 = East
	if ty >= y:
		u = North
		u2 = South
	else:
		u = South
		u2 = North
	if abs(tx - x) >= abs(ty - y):
		return [h, u, u2, h2]
	return [u, h, h2, u2]

def find_path(start, target):
	# Breadth-first search over the cells mapped so far.
	# Returns the moves in reverse order, or None if the map can't reach the target yet.
	prev = {start: None}
	queue = [start]
	k = 0
	while k < len(queue):
		cell = queue[k]
		k += 1
		if cell == target:
			break
		if not cell in links:
			continue
		cx, cy = cell
		for d in links[cell]:
			dx, dy = DELTA[d]
			nxt = (cx + dx, cy + dy)
			if not nxt in prev:
				prev[nxt] = (cell, d)
				queue.append(nxt)
	if not target in prev:
		return None
	path = []
	cell = target
	while prev[cell] != None:
		cell, d = prev[cell]
		path.append(d)
	return path

def explore(tx, ty):
	# Depth-first search that prefers directions toward the treasure.
	seen = set()
	trail = []
	while x != tx or y != ty:
		seen.add((x, y))
		moved = False
		for d in ordered_dirs(tx, ty):
			if not d in links[(x, y)]:
				continue
			dx, dy = DELTA[d]
			if (x + dx, y + dy) in seen:
				continue
			step(d)
			trail.append(d)
			moved = True
			break
		if not moved:
			step(OPP[trail.pop()])

def go_to_treasure():
	tx, ty = measure()
	path = find_path((x, y), (tx, ty))
	if path == None:
		explore(tx, ty)
	else:
		k = len(path) - 1
		while k >= 0:
			step(path[k])
			k -= 1

clear()
x = get_pos_x()
y = get_pos_y()

while True:
	amount = get_world_size() * 2**(num_unlocked(Unlocks.Mazes) - 1)
	plant(Entities.Bush)
	use_item(Items.Weird_Substance, amount)
	links = {}
	scan()

	for n in range(REUSES):
		go_to_treasure()
		if num_items(Items.Weird_Substance) < amount:
			break
		use_item(Items.Weird_Substance, amount)  # moves the treasure

	go_to_treasure()
	harvest()