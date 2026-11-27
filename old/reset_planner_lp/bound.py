# Lower bound per stretch for the hay/wood/carrot stretches of run_reset (LP over crops).
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(_os.path.dirname(HERE))
import re, sys
from scipy.optimize import linprog
RS = REPO + '/.claude/skills/tfwr-sim/tfwr_sim.rs'
PROF = sys.argv[1]
src = open(RS).read()
SO = {}
for m in re.finditer(r'UnlockSO \{ name: "(\w+)".*?cost: &\[(.*?)\], multi_cost: &\[(.*?)\], multi_factor: ([\d.]+), max_level: (\d+)', src):
    pairs = lambda s: [(a, float(b)) for a, b in re.findall(r'\("(\w+)", ([\d.]+)\)', s)]
    mc = [pairs(x) for x in re.findall(r'&\[(.*?)\]', m.group(3))]
    SO[m.group(1)] = (pairs(m.group(2)), mc, float(m.group(4)))
def cost(name, num):  # num = levels already owned
    base, mc, f = SO[name]
    if num == 0: return dict(base)
    c = len(mc)
    if c < num:
        return {k: v * f ** (num - c) for k, v in mc[c - 1]}
    return dict(mc[num - 1])
CELLS = {0: 1, 1: 3, 2: 9, 3: 16, 4: 36, 5: 64, 6: 144, 7: 256}
rows = []
for l in open(PROF):
    m = re.match(r'\s+([\d:.]+s?)\s+([\d:.]+s?)\s+(\w+(?: \d+)?)\s+(\w+|-)\s+([\d.]+)s\s+([\d.]+) of (\d+)', l)
    if m: rows.append(m.groups())
def sec(t):
    t = t.rstrip('s'); p = t.split(':')
    return float(p[0]) * 60 + float(p[1]) if len(p) == 2 else float(p[0])
lv = {'speed': 0, 'expand': 0, 'grass': 1, 'trees': 0, 'carrots': 0, 'watering': 0, 'sunflowers': 0, 'polyculture': 0, 'megafarm': 0, 'plant': 0}
def lp(need, comp):
    a = 200 / (400 * 1.5 ** lv['speed']) / (2 if lv['sunflowers'] else 1)
    cells = CELLS[lv['expand']]; D = 2 ** lv['megafarm']
    c = comp if cells >= 3 else 1
    crops = []  # (actions, grow, {item: +yield})
    G = 2 ** (lv['grass'] - 1) * c; T = 2 ** max(lv['trees'] - 1, 0) * c; C = 2 ** max(lv['carrots'] - 1, 0) * c
    if lv['plant'] == 0:
        crops.append((1, 0.5, {'hay': 1}))  # 1x1 grass, harvest only, no plant unlock
    else:
        crops.append((2, 0.5, {'hay': G}))
        crops.append((3, 4.0, {'wood': T}))
        if lv['trees']: crops.append((3, 7.0, {'wood': 5 * T}))
        if lv['carrots']: crops.append((3, 6.0, {'carrot': C, 'wood': -1, 'hay': -1}))
    if lv['watering']:
        crops += [(k + 1, g / 5, y) for k, g, y in crops if k > 1]
    items = ['hay', 'wood', 'carrot']
    # vars: n_c..., T ; minimise T
    nv = len(crops) + 1
    A, b = [], []
    for it in items:
        A.append([-y.get(it, 0) for _, _, y in crops] + [0]); b.append(-need.get(it, 0))
    A.append([k * a for k, _, _ in crops] + [-D]); b.append(0)
    A.append([g for _, g, _ in crops] + [-cells]); b.append(0)
    r = linprog([0] * len(crops) + [1], A_ub=A, b_ub=b, bounds=[(0, None)] * nv)
    return r.x[-1] if r.success else float('nan')
print(f"{'unlock':16}{'last':10}{'actual':>8}{'bound c1':>10}{'bound c1.8':>10}")
tot = [0, 0, 0, 0]
PH = {}
def phase():
    return 'A 1 drone' if lv['megafarm']==0 else ('B 2 drones pre-poly' if lv['polyculture']==0 else ('C 2 drones poly' if lv['megafarm']==1 else 'D Megafarm 2 on'))
for at, took, u, last, slack, dr, dl in rows:
    name, _, n = u.partition(' ')
    name = name.lower(); n = int(n) if n else 1
    if name not in SO and name != 'leaderboard': continue
    need = cost(name, n - 1)
    act = sec(took)
    ok = set(need) <= {'hay', 'wood', 'carrot'}
    if ok:
        b1 = lp(need, 10 if lv['polyculture'] else 1); b5 = lp(need, 10 if lv["polyculture"] else 1.8)
        tot[0] += act; tot[1] += b1; tot[2] += b5
        p=PH.setdefault(phase(),[0,0,0]); p[0]+=act; p[1]+=b5
        print(f"{u:16}{last:10}{act:8.1f}{b1:10.1f}{b5:10.1f}   {need}")
    else:
        tot[3] += act
        p=PH.setdefault(phase(),[0,0,0]); p[2]+=act
        print(f"{u:16}{last:10}{act:8.1f}{'-':>10}{'-':>10}   {need}")
    lv[name] = n
print(f"hay/wood/carrot stretches: actual {tot[0]:.0f}s, bound (no companion pre-poly) {tot[1]:.0f}s, bound (1.8x pre-poly) {tot[2]:.0f}s; other stretches {tot[3]:.0f}s")
for k in sorted(PH): print(f'{k:22} hay/wood/carrot actual {PH[k][0]:5.0f}s bound {PH[k][1]:5.0f}s   other {PH[k][2]:5.0f}s')
