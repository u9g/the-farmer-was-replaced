# Score a farm design: a .py file that defines run_farm(need) (need: {Items.X: amount}; farm until
# num_items(X) >= amount for every X). It runs from a fresh field with no hay, wood or carrots in
# the states the fastest reset passes through with one drone, and is scored by game seconds.
# usage: python3 eval_farm.py cand.py [more.py ...] [--seeds N]     (baseline: cands/baseline.py)
import os, re, subprocess, sys, json
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SIM = REPO + '/.claude/skills/tfwr-sim/tfwr_sim.rs'
# (name, unlocks, need, what run_reset's stretch took in the real run)
STATES = [
    ('A 3x3 speed2', dict(plant=1, expand=2, speed=2, carrots=1), {'Wood': 50, 'Carrot': 50}),
    ('B 4x4 no trees', dict(plant=1, expand=3, speed=3, carrots=1, grass=2), {'Wood': 50, 'Carrot': 70}),
    ('C 4x4 trees2', dict(plant=1, expand=3, speed=3, carrots=2, grass=2, trees=2, watering=2), {'Wood': 1250}),
    ('D 6x6 carrots', dict(plant=1, expand=4, speed=3, carrots=3, grass=3, trees=2, watering=2, sunflowers=1), {'Carrot': 500}),
    ('E 6x6 mixed', dict(plant=1, expand=4, speed=4, carrots=3, grass=3, trees=3, watering=2, sunflowers=1, fertilizer=1), {'Hay': 1200, 'Wood': 800, 'Carrot': 300}),
]
DRIVER = '''

def _need_short(need):
	for it in need:
		if num_items(it) < need[it]:
			return True
	return False


_need = {%s}
_t0 = get_time()
run_farm(_need)
if _need_short(_need):
	quick_print("EVAL short")
quick_print("EVAL dt " + str(get_time() - _t0))
'''
def run(job):
    cand, (name, st, need), seed = job
    src = open(cand).read()
    d = os.path.join(HERE, 'work', os.path.basename(cand)[:-3])
    os.makedirs(d, exist_ok=True)
    tag = re.sub(r'\W', '', name)
    f = os.path.join(d, f'h_{tag}_s{seed}.py')
    open(f, 'w').write(src + DRIVER % ', '.join(f'Items.{k}: {v}' for k, v in need.items()))
    args = ['cargo', '+nightly', '-Zscript', SIM, f, '--leaderboard', 'fastest_reset', '--seed', str(seed), '--seeds', '1', '--jobs', '1']
    for k, v in st.items(): args += ['--set', f'{k}={v}']
    out = subprocess.run(args, capture_output=True, text=True, timeout=900).stdout + ''
    m = re.search(r'EVAL dt ([\d.]+)', out)
    if not m or 'EVAL short' in out:
        err = re.search(r'(ERROR[^\n]*|error[^\n]*)', out)
        return (cand, name, seed, None, err.group(1)[:200] if err else out[-300:])
    return (cand, name, seed, float(m.group(1)), '')
if __name__ == '__main__':
    args = sys.argv[1:]; seeds = 2
    if '--seeds' in args:
        i = args.index('--seeds'); seeds = int(args[i + 1]); del args[i:i + 2]
    jobs = [(c, s, 1000 + k) for c in args for s in STATES for k in range(seeds)]
    with ThreadPoolExecutor(4) as ex: res = list(ex.map(run, jobs))
    for c in args:
        tot = 0; ok = True; parts = []
        for name, _, _ in STATES:
            ts = [r[3] for r in res if r[0] == c and r[1] == name]
            if any(t is None for t in ts):
                ok = False; e = [r[4] for r in res if r[0] == c and r[1] == name and r[3] is None][0]
                parts.append(f'{name}: FAILED ({e})')
            else:
                m = sum(ts) / len(ts); tot += m; parts.append(f'{name}: {m:.1f}s')
        print(f"{os.path.basename(c)}: total {'FAILED' if not ok else f'{tot:.1f}s'}")
        for p in parts: print('   ', p)
