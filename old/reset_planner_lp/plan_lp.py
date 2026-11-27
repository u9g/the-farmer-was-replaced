# Whole-prefix LP (to Megafarm 2) over a given unlock order + local search over orders.
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.dirname(_os.path.dirname(HERE))
import re, sys, random
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
RS = REPO + '/.claude/skills/tfwr-sim/tfwr_sim.rs'
src = open(RS).read()
SO = {}
for m in re.finditer(r'UnlockSO \{ name: "(\w+)".*?parent: "(\w*)", req: \("(\w*)", (\d+)\), cost: &\[(.*?)\], multi_cost: &\[(.*?)\], multi_factor: ([\d.]+), max_level: (\d+)', src):
    pairs = lambda s: [(a, float(b)) for a, b in re.findall(r'\("(\w+)", ([\d.]+)\)', s)]
    SO[m.group(1)] = dict(parent=m.group(2), req=(m.group(3), int(m.group(4))), base=pairs(m.group(5)),
                          mc=[pairs(x) for x in re.findall(r'&\[(.*?)\]', m.group(6))], f=float(m.group(7)))
def cost(name, num):
    s = SO[name]
    if num == 0: return dict(s['base'])
    c = len(s['mc'])
    if c < num: return {k: v * s['f'] ** (num - c) for k, v in s['mc'][c - 1]}
    return dict(s['mc'][num - 1])
CELLS = {0: 1, 1: 3, 2: 9, 3: 16, 4: 36, 5: 64, 6: 144, 7: 256}
# measured run (profile, mean of 8 seeds): unlock -> (took s)
ACT = {}
for l in open(sys.argv[1]):
    m = re.match(r'\s+[\d:.]+s?\s+([\d:.]+s?)\s+(\w+(?: \d+)?)\s+(\w+|-)\s', l)
    if m:
        t = m.group(1).rstrip('s').split(':')
        ACT[m.group(2)] = float(t[0]) * 60 + float(t[1]) if len(t) == 2 else float(t[0])
HWC = ('hay', 'wood', 'carrot')
def key(u): return u[0].capitalize() + ' ' + str(u[1]) if SO[u[0]]['mc'] or u[1] > 1 else u[0].capitalize()
def label(u):
    k = u[0].capitalize() + ' ' + str(u[1])
    return k if k in ACT else u[0].capitalize()
def act_time(lv):
    return 200 / (400 * 1.5 ** lv.get('speed', 0)) / (2 if lv.get('sunflowers', 0) else 1)
EFF0 = {'A': 0.755, 'B': 0.59, 'C': 0.29, 'D': 0.31}
EFF = dict(EFF0)
def cls(lv):
    if lv.get('megafarm', 0) == 0: return 'A'
    if lv.get('polyculture', 0) == 0: return 'B'
    return 'C' if lv['megafarm'] == 1 else 'D'
def crops(lv):
    c = 10 if lv.get('polyculture') else 1.8
    if CELLS[lv.get('expand', 0)] < 3: c = 1
    G = 2 ** (lv.get('grass', 1) - 1) * c; T = 2 ** max(lv.get('trees', 0) - 1, 0) * c; C = 2 ** max(lv.get('carrots', 0) - 1, 0) * c
    if lv.get('plant', 0) == 0: out = [(1, 0.5, (1, 0, 0))]
    else:
        out = [(2, 0.5, (G, 0, 0)), (3, 4.0, (0, T, 0))]
        if lv.get('trees'): out.append((3, 7.0, (0, 5 * T, 0)))
        if lv.get('carrots'): out.append((3, 6.0, (-1, -1, C)))
    if lv.get('watering'): out += [(k + 1, g / 5, y) for k, g, y in out if k > 1]
    return out
import json
RATES = {}
for item, st, dt, d in json.load(open(HERE + '/data/rates.json')):
    if dt is None: continue
    key = (item, st['expand'], st['megafarm'], st.get('pumpkins', 0))
    RATES[key] = {'hay': d.get('hay', 0) / dt, 'wood': d.get('wood', 0) / dt, 'carrot': d.get('carrot', 0) / dt,
                  'pumpkin': d.get('pumpkin', 0) / dt, 'weird_substance': d.get('weird', 0) / dt, 'gold': d.get('gold', 0) / dt, 'power': d.get('power', 0) / dt}
