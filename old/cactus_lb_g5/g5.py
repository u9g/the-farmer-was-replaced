# g5: the g3 generator (../cactus_lb_g2) with a different planner and code layout.
#   - plan5(): exactly 32 chunks chosen to minimise the sum of exp(finish / SOFT) rather than only
#     the latest finish, with the wait at a facing cut (two walks ending at one cut) counted;
#     costs fitted to the simulator (C_FM=350, PTM ticks of extra pre-travel slack).
#   - one function per drone (launch steps, round A, pre-travel, round B) instead of fa/fb/pt
#     functions and FA/FB/PT/LP tables, which cost the main drone ~365 ticks before its first spawn.
#   - 3-wide bands walked column by column in one direction; in round B a column is planted
#     from two cells (plant the entry cell, step to the middle, plant, swap that cactus into the
#     far cell, plant again): 6 actions per column instead of 7 (PUSH=0 turns it off).
#   - the growth wait is counted from when the last plant took effect, 200 ticks before tl (GSUB).
#   python g5.py out.py      (environment variables as for g3.py; see README.md)
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cactus_lb_g2"))
os.environ.setdefault("C_FM", "350")  # isolated mixed cell fix, measured (g2 reads it on import; g3 used 230)
import lay as laymod

E = os.environ.get
COLS = E("COLS", "1") == "1"
GSUB = float(E("GSUB", "0.039"))  # tl is read 200 ticks after the last plant took effect


def zig_order5(ds, inc):
    """3-wide strips: every column walked the same way (top to bottom going SE, bottom to top
    going NW), so a column is three consecutive cells and its middle is next to both others."""
    cells = laymod.strip_cells(ds)
    if len(ds) <= 2:
        cells.sort(key=lambda c: (c[0] - c[1]))
        return cells if inc else cells[::-1]
    cols = {}
    for c in cells:
        cols.setdefault(c[0], []).append(c)
    xs = sorted(cols)
    if not inc:
        xs = xs[::-1]
    out = []
    for x in xs:
        out += sorted(cols[x], key=lambda c: -c[1] if inc else c[1])
    return out


if COLS:
    laymod.zig_order = zig_order5

import g3
from g2 import Layout, ND, T_ACT, DN, render
from g3 import walk_of, water_n, plan, xstarts, facing
from lay import tdist, N
from build_entry import path_moves, lit, DV
from g5_cols import chunk_eval, phase_ops, cell_items5, corr, RUNTIME


