"""Head-of-line chain: for each run and round, the drone the harvest waits for, and what its
critical chain (round start -> last plant, plus its tail when the tail outlasts growth) spent
time on, by function and action kind.  python3 hol_chain.py ENTRY.py TRACES..."""
import sys, re, collections, statistics as st
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import growth as GB


entry, traces = sys.argv[1], sys.argv[2:]
src = open(entry).read().split('\n')
func_of = {}
stack = []
for i, l in enumerate(src, 1):
    s = l.lstrip('\t')
    ind = len(l) - len(s)
    if s.strip():
        while stack and ind <= stack[-1][0]:
            stack.pop()
        m = re.match(r'def (\w+)', s)
        if m:
            stack.append((ind, m.group(1)))
    func_of[i] = stack[-1][1] if stack else '<top>'

ACT_S = 200 / 6075.0
GROW = 0.9676
blame = collections.defaultdict(float)
lineblame = collections.defaultdict(float)
bound = collections.Counter()
chain_len = {0: [], 1: []}
heads = collections.Counter()
for fn in traces:
    ev = []
    pc = []
    G = []
    for l in open(fn):
        p = l.rstrip('\n').split('\t')
        if p[0] == 'G':
            G.append((float(p[1]), int(p[3]), int(p[4])))
            continue
        if p[0] != 'E':
            continue
        if p[3] == 'plant' and p[7] == '200':
            pc.append((float(p[1]), int(p[2]), int(p[4]), int(p[5])))
        ev.append((float(p[1]), int(p[2]), p[3], int(p[7]), int(p[8].split(':')[1]) if ':' in p[8] else 0, p[9] if len(p) > 9 else ''))
    hv = [e[0] for e in ev if e[2] == 'harvest' and e[5] and float(e[5]) > 1e6]
    _rows = GB.plants_grown(fn)
    starts = [0.0, hv[0]]
    for r in (0, 1):
        lo, hi = starts[r], hv[r]
        la, lp = {}, {}
        for e in ev:
            if not (lo <= e[0] <= hi and e[3] == 200):
                continue
            if e[0] == hi and not (r == 0 and e[2] == 'harvest'):
                continue  # the round-A harvester's harvest() is its done event, exactly at hi
            if e[2] == 'plant':
                lp[e[1]] = max(lp.get(e[1], 0), e[0] + ACT_S)
            if e[2] != 'end' and (r == 1 and e[2] != 'harvest' or r == 0 and e[2] in ('use', 'harvest')):
                la[e[1]] = max(la.get(e[1], 0), e[0] + ACT_S)
        gb = GB.grown_by(_rows, lo, hi)
        gd = {d: (gb.get(d) or lp[d] + GROW) for d in lp}
        fin = {d: max(la[d], gd[d]) for d in la if d in lp}
        h = max(fin, key=fin.get)
        heads[(r, h)] += 1
        growth = gd[h] >= la[h]
        bound['growth' if growth else 'tail'] += 1
        end = lp[h] if growth else la[h]
        es = [e for e in ev if e[1] == h and lo <= e[0] < end + 1e-9]
        # in round A a drone's chain starts at its spawn; book the time before it as 'launch (parent)'
        first = es[0][0] if es else lo
        if r == 0:
            blame[('<before this drone started>', 'spawn chain')] += first - lo
        for i, e in enumerate(es):
            nt = es[i + 1][0] if i + 1 < len(es) else end
            dt = nt - e[0]
            k = e[2] if e[3] == 200 else ('read/poll' if e[2] in ('measure', 'items', 'time', 'drones', 'other') else e[2])
            if e[3] == 200 and dt > ACT_S + 1e-4:
                blame[(func_of.get(e[4], '?'), k)] += ACT_S
                blame[(func_of.get(e[4], '?'), 'compute/wait')] += dt - ACT_S
            else:
                blame[(func_of.get(e[4], '?'), k)] += dt
            lineblame[e[4]] += dt
        chain_len[r].append(end - lo)

n = len(traces)
print(f'{n} runs. Harvest bound by the head drone\'s growth wait in {bound["growth"]} of {2 * n} rounds, by its tail in {bound["tail"]}.')
for r in (0, 1):
    print(f'round {"AB"[r]}: head chain {st.mean(chain_len[r]):.3f} s to its last plant/tail end; heads: ' +
          ', '.join(f'drone {d}: {c}' for (rr, d), c in heads.most_common() if rr == r))
print('\nHead-of-line chain time by function and kind (s per run):')
agg = collections.defaultdict(float)
for (f, k), v in blame.items():
    f2 = 'w* routes' if re.fullmatch(r'w\d+', f) else f
    agg[(f2, k)] += v
for (f, k), v in sorted(agg.items(), key=lambda x: -x[1])[:25]:
    print(f'  {f:28} {k:14} {v / n:6.3f}')
print('\nTop lines on the head chain (s per run):')
for ln, v in sorted(lineblame.items(), key=lambda x: -x[1])[:25]:
    print(f'  {ln:6} {func_of.get(ln, "?"):22} {v / n:6.3f}  {src[ln - 1].strip()[:70]}')
