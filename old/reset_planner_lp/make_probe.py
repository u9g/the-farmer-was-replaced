# Writes probe/run_probe.py: run_reset.py's code with its final run replaced by one farm() call
# that is timed and reports the net change of every item (one row of measured rates).
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(_os.path.dirname(HERE))
import sys
src = open(REPO + '/run_reset.py').read()
tail = src.index('# (skipped when the script is restarted')
probe = '''
PITEM = Items.Pumpkin
PAMT = 3000
PPOWER = 0
PMIX = []
ITS = [Items.Hay, Items.Wood, Items.Carrot, Items.Pumpkin, Items.Cactus, Items.Weird_Substance, Items.Gold, Items.Bone, Items.Power, Items.Water, Items.Fertilizer]
NAMES = ["hay", "wood", "carrot", "pumpkin", "cactus", "weird", "gold", "bone", "power", "water", "fert"]
b0 = []
for it in ITS:
	b0.append(num_items(it))
tp = get_time()
if len(PMIX) > 0:
	need = {}
	mi = [Items.Hay, Items.Wood, Items.Carrot]
	for q in range(3):
		if PMIX[q] > 0:
			need[mi[q]] = num_items(mi[q]) + PAMT * PMIX[q]
	while True:
		short = False
		for it in need:
			if num_items(it) < need[it]:
				short = True
		if not short:
			break
		mixed_round((need, need))
	PAMT = 0
goal = num_items(PITEM) + PAMT
while num_items(PITEM) < goal:
	if PITEM == Items.Power:
		power_round()
	else:
		farm(PITEM, goal)
dt = get_time() - tp
s = "PROBE dt " + str(dt)
for i in range(len(ITS)):
	d = num_items(ITS[i]) - b0[i]
	if d != 0:
		s = s + " " + NAMES[i] + " " + str(d)
quick_print(s)
if num_items(Items.Gold) < 0:
	pass
unlock(Unlocks.Leaderboard)
'''
open(sys.argv[1] + '/run_probe.py', 'w').write(src[:tail] + probe)
