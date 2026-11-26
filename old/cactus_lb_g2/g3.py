# g3: g2 layout, chunks walked in either direction (start at the end nearer the spawn tree),
# race-free boundary rules:
#   F|F  the left chunk (walk ends at the cut) fixes every cross edge in its back-walk start
#   R|R  the right chunk (walk ends at the cut) does
#   R|F  (both walks start at the cut; cut must be clean: one pure cross edge, no mixed cell
#        near) the later-arriving drone fixes the edge right after planting its first cell
#   F|R  (both end at the cut) is not allowed
#   python g3.py out.py
import os, sys, bisect
import g2
from g2 import Layout, E, ND, DN, T_ACT, GROW_T, C_CAS, C_FM, DEPTH, render
from lay import nb, UPD, tdist, mdist, N
from build_entry import path_moves, spawn_plan, Dr, lit, DV

TILL_A = 2 * T_ACT        # till + plant
PLANT_B = T_ACT


def clean_cuts(lay):
    o, R = lay.o, lay.R
    ok = [False] * (lay.n + 1)
    for q in range(1, lay.n):
        a, b = o[q - 1], o[q]
        if mdist(a, b) != 1 or a in lay.M or b in lay.M:
            continue
        if any(m in lay.M for c in (a, b) for d, m in nb(c, R)):
            continue
        bad = False
        for i in range(max(0, q - 8), q):
            for d, m in nb(o[i], R):
                j = lay.pos[m]
                if j >= q and not (i == q - 1 and j == q):
                    bad = True
        if not bad:
            ok[q] = True
    return ok


def walk_of(p, q, d):
    return list(range(p, q)) if d == 0 else list(range(q - 1, p - 1, -1))


def is_foreign_end(j, p, q, d):
    return j >= q if d == 0 else j < p


def cell_items(lay, w, p, q, d, hx=True):
    """per walk position: (#own-earlier pure CAS, always-deferred items cost, items)"""
    o, R = lay.o, lay.R
    tpos = {i: t for t, i in enumerate(w)}
    out = []
    for t, i in enumerate(w):
        c = o[i]
        cas = []
        alw = []
        for dd, m in nb(c, R):
            j = lay.pos[m]
            if j in tpos and tpos[j] < t and lay.pure(c, m):
                cas.append(("cas", dd, dd in UPD))
            elif hx and j not in tpos and is_foreign_end(j, p, q, d) and lay.pure(c, m):
                alw.append(("xcas", dd, dd in UPD))
        if c in lay.iso and not (d == 0 and any(lay.pos[m] < p for dd, m in nb(c, R))):
            alw.append(("fm", lay.lo[c], lay.up[c]))
        if d == 0 and t == len(w) - 1:
            for i2 in range(q, min(lay.n, q + 12)):
                c2 = o[i2]
                if c2 in lay.iso and any(lay.pos[m] < q for dd, m in nb(c2, R)):
                    alw.append(("fmx", c2, lay.lo[c2], lay.up[c2]))
        if c in lay.comp:
            k = lay.comp[c]
            comp = lay.comps[k]
            last = max(comp, key=lambda x: tpos.get(lay.pos[x], -1))
            if c == last:
                alw.append(("jx", k))
        out.append((cas, alw))
    return out


def item_cost(lay, it):
    if it[0] in ("cas", "xcas"):
        return C_CAS
    if it[0] == "fm":
        return C_FM
    if it[0] == "fmx":
        return C_FM + 2 * T_ACT * 2
    if it[0] == "jx":
        return lay.net[it[1]][2]
    return 0.0


def item_var(lay, it):
    if it[0] in ("cas", "xcas"):
        return 8400.0
    if it[0] in ("fm", "fmx"):
        return 32000.0
    if it[0] == "jx":
        return (0.35 * lay.net[it[1]][2]) ** 2
    return 0.0


ZB = float(E("ZB", "0"))
ZF = float(E("ZF", "0"))


def water_n(till):
    return int(E("WA" if till else "WB", "0"))


def grow_window(lay, w, start, till, W):
    """growth wait after the last plant when the last W cells are watered (0.5 s growth)."""
    o = lay.o
    t = 0.0
    cur = start
    tp = []
    n = len(w)
    for j, i in enumerate(w):
        t += T_ACT * tdist(cur, o[i]) + (T_ACT if till else 0)
        if j >= n - W:
            t += T_ACT
        t += T_ACT
        tp.append(t)
        cur = o[i]
    G = 0.0
    for j in range(n):
        g = 0.5 * 6075 if j >= n - W else 6075.0
        G = max(G, tp[j] + g - tp[-1])
    return G + 60


