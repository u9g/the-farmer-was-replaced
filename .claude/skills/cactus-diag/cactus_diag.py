"""Analyse a cactus leaderboard trace written by tfwr_diag.rs (CACTUS_TRACE).

    python cactus_diag.py TRACE.tsv ENTRY.py [--drone K] [--top N]
    python cactus_diag.py --summary TRACE1.tsv TRACE2.tsv ... ENTRY.py
    python cactus_diag.py --chunks TRACE1.tsv TRACE2.tsv ... ENTRY.py

Trace lines (tab separated):
    E  t  drone  kind  x  y  dir  ticks  file:line  extra     one per side effect
    G  t  -      x  y                                       a cactus finished growing
t is the game time the side effect was applied. extra: plant -> value planted, swap -> values of
the drone's cell and the neighbour before the swap, harvest -> cactus gained.
"""
import sys, re, collections, statistics as st

ACTIONS = {"move", "swap", "plant", "till", "harvest", "use", "spawn"}
# a drone's chunk routine: fa<N> / fb<N> (g3 entries) or w<N> (one function per drone, g5)
ROUTINE = re.compile(r"(f[ab]|w)\d+$")
READS = {"measure", "time", "items", "drones", "other"}


def load(path):
    ev, grown = [], []
    for ln in open(path):
        f = ln.rstrip("\n").split("\t")
        if f[0] == "E":
            ev.append((float(f[1]), int(f[2]), f[3], int(f[4]), int(f[5]), int(f[6]), float(f[7]), f[8], f[9] if len(f) > 9 else ""))
        elif f[0] == "G":
            grown.append((float(f[1]), int(f[3]), int(f[4])))
    return ev, grown


def func_map(entry):
    """line number -> enclosing top-level function name"""
    names = {}
    cur = "<module>"
    for i, ln in enumerate(open(entry), 1):
        m = re.match(r"def (\w+)\(", ln)
        if m:
            cur = m.group(1)
        elif ln and not ln[0].isspace() and ln.strip():
            cur = "<module>"
        names[i] = cur
    return names


def fname(fm, loc):
    try:
        return fm.get(int(loc.split(":")[1]), "?")
    except (ValueError, IndexError):
        return "?"


def group(fn):
    """fa12 -> fa, fb3 -> fb: per-drone generated routines share a role"""
    m = re.match(r"([a-z]+?)(\d+)$", fn)
    return m.group(1) if m else fn