def plan5(lay):
    """g3's plan() with a balanced objective: exactly ND chunks minimising the sum of
    exp(finish / SOFT) instead of only the latest finish, so no chunk sits at the limit while
    others have slack, and small changes in the costs move the cuts only a little."""
    import math
    from g2 import DEPTH
    TAU = float(E("SOFT", "600"))
    o, n = lay.o, lay.n
    LMAX = int(E("LMAX", "40"))
    LMIN = int(E("LMIN", "6"))
    dirs = (0,) if E('DIRS', '0') != '1' else (0, 1)
    cuts = [q for q in range(n + 1) if lay.cut_ok[q]]
    clean = g3.clean_cuts(lay)
    lay.clean = clean
    memo = {}

    def start_of(p, q, d):
        return o[p] if d == 0 else o[q - 1]

    def cA(p, q, d):
        key = (p, q, d)
        if key not in memo:
            memo[key] = chunk_eval(lay, p, q, d, True, start_of(p, q, d))
        return memo[key]

    def est_off(c):
        return T_ACT * (tdist((0, 0), c) + DEPTH)

    nxt = {p: [q for q in cuts if LMIN <= q - p <= LMAX] for p in cuts}

    WAITX = 300.0 + T_ACT

    def solve(offf, ref):
        # state (cut, direction of the chunk ending there) -> (cost, back pointer, forward end
        # and tail of that chunk). At an F|R cut both walks end at the cut: the drone whose
        # forward pass ends first waits there for the other's last plant before its tail.
        f = [{(0, 1): (0.0, None, 0.0, 0.0)}]
        for k in range(1, ND + 1):
            g = {}
            left = ND - k
            for (p, dp_), (v, _, pfe, ptl) in f[k - 1].items():
                for q in nxt[p]:
                    rem = n - q
                    if rem > left * LMAX or rem < left * LMIN:
                        continue
                    for d in dirs:
                        if p > 0 and dp_ != d and not clean[p]:
                            continue
                        r = cA(p, q, d)
                        fe = offf(start_of(p, q, d)) + r[2]
                        tl = r[0] - r[2]
                        c = v
                        if p > 0 and dp_ == 0 and d == 1:
                            if pfe <= fe:
                                c += math.exp((fe + WAITX + ptl - ref) / TAU) - math.exp((pfe + ptl - ref) / TAU)
                            else:
                                fe = pfe + WAITX
                        c += math.exp((fe + tl - ref) / TAU)
                        key = (q, d)
                        if key not in g or g[key][0] > c:
                            g[key] = (c, (p, dp_), fe, tl)
            f.append(g)
        ends = [(f[ND][(n, d)][0], d) for d in (0, 1) if (n, d) in f[ND]]
        d = min(ends)[1]
        ch = []
        q = n
        for k in range(ND, 0, -1):
            p, dp_ = f[k][(q, d)][1]
            ch.append((p, q, d))
            q, d = p, dp_
        return ch[::-1]

    def finishes(ch, act):
        fe = [act[start_of(*c)] + cA(*c)[2] for c in ch]
        tl = [cA(*c)[0] - cA(*c)[2] for c in ch]
        for k in range(ND - 1):
            if ch[k][2] == 0 and ch[k + 1][2] == 1:
                if fe[k] <= fe[k + 1]:
                    fe[k] = fe[k + 1] + WAITX
                else:
                    fe[k + 1] = fe[k] + WAITX
        return [fe[k] + tl[k] for k in range(ND)]

    offf = est_off
    ref = 26000.0
    for it in range(int(E("AITER", "4"))):
        ch = solve(offf, ref)
        starts = [start_of(*c) for c in ch]
        from spawnmm import spawn_plan_mm
        offs, plans, _mk = spawn_plan_mm(tuple(starts), tuple(cA(*c)[0] for c in ch), (0, 0))
        act = {starts[k]: offs[k] * T_ACT + T_ACT for k in range(ND)}
        fin = finishes(ch, act)
        ref = max(fin)
        print("A iter", it, "max %.0f (%.3fs) mean %.0f" % (max(fin), max(fin) / 6075, sum(fin) / ND), file=sys.stderr)
        offf = (lambda a: (lambda c: a.get(c, est_off(c))))(dict(act))
    lay.chA, lay.offs, lay.plans = ch, offs, plans
    lay.TA = max(fin)
    lay.arrA = [offs[k] * T_ACT + T_ACT for k in range(ND)]
    lay.KA = [cA(*c)[1] for c in ch]
    lay.GA = [cA(*c)[4] / 6075.0 for c in ch]
    lay.endA = []
    for k, (p, q, d) in enumerate(ch):
        ops, cur = phase_ops(lay, p, q, d, True, lay.KA[k], start_of(p, q, d))
        lay.endA.append(cur)
    finA = fin
    lay.finA = fin
    # the harvest comes after the latest drone of the run, which is later than any one drone's
    # mean finish: PTM ticks of extra slack for the pre-travel
    TAh = max(finA) + float(E("PTM", "300"))
    PTF = float(E("PTF", "1.0"))
    lay.slack = [0.0 if k == 0 else max(0.0, TAh - finA[k]) * PTF for k in range(ND)]
    memoB = {}

    def cB(k, p, q, d):
        key = (k, p, q, d)
        if key not in memoB:
            st = o[p] if d == 0 else o[q - 1]
            r = chunk_eval(lay, p, q, d, False, st)
            tr = T_ACT * tdist(lay.endA[k], st)
            eff = tr if k == 0 else max(0.0, tr - lay.slack[k])
            memoB[key] = (r[0] + eff, r[1], r[2] + eff, r[3], r[4])
        return memoB[key]

    W = int(E("BWIN", "24"))
    refB = float(E("REFB", "18500"))
    cand = [[0]] + [[c for c in cuts if abs(c - ch[k][0]) <= W] for k in range(1, ND)] + [[n]]
    f = {(0, 1): (0.0, None, 0.0, 0.0)}
    hist = [f]
    for k in range(ND):
        g = {}
        for b in cand[k + 1]:
            for d in dirs:
                bv = None
                for (a, da), (v, _, pfe, ptl) in f.items():
                    if b <= a or b - a > LMAX:
                        continue
                    if a > 0:
                        if da != d and not clean[a]:
                            continue
                        if da == 1 and d == 0:
                            continue
                    r = cB(k, a, b, d)
                    fe = r[2]
                    tl = r[0] - r[2]
                    c = v
                    if a > 0 and da == 0 and d == 1:
                        if pfe <= fe:
                            c += math.exp((fe + WAITX + ptl - refB) / TAU) - math.exp((pfe + ptl - refB) / TAU)
                        else:
                            fe = pfe + WAITX
                    c += math.exp((fe + tl - refB) / TAU)
                    if bv is None or c < bv[0]:
                        bv = (c, (a, da), fe, tl)
                if bv is not None:
                    g[(b, d)] = bv
        hist.append(g)
        f = g
    _, dl = min((f[(n, d)][0], d) for d in (0, 1) if (n, d) in f)
    key = (n, dl)
    chB = []
    for k in range(ND, 0, -1):
        prev = hist[k][key][1]
        chB.append((prev[0], key[0], key[1]))
        key = prev
    lay.chB = chB[::-1]
    lay.KB = [cB(k, *c)[1] for k, c in enumerate(lay.chB)]
    lay.GB = [cB(k, *c)[4] / 6075.0 for k, c in enumerate(lay.chB)]
    lay.TB = max(cB(k, *c)[0] for k, c in enumerate(lay.chB))
    lay.arrB = []
    for k, (p, q, d) in enumerate(lay.chB):
        lay.arrB.append(T_ACT * tdist(lay.endA[k], start_of(p, q, d)))
    print("plan TA %.0f TB %.0f est total %.3fs" % (lay.TA, lay.TB, (lay.TA + lay.TB + 400) / 6075), file=sys.stderr)