def chunk_eval(lay, p, q, d, till, start):
    o = lay.o
    w = walk_of(p, q, d)
    n = len(w)
    ci = cell_items(lay, w, p, q, d)
    Wn = min(water_n(till), n)
    GW = grow_window(lay, w, start, till, Wn) if Wn else GROW_T
    fwd = Wn * T_ACT
    cur = start
    for i in w:
        fwd += T_ACT * tdist(cur, o[i]) + (TILL_A if till else PLANT_B)
        cur = o[i]
    cas = {}
    alw = {}
    vb = 0.0
    for t in range(n):
        a, b = ci[t]
        if a:
            cas[t] = C_CAS * len(a)
        if b:
            alw[t] = sum(item_cost(lay, x) for x in b)
            vb += sum(item_var(lay, x) for x in b)
    inl = sum(cas.values())
    vf = sum(8400.0 * len(ci[t][0]) for t in range(n))
    lst = sorted(alw)
    itc = sum(alw.values())

    def mv(a, b):
        return T_ACT * tdist(o[w[a]], o[w[b]])
    end = n - 1
    moves = 0.0
    if lst:
        moves = mv(end, lst[-1]) + sum(mv(lst[j + 1], lst[j]) for j in range(len(lst) - 1))
    best = None
    for K in range(0, max(1, n - 1)):
        if K > 0:
            x = n - K
            if x in cas:
                inl -= cas[x]
                itc += cas[x]
                vv = 8400.0 * len(ci[x][0])
                vf -= vv
                vb += vv
                if x not in alw:
                    pos = bisect.bisect_left(lst, x)
                    hi = lst[pos] if pos < len(lst) else None
                    lo = lst[pos - 1] if pos > 0 else None
                    top = end if hi is None else hi
                    moves += mv(top, x) - (mv(top, lo) if lo is not None else 0) + (mv(x, lo) if lo is not None else 0)
                    if hi is None and lo is None:
                        moves = mv(end, x)
                    lst.insert(pos, x)
        f = fwd + inl + ZF * max(vf, 0) ** 0.5
        b = moves + itc + ZB * vb ** 0.5
        tot = f + max(GW, b)
        if best is None or tot < best[0] - 1e-9:
            best = (tot, K, f, b, GW)
    return best


def phase_ops(lay, p, q, d, till, K, start, xstart=None, hx=True, nolast=False, xw=False):
    o = lay.o
    w = walk_of(p, q, d)
    n = len(w)
    ci = cell_items(lay, w, p, q, d, hx)
    ops = []
    cur = start
    deferred = {}
    for t, i in enumerate(w):
        c = o[i]
        for m in path_moves(cur, c):
            ops.append(("move", int(m)))
        cur = c
        if till:
            ops.append(("till",))
        if t >= n - water_n(till):
            ops.append(("water",))
        ops.append(("plant",))
        if t == 0 and xstart is not None:
            ops.append(("xcas", xstart[0], xstart[1]))
        cas, alw = ci[t]
        if t >= n - K and not (nolast and t == n - 1):
            if cas:
                deferred.setdefault(t, []).extend(cas)
        else:
            ops += cas
        if alw:
            deferred.setdefault(t, []).extend(alw)
    ops.append(("LP",))
    for t in sorted(deferred, reverse=True):
        c = o[w[t]]
        for m in path_moves(cur, c):
            ops.append(("move", int(m)))
        cur = c
        for it in deferred[t]:
            if it[0] == "jx":
                comp, order, cst, J, P = lay.net[it[1]]
                st = comp[order[0]]
                for m in path_moves(cur, st):
                    ops.append(("move", int(m)))
                cur = st
                ops.append(("jf", J, P, order))
            elif it[0] == "fmx":
                c2 = it[1]
                for m in path_moves(cur, c2):
                    ops.append(("move", int(m)))
                ops.append(("fm", it[2], it[3]))
                for m in path_moves(c2, cur):
                    ops.append(("move", int(m)))
            elif it[0] == "xcas" and xw:
                ops.append(("xcasw", it[1], it[2]))
            else:
                ops.append(it)
    return ops, cur


