# Mixed-integer version of plan_lp.py: in each stretch every round type (one hay/wood/carrot round per item,
# power, pumpkin, weird substance, gold) either does not run or runs for at least its measured minimum
# time (data/setup.json: a farm() call asked for one item), at its measured rate.
# usage: python3 plan_milp.py data/profile_seeds1-8.txt SEED ITERATIONS  -> work/sched_SEED.pkl
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, json, random, pickle, time
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix
_src = open(HERE + '/plan_lp.py').read()
exec(_src[:_src.index("print('unscaled LP")])
SET = {}
for item, st, seed, dt in json.load(open(HERE + '/data/setup.json')):
    if dt is not None: SET.setdefault((item, st['expand'], st['megafarm'], st['polyculture']), []).append(dt)
SET = {k: sum(v) / len(v) for k, v in SET.items()}
MIX = {}
for mix, st, dt, d in json.load(open(HERE + '/data/mix.json')):
    if dt: MIX[(mix, st['expand'], st['megafarm'], st['polyculture'], st['watering'], st['trees'], st['speed'])] = {k: d.get(k, 0) / dt for k in HWC}
MIXITEMS = {'hw': ('hay', 'wood'), 'hc': ('hay', 'carrot'), 'wc': ('wood', 'carrot'), 'hwc': ('hay', 'wood', 'carrot')}
def mix_rates(lv):
    ex = min(max(lv.get('expand', 0), 2), 5); mf = min(lv.get('megafarm', 0), 2) if ex >= 4 else 0
    po = 1 if lv.get('polyculture') and ex >= 4 else 0
    w = 1 if lv.get('watering') else 0; t = 1 if (lv.get('trees') or po) else 0
    if not lv.get('carrots'): return []
    mul = {'hay': 2 ** (lv.get('grass', 1) - 1), 'wood': 2 ** max(lv.get('trees', 0) - 1, 0), 'carrot': 2 ** max(lv.get('carrots', 0) - 1, 0)}
    out = []
    for powered in ((0, 1) if lv.get('sunflowers') else (0,)):
        sp = lv.get('speed', 0) + 1.71 * powered
        for mix in MIXITEMS:
            r = {}
            for it in HWC:
                g = lambda s_: MIX[(mix, ex, mf, po, w, t, s_)][it]
                v1, v3, v5 = g(1), g(3), g(5)
                lo_, hi_, f = (v1, v3, (sp - 1) / 2) if sp <= 3 else (v3, v5, (sp - 3) / 2)
                v = lo_ * (hi_ / lo_) ** f if lo_ > 0 and hi_ > 0 else lo_ + (hi_ - lo_) * f
                r[it] = v * mul[it] if v > 0 else v
            key = ('mix', mix, ex, mf, po, w, t, powered)
            c = cf(key)
            for it in HWC: r[it] *= c
            if powered: r['power'] = -1.33 * 1.5 ** (lv.get('speed', 0) - 4) * min(2 ** lv.get('megafarm', 0), 4)
            r['_item'] = mix; r['_key'] = key
            out.append(r)
    return out
def tmin(key, lv):
    kind = key[0]
    if kind == 'mix':
        _, mix, ex, mf, po, w, t, powered = key
        return max(tmin(('hwc', it, ex, mf, po, w, t, powered), lv) for it in MIXITEMS[mix])
    if kind == 'hwc':
        _, item, ex, mf, po, w, t, powered = key
        base = SET.get((item, ex, mf, po)) or SET.get((item, ex, mf, 0)) or SET.get((item, ex, 0, 0))
        a_meas = 200 / (400 * 1.5 ** 3)
        a = act_time(lv) if powered else 200 / (400 * 1.5 ** lv.get('speed', 0))
    else:
        item = kind
        ex, mf = key[1], key[2]
        base = SET.get((item, ex, mf, 0)) or SET.get((item, max(ex, 4), mf, 0))
        a_meas = 200 / (400 * 1.5 ** 3 * 2)
        a = act_time(lv)
    return base * a / a_meas
