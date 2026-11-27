# Measure the script's own rounds (farm(item, ...)) in many states; writes rates.json
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(_os.path.dirname(HERE))
import subprocess, json, re, itertools, sys
from concurrent.futures import ThreadPoolExecutor
SIM = REPO + '/.claude/skills/tfwr-sim/tfwr_sim.rs'
PROBE = HERE + '/work/probe/run_probe.py'
BASE = dict(plant=1, speed=4, carrots=3, trees=3, grass=3, watering=3, sunflowers=1, fertilizer=1)
GIVE = dict(carrot=1e6, wood=1e6, hay=1e6, power=1e6, gold=1e6, bone=2e6, weird_substance=1e5)
jobs = []
for ex, mf, pk in itertools.product([4, 5, 6], [0, 1, 2], [1, 2, 3]):
    jobs.append(('pumpkin', dict(expand=ex, megafarm=mf, pumpkins=pk), {'cells': [36, 64, 144][ex - 4] * 5}))
for ex, mf in itertools.product([4, 5, 6], [0, 1, 2]):
    jobs.append(('weird_substance', dict(expand=ex, megafarm=mf), {}))
    jobs.append(('gold', dict(expand=ex, megafarm=mf, mazes=1), {}))
def run(j):
    item, st, extra = j
    s = dict(BASE); s.update(st)
    if s.get('megafarm'): s['mazes'] = max(s.get('mazes', 0), 1)
    n = {4: 6, 5: 8, 6: 12}[s['expand']]
    amt = {'pumpkin': n * n * 6 * 2 ** (s.get('pumpkins', 1) - 1) * 5, 'weird_substance': 1500, 'gold': n * n * 40}[item]
    give = dict(GIVE)
    if item == 'gold': give['weird_substance'] = 1e6
    if item == 'weird_substance': give['weird_substance'] = 0
    if item == 'gold': give['gold'] = 0
    args = ['cargo', '+nightly', '-Zscript', SIM, PROBE + '@PITEM=Items.' + item.capitalize().replace('_s', '_S') + '@PAMT=' + str(amt),
            '--leaderboard', 'fastest_reset', '--seeds', '1', '--jobs', '1']
    for k, v in s.items(): args += ['--set', f'{k}={v}']
    for k, v in give.items(): args += ['--give', f'{k}={v}']
    if item == 'gold':  # the probe waits for 1M gold to end: give it after
        pass
    out = subprocess.run(args, capture_output=True, text=True, timeout=600).stdout
    m = re.search(r'PROBE dt ([\d.]+)(.*)', out)
    if not m: return (item, st, None, out[-300:])
    d = dict(zip(m.group(2).split()[::2], map(float, m.group(2).split()[1::2])))
    return (item, st, float(m.group(1)), d)
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(run, jobs))
json.dump(res, open(sys.argv[1], 'w'), indent=0)
for r in res:
    print(r[0], r[1], r[2], r[3] if r[2] is None else {k: round(v) for k, v in r[3].items()})