def plan(lay):
    o, n = lay.o, lay.n
    LMAX = int(E("LMAX", "40"))
    def safe(q):
        if q in (0, n):
            return True
        for i in range(q, min(n, q + 12)):
            c = o[i]
            if c in lay.M and any(lay.pos[m] < q for dd, m in nb(c, lay.R)):
                return False
        return True
    cuts = [q for q in range(n + 1) if lay.cut_ok[q] and (E('STRICT') != '1' or safe(q))]
    clean = clean_cuts(lay)
    lay.clean = clean
    memo = {}

    def cA(p, q, d):
        key = (p, q, d)
        if key not in memo:
            st = o[p] if d == 0 else o[q - 1]
            memo[key] = chunk_eval(lay, p, q, d, True, st)
        return memo[key]

    def start_of(p, q, d):
        return o[p] if d == 0 else o[q - 1]

    def est_off(c):
        return T_ACT * (tdist((0, 0), c) + DEPTH)

    def feas(T, offf):
        best = {(0, 1): (0, None)}  # virtual: previous chunk "reversed" so first may be F or R
        for p in cuts:
            for dp_ in (0, 1):
                if (p, dp_) not in best or p == n:
                    continue
                k = best[(p, dp_)][0]
                for q in cuts:
                    if q <= p:
                        continue
                    if q - p > LMAX:
                        break
                    for d in ((0,) if E('DIRS', '0') != '1' else (0, 1)):
                        if p > 0:
                            if dp_ != d and not clean[p]:
                                continue
                        if offf(start_of(p, q, d)) + cA(p, q, d)[0] > T:
                            continue
                        key = (q, d)
                        if key not in best or best[key][0] > k + 1:
                            best[key] = (k + 1, (p, dp_))
        ends = [(best[(n, d)][0], d) for d in (0, 1) if (n, d) in best]
        if not ends or min(ends)[0] > ND:
            return None
        d = min(ends)[1]
        ch = []
        q = n
        while q > 0:
            k, (p, dp_) = best[(q, d)]
            ch.append((p, q, d))
            q, d = p, dp_
        return ch[::-1]

    offf = est_off
    for it in range(int(E("AITER", "4"))):
        lo, hi = 0.0, 400000.0
        for _ in range(26):
            T = (lo + hi) / 2
            if feas(T, offf) is not None:
                hi = T
            else:
                lo = T
        ch = feas(hi, offf)
        while len(ch) < ND:
            k = max(range(len(ch)), key=lambda i: ch[i][1] - ch[i][0])
            p, q, d = ch[k]
            mids = [m for m in cuts if p + 2 < m < q - 2]
            m = min(mids, key=lambda m: abs(m - (p + q) / 2))
            ch[k:k + 1] = [(p, m, d), (m, q, d)] if d == 0 else [(p, m, d), (m, q, d)]
        starts = [start_of(*c) for c in ch]
        if E("SPMM", "1") == "1":
            from spawnmm import spawn_plan_mm
            offs, plans, _mk = spawn_plan_mm(tuple(starts), tuple(cA(*c)[0] for c in ch), (0, 0))
        else:
            offs, plans = spawn_plan(tuple(starts), (0, 0))
        act = {starts[k]: offs[k] * T_ACT + T_ACT for k in range(ND)}
        fin = [act[starts[k]] + cA(*ch[k])[0] for k in range(ND)]
        print("A iter", it, "T %.0f" % hi, "actual max %.0f (%.3fs)" % (max(fin), max(fin) / 6075), file=sys.stderr)
        offf = (lambda a: (lambda c: a.get(c, est_off(c))))(dict(act))
    lay.chA, lay.offs, lay.plans = ch, offs, plans
    lay.TA = max(fin)
    lay.arrA = [offs[k] * T_ACT + T_ACT for k in range(ND)]
    # positions after round A
    lay.KA = [cA(*c)[1] for c in ch]
    lay.GA = [cA(*c)[4] / 6075.0 for c in ch]
    lay.endA = []
    for k, (p, q, d) in enumerate(ch):
        ops, cur = phase_ops(lay, p, q, d, True, lay.KA[k], start_of(p, q, d))
        lay.endA.append(cur)
    # round B: chunk k for drone k, consecutive, any direction; travel from endA happens in the
    # drone's round-A slack (after it signals) where possible
    finA = [lay.arrA[k] + cA(*ch[k])[0] for k in range(ND)]
    TAh = max(finA)
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
    cand = [[0]] + [[c for c in cuts if abs(c - ch[k][0]) <= W] for k in range(1, ND)] + [[n]]
    f = {(0, 1): (0.0, None)}
    hist = [f]
    for k in range(ND):
        g = {}
        for b in cand[k + 1]:
            for d in ((0,) if E('DIRS', '0') != '1' else (0, 1)):
                bv = None
                for (a, da), (v, _) in f.items():
                    if b <= a or b - a > LMAX:
                        continue
                    if a > 0:
                        if da != d and not clean[a]:
                            continue
                        if da == 1 and d == 0:
                            continue
                    c = max(v, cB(k, a, b, d)[0])
                    if bv is None or c < bv[0]:
                        bv = (c, (a, da))
                if bv is not None:
                    g[(b, d)] = bv
        hist.append(g)
        f = g
    TB, dl = min((f[(n, d)][0], d) for d in (0, 1) if (n, d) in f)
    key = (n, dl)
    chB = []
    for k in range(ND, 0, -1):
        prev = hist[k][key][1]
        chB.append((prev[0], key[0], key[1]))
        key = prev
    lay.chB = chB[::-1]
    lay.KB = [cB(k, *c)[1] for k, c in enumerate(lay.chB)]
    lay.GB = [cB(k, *c)[4] / 6075.0 for k, c in enumerate(lay.chB)]
    lay.TB = TB
    lay.arrB = []
    for k, (p, q, d) in enumerate(lay.chB):
        lay.arrB.append(T_ACT * tdist(lay.endA[k], start_of(p, q, d)))
    print("plan TA %.0f TB %.0f est total %.3fs" % (lay.TA, TB, (lay.TA + TB + 400) / 6075), file=sys.stderr)