def main():
    args = sys.argv[1:]
    path, entry = args[0], args[1]
    focus = int(args[args.index("--drone") + 1]) if "--drone" in args else None
    top = int(args[args.index("--top") + 1]) if "--top" in args else 6
    ev, grown = load(path)
    fm = func_map(entry)
    harvests = [e for e in ev if e[2] == "harvest" and e[8] not in ("", "0", "0.0")]
    hts = [e[0] for e in harvests]
    end = max(e[0] for e in ev)
    print("harvests at", ["%.3f" % t for t in hts], "(cactus %s)" % [h[8] for h in harvests], " run ends %.3f" % end)
    bounds = [0.0] + hts + [end + 1]
    rounds = list(zip(bounds[:-1], bounds[1:]))[:2]
    by_drone = collections.defaultdict(list)
    for e in ev:
        by_drone[e[1]].append(e)

    # per drone per round: arrival (first till/plant), last plant, last work (last action that is
    # not a poll), and booked time by category
    for ri, (a, b) in enumerate(rounds):
        name = "AB"[ri]
        rows = []
        for d, es in by_drone.items():
            es = [e for e in es if a <= e[0] < b]
            if not es:
                continue
            plants = [e for e in es if e[2] == "plant"]
            acts = [e for e in es if e[2] in ACTIONS and e[2] != "harvest"]
            if not plants:
                continue
            arr = plants[0][0]
            tl = plants[-1][0] + 200 / 6075.0
            work_end = (acts[-1][0] if acts else tl) + 200 / 6075.0
            # book the gap before each event to that event (its kind and function)
            # each side effect is stamped when it starts: the time until the drone's next one
            # (its own ticks plus the compute after it) belongs to it
            book = collections.Counter()
            fbook = collections.Counter()
            prevkey = None
            for e, nx in zip(es, es[1:] + [None]):
                gap = (nx[0] if nx else b) - e[0]
                fn = group(fname(fm, e[7]))
                key = (e[2], e[7])
                if e[2] in READS:
                    cat = "poll" if key == prevkey else "read"
                else:
                    cat = e[2]
                book[cat] += gap
                fbook[fn] += gap
                prevkey = key if e[2] in READS else None
            tail = [e for e in es if e[0] >= tl]
            tb = collections.Counter()
            pk = None
            for e, nx in zip(tail, tail[1:] + [None]):
                if e[0] >= work_end - 1e-9:
                    # the last action itself
                    tb[e[2]] += 200 / 6075.0
                    tb["fn:" + group(fname(fm, e[7]))] += 200 / 6075.0
                    break
                key = (e[2], e[7])
                fn = group(fname(fm, e[7]))
                gap = (nx[0] if nx else work_end) - e[0]
                if e[2] in READS:
                    tb["spin" if key == pk else "read"] += gap
                else:
                    tb[e[2]] += gap
                tb["fn:" + fn] += gap
                pk = key if e[2] in READS else None
            routine = collections.Counter(fname(fm, e[7]) for e in es if ROUTINE.match(fname(fm, e[7])))
            rname = routine.most_common(1)[0][0] if routine else "?"
            rows.append(dict(d=d, r=rname, arr=arr, tl=tl, end=work_end, n=len(plants), book=book, fbook=fbook, tb=tb,
                             swaps=sum(1 for e in es if e[2] == "swap"), moves=sum(1 for e in es if e[2] == "move")))
        rows.sort(key=lambda r: -r["end"])
        H = b if ri < len(hts) else end
        ends = [r["end"] for r in rows]
        tls = [r["tl"] for r in rows]
        print("\n== round %s  (%.3f -> harvest %.3f)" % (name, a, H))
        print("  work end: mean %.3f  max %.3f  (harvest - max %.3f, max - mean %.3f)" % (st.mean(ends), max(ends), H - max(ends), max(ends) - st.mean(ends)))
        print("  last plant: mean %.3f  max %.3f   arrival mean %.3f" % (st.mean(tls), max(tls), st.mean(r["arr"] for r in rows)))
        g = [t for t, x, y in grown if a <= t <= H]
        if g:
            print("  last cactus grown at %.3f -> harvest waited %.3f s on growth after it" % (max(g), H - max(g)))
            print("  harvest bound by %s" % ("GROWTH" if max(g) >= max(ends) - 1e-3 else "FIX WORK (drone %d, %s)" % (rows[0]["d"], rows[0]["r"])))
        print("  latest drones (tail = after last plant):")
        for r in rows[:top]:
            tb = r["tb"]
            fns = sorted(((k[3:], v) for k, v in tb.items() if k.startswith("fn:")), key=lambda x: -x[1])[:4]
            parts = " ".join("%s %.2f" % (k, tb[k]) for k in ("move", "swap", "spin", "read", "use") if tb.get(k, 0) > 0.004)
            print("   drone %-2d %-5s n=%2d arr %.2f last plant %.2f end %.2f | tail %.2f: %s | in %s" % (
                r["d"], r["r"], r["n"], r["arr"], r["tl"], r["end"], r["end"] - r["tl"], parts, ", ".join("%s %.2f" % f for f in fns)))
        tot = collections.Counter()
        for r in rows:
            tot.update(r["book"])
        cap = sum(H - r["arr"] for r in rows)
        print("  all drones, booked time by kind (drone-s): " + " ".join("%s %.1f" % kv for kv in tot.most_common()))
        if focus is not None:
            for r in rows:
                if r["d"] == focus:
                    print("  drone %d by function: %s" % (focus, " ".join("%s %.2f" % kv for kv in r["fbook"].most_common(10))))

    # races: two drones swapping a common cell within 0.1 s
    touch = collections.defaultdict(list)
    for e in ev:
        if e[2] == "swap":
            dx, dy = [(0, 1), (1, 0), (0, -1), (-1, 0)][e[5]]
            for c in ((e[3], e[4]), (e[3] + dx, e[4] + dy)):
                touch[c].append((e[0], e[1]))
    races = []
    for c, ts in touch.items():
        ts.sort()
        for (t1, d1), (t2, d2) in zip(ts, ts[1:]):
            if d1 != d2 and t2 - t1 < 0.1:
                races.append((t2 - t1, c, d1, d2, t1))
    print("\nclose cross-drone swaps on one cell (<0.1 s apart): %d" % len(races))
    for r in sorted(races)[:8]:
        print("   %.3fs apart at %s by drones %d and %d (t=%.2f)" % r)


