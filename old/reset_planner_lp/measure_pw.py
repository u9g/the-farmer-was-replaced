import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(_os.path.dirname(HERE))
import subprocess, json, re, itertools, sys
from concurrent.futures import ThreadPoolExecutor
SIM = REPO + '/.claude/skills/tfwr-sim/tfwr_sim.rs'
PROBE = HERE + '/work/probe/run_probe.py'
jobs = list(itertools.product((3, 4, 5), (0, 1, 2), (3, 5)))
def run(j):
    ex, mf, sp = j
    s = dict(plant=1, carrots=3, grass=3, trees=3, watering=3, sunflowers=1, speed=sp, expand=ex)
    if mf: s.update(megafarm=mf, mazes=1, fertilizer=1)
    args = ['cargo', '+nightly', '-Zscript', SIM, PROBE + '@PITEM=Items.Power@PAMT=300', '--leaderboard', 'fastest_reset', '--seeds', '1', '--jobs', '1']
    for k, v in s.items(): args += ['--set', f'{k}={v}']
    for k, v in dict(carrot=1e5, wood=1e5, hay=1e5, water=1e4).items(): args += ['--give', f'{k}={v}']
    out = subprocess.run(args, capture_output=True, text=True, timeout=600).stdout
    m = re.search(r'PROBE dt ([\d.]+)(.*)', out)
    if not m: return (j, None, out[-200:])
    return (j, float(m.group(1)), dict(zip(m.group(2).split()[::2], map(float, m.group(2).split()[1::2]))))
with ThreadPoolExecutor(4) as ex: res = list(ex.map(run, jobs))
json.dump(res, open(sys.argv[1], 'w'))
for r in res: print(r[0], r[1], r[2] if r[1] is None else {k: round(v) for k, v in r[2].items()})