def xstarts(lay, ch, arr, till):
    """R|F boundaries: the later arriver fixes the single cross edge after planting its first cell."""
    o = lay.o
    xs = [None] * ND
    for k in range(ND - 1):
        p, q, d = ch[k]
        p2, q2, d2 = ch[k + 1]
        if d == 1 and d2 == 0:
            a, b = o[q - 1], o[q]  # a first cell of k, b first cell of k+1
            act = TILL_A if till else PLANT_B
            # early drone touches its boundary cell again at arr + act + move + act (its 2nd cell's CAS)
            # handler h does its xcas at max(arr_h + act, arr_o + act); the other touches its first
            # cell again at arr_o + 2 act + move; pick the handler with the larger gap
            opts = []
            for h, cell, other, ah, ao in ((k + 1, b, a, arr[k + 1], arr[k]), (k, a, b, arr[k], arr[k + 1])):
                tx = max(ah + act, ao + act)
                to = ao + 2 * act + T_ACT
                opts.append((abs(tx - to), h, cell, other))
            gap, late, cell, other = max(opts)
            if gap < 150:
                print("warning: R|F timing close at cut", q, gap, file=sys.stderr)
            for dd, m in nb(cell, lay.R):
                if m == other:
                    xs[late] = (dd, dd in UPD)
    return xs


def facing(lay, ch, arr, till):
    """F|R boundaries: the drone whose forward pass ends first handles the cross edge (it waits for
    the other's last plant); the other fixes its own last cell inline."""
    hx = [True] * ND
    nolast = [False] * ND
    xw = [False] * ND
    for k in range(ND - 1):
        p, q, d = ch[k]
        p2, q2, d2 = ch[k + 1]
        if d == 0 and d2 == 1:
            tk = arr[k] + chunk_eval(lay, p, q, d, till, lay.o[p])[2]
            tk1 = arr[k + 1] + chunk_eval(lay, p2, q2, d2, till, lay.o[q2 - 1])[2]
            if tk <= tk1:
                hx[k + 1] = False
                nolast[k + 1] = True
                xw[k] = True
            else:
                hx[k] = False
                nolast[k] = True
                xw[k + 1] = True
    return hx, nolast, xw


