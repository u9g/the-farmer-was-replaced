import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(_os.path.dirname(HERE))
import subprocess, json, re, itertools, sys
from concurrent.futures import ThreadPoolExecutor
SIM = REPO + '/.claude/skills/tfwr-sim/tfwr_sim.rs'
PROBE = HERE + '/work/probe/run_probe.py'
CELLS = {2: 9, 3: 16, 4: 36, 5: 64}
jobs = []
for ex in (2, 3, 4, 5):
    for mf, poly in ([(0, 0)] if ex < 4 else [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]):
        for w, t, sp in itertools.product((0, 1), (0, 1), (1, 3, 5)):
            for item in ('hay', 'wood', 'carrot'):
                jobs.append((item, dict(expand=ex, megafarm=mf, polyculture=poly, watering=w, trees=t, speed=sp)))
def run(j):
    item, st = j
    s = dict(plant=1, carrots=1, grass=1); s.update({k: v for k, v in st.items() if v})
    if s.get('polyculture'): s['pumpkins'] = 1
    if s.get('megafarm'): s['mazes'] = 1; s['fertilizer'] = 1
    mult = 10 if st['polyculture'] else 1.8
    amt = int(CELLS[st['expand']] * (6 if item != 'carrot' else 3) * mult * 2 ** st['megafarm'] * (1.5 ** st['speed']) / 2) + 20
    give = dict(carrot=1e6, wood=1e6, hay=1e6, gold=1e6, bone=2e6)
    give[item] = 0
    args = ['cargo', '+nightly', '-Zscript', SIM, PROBE + '@PITEM=Items.' + item.capitalize() + '@PAMT=' + str(amt),
            '--leaderboard', 'fastest_reset', '--seeds', '1', '--jobs', '1']
    for k, v in s.items(): args += ['--set', f'{k}={v}']
    for k, v in give.items(): args += ['--give', f'{k}={v}']
    out = subprocess.run(args, capture_output=True, text=True, timeout=600).stdout
    m = re.search(r'PROBE dt ([\d.]+)(.*)', out)
    if not m: return (item, st, None, out[-200:])
    d = dict(zip(m.group(2).split()[::2], map(float, m.group(2).split()[1::2])))
    return (item, st, float(m.group(1)), d)
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(run, jobs))
json.dump(res, open(sys.argv[1], 'w'))
bad = [r for r in res if r[2] is None]
print(len(res), 'runs,', len(bad), 'failed')
for r in bad[:5]: print(r)
for r in res[:: max(1, len(res) // 25)]:
    if r[2]: print(r[0], r[1], round(r[2], 1), {k: round(v) for k, v in r[3].items()}, 'rate', round(r[3].get({'hay':'hay','wood':'wood','carrot':'carrot'}[r[0]], 0) / r[2], 2))
