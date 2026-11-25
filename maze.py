DIRS = [North, East, South, West]
DELTA = {North: (0, 1), South: (0, -1), East: (1, 0), West: (-1, 0)}
OPP = {North: South, South: North, East: West, West: East}
REUSES = 300

# Every drone has its own copy of these. A new drone starts with a copy of
# its parent's values, which is how the map gets handed to the workers.
links = {}  # (x, y) -> list of directions you can walk from that cell
up = {}  # (x, y) -> direction of the next cell toward homes[0]
depth = {}  # (x, y) -> number of steps to homes[0]
homes = []  # homes[i] is the cell where drone i waits
dists = []  # dists[i][(x, y)] -> number of steps from homes[i]
x = 0
y = 0
me = 0  # which home this drone owns
branch_dir = None
amount = 0
stop_level = 0  # harvest once the Weird Substance count is down to this


def scan():
	open_dirs = []
	for d in DIRS:
		if can_move(d):
			open_dirs.append(d)
	links[(x, y)] = open_dirs


def go(d):
	global x
	global y
	moved = move(d)
	x = get_pos_x()
	y = get_pos_y()
	return moved


# ---------- Phase 1: map the maze with every drone ----------


def map_from_here(blocked):
	# Depth-first walk of everything reachable without entering `blocked`.
	# At every fork, side branches are handed to new drones while any are free.
	global branch_dir
	seen = set()
	if blocked != None:
		seen.add(blocked)
	helpers = []
	trail = []
	while True:
		here = (x, y)
		if not here in links:
			scan()
		seen.add(here)
		todo = []
		for d in links[here]:
			dx, dy = DELTA[d]
			if not (x + dx, y + dy) in seen:
				todo.append(d)
		while len(todo) > 1:
			d = todo[len(todo) - 1]
			branch_dir = d
			helper = spawn_drone(map_branch)
			if helper == None:
				break
			todo.pop()
			helpers.append(helper)
			dx, dy = DELTA[d]
			seen.add((x + dx, y + dy))
		if len(todo) > 0:
			go(todo[0])
			trail.append(todo[0])
		elif len(trail) > 0:
			go(OPP[trail.pop()])
		else:
			break
	for helper in helpers:
		found = wait_for(helper)
		for cell in found:
			links[cell] = found[cell]


def map_branch():
	global links
	links = {}
	origin = (x, y)
	go(branch_dir)
	map_from_here(origin)
	return links


# ---------- Phase 2: distance tables, one drone per table ----------


def flood(src):
	# Breadth-first search over the whole map.
	# Returns (steps from src, direction toward src) for every cell.
	dist = {src: 0}
	toward = {}
	queue = [src]
	k = 0
	while k < len(queue):
		cell = queue[k]
		k += 1
		cx, cy = cell
		for d in links[cell]:
			dx, dy = DELTA[d]
			nxt = (cx + dx, cy + dy)
			if not nxt in dist:
				dist[nxt] = dist[cell] + 1
				toward[nxt] = OPP[d]
				queue.append(nxt)
	return dist, toward


def flood_task():
	dist, toward = flood(homes[me])
	return dist


def pick_homes(count):
	# Spread the homes over the field in a grid.
	n = get_world_size()
	cols = 1
	while cols * cols < count:
		cols += 1
	rows = (count + cols - 1) // cols
	result = []
	for i in range(count):
		hx = ((i % cols) * 2 + 1) * n // (cols * 2)
		hy = ((i // cols) * 2 + 1) * n // (rows * 2)
		result.append((hx, hy))
	return result


# ---------- Phase 3: fetch treasures ----------


def route(a, b):
	# Moves from a to b along the tree rooted at homes[0].
	head = []
	tail = []
	while a != b:
		if depth[a] >= depth[b]:
			d = up[a]
			head.append(d)
			dx, dy = DELTA[d]
			a = (a[0] + dx, a[1] + dy)
		else:
			d = up[b]
			tail.append(OPP[d])
			dx, dy = DELTA[d]
			b = (b[0] + dx, b[1] + dy)
	k = len(tail) - 1
	while k >= 0:
		head.append(tail[k])
		k -= 1
	return head


def owner(cell):
	# The drone whose home is closest to the cell. Every drone gets the same answer.
	best = 0
	for i in range(1, len(dists)):
		if dists[i][cell] < dists[best][cell]:
			best = i
	return best


def work():
	goal = None
	path = []
	k = 0
	while True:
		kind = get_entity_type()
		if kind != Entities.Hedge and kind != Entities.Treasure:
			return  # the maze was harvested
		treasure = measure()
		if treasure == None:
			return
		if owner(treasure) == me:
			target = treasure
		else:
			target = homes[me]
		here = (x, y)
		if kind == Entities.Treasure:
			# Any drone standing on the treasure uses it, owner or not.
			left = num_items(Items.Weird_Substance)
			if left < amount or left <= stop_level:
				harvest()
				return
			if not use_item(Items.Weird_Substance, amount):
				if get_entity_type() == Entities.Treasure:
					quick_print(
						"reuse refused, substance left:", left, "amount:", amount
					)
					harvest()
					return
			continue
		if here == target:
			continue
		if target != goal:
			path = route(here, target)
			goal = target
			k = 0
		if go(path[k]):
			k += 1
		else:
			goal = None  # blocked: plan again from the real position


def spawn_worker():
	return spawn_drone(work)


# ---------- Main loop ----------

clear()

while True:
	amount = get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
	plant(Entities.Bush)
	use_item(Items.Weird_Substance, amount)
	stop_level = num_items(Items.Weird_Substance) - REUSES * amount
	x = get_pos_x()
	y = get_pos_y()

	links = {}
	map_from_here(None)

	homes = pick_homes(max_drones())
	tasks = []
	for i in range(1, len(homes)):
		me = i
		tasks.append(spawn_drone(flood_task))
	me = 0
	depth, up = flood(homes[0])
	dists = [depth]
	for task in tasks:
		dists.append(wait_for(task))

	crew = []
	for i in range(1, len(homes)):
		me = i
		crew.append(spawn_worker())
	me = 0
	work()
	for drone in crew:
		if drone != None:
			wait_for(drone)