M = 3000.0
TIME_LIMIT = float(_os.environ.get('MILP_TIME', '3'))
USE_MIX = True
RELAX = False
def build_milp(order, detail=False):
    lv = {'grass': 1}
    for u in order[:NFROZEN]: lv[u[0]] = u[1]
    ivs = []
    for u in order[NFROZEN:]:
        tp = hw_rates(lv) + (mix_rates(lv) if USE_MIX else []) + jobs_for(lv)
        if lv.get('sunflowers'):
            tp = [t for t in tp if not (t['_key'][0] in ('hwc', 'mix') and not t['_key'][7])]
        ivs.append((cost(u[0], u[1] - 1), tp, [tmin(t['_key'], lv) for t in tp]))
        lv[u[0]] = u[1]
    nt = sum(len(t) for _, t, _ in ivs)
    nv = 2 * nt            # x (seconds) then z (runs or not)
    nrow = len(ivs) * len(ITEMS) + 2 * nt
    TLIM = TIME_LIMIT
    A = lil_matrix((nrow, nv)); lo = np.full(nrow, -np.inf); hi = np.zeros(nrow)
    starts = []; c = 0
    for _, t, _ in ivs: starts.append(c); c += len(t)
    r = 0
    for k in range(len(ivs)):
        for it in ITEMS:
            for q in range(k + 1):
                for j, v in enumerate(ivs[q][1]):
                    x = v.get(it, 0)
                    if x: A[r, starts[q] + j] = x
            lo[r] = sum(iv[0].get(it, 0) for iv in ivs[:k + 1]); hi[r] = np.inf; r += 1
    for k, (_, t, tm) in enumerate(ivs):
        for j in range(len(t)):
            xi = starts[k] + j; zi = nt + xi
            if tm[j] < 2:
                r += 2; continue           # cheap to start: plain continuous, z unused
            A[r, xi] = 1; A[r, zi] = -tm[j]; lo[r] = 0; hi[r] = np.inf; r += 1      # x >= tmin * z
            A[r, xi] = 1; A[r, zi] = -M; lo[r] = -np.inf; hi[r] = 0; r += 1         # x <= M * z
    cobj = np.concatenate([np.ones(nt), np.zeros(nt)])
    integ = np.concatenate([np.zeros(nt), np.zeros(nt) if RELAX else np.ones(nt)])
    res = milp(cobj, constraints=LinearConstraint(A.tocsr(), lo, hi), integrality=integ,
               bounds=Bounds(np.zeros(nv), np.concatenate([np.full(nt, M), np.ones(nt)])),
               options={'time_limit': TLIM, 'mip_rel_gap': 0.01})
    if res.x is None: return 1e9
    global LAST_STATUS
    LAST_STATUS = res.status
    tt = cobj @ res.x + FROZEN_T
    if detail:
        return tt, [[(res.x[starts[k] + j], ivs[k][1][j]) for j in range(len(ivs[k][1]))] for k in range(len(ivs))]
    return tt
STAGE = {'power': 0, 'hay': 1, 'wood': 1, 'carrot': 1, 'weird_substance': 2, 'pumpkin': 3, 'gold': 4}
def tstage(tpl):
    k = tpl['_key'][0]
    return 1 if k in ('hwc', 'mix') else STAGE[k]
def schedule(order):
    # per stretch: absolute stock targets for each farming stage, worked backwards from the plan so the
    # executor makes what the rest of the plan needs (not the plan's predicted by-products)
    t, det = build_milp(order, detail=True)
    us = order[NFROZEN:]
    C = [cost(u[0], u[1] - 1) for u in us]
    P = [{it: sum(x * tpl.get(it, 0) for x, tpl in row) for it in ITEMS} for row in det]
    out = []
    for k, (u, row) in enumerate(zip(us, det)):
        need = {}
        for it in ITEMS:
            best_, acc = 0.0, 0.0
            for j in range(k, len(us)):
                acc += C[j].get(it, 0) - (P[j][it] if j > k else 0)
                best_ = max(best_, acc)
            need[it] = best_
        acts = {}
        for it in ITEMS:
            st = STAGE[it]
            later = sum(-x * tpl.get(it, 0) for x, tpl in row if tstage(tpl) > st and tpl.get(it, 0) < 0)
            made = sum(x * tpl.get(it, 0) for x, tpl in row if tstage(tpl) == st and tpl.get(it, 0) > 0)
            if made > 0 or need[it] > 0:
                acts[it] = need[it] + later
        out.append((u, acts, [(x, tpl['_key']) for x, tpl in row if x > 0.05]))
    return t, out
if __name__ == '__main__':
    FROZEN_T = sum(ACT[label(u)] for u in PLAN[:NFROZEN])
    t0 = time.time(); base = build_milp(pre)
    print(f'current order to Megafarm 2: run_plan {sum(ACT[label(u)] for u in pre):.0f}s, MILP {base:.0f}s (solve {time.time() - t0:.1f}s)', flush=True)
    random.seed(int(sys.argv[2])); NIT = int(sys.argv[3])
    RELAX = True; rb = build_milp(pre)
    best = list(pre); bt = rb; cur = list(pre); ct = rb; seen = {}
    for it in range(NIT):
        o = list(cur); a = random.randrange(NFROZEN, len(o)); x = o.pop(a); o.insert(random.randrange(NFROZEN, len(o) + 1), x)
        if o[-1] != ('megafarm', 2) or not valid(o): continue
        t = build_milp(o)
        seen[tuple(o)] = t
        temp = 20.0 * (1 - it / NIT) + 0.1
        if t < ct or random.random() < np.exp((ct - t) / temp):
            cur, ct = o, t
    RELAX = False
    cands = sorted(seen, key=seen.get)[:12]
    scored = [(build_milp(list(o)), list(o)) for o in cands]
    bt, best = min(scored)
    print(f'relaxed: current {rb:.0f}s, best visited {min(seen.values()):.0f}s; MILP on the 12 best: ' + ', '.join(str(round(v)) for v, _ in scored), flush=True)
    print(f'best order found: MILP {bt:.0f}s ({bt - base:+.0f}s)')
    for k, u in enumerate(best): print(f'  {k:2} {u[0]} {u[1]}' + ('' if pre[k] == u else '   *'))
    os.makedirs(HERE + '/work', exist_ok=True)
    pickle.dump((best, schedule(best), schedule(pre)), open(HERE + '/work/sched_%s.pkl' % sys.argv[2], 'wb'))
