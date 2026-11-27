"""cactlint: find repeated / unnecessary work in a cactus leaderboard entry.

    python3 cactlint.py ENTRY.py [TRACE.tsv ...] [--top N]

Static checks (source only):
  S1  move runs that a shorter run reaches (cancelling moves, or a long way round the 32-wide torus)
  S2  two actions back to back that undo each other (swap(d) twice, move(d) + move(opposite))
Dynamic checks (cactus-diag traces, every drone's real cells and values):
  D1  walks between two side effects longer than the torus distance between their cells
  D2  walks between two *work* actions longer than the distance (reads on the way cost moves)
  D3  swaps of two equal values (no effect)
  D4  swaps undone: the same two cells swapped back with neither changed in between
  D5  swaps that move both cacti away from every cell their value ends in at the harvest
  D6  till that turns soil back to grass (or tills a cell twice)
  D7  water used on a cell whose cactus is swapped away before it grows
  D8  moves after a drone's last work action (walking for nothing before it ends)
  D9  reads repeated with nothing changed in between (1 tick each, counted per line)
Findings are grouped by source line and reported as actions (200 ticks) saved per run.
"""
import sys, re, collections
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import growth as GB

N = 32
DX = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}  # North East South West
NAME = {'North': 0, 'East': 1, 'South': 2, 'West': 3}
OPP = {0: 2, 2: 0, 1: 3, 3: 1}
WORK = {'plant', 'till', 'swap', 'use', 'harvest', 'spawn'}
READS = {'measure', 'items', 'time', 'drones', 'other'}


def tdist(a, b):
    dx = abs(a[0] - b[0]) % N
    dy = abs(a[1] - b[1]) % N
    return min(dx, N - dx) + min(dy, N - dy)


def step(p, d):
    return ((p[0] + DX[d][0]) % N, (p[1] + DX[d][1]) % N)


args = [a for a in sys.argv[1:] if not a.startswith('--')]
top = 25
if '--top' in sys.argv:
    top = int(sys.argv[sys.argv.index('--top') + 1])
    args.remove(str(top))
entry, traces = args[0], args[1:]
src = open(entry).read().split('\n')

# ------------------------------------------------------------------ static
MOVE_RE = re.compile(r'^(\t*)move\((North|East|South|West)\)\s*$')
SWAP_RE = re.compile(r'^(\t*)swap\((North|East|South|West)\)\s*$')
static = []
i = 0
while i < len(src):
    m = MOVE_RE.match(src[i])
    if not m:
        i += 1
        continue
    ind = m.group(1)
    j = i
    p = (0, 0)
    ds = []
    while j < len(src):
        mm = MOVE_RE.match(src[j])
        if not mm or mm.group(1) != ind:
            break
        d = NAME[mm.group(2)]
        ds.append(d)
        p = step(p, d)
        j += 1
    best = tdist((0, 0), p)
    if len(ds) > best:
        static.append(('S1', i + 1, j, len(ds) - best, f'{len(ds)} moves reach a cell {best} away'))
    i = j
for i in range(len(src) - 1):
    a, b = SWAP_RE.match(src[i]), SWAP_RE.match(src[i + 1])
    if a and b and a.group(1) == b.group(1) and a.group(2) == b.group(2):
        static.append(('S2', i + 1, i + 2, 2, f'swap({a.group(2)}) twice in a row undoes itself'))
static_lines = set()
for _, a, b, _, _ in static:
    static_lines.update(range(a, b + 1))

# ------------------------------------------------------------------ dynamic
def line_of(s):
    return int(s.split(':')[1]) if ':' in s else 0


find = collections.defaultdict(lambda: [0.0, 0, set(), 0.0])  # (check, line) -> [actions saved, hits, runs, critical saved]
CRIT = 0.05
crit_tot = collections.Counter()
ctx = {'crit': lambda t, d: False}
read_rep = collections.defaultdict(int)
totals = collections.Counter()


run_log = []
hol = collections.defaultdict(float)      # (check, line) -> harvest seconds saved (head-of-line)
hol_tot = collections.Counter()
hol_meta = collections.Counter()
gaps = {0: [], 1: []}                      # head finish - k-th finish
allfix = collections.Counter()             # check -> harvest seconds saved if removed on every drone