g3.chunk_eval = chunk_eval
g3.phase_ops = phase_ops


def body(ops):
    """the lines of a rendered op list, without the def line and the return."""
    out = []
    run = []
    for op in ops:
        if op[0] in ("push", "cm"):
            out += render("x", run)[1:-2]
            run = []
            if op[0] == "push":
                out.append("\tswap(%s)" % DN[op[1]])
            else:
                out.append("\t%s(%d, %d)" % ("cmd" if op[1] else "cmu", 1 if op[2] else 0, 1 if op[3] else 0))
        else:
            run.append(op)
    out += render("x", run)[1:-2]
    return out


def main():
    widths = [int(x) for x in E("WIDTHS", "2,2,2,2,2,2,2,2,3,3,2,2,2,2,2,3,2,2,2,3").split(",")]
    lay = Layout(widths)
    if float(E("SOFT", "600")) > 0:
        plan5(lay)
    else:
        plan(lay)
    if E("DIAG"): g3.diag(lay)
    if E("MDUMP"): g3.model_dump(lay)
    if E("DECOMP"): g3.decompose(lay)
    o = lay.o
    if E("MODEL"):
        import json
        rows = []
        for k in range(ND):
            row = {}
            for rnd, ch, till in (("A", lay.chA, True), ("B", lay.chB, False)):
                p, q, d = ch[k]
                st = o[p] if d == 0 else o[q - 1]
                r = chunk_eval(lay, p, q, d, till, st)
                c = corr(till, p, q)
                w = walk_of(p, q, d)
                ci = cell_items5(lay, w, p, q, d)
                kinds = {}
                for t in range(len(w)):
                    for it in ci[t][1]:
                        kinds[it[0]] = kinds.get(it[0], 0) + 1
                    if t >= len(w) - r[1] and ci[t][0]:
                        kinds["dcas"] = kinds.get("dcas", 0) + len(ci[t][0])
                    elif ci[t][0]:
                        kinds["icas"] = kinds.get("icas", 0) + len(ci[t][0])
                if till:
                    arr = lay.arrA[k]
                else:
                    tr = T_ACT * tdist(lay.endA[k], st)
                    arr = tr if k == 0 else max(0.0, tr - lay.slack[k])
                row[rnd] = [p, q, d]
                row["fin" + rnd] = lay.finA[k] if till else arr + r[0]
                row["d" + rnd] = {"arr": arr, "f": r[2] - c, "b": r[3], "gw": r[4], "K": r[1], "corr": c, "kinds": kinds,
                                  "jx": sum(lay.net[it[1]][2] for t in range(len(w)) for it in ci[t][1] if it[0] == "jx")}
            rows.append(row)
        json.dump({"n": lay.n, "chunks": rows, "TA": lay.TA, "TB": lay.TB}, open(E("MODEL"), "w"))
    pos_end = {}

    def sim_plan(c, pp):
        for st in lay.plans[c]:
            for m in st[0]:
                dx, dy = DV[int(m)]
                pp = ((pp[0] + dx) % N, (pp[1] + dy) % N)
            sim_plan(st[1], pp)
        pos_end[c] = pp

    sim_plan(0, (0, 0))
    xa = xstarts(lay, lay.chA, lay.arrA, True)
    xb = xstarts(lay, lay.chB, lay.arrB, False)
    hA, nA, wA = facing(lay, lay.chA, lay.arrA, True)
    hB, nB, wB = facing(lay, lay.chB, lay.arrB, False)
    L = []
    for k in range(ND - 1, -1, -1):
        p, q, d = lay.chA[k]
        opsA, curA = phase_ops(lay, p, q, d, True, lay.KA[k], pos_end[k], xa[k], hA[k], nA[k], wA[k])
        p, q, d = lay.chB[k]
        stB = o[p] if d == 0 else o[q - 1]
        pt = [("move", int(m)) for m in path_moves(curA, stB)]
        if k == 0:
            opsB, curB = phase_ops(lay, p, q, d, False, lay.KB[k], curA, xb[k], hB[k], nB[k], wB[k])
            pt = []
        else:
            opsB, curB = phase_ops(lay, p, q, d, False, lay.KB[k], stB, xb[k], hB[k], nB[k], wB[k])
        L.append("def w%d():" % k)
        for st in lay.plans[k]:
            for m in st[0]:
                L.append("\tmove(%s)" % lit(m))
            L.append("\tspawn_drone(w%d)" % st[1])
        L += body(opsA)
        L.append("\twait_until(tl + %.4f)" % (lay.GA[k] - GSUB))
        if k == 0:
            L.append("\twhile (get_time() // WDT) - num_items(Items.Water) < NSIG:")
            L.append("\t\tpass")
            L.append("\tharvest()")
        else:
            L.append("\tuse_item(Items.Water)")
            L += body(pt)
            L.append("\twhile num_items(Items.Cactus) <= 0:")
            L.append("\t\tpass")
        L += body(opsB)
        L.append("\twait_until(tl + %.4f)" % (lay.GB[k] - GSUB))
        if k == 0:
            L.append("\twhile num_drones() > 1:")
            L.append("\t\tpass")
            L.append("\tharvest()")
        L.append("")
    tpl = open(os.path.join(HERE, E("TPL", "t5.py"))).read()
    usedA = sum(min(water_n(True), q - p) for p, q, d in lay.chA)
    rt = RUNTIME if any(ln.startswith("\tcm") for ln in L) else ""
    src = tpl.replace("#DATA#", rt + "\n".join(L)).replace("#NSIG#", str(ND - 1 + usedA))
    open(sys.argv[1], "w", newline="\n").write(src)
    print("A", [(q - p, d) for p, q, d in lay.chA], file=sys.stderr)
    print("B", [(q - p, d) for p, q, d in lay.chB], file=sys.stderr)
    print("offs", [round(x) for x in lay.offs], "avg %.1f" % (sum(lay.offs) / ND), file=sys.stderr)


if __name__ == "__main__":
    main()
