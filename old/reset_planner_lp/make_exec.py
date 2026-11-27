import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(_os.path.dirname(HERE))
import pickle, sys
src = open(REPO + '/run_reset.py').read()
tail = src.index('# (skipped when the script is restarted')
ORDER = ['power', 'hay', 'wood', 'carrot', 'weird_substance', 'pumpkin', 'gold']
CAP = {'speed': 'Speed', 'plant': 'Plant', 'expand': 'Expand', 'carrots': 'Carrots', 'trees': 'Trees', 'grass': 'Grass', 'watering': 'Watering', 'sunflowers': 'Sunflowers', 'fertilizer': 'Fertilizer', 'mazes': 'Mazes', 'megafarm': 'Megafarm', 'pumpkins': 'Pumpkins', 'polyculture': 'Polyculture'}
IT = {'power': 'Power', 'hay': 'Hay', 'wood': 'Wood', 'carrot': 'Carrot', 'weird_substance': 'Weird_Substance', 'pumpkin': 'Pumpkin', 'gold': 'Gold'}
runner = '''
def run_sched(sc):
	for e in sc:
		u = e[0]
		if num_unlocked(u) >= e[1]:
			continue
		need = {}
		for p in e[2]:
			if p[0] == Items.Hay or p[0] == Items.Wood or p[0] == Items.Carrot:
				need[p[0]] = p[1]
		for p in e[2]:
			if p[0] == Items.Power:
				goal = p[1]
				while num_items(Items.Power) < goal:
					c = get_world_size() * get_world_size()
					if num_items(Items.Carrot) < c:
						mixed_round(({Items.Carrot: c * 2}, {Items.Carrot: c * 2}))
					power_round()
		if len(need) > 0:
			power_check()
			while True:
				short = False
				for it in need:
					if num_items(it) < need[it]:
						short = True
				if not short:
					break
				mixed_round((need, need))
		for p in e[2]:
			if p[0] == Items.Weird_Substance or p[0] == Items.Pumpkin or p[0] == Items.Gold:
				goal = p[1]
				while num_items(p[0]) < goal:
					farm(p[0], goal)
		while num_unlocked(u) < e[1]:
			if buy(u):
				break
			it = lacking(u)
			if it == Items.Hay or it == Items.Wood or it == Items.Carrot:
				power_check()
				mixed_round(set_need([(u, e[1])], 0))
			else:
				farm(it, get_cost(u)[it])


if num_unlocked(Unlocks.Carrots) == 0:
	opening()
run_sched(SCHED)
run_plan(PLAN)
log("done")
'''
for which in sys.argv[2:]:
    best, (t, sc), (t0, sc0) = pickle.load(open(sys.argv[1], 'rb'))
    use = sc if which == 'best' else sc0
    rows = []
    for u, acts, _ in use:
        ps = ['[Items.%s, %d]' % (IT[k], round(acts[k])) for k in ORDER if acts.get(k, 0) >= 1]
        rows.append('\t[Unlocks.%s, %d, [%s]],' % (CAP[u[0]], u[1], ', '.join(ps)))
    order = best if which == 'best' else None
    body = src[:tail]
    if which == 'best':
        # PLAN = the searched prefix + the rest of the current PLAN
        i = body.index('PLAN = [\n'); j = body.index(']\n', i)
        cur = body[i:j]
        lines = cur.splitlines()[1:]
        rest_start = [k for k, l in enumerate(lines) if 'Megafarm, 2' in l][0] + 1
        newplan = 'PLAN = [\n' + '\n'.join('\t(Unlocks.%s, %d),' % (CAP[a], b) for a, b in best) + '\n' + '\n'.join(lines[rest_start:]) + '\n'
        body = body[:i] + newplan + body[j:]
    _os.makedirs('exec', exist_ok=True)
    open(f'exec/run_{which}.py', 'w').write(body + 'SCHED = [\n' + '\n'.join(rows) + '\n]\n' + runner)
