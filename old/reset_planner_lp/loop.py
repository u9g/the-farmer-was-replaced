# closed loop: solve -> execute in the simulator -> correct the rates of the rounds each stretch used -> repeat
import subprocess, pickle, json, re, os, sys
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(_os.path.dirname(HERE))
D = HERE + '/work'
os.makedirs(D + '/exec', exist_ok=True)
SIM = REPO + '/.claude/skills/tfwr-sim/tfwr_sim.rs'
def sim_profile(script, seeds=4):
    out = subprocess.run(['cargo', '+nightly', '-Zscript', SIM, script, '--leaderboard', 'fastest_reset', '--seed', '1', '--seeds', str(seeds),
                          '--quiet', '--profile', '--until', 'megafarm=2'], capture_output=True, text=True, cwd=REPO).stdout
    t = {}
    for l in out.splitlines():
        m = re.match(r'\s+[\d:.]+s?\s+([\d:.]+s?)\s+(\w+(?: \d+)?)\s', l)
        if m:
            x = m.group(1).rstrip('s').split(':'); t[m.group(2)] = float(x[0]) * 60 + float(x[1]) if len(x) == 2 else float(x[0])
    m = re.search(r'mean of \d+ runs, ([\d:]+) each', out)
    tot = m.group(1) if m else '?'
    return t, tot
def lab(u):
    n = u[0].capitalize()
    return n if u[0] in ('plant', 'sunflowers', 'polyculture') else f'{n} {u[1]}'
def update(sched, ex):
    corr = json.load(open(f'{D}/corr.json')) if os.path.exists(f'{D}/corr.json') else {}
    for u, acts, used in sched:
        L = sum(x for x, _ in used); E = ex.get(lab(u))
        if E is None or L < 1: continue
        ratio = min(max(E / L, 0.25), 4.0)
        for x, key in used:
            k = repr(tuple(key)); corr[k] = corr.get(k, 1.0) / ratio ** (0.7 * x / L)
    json.dump(corr, open(f'{D}/corr.json', 'w'))
for it in range(int(sys.argv[1])):
    procs = [subprocess.Popen(['python3', HERE + '/plan_lp.py', HERE + '/data/profile_seeds1-8.txt', str(s), sys.argv[2]], cwd=HERE, stdout=subprocess.PIPE, text=True) for s in (1, 2)]
    outs = [p.communicate()[0] for p in procs]
    preds = [float(re.search(r'best order found: LP (\d+)', o).group(1)) for o in outs]
    s = 1 + preds.index(min(preds))
    subprocess.run(['python3', HERE + '/make_exec.py', f'{D}/sched_{s}.pkl', 'best', 'cur'], cwd=D)
    best, (tb, sb), (tc, sc) = pickle.load(open(f'{D}/sched_{s}.pkl', 'rb'))
    eb, totb = sim_profile(f'{D}/exec/run_best.py'); ec, totc = sim_profile(f'{D}/exec/run_cur.py')
    print(f'iter {it}: searched plan predicted {tb:.0f}s executed {totb} | current-order plan predicted {tc:.0f}s executed {totc}  (base run_plan 15:24)', flush=True)
    update(sb, eb); update(sc, ec)
    pickle.dump((best, sb), open(f'{D}/iter_{it}.pkl', 'wb'))