A_MEAS = 200 / (400 * 1.5 ** 4 * 2)
ITEMS = ('hay', 'wood', 'carrot', 'pumpkin', 'weird_substance', 'gold', 'power')
def jobs_for(lv):
    out = []
    ex = lv.get('expand', 0)
    if ex < 4: return out
    exk = min(ex, 6); mf = min(lv.get('megafarm', 0), 2)
    sc = A_MEAS / act_time(lv) * JOBSCALE
    if lv.get('pumpkins', 0) >= 1:
        p = lv['pumpkins']; pk = min(p, 3)
        r = dict(RATES[('pumpkin', exk, mf, pk)])
        r = {k: v * 2 ** (p - pk) if k in ('pumpkin', 'carrot') else v for k, v in r.items()}
        key = ('pumpkin', exk, mf); d = {k: v * sc * cf(key) for k, v in r.items()}; d['_item'] = 'pumpkin'; d['_key'] = key; out.append(d)
    if lv.get('fertilizer', 0) >= 1:
        key = ('weird_substance', exk, mf); d = {k: v * sc * cf(key) for k, v in RATES[('weird_substance', exk, mf, 0)].items()}; d['_item'] = 'weird_substance'; d['_key'] = key; out.append(d)
    if lv.get('mazes', 0) >= 1:
        key = ('gold', exk, mf); d = {k: v * sc * cf(key) for k, v in RATES[('gold', exk, mf, 0)].items()}; d['_item'] = 'gold'; d['_key'] = key; out.append(d)
    return out
JOBSCALE = 1.0
import os
CORR = json.load(open(HERE + '/work/corr.json')) if os.path.exists(HERE + '/work/corr.json') else {}
def cf(key): return CORR.get(repr(key), 1.0)
HW = {}
for item, st, dt, d in json.load(open(HERE + '/data/hwc.json')):
    if dt is None: continue
    HW[(item, st['expand'], st['megafarm'], st['polyculture'], st['watering'], st['trees'], st['speed'])] = {k: d.get(k, 0) / dt for k in ('hay', 'wood', 'carrot')}
def hw_rates(lv):
    ex = min(max(lv.get('expand', 0), 2), 5); mf = min(lv.get('megafarm', 0), 2) if ex >= 4 else 0
    po = 1 if lv.get('polyculture') and ex >= 4 else 0
    w = 1 if lv.get('watering') else 0; t = 1 if lv.get('trees') else 0
    if po: t = 1
    return hw_one(lv, ex, mf, po, w, t, lv.get('speed', 0), 0) + (hw_one(lv, ex, mf, po, w, t, lv.get('speed', 0) + 1.71, 1) + pw_round(lv) if lv.get('sunflowers') else [])
PW = {}
for j, dt, d in json.load(open(HERE + '/data/pw.json')):
    if dt: PW[tuple(j)] = {'hay': d.get('hay', 0) / dt, 'carrot': d.get('carrot', 0) / dt, 'power': d.get('power', 0) / dt}
def pw_round(lv):
    ex = min(max(lv.get('expand', 0), 3), 5); mf = min(lv.get('megafarm', 0), 2); sp = lv.get('speed', 0)
    a, b = PW[(ex, mf, 3)], PW[(ex, mf, 5)]
    f = (sp - 3) / 2
    d = {k: (a[k] * (b[k] / a[k]) ** f if a[k] * b[k] > 0 else a[k] + (b[k] - a[k]) * f) for k in a}
    key = ('power', ex, mf)
    d = {k: v * cf(key) for k, v in d.items()}
    d['_item'] = 'power'; d['_key'] = key
    return [d]
def hw_one(lv, ex, mf, po, w, t, sp, powered):
    mul = {'hay': 2 ** (lv.get('grass', 1) - 1), 'wood': 2 ** max(lv.get('trees', 0) - 1, 0), 'carrot': 2 ** max(lv.get('carrots', 0) - 1, 0)}
    out = []
    for item in ('hay', 'wood', 'carrot'):
        if item == 'carrot' and not lv.get('carrots'): continue
        r = {}
        for it in ('hay', 'wood', 'carrot'):
            g = lambda s_: max(HW[(item, ex, mf, po, w, t, s_)][it], 0) if HW[(item, ex, mf, po, w, t, s_)][it] > 0 else HW[(item, ex, mf, po, w, t, s_)][it]
            v1, v3, v5 = g(1), g(3), g(5)
            if sp <= 3: lo, hi, f = v1, v3, (sp - 1) / 2
            else: lo, hi, f = v3, v5, (sp - 3) / 2
            if lo > 0 and hi > 0: v = lo * (hi / lo) ** f
            else: v = lo + (hi - lo) * f
            r[it] = v * mul[it] * HWSCALE if v > 0 else v * HWSCALE
        if powered: r['power'] = -1.33 * 1.5 ** (lv.get('speed', 0) - 4) * min(2 ** lv.get('megafarm', 0), 4)
        key = ('hwc', item, ex, mf, po, w, t, powered)
        c = cf(key)
        for it in list(r): r[it] *= c
        r['_item'] = item; r['_key'] = key
        out.append(r)
    return out