def add(check, line, saved, run, t=None, d=None):
    if t is not None:
        run_log.append((check, line, saved, t, d))
    f = find[(check, line)]
    if t is not None and ctx['crit'](t, d):
        f[3] += saved
        crit_tot[check] += saved
    f[0] += saved
    f[1] += 1
    f[2].add(run)
    totals[check] += saved


ACT_S = 200 / 6075.0
cur_rows = [[]]


GROW = 0.9676


def settle_run(ev, harvests):
    # finish of each drone per round = max(last action, last plant + growth); the harvest waits for the max
    hb = harvests + [1e9]
    last_act = {}
    last_plant = {}
    for e in ev:
        if e[6] != 200 or e[2] == 'end':
            continue
        r = 0 if e[0] < hb[0] or (e[0] == hb[0] and e[2] == 'harvest') else 1
        key = (e[1], r)
        # round A: a drone is done at its signal (water / the harvest); later moves are pre-travel
        if (r == 1 and e[2] != 'harvest') or (r == 0 and e[2] in ('use', 'harvest')):
            last_act[key] = max(last_act.get(key, 0), e[0] + ACT_S)
        if e[2] == 'plant':
            last_plant[key] = max(last_plant.get(key, 0), e[0] + ACT_S)
    for r in (0, 1):
        gb = GB.grown_by(cur_rows[0], hb[r - 1] if r else 0.0, hb[r])
        gd = {d: (gb.get(d) or last_plant[(d, rr)] + GROW) for (d, rr) in last_plant if rr == r}
        fin = {d: max(a, gd[d]) for (d, rr), a in last_act.items() if rr == r and (d, rr) in last_plant}
        if len(fin) < 2:
            continue
        order = sorted(fin, key=lambda d: -fin[d])
        gaps[r].append([fin[order[0]] - fin[order[k]] for k in (1, 2, 4, 8)])
        for chk in set(f[0] for f in run_log):
            newfin = {}
            for d in fin:
                lp_ = last_plant.get((d, r), 0)
                mine_ = [f for f in run_log if f[0] == chk and f[4] == d and (0 if f[3] < hb[0] else 1) == r]
                b_ = sum(f[2] for f in mine_ if f[3] < lp_) * ACT_S
                a_ = sum(f[2] for f in mine_ if f[3] >= lp_) * ACT_S
                newfin[d] = max(last_act[(d, r)] - a_ - b_, gd[d] - b_) if (d, r) in last_act else 0
            allfix[chk] += max(fin.values()) - max(newfin.values())
        head, second = order[0], fin[order[1]]
        hol_meta[f'head{r}:{head}'] += 1
        lp = last_plant.get((head, r), 0)
        # waste on the head drone in this round
        mine = [f for f in run_log if f[4] == head and (0 if f[3] < hb[0] else 1) == r]
        if not mine:
            continue
        before = sum(f[2] for f in mine if f[3] < lp) * ACT_S
        after = sum(f[2] for f in mine if f[3] >= lp) * ACT_S
        cap_after = max(0.0, fin[head] - max(second, gd[head]))
        got_after = min(after, cap_after)
        got_before = min(before, max(0.0, fin[head] - second - got_after))
        for f in mine:
            w = f[2] * ACT_S
            share = (got_before / before * w) if f[3] < lp and before else (got_after / after * w) if after else 0
            hol[(f[0], f[1])] += share
            hol_tot[f[0]] += share


