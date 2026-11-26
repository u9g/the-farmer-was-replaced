# Generator for the two-harvest cactus leaderboard entry.
#   python build_entry.py out.py [costs.json]
import json, random, sys
from lay import build, nb, UPD, Drone, check_sorted, tdist, mdist, N
from lay2 import settle2
from evalb_lib import dp_walls

ND = 32
ACT = 200.0 / 6075.0        # seconds per action
TICK = 1.0 / 6075.0
DN = ["North", "East", "South", "West"]
OPP = [2, 3, 0, 1]
DV = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}


class Dr(int):
    pass


def lit(o):
    if isinstance(o, Dr):
        return DN[int(o)]
    if isinstance(o, bool):
        return "True" if o else "False"
    if isinstance(o, int):
        return str(o)
    if isinstance(o, (list, tuple)):
        return "[" + ", ".join(lit(x) for x in o) + "]"
    if isinstance(o, dict):
        return "{" + ", ".join(lit(k) + ": " + lit(v) for k, v in o.items()) + "}"
    raise TypeError(o)


def pidx(c):
    return c[0] * N + c[1]


def path_moves(a, b):
    """torus moves from a to b as direction ids (x first)."""
    out = []
    dx = (b[0] - a[0]) % N
    W = Dr
    if dx <= N // 2:
        out += [W(1)] * dx
    else:
        out += [W(3)] * (N - dx)
    dy = (b[1] - a[1]) % N
    if dy <= N // 2:
        out += [W(0)] * dy
    else:
        out += [W(2)] * (N - dy)
    return out


def model_costs(R, order, till, seeds=60, seed=7):
    rng = random.Random(seed)
    tot = [0.0] * len(order)
    for _ in range(seeds):
        vals = {}
        dr = Drone(order[0])
        for i, c in enumerate(order):
            m0, s0 = dr.moves, dr.swaps
            dr.go(c)
            vals[c] = rng.randrange(10)
            settle2(dr, c, R, vals)
            act = (dr.moves - m0) + (dr.swaps - s0) + 1 + (1 if till else 0)
            tot[i] += act * ACT + 30 * TICK
        assert check_sorted(R, vals) == 0
    return [t / seeds for t in tot]


OKCUT = {}


def chunk_costs(R, order, chunks, till, seeds=40, seed=11):
    """per-cell cost with chunks simulated last-to-first (cut effects included)."""
    rng = random.Random(seed)
    tot = [0.0] * len(order)
    for _ in range(seeds):
        vals = {}
        for ci in range(len(chunks) - 1, -1, -1):
            p, q = chunks[ci]
            dr = Drone(order[p])
            for i in range(p, q):
                c = order[i]
                m0, s0 = dr.moves, dr.swaps
                dr.go(c)
                vals[c] = rng.randrange(10)
                settle2(dr, c, R, vals)
                act = (dr.moves - m0) + (dr.swaps - s0) + 1 + (1 if till else 0)
                tot[i] += act * ACT + 30 * TICK
    return [t / seeds for t in tot]


def split(costs, starts_fn, T, order):
    ok = OKCUT.get(id(order))
    chunks = []
    p = 0
    while p < len(order):
        c = starts_fn(len(chunks), order[p])
        q = p
        last_ok = None
        while q < len(order):
            c += costs[q]
            q += 1
            if q == len(order) or ok is None or ok[q]:
                if c <= T or last_ok is None:
                    last_ok = q
                if c > T:
                    break
        chunks.append((p, last_ok))
        p = last_ok
    return chunks


def best_split(costs, starts_fn, order):
    lo, hi = 0.0, 100.0
    for _ in range(50):
        T = (lo + hi) / 2
        if len(split(costs, starts_fn, T, order)) <= ND:
            hi = T
        else:
            lo = T
    ch = split(costs, starts_fn, hi, order)
    ok = OKCUT.get(id(order))
    while len(ch) < ND:
        # split the longest chunk
        k = max(range(len(ch)), key=lambda i: ch[i][1] - ch[i][0])
        p, q = ch[k]
        cand = [m for m in range(p + 1, q) if ok is None or ok[m]]
        m = min(cand, key=lambda m: abs(m - (p + q) / 2))
        ch[k:k + 1] = [(p, m), (m, q)]
    return ch, hi


def spawn_times(nd):
    # binary launch tree at the origin: drone c starts after depth(c) spawns
    t = [0.0] * nd

    def rec(xs, t0):
        while len(xs) > 1:
            half = len(xs) // 2
            rest = xs[half:]
            t0 += ACT
            rec(rest, t0 + ACT)
            xs = xs[:half]
        t[xs[0]] = t0

    rec(list(range(nd)), 0.0)
    return t


def ring(S, R, k):
    S = set(S)
    for _ in range(k):
        S |= {n for c in S for d, n in nb(c, R)}
    return S


def nbr_table(R, cells, owner_of, me):
    """dict p -> [ups, dns], each a flat list [dir, q, foreign, ...] for region neighbours."""
    tab = {}
    for c in cells:
        ups = []
        dns = []
        for d, n in nb(c, R):
            o = owner_of.get(n)
            f = 0 if o == me else 1
            ent = [Dr(d), pidx(n), f, Dr(OPP[d])]
            (ups if d in UPD else dns).extend(ent)
        tab[pidx(c)] = [ups, dns]
    return tab


