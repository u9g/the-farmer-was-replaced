# Start-up cost of each round type: time of a farm() call asked for 1 more item (the round's fixed cost)
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(_os.path.dirname(HERE))
import subprocess, json, re, itertools, sys
from concurrent.futures import ThreadPoolExecutor
SIM = REPO + '/.claude/skills/tfwr-sim/tfwr_sim.rs'
PROBE = HERE + '/work/probe/run_probe.py'
jobs = []
for ex in (2, 3, 4, 5):
    for mf, poly in ([(0, 0)] if ex < 4 else [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]):
        for item in ('hay', 'wood', 'carrot'):
            for seed in (1, 2):
                jobs.append((item, dict(expand=ex, megafarm=mf, polyculture=poly), seed))
for ex in (3, 4, 5):
    for mf in (0, 1, 2):
        for item in ('power', 'pumpkin', 'weird_substance', 'gold'):
            if item != 'power' and ex < 4: continue
            for seed in (1, 2):
                jobs.append((item, dict(expand=ex, megafarm=mf, polyculture=0), seed))
def run(j):
    item, st, seed = j
    s = dict(plant=1, carrots=3, grass=3, trees=3, watering=1, speed=3, expand=st['expand'])
    if st['polyculture']: s.update(polyculture=1, pumpkins=1)
    if st['megafarm']: s.update(megafarm=st['megafarm'], mazes=1, fertilizer=1)
    if item in ('power', 'pumpkin', 'weird_substance', 'gold'): s.update(sunflowers=1, pumpkins=1, fertilizer=1, mazes=1)
    give = dict(carrot=1e6, wood=1e6, hay=1e6, power=1e5, weird_substance=1e6, gold=1e6, bone=2e6)
    give[item] = 0
    name = {'weird_substance': 'Weird_Substance'}.get(item, item.capitalize())
    args = ['cargo', '+nightly', '-Zscript', SIM, PROBE + '@PITEM=Items.' + name + '@PAMT=1', '--leaderboard', 'fastest_reset',
            '--seed', str(seed), '--seeds', '1', '--jobs', '1']
    for k, v in s.items(): args += ['--set', f'{k}={v}']
    for k, v in give.items(): args += ['--give', f'{k}={v}']
    out = subprocess.run(args, capture_output=True, text=True, timeout=600).stdout
    m = re.search(r'PROBE dt ([\d.]+)', out)
    return (item, st, seed, float(m.group(1)) if m else None)
with ThreadPoolExecutor(4) as ex: res = list(ex.map(run, jobs))
json.dump(res, open(sys.argv[1], 'w'))
agg = {}
for item, st, seed, dt in res:
    if dt is not None: agg.setdefault((item, st['expand'], st['megafarm'], st['polyculture']), []).append(dt)
for k in sorted(agg): print(k, [round(x, 1) for x in agg[k]])
print(sum(1 for r in res if r[3] is None), 'failed')
