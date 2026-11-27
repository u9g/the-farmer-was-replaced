# econ_1: fixed per-state layout, serpentine passes, demand-driven harvest/replant,
# minimal sunflower power (10+ sunflowers, cut only the max when power is low).

G = 0
W = 1
C = 2
S = 3

LAYOUTS = {
	3: [
		[C, W, G],
		[W, C, W],
		[G, W, C],
	],
	4: [
		[W, C, W, C],
		[C, W, G, W],
		[W, C, W, C],
		[G, W, C, W],
	],
	6: [
		[S, C, W, C, G, C],
		[S, G, C, G, C, G],
		[S, C, W, C, G, C],
		[S, G, C, G, C, G],
		[S, C, W, C, G, C],
		[S, S, S, S, S, G],
	],
}
M_EST = 1.5
PW_LO = 3
DBG = False


def lv(u):
	k = num_unlocked(u)
	if k <= 1:
		return 1
	return 2 ** (k - 1)


def run_farm(need):
	n = get_world_size()
	nh = 0
	nw = 0
	nc = 0
	if Items.Hay in need:
		nh = need[Items.Hay]
	if Items.Wood in need:
		nw = need[Items.Wood]
	if Items.Carrot in need:
		nc = need[Items.Carrot]
	trees = num_unlocked(Unlocks.Trees) > 0
	sun = num_unlocked(Unlocks.Sunflowers) > 0
	wood_e = Entities.Bush
	wy = lv(Unlocks.Trees)
	if trees:
		wood_e = Entities.Tree
		wy = 5 * lv(Unlocks.Trees)
	cy = lv(Unlocks.Carrots)
	lay = LAYOUTS[n]
	sf = {}
	pc = 0
	pw = 0
	x = 0
	y = 0
	dy = 1
	step = 0
	while True:
		r = lay[y][x]
		hv = num_items(Items.Hay)
		wd = num_items(Items.Wood)
		ca = num_items(Items.Carrot)
		rc = nc - ca - pc * cy * M_EST
		plantings = 0
		if rc > 0:
			plantings = rc / (cy * M_EST)
		hreq = nh + plantings * cy - hv
		wreq = nw + plantings * cy - wd - pw * wy * M_EST
		if r == G:
			if hreq > 0 and can_harvest():
				harvest()
		elif r == W:
			e = get_entity_type()
			if e == wood_e:
				if can_harvest():
					harvest()
					pw -= 1
					e = None
			if e != wood_e and wreq > 0:
				if plant(wood_e):
					pw += 1
					if trees and get_water() < 0.1 and num_items(Items.Water) >= 1:
						use_item(Items.Water)
		elif r == C:
			e = get_entity_type()
			if e == Entities.Carrot:
				if can_harvest():
					harvest()
					pc -= 1
					e = None
			if e != Entities.Carrot and rc > 0 and wd >= cy and hv >= cy:
				if get_ground_type() != Grounds.Soil:
					till()
				if plant(Entities.Carrot):
					pc += 1
		elif r == S:
			if sun:
				pos = (x, y)
				e = get_entity_type()
				if e == Entities.Sunflower:
					if num_items(Items.Power) < PW_LO and len(sf) >= 10 and can_harvest():
						m = 0
						for q in sf:
							if sf[q] > m:
								m = sf[q]
						if sf[pos] >= m:
							harvest()
							sf.pop(pos)
							e = None
				if e != Entities.Sunflower and ca >= 1:
					if get_ground_type() != Grounds.Soil:
						till()
					if plant(Entities.Sunflower):
						sf[pos] = measure()
		if num_items(Items.Hay) >= nh and num_items(Items.Wood) >= nw and num_items(Items.Carrot) >= nc:
			return
		# serpentine
		if (dy == 1 and y == n - 1) or (dy == -1 and y == 0):
			move(East)
			x = (x + 1) % n
			if DBG and x == 0:
				quick_print(get_time(), num_items(Items.Hay), num_items(Items.Wood), num_items(Items.Carrot), num_items(Items.Power), pc, pw)
			dy = -dy
		elif dy == 1:
			move(North)
			y += 1
		else:
			move(South)
			y -= 1