def emit(out, A, B, extra):
    tpl = open(extra["template"]).read()
    lines = []
    for c in range(ND):
        lines.append("def da%d():\n\treturn %s\n" % (c, lit(A[c])))
        lines.append("def db%d():\n\treturn %s\n" % (c, lit(B[c])))
    lines.append("FA = [%s]\n" % ", ".join("da%d" % i for i in range(ND)))
    lines.append("FB = [%s]\n" % ", ".join("db%d" % i for i in range(ND)))
    src = tpl.replace("#DATA#", "\n\n".join(lines))
    for k, v in extra["consts"].items():
        src = src.replace("#%s#" % k, str(v))
    open(out, "w").write(src)


def safe_cuts(R, order):
    from lay import is_mid
    idx = {c: i for i, c in enumerate(order)}
    n = len(order)
    cross = [0] * (n + 1)
    for c in order:
        i = idx[c]
        for d, m in nb(c, R):
            j = idx[m]
            if i < j:
                for q in range(i + 1, j + 1):
                    cross[q] += 1

    def plain(c):
        return not is_mid(c, R) and all(not is_mid(m, R) for d, m in nb(c, R))

    ok = [False] * (n + 1)
    for q in range(1, n):
        a, b = order[q - 1], order[q]
        ok[q] = cross[q] == 1 and mdist(a, b) == 1 and plain(a) and plain(b)
    print("safe cuts", sum(ok), file=sys.stderr)
    return ok


def spawn_plan(starts, origin):
    """min-sum-of-start-times launch tree over consecutive chunk ranges. returns (offsets in actions, plans).
    plan for a drone: list of steps [moves, child_lo, child_hi] executed before its own travel."""
    from functools import lru_cache
    n = len(starts)

    @lru_cache(None)
    def h(i, j, p):
        if j - i == 1:
            return (tdist(p, starts[i]), None)
        best = None
        cand = {p} | {starts[k] for k in range(i, j)}
        for q in cand:
            dq = tdist(p, q)
            for m in range(i + 1, j):
                a = h(i, m, q)[0]
                b = h(m, j, q)[0]
                v = (j - i) * (dq + 1) + a + b
                if best is None or v < best[0]:
                    best = (v, (q, m))
        return best

    offs = [0.0] * n
    plans = [[] for _ in range(n)]

    def walk(i, j, p, t, owner):
        # drone `owner` is at p at time t and is responsible for chunks i..j-1; it keeps i..m-1
        if j - i == 1:
            offs[i] = t + tdist(p, starts[i])
            return
        q, m = h(i, j, p)[1]
        plans[owner].append([path_moves(p, q), m, j])
        t2 = t + tdist(p, q) + 1
        walk(m, j, q, t2, m)
        walk(i, m, q, t2, owner)

    walk(0, n, origin, 0, 0)
    return offs, plans


def middles(R):
    from lay import is_mid
    return {c for c in R if is_mid(c, R)}


def table_for(cells, R, own, me):
    mids = middles(R)
    near = set(cells)
    near = ring(near, R, 3)
    m = {c for c in near if c in mids}
    T = set(cells) | ring(m, R, 2)
    return nbr_table(R, sorted(T), own, me)


import os