for run, fn in enumerate(traces):
    run_log.clear()
    ev = []
    cur_rows[0] = GB.plants_grown(fn)
    for l in open(fn):
        p = l.rstrip('\n').split('\t')
        if p[0] != 'E':
            continue
        ev.append((float(p[1]), int(p[2]), p[3], int(p[4]), int(p[5]), int(p[6]), int(p[7]), line_of(p[8]), p[9] if len(p) > 9 else ''))
    ev.sort(key=lambda e: e[0])  # stable: simulator order within a tick
    harvests = [e[0] for e in ev if e[2] == 'harvest' and e[8] and float(e[8]) > 1e6]

    # drone work end per round, for criticality
    hb = harvests + [1e9]
    wend = {}
    for e in ev:
        if e[2] in WORK and e[2] != 'harvest' or e[2] == 'move':
            r = 0 if e[0] < hb[0] else 1
            wend[(e[1], r)] = max(wend.get((e[1], r), 0), e[0])
    def crit(t, d, hb=hb, wend=wend):
        r = 0 if t < hb[0] else 1
        return wend.get((d, r), 0) >= hb[r] - CRIT
    ctx['crit'] = crit
    # --- per-drone walks (D1, D2, D8); a drone id is reused after 'end'
    segs = collections.defaultdict(list)
    life = collections.Counter()
    for e in ev:
        segs[(e[1], life[e[1]])].append(e)
        if e[2] == 'end':
            life[e[1]] += 1
    for key, es in segs.items():
        for anchors, check in ((None, 'D1'), (WORK, 'D2')):
            start = None
            nmov = 0
            first_line = 0
            for e in es:
                t, d, k, x, y, dr, tk, ln, ex = e
                if k == 'move' and tk == 200:
                    if nmov == 0:
                        first_line = ln
                    nmov += 1
                    continue
                if k == 'move':
                    continue
                if anchors is not None and k not in anchors:
                    continue
                if start is not None and nmov:
                    w = nmov - tdist(start, (x, y))
                    if w > 0:
                        add(check, first_line, w, run, t, d)
                start = (x, y)
                nmov = 0
        # D8: moves after the last work action before 'end'
        last_work = max((i for i, e in enumerate(es) if e[2] in WORK), default=-1)
        if es and es[-1][2] == 'end' and last_work >= 0:
            tail = [e for e in es[last_work + 1:] if e[2] == 'move' and e[6] == 200]
            if tail:
                add('D8', tail[0][7], len(tail), run, tail[0][0], tail[0][1])
        # D9: repeated reads (same line, same cell) with nothing else between
        prev = None
        for e in es:
            if e[2] == 'measure':
                sig = (e[7], e[3], e[4], e[5])
                if prev == sig:
                    read_rep[e[7]] += 1
                prev = sig
            elif e[2] not in ('time', 'items'):
                prev = None

    # --- global grid replay (D3-D7)
    val = {}       # cell -> (value, token)
    ground = collections.defaultdict(lambda: 'grass')
    tilled_by = {}
    last_change = collections.defaultdict(lambda: -1)  # cell -> event index of last change
    swaps_at = {}  # frozenset(cells) -> (index, line, (va, vb) before)
    watered = {}   # cell -> (token, line)
    tok = 0
    swap_log = []  # (round, line, cells, tokens moved)
    hist = []
    for idx, e in enumerate(ev):
        t, d, k, x, y, dr, tk, ln, ex = e
        c = (x, y)
        if k == 'plant' and tk == 200:
            tok += 1
            val[c] = (int(ex) if ex.lstrip('-').isdigit() else None, tok)
            last_change[c] = idx
        elif k == 'till' and tk == 200:
            if ground[c] == 'soil':
                add('D6', ln, 1, run, t, d)
            ground[c] = 'soil' if ground[c] == 'grass' else 'grass'
        elif k == 'use' and tk == 200:
            if c in val:
                watered[c] = (val[c][1], ln)
        elif k == 'swap' and tk == 200:
            o = step(c, dr)
            va, vb = val.get(c), val.get(o)
            if va and vb and va[0] == vb[0]:
                add('D3', ln, 1, run, t, d)
            pair = frozenset((c, o))
            prevs = swaps_at.get(pair)
            if prevs and last_change[c] < prevs[0] and last_change[o] < prevs[0] and not (va and vb and va[0] == vb[0]):
                add('D4', ln, 2, run, t, d)
            for cc, vv in ((c, vb), (o, va)):
                if vv is None:
                    val.pop(cc, None)
                else:
                    val[cc] = vv
            for cc in (c, o):
                if cc in watered and watered[cc][0] != (val.get(cc) or (None, None))[1]:
                    add('D7', watered[cc][1], 1, run)
                    del watered[cc]
            last_change[c] = last_change[o] = idx
            swaps_at[pair] = (idx, ln)
            rnd = 0 if not harvests or t < harvests[0] else 1
            swap_log.append((rnd, ln, c, o, va, vb, t, d))
        elif k == 'harvest' and tk == 200 and ex and float(ex) > 1e6:
            # final layout of this round: value -> cells
            fin = collections.defaultdict(list)
            for cc, (v, _) in val.items():
                fin[v].append(cc)
            rnd = 0 if t == harvests[0] else 1
            for r, sl, a, b, va, vb, st_, sd_ in swap_log:
                if r != rnd or not va or not vb:
                    continue
                def gain(v, frm, to):
                    cells = fin.get(v[0], [])
                    if not cells:
                        return 0
                    return min(tdist(frm, q) for q in cells) - min(tdist(to, q) for q in cells)
                ga, gb = gain(va, a, b), gain(vb, b, a)
                if ga < 0 and gb < 0:
                    add('D5', sl, 1, run, st_, sd_)
            swap_log = [s for s in swap_log if s[0] != rnd]
            val.clear()
            watered.clear()
            swaps_at.clear()


    # --- visits (D10-D12): what each stop between moves read, against every change on the farm
    import bisect
    changes = collections.defaultdict(list)
    for idx, e in enumerate(ev):
        if e[6] == 200 and e[2] == 'plant':
            changes[(e[3], e[4])].append(idx)
        elif e[6] == 200 and e[2] == 'swap':
            changes[(e[3], e[4])].append(idx)
            changes[step((e[3], e[4]), e[5])].append(idx)
        elif e[6] == 200 and e[2] == 'harvest' and e[8] and float(e[8]) > 1e6:
            changes['ALL'].append(idx)

    def changed(cell, i, j, me):
        for key in (cell, 'ALL'):
            L = changes.get(key, [])
            k = bisect.bisect_right(L, i)
            while k < len(L) and L[k] < j:
                if key == 'ALL' or not (ev[L[k]][1] == me and ev[L[k]][2] == 'swap' and L[k] in mine_known):
                    return True
                k += 1
        return False

    life = collections.Counter()
    lives = collections.defaultdict(list)
    for idx, e in enumerate(ev):
        lives[(e[1], life[e[1]])].append(idx)
        if e[2] == 'end':
            life[e[1]] += 1
    for (dr_, _), idxs in lives.items():
        stops = []  # [pos, [idx...], first move line into it]
        mv_line = 0
        for idx in idxs:
            e = ev[idx]
            if e[2] == 'move' and e[6] == 200:
                stops.append(None)
                mv_line = e[7]
                continue
            pos = (e[3], e[4])
            if not stops or stops[-1] is None or stops[-1][0] != pos:
                stops.append([pos, [], mv_line])
            stops[-1][1].append(idx)
        stops = [s for s in stops if s is not None]
        known = {}   # cell -> idx it was last read (or exchanged by own swap of two known cells)
        mine_known = set()
        for si, (pos, ids, mline) in enumerate(stops):
            reads = []
            work = []
            for idx in ids:
                e = ev[idx]
                if e[2] == 'measure':
                    reads.append((pos if e[5] == -1 else step(pos, e[5]), idx))
                elif e[2] in WORK and e[6] == 200:
                    work.append(idx)
            if 0 < si < len(stops) - 1 and reads:
                pp, np_ = stops[si - 1][0], stops[si + 1][0]
                save = tdist(pp, pos) + tdist(pos, np_) - tdist(pp, np_)
                t0 = ev[ids[0]][0]
                cells = {c for c, _ in reads}
                if not work and save > 0:
                    rt_known = all(c in known for c in cells)
                    allknown = rt_known and all(not changed(c, known[c], ids[0], dr_) for c in cells)
                    if allknown:
                        add('D10', mline, save, run, t0, dr_)
                    elif rt_known:
                        add('D10u', mline, save, run, t0, dr_)
                    elif all(min(tdist(c, pp), tdist(c, np_)) <= 1 for c in cells):
                        add('D11', mline, save, run, t0, dr_)
                elif len(work) == 1 and ev[work[0]][2] == 'swap' and save > 0:
                    o = step(pos, ev[work[0]][5])
                    if o == pp and all(tdist(c, pp) <= 1 for c in cells):
                        add('D12', mline, save, run, t0, dr_)
            for c, idx in reads:
                known[c] = idx
            for idx in work:
                e = ev[idx]
                if e[2] == 'swap':
                    a, b = (e[3], e[4]), step((e[3], e[4]), e[5])
                    if a in known and b in known and not changed(a, known[a], idx, dr_) and not changed(b, known[b], idx, dr_):
                        known[a] = known[b] = idx
                        mine_known.add(idx)
                    else:
                        known.pop(a, None); known.pop(b, None)
                elif e[2] == 'plant':
                    known.pop((e[3], e[4]), None)

    settle_run(ev, harvests)

