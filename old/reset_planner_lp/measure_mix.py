# Mixed hay/wood/carrot rounds (one mixed_round with targets for several items, as the executor runs them)
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(_os.path.dirname(HERE))
import subprocess, json, re, itertools, sys
from concurrent.futures import ThreadPoolExecutor
SIM = REPO + '/.claude/skills/tfwr-sim/tfwr_sim.rs'
PROBE = HERE + '/work/probe/run_probe.py'
CELLS = {2: 9, 3: 16, 4: 36, 5: 64}
MIXES = {'hw': [1, 1, 0], 'hc': [1, 0, 1], 'wc': [0, 1, 1], 'hwc': [1, 1, 1]}
jobs = []
for ex in (2, 3, 4, 5):
    for mf, poly in ([(0, 0)] if ex < 4 else [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]):
        for w, t, sp in itertools.product((0, 1), (0, 1), (1, 3, 5)):
            if poly and not t: continue
            for mix in MIXES:
                jobs.append((mix, dict(expand=ex, megafarm=mf, polyculture=poly, watering=w, trees=t, speed=sp)))
def run(j):
    mix, st = j
    s = dict(plant=1, carrots=1, grass=1); s.update({k: v for k, v in st.items() if v})
    if s.get('polyculture'): s['pumpkins'] = 1
    if s.get('megafarm'): s['mazes'] = 1; s['fertilizer'] = 1
    mult = 10 if st['polyculture'] else 1.8
    amt = int(CELLS[st['expand']] * 3 * mult * 2 ** st['megafarm'] * (1.5 ** st['speed']) / 2) + 20
    f = MIXES[mix]
    give = dict(gold=1e6, bone=2e6, hay=2000 if not f[0] else 0, wood=2000 if not f[1] else 0, carrot=0)
    args = ['cargo', '+nightly', '-Zscript', SIM, PROBE + '@PMIX=' + str(f).replace(' ', '') + '@PAMT=' + str(amt),
            '--leaderboard', 'fastest_reset', '--seeds', '1', '--jobs', '1']
    for k, v in s.items(): args += ['--set', f'{k}={v}']
    for k, v in give.items(): args += ['--give', f'{k}={v}']
    out = subprocess.run(args, capture_output=True, text=True, timeout=600).stdout
    m = re.search(r'PROBE dt ([\d.]+)(.*)', out)
    if not m: return (mix, st, None, out[-200:])
    return (mix, st, float(m.group(1)), dict(zip(m.group(2).split()[::2], map(float, m.group(2).split()[1::2]))))
with ThreadPoolExecutor(4) as ex: res = list(ex.map(run, jobs))
json.dump(res, open(sys.argv[1], 'w'))
print(len(res), 'runs,', sum(1 for r in res if r[2] is None), 'failed')
for r in [r for r in res if r[2] is None][:3]: print(r)