def main():
    widths = [int(x) for x in E("WIDTHS", "2,2,2,2,2,2,2,2,3,3,2,2,2,2,2,3,2,2,2,3").split(",")]
    lay = Layout(widths)
    plan(lay)
    if E("DIAG"): diag(lay)
    if E("MDUMP"): model_dump(lay)
    if E("DECOMP"): decompose(lay)
    o = lay.o
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
    for k in range(ND):
        p, q, d = lay.chA[k]
        opsA, curA = phase_ops(lay, p, q, d, True, lay.KA[k], pos_end[k], xa[k], hA[k], nA[k], wA[k])
        L += render("fa%d" % k, opsA)
        p, q, d = lay.chB[k]
        stB = o[p] if d == 0 else o[q - 1]
        pt = [("move", int(m)) for m in path_moves(curA, stB)]
        if k == 0:
            opsB, curB = phase_ops(lay, p, q, d, False, lay.KB[k], curA, xb[k], hB[k], nB[k], wB[k])
            pt = []
        else:
            opsB, curB = phase_ops(lay, p, q, d, False, lay.KB[k], stB, xb[k], hB[k], nB[k], wB[k])
        L += render("fb%d" % k, opsB)
        L += render("pt%d" % k, pt + [("LP",)])
    L.append("FA = [%s]" % ", ".join("fa%d" % c for c in range(ND)))
    L.append("FB = [%s]" % ", ".join("fb%d" % c for c in range(ND)))
    L.append("PT = [%s]" % ", ".join("pt%d" % c for c in range(ND)))
    L.append("GA = [%s]" % ", ".join("%.4f" % g for g in lay.GA))
    L.append("GB = [%s]" % ", ".join("%.4f" % g for g in lay.GB))
    L.append("LP = %s" % lit([[[st[0], st[1]] for st in lay.plans[c]] for c in range(ND)]))
    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), E("TPL", "t3.py"))).read()
    usedA = sum(min(water_n(True), q - p) for p, q, d in lay.chA)
    src = tpl.replace("#DATA#", "\n".join(L)).replace("#NSIG#", str(ND - 1 + usedA))
    open(sys.argv[1], "w").write(src)
    print("A", [(q - p, d) for p, q, d in lay.chA], file=sys.stderr)
    print("B", [(q - p, d) for p, q, d in lay.chB], file=sys.stderr)
    print("offs", [round(x) for x in lay.offs], "avg %.1f" % (sum(lay.offs) / ND), file=sys.stderr)



def diag(lay):
    o = lay.o
    for k, (p, q, d) in enumerate(lay.chA):
        st = o[p] if d == 0 else o[q - 1]
        md = min(tdist((0, 0), o[i]) for i in range(p, q))
        print("k%2d d=%d start dist %2d  min-in-chunk %2d  off %2d" % (k, d, tdist((0, 0), st), md, round(lay.offs[k])), file=sys.stderr)



def model_dump(lay):
    o = lay.o
    for k in range(ND):
        p, q, d = lay.chA[k]
        ra = chunk_eval(lay, p, q, d, True, o[p] if d == 0 else o[q - 1])
        p2, q2, d2 = lay.chB[k]
        rb = chunk_eval(lay, p2, q2, d2, False, lay.endA[k])
        print("M", k, "%.3f %.3f %.3f | %.3f %.3f" % (lay.arrA[k] / 6075, (lay.arrA[k] + ra[2]) / 6075, (lay.arrA[k] + ra[2] + ra[3]) / 6075, rb[2] / 6075, (rb[2] + rb[3]) / 6075), file=sys.stderr)



def decompose(lay):
    o = lay.o
    for rnd in ("A", "B"):
        ch = lay.chA if rnd == "A" else lay.chB
        rows = []
        for k in range(ND):
            p, q, d = ch[k]
            till = rnd == "A"
            st = (o[p] if d == 0 else o[q - 1])
            arr = lay.arrA[k] if till else lay.arrB[k]
            r = chunk_eval(lay, p, q, d, till, st)
            base = (q - p) * (TILL_A if till else PLANT_B)
            mv = sum(tdist(o[w], o[w2]) for w, w2 in zip(walk_of(p, q, d), walk_of(p, q, d)[1:])) * T_ACT
            inl = r[2] - base - mv
            rows.append((arr, base, mv, inl, max(GROW_T, r[3]) - GROW_T, arr + r[2] + max(GROW_T, r[3])))
            print(rnd, k, q - p, d, 'arr %.2f fwd %.2f back %.2f fin %.2f K %d' % (arr / 6075, r[2] / 6075, r[3] / 6075, rows[-1][5] / 6075, r[1]), file=sys.stderr)
        import statistics as S
        tot = max(x[5] for x in rows)
        print(rnd, "max %.3f | avg arr %.3f base %.3f moves %.3f inline %.3f backover %.3f -> avg %.3f" % tuple(
            [tot / 6075] + [S.mean(x[i] for x in rows) / 6075 for i in range(5)] + [S.mean(x[5] for x in rows) / 6075]), file=sys.stderr)


if __name__ == "__main__":
    main()