runs = max(len(traces), 1)
DESC = {
    'D1': 'walk longer than the distance between two side effects',
    'D2': 'walk longer than the distance between two work actions (reads on the way)',
    'D3': 'swap of two equal values',
    'D4': 'swap undone by a later swap of the same cells',
    'D5': 'swap moves both cacti away from where their values end',
    'D6': 'till on a tilled cell',
    'D7': 'water on a cell whose cactus is swapped away',
    'D8': 'moves after the last work action',
    'D10': 'read-only visit whose every value the drone already knew (unchanged since)',
    'D10u': 'same, but another drone changed a value since: a value cache would be WRONG here',
    'D11': 'read-only visit whose reads could be made from the stop before or after',
    'D12': 'walk onto a cell to swap back toward the cell it came from',
}
print(f'cactlint {entry}: {len(traces)} traced runs\n')
print('Static findings (source only):')
if not static:
    print('  none')
for c, a, b, s, why in static[:top]:
    print(f'  {c} lines {a}-{b}: {why} (saves {s})')
if len(static) > top:
    print(f'  ... {len(static) - top} more')
if traces:
    print('\nDynamic findings, actions saved per run if removed (all drones):')
    for c in sorted(DESC, key=lambda s: (int(s[1:].rstrip('u')), s)):
        print(f'  {c:4} {totals[c] / runs:7.2f} actions  head-of-line {hol_tot[c] / runs * 1000:6.2f} ms  {DESC[c]}')
    print(f'\nTop lines by head-of-line harvest time saved (ms/run, all-drone actions/run, runs hit of {runs}, source):')
    items = sorted(find.items(), key=lambda kv: (-hol[kv[0]], -kv[1][0]))
    for (c, ln), (s, h, rs, cs) in items[:top]:
        fnm = ''
        for j in range(ln - 1, -1, -1):
            m = re.match(r'\s*def (\w+)', src[j])
            if m and len(src[j]) - len(src[j].lstrip('\t')) <= len(src[ln - 1]) - len(src[ln - 1].lstrip('\t')):
                fnm = m.group(1)
                break
        print(f'  {c:4} {ln:6} {fnm:24} {hol[(c, ln)] / runs * 1000:6.2f} {s / runs:6.2f}  {len(rs):3}/{runs}  {src[ln - 1].strip()[:60]}')
    print('\nRemoving each pattern on EVERY drone at once (harvest ms saved per run, both rounds):')
    for c in sorted(DESC, key=lambda s: (int(s[1:].rstrip('u')), s)):
        if allfix[c]:
            print(f'  {c:4} {allfix[c] / runs * 1000:6.1f} ms')
    import statistics as _st
    for r in (0, 1):
        if gaps[r]:
            g = [_st.mean(x[i] for x in gaps[r]) * 1000 for i in range(4)]
            print(f'round {"AB"[r]}: head drone finishes ahead of the 2nd by {g[0]:.0f} ms, 3rd {g[1]:.0f}, 5th {g[2]:.0f}, 9th {g[3]:.0f} (mean)')
    print('\nHead-of-line drones (round:drone id, runs):', ', '.join(f'{k}={v}' for k, v in hol_meta.most_common(12)))
    print('\nD9 repeated reads with nothing changed between (ticks per run), top lines:')
    for ln, v in sorted(read_rep.items(), key=lambda kv: -kv[1])[:8]:
        print(f'  {ln:6} {v / runs:7.1f}  {src[ln - 1].strip()[:60]}')
