# Writes cands/baseline.py: run_reset.py's code with run_farm(need) = its own one-drone mixed farm
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(os.path.dirname(os.path.dirname(HERE)), 'run_reset.py')).read()
tail = src.index('# (skipped when the script is restarted')
os.makedirs(os.path.join(HERE, 'cands'), exist_ok=True)
open(os.path.join(HERE, 'cands', 'baseline.py'), 'w').write(src[:tail] + '''

def run_farm(need):
	# run_reset's own one-drone mixed farm, as run_plan uses it
	while _need_short(need):
		power_check()
		mixed_round((need, need))
''')