def main():
    out = sys.argv[1]
    kB = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    calib = sys.argv[3] if len(sys.argv) > 3 else None
    wA = [d for d in range(63) if d % 3 == 0]
    wB = dp_walls(kB)
    RA, oA = build(wA)
    RB, oB = build(wB)
    oB = oB[::-1]
    print("A", len(RA), "B", len(RB), "check", 32 * (len(RA) ** 2 + len(RB) ** 2), file=sys.stderr)
    cA = model_costs(RA, oA, True)
    cB = model_costs(RB, oB, False)


    if calib:
        C = json.load(open(calib))
        for i, c in enumerate(oA):
            if str(pidx(c)) in C["A"]:
                cA[i] = C["A"][str(pidx(c))]
        for i, c in enumerate(oB):
            if str(pidx(c)) in C["B"]:
                cB[i] = C["B"][str(pidx(c))]
    origin = (0, 0)
    BOOT = 0.20  # data build + first spawn delay (s)
    offs = [i * 0.0 + 0.3 for i in range(ND)]
    for it in range(6):
        chA, TA = best_split(cA, lambda k, p: BOOT + offs[min(k, ND - 1)], oA)
        starts = [oA[p] for p, q in chA]
        o2, plans = spawn_plan(tuple(starts), origin)
        offs = [x * ACT for x in o2]
    chA, TA = best_split(cA, lambda k, p: BOOT + offs[min(k, ND - 1)], oA)
    for it2 in range(int(os.environ.get("CIT", "0"))):
        cA = chunk_costs(RA, oA, chA, True)
        for it in range(3):
            chA, TA = best_split(cA, lambda k, p: BOOT + offs[min(k, ND - 1)], oA)
            starts = [oA[p] for p, q in chA]
            o2, plans = spawn_plan(tuple(starts), origin)
            offs = [x * ACT for x in o2]
        chA, TA = best_split(cA, lambda k, p: BOOT + offs[min(k, ND - 1)], oA)
    starts = [oA[p] for p, q in chA]
    o2, plans = spawn_plan(tuple(starts), origin)
    print("TA", round(TA, 3), "sum start", round(sum(o2) * ACT, 2), "max start", round(max(o2) * ACT, 2), file=sys.stderr)
    chB, TB = best_split(cB, lambda k, p: 0.0, oB)
    for it2 in range(int(os.environ.get("CIT", "0"))):
        cB = chunk_costs(RB, oB, chB, False)
        chB, TB = best_split(cB, lambda k, p: 0.0, oB)
    if os.environ.get("BOUNDS"):
        Bd_ = json.load(open(os.environ["BOUNDS"]))
        chA = [tuple(x) for x in Bd_["chA"]]
        chB = [tuple(x) for x in Bd_["chB"]]
        starts = [oA[p] for p, q in chA]
        o2, plans = spawn_plan(tuple(starts), origin)
    print("TB", round(TB, 3), file=sys.stderr)
    ownA = {}
    for k, (p, q) in enumerate(chA):
        for i in range(p, q):
            ownA[oA[i]] = k
    ownB = {}
    for k, (p, q) in enumerate(chB):
        for i in range(p, q):
            ownB[oB[i]] = k
    endA = [oA[q - 1] for p, q in chA]

    def route(c, j):
        p2, q2 = chB[j]
        bcells = oB[p2:q2]
        NW = int(os.environ.get("NW", "0"))
        wat = set(bcells[-NW:]) if NW > 0 else set()
        tl = [cc for cc in bcells[::-1] if cc not in RA or cc in wat]
        pos = endA[c]
        steps = []
        L = 0
        for cc in tl:
            mv = path_moves(pos, cc)
            fl = (1 if cc not in RA else 0) + (2 if cc in wat else 0)
            steps.append([mv, fl])
            L += len(mv) + (1 if fl & 1 else 0) + (1 if fl & 2 else 0)
            pos = cc
        mv = path_moves(pos, bcells[0])
        steps.append([mv, 0])
        L += len(mv)
        return steps, L

    from scipy.optimize import linear_sum_assignment
    import numpy as np
    M = np.array([[route(c, j)[1] for j in range(ND)] for c in range(ND)])
    r, a = linear_sum_assignment(M)
    asg = [int(x) for x in a]
    # harvester: drone with the shortest pre-till route (it does it after harvesting)
    hv = min(range(ND), key=lambda c: M[c][asg[c]])
    print("pretill route max", int(M[r, a].max()), "hv", hv, "hv route", int(M[hv][asg[hv]]), file=sys.stderr)
    A = []
    Bd = []
    for c in range(ND):
        p, q = chA[c]
        cells = oA[p:q]
        mv = [path_moves(starts[c] if False else cells[0], cells[0])] + [path_moves(cells[i - 1], cells[i]) for i in range(1, len(cells))]
        tab = table_for(cells, RA, ownA, c)
        A.append([[pidx(x) for x in cells], mv, tab])
        j = asg[c]
        p2, q2 = chB[j]
        bcells = oB[p2:q2]
        steps, L = route(c, j)
        mvb = [[]] + [path_moves(bcells[i - 1], bcells[i]) for i in range(1, len(bcells))]
        tabB = table_for(bcells, RB, ownB, j)
        rvb = [path_moves(bcells[i + 1], bcells[i]) for i in range(len(bcells) - 1)] + [[]]
        Bd.append([[pidx(x) for x in bcells], mvb, tabB, steps, rvb])
    json.dump({"oA": [pidx(c) for c in oA], "oB": [pidx(c) for c in oB], "chA": chA, "chB": chB, "cA": cA, "cB": cB, "asg": asg, "hv": hv, "starts": [BOOT + o * ACT for o in o2]}, open(out + ".json", "w"))
    # launch plans: plans[c] = [[moves, lo, hi]...]; after them the drone travels to its first cell
    LP = []
    for c in range(ND):
        LP.append([[st[0], st[1], st[2]] for st in plans[c]])
    # where is each drone when its plan ends? compute to get travel moves to its first A cell
    pos = {0: origin}
    order_ = [0]
    endpos = {}

    def sim_plan(c, p):
        for st in plans[c]:
            for m in st[0]:
                dx, dy = DV[int(m)]
                p = ((p[0] + dx) % N, (p[1] + dy) % N)
            sim_plan(st[1], p)
        endpos[c] = p

    sim_plan(0, origin)
    for c in range(ND):
        A[c][1][0] = path_moves(endpos[c], oA[chA[c][0]])
    emit(out, A, Bd, {"template": "template.py", "consts": {"NA": len(RA), "NB": len(RB), "HV": hv, "LP": lit(LP), "KD": os.environ.get("KD", "20"), "BW": "%.4f" % max(0.5001, 1.0001 - int(os.environ.get("NW", "0")) * 400 / 6075.0)}})


if __name__ == "__main__":
    main()