def summary(paths, entry):
    """over many runs: which routine sets each harvest, and every jf call's duration."""
    fm = func_map(entry)
    crit = [collections.Counter(), collections.Counter()]
    gap = [[], []]
    calls = collections.defaultdict(list)     # (routine, kind, n-th call) -> durations
    for path in paths:
        ev, grown = load(path)
        hts = [e[0] for e in ev if e[2] == "harvest" and e[8] not in ("", "0", "0.0")]
        if len(hts) < 2:
            continue
        bounds = [0.0] + hts[:2]
        by = collections.defaultdict(list)
        for e in ev:
            by[e[1]].append(e)
        for ri in range(2):
            a, b = bounds[ri], bounds[ri + 1]
            ends = []
            for d, es in by.items():
                es = [e for e in es if a <= e[0] < b]
                acts = [e for e in es if e[2] in ACTIONS and e[2] != "harvest"]
                if not any(e[2] == "plant" for e in es) or not acts:
                    continue
                rt = collections.Counter(fname(fm, e[7]) for e in es if ROUTINE.match(fname(fm, e[7])))
                rn = rt.most_common(1)[0][0] if rt else "?"
                ends.append((acts[-1][0], rn))
                cur, t0, n = None, 0.0, collections.Counter()
                for e in es:
                    f = fname(fm, e[7])
                    k = f if f in ("jf", "fmc") else None
                    if k != cur:
                        if cur is not None:
                            n[cur] += 1
                            calls[(rn, cur, n[cur])].append(e[0] - t0)
                        cur, t0 = k, e[0]
            ends.sort()
            crit[ri][ends[-1][1]] += 1
            gap[ri].append(ends[-1][0] - st.mean(x[0] for x in ends))
    for ri in range(2):
        print("round %s: harvest set by %s; slowest drone minus mean work end: mean %.3f s" % (
            "AB"[ri], ", ".join("%s x%d" % kv for kv in crit[ri].most_common(8)), st.mean(gap[ri])))
    js = sorted(((st.mean(v), max(v), k) for k, v in calls.items() if k[1] == "jf" and len(v) > 1), reverse=True)
    print("junction settles (jf), mean / max seconds per call over %d runs:" % len(paths))
    for m, mx, k in js[:12]:
        print("   %-5s call %d: mean %.3f max %.3f" % (k[0], k[2], m, mx))


def chunks(paths, entry):
    """over many runs: when each chunk's drone is finished in each round (fix work done and its
    last cactus grown), mean and sd, and how often it was the last. A harvest waits for the
    latest drone, so a chunk whose mean is above the others, or a wide sd, is time lost."""
    fm = func_map(entry)
    act = 200 / 6075.0
    fin = [collections.defaultdict(list), collections.defaultdict(list)]
    lastp = [collections.defaultdict(list), collections.defaultdict(list)]
    last = [collections.Counter(), collections.Counter()]
    emax = [[], []]
    harv = [[], []]
    for path in paths:
        ev, grown = load(path)
        hts = [e[0] for e in ev if e[2] == "harvest" and e[8] not in ("", "0", "0.0")]
        if len(hts) < 2:
            continue
        bounds = [0.0] + hts[:2]
        by = collections.defaultdict(list)
        for e in ev:
            by[e[1]].append(e)
        for ri in range(2):
            a, b = bounds[ri], bounds[ri + 1]
            rows = []
            for d, es in by.items():
                es = [e for e in es if a <= e[0] < b and e[2] in ACTIONS and e[2] != "harvest"]
                plants = [e for e in es if e[2] == "plant"]
                if not plants:
                    continue
                rt = collections.Counter(fname(fm, e[7]) for e in es if ROUTINE.match(fname(fm, e[7])))
                rn = rt.most_common(1)[0][0] if rt else "?"
                lp = plants[-1][0]
                # round A: the drone signals with a water use once it is done; its pre-travel follows
                sig = [e[0] for e in es if e[2] == "use" and e[0] > lp + 0.5]
                if sig:
                    f = sig[0]
                else:
                    f = max(es[-1][0] + act, lp + 1.0)
                rows.append((f - a, rn))
                fin[ri][rn].append(f - a)
                lastp[ri][rn].append(lp - a)
            rows.sort()
            last[ri][rows[-1][1]] += 1
            emax[ri].append(rows[-1][0])
            harv[ri].append(b - a)

    def num(s):
        m = re.search(r"\d+", s)
        return int(m.group(0)) if m else -1
    for ri in range(2):
        names = sorted(fin[ri], key=lambda s: (num(s), s))
        means = [st.mean(fin[ri][k]) for k in names]
        print("round %s: harvest %.3f s after the round starts; latest drone done at %.3f on average; chunk means: avg %.3f, max %.3f" % (
            "AB"[ri], st.mean(harv[ri]), st.mean(emax[ri]), st.mean(means), max(means)))
        print("   chunk  last plant  done (mean  sd)  latest in runs")
        for k, m in zip(names, means):
            print("   %-6s %8.3f   %8.3f %5.3f   %3d%s" % (k, st.mean(lastp[ri][k]), m, st.pstdev(fin[ri][k]), last[ri][k],
                                                   "   <- above the average by %.2f" % (m - st.mean(means)) if m - st.mean(means) > 0.08 else ""))


if __name__ == "__main__":
    if "--chunks" in sys.argv:
        a = [x for x in sys.argv[1:] if x != "--chunks"]
        chunks(a[:-1], a[-1])
    elif "--summary" in sys.argv:
        a = [x for x in sys.argv[1:] if x != "--summary"]
        summary(a[:-1], a[-1])
    else:
        main()