HWSCALE = 1.0
def build(order, record=False, detail=False):
    lv = {'grass': 1}
    for u in order[:NFROZEN]: lv[u[0]] = u[1]
    ivs = []
    for u in order[NFROZEN:]:
        ivs.append((cost(u[0], u[1] - 1), hw_rates(lv) + jobs_for(lv)))
        lv[u[0]] = u[1]
    nv = sum(len(j) for _, j in ivs)
    A = lil_matrix((len(ivs) * len(ITEMS), nv)); b = []; r = 0
    starts = []; c = 0
    for need, jb in ivs: starts.append(c); c += len(jb)
    for k in range(len(ivs)):
        for it in ITEMS:
            for q in range(k + 1):
                for j, v in enumerate(ivs[q][1]):
                    x = v.get(it, 0) if it in v else 0
                    if x: A[r, starts[q] + j] = -x
            b.append(-sum(iv[0].get(it, 0) for iv in ivs[:k + 1])); r += 1
    res = linprog(np.ones(nv), A_ub=A.tocsr(), b_ub=b, bounds=[(0, None)] * nv, method='highs')
    if res.status != 0: return 1e9
    t = res.fun + FROZEN_T
    if detail: return t, [[(res.x[starts[k] + j], ivs[k][1][j]) for j in range(len(ivs[k][1]))] for k in range(len(ivs))]
    return t
NFROZEN = 6
FROZEN_T = 0
def valid(order):
    lv = {'grass': 1}
    for u in order:
        s = SO[u[0]]
        if lv.get(u[0], 0) != u[1] - 1: return False
        if s['parent'] and lv.get(s['parent'], 0) < 1 and s['parent'] not in ('loops', 'speed', 'plant', 'simulation', 'timing', 'mazes', 'fertilizer', 'watering', 'carrots', 'trees', 'pumpkins', 'cactus') : pass
        if s['parent'] in SO and s['parent'] not in ('loops',) and lv.get(s['parent'], 0) < 1 and s['parent'] in ('watering','carrots','trees','pumpkins','fertilizer','mazes','plant'): return False
        if s['req'][0] and lv.get(s['req'][0], 0) < s['req'][1]: return False
        lv[u[0]] = u[1]
    return True
src2 = open(REPO + '/run_reset.py').read()
i = src2.index('PLAN = [\n'); j = src2.index(']\n', i)
PLAN = [(a.lower(), int(b)) for a, b in re.findall(r'\(Unlocks\.(\w+), (\d+)\)', src2[i:j])]
cut = PLAN.index(('megafarm', 2)) + 1
pre = PLAN[:cut]
FROZEN_T = sum(ACT[label(u)] for u in PLAN[:NFROZEN])
print('unscaled LP, current order:', round(build(pre)))
actual0 = sum(ACT[label(u)] for u in pre)
lo, hi = 0.2, 3.0
for _ in range(0):
    mid = (lo + hi) / 2
    HWSCALE = mid; JOBSCALE = mid
    if build(pre) > actual0: lo = mid
    else: hi = mid
base = build(pre)
base = build(pre)
actual = sum(ACT[label(u)] for u in pre)
print(f"current order to Megafarm 2: actual {actual:.0f}s, calibrated LP {base:.0f}s")
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
best = list(pre); bt = base; cur = list(pre); ct = base
T0 = 20.0
NIT = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
for it in range(NIT):
    o = list(cur); a = random.randrange(NFROZEN, len(o)); x = o.pop(a); o.insert(random.randrange(NFROZEN, len(o) + 1), x)
    if o[-1] != ('megafarm', 2) or not valid(o): continue
    t = build(o)
    temp = T0 * (1 - it / NIT) + 0.1
    if t < ct or random.random() < np.exp((ct - t) / temp):
        cur, ct = o, t
        if t < bt: best, bt = list(o), t
print(f"best order found: LP {bt:.0f}s ({bt - base:+.0f}s)")
for k, u in enumerate(best):
    print(f"  {k:2} {u[0]} {u[1]}" + ("" if k < len(pre) and pre[k] == u else "   *"))

def schedule(order):
    t, det = build(order, detail=True)
    # per interval: (unlock, [(item, amount to make)]) where amount = seconds x the template's own-item rate
    out = []
    for u, row in zip(order[NFROZEN:], det):
        acts = {}
        for x, tpl in row:
            if x > 0.05:
                it = tpl['_item']; acts[it] = acts.get(it, 0) + x * tpl.get(it, 0)
        out.append((u, acts, [(x, tpl['_key']) for x, tpl in row if x > 0.05]))
    return t, out
import pickle
os.makedirs(HERE + '/work', exist_ok=True)
pickle.dump((best, schedule(best), schedule(pre)), open(HERE + '/work/sched_%s.pkl' % sys.argv[2], 'wb'))
