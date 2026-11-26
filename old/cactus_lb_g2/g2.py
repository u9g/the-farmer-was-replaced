# g2: snake of antidiagonal bands, pure-edge CAS inline, mixed cells (fm) and junction
# components (settle passes) deferred into a back-walk during growth.
#   python g2.py out.py
import os, sys
from lay import build, nb, UPD, tdist, mdist, N
from build_entry import path_moves, spawn_plan, Dr, lit

E = os.environ.get
ND = 32
DN = ["North", "East", "South", "West"]
OPP = [2, 3, 0, 1]
T_ACT = 201.0
GROW_T = 6075.0 * float(E("GROWF", "1.0")) + 40
C_CAS = float(E("C_CAS", "65"))      # inline CAS: ticks + p(swap)*200
C_FM = float(E("C_FM", "230"))       # isolated mixed cell fix
C_JX = float(E("C_JX", "2600"))      # junction component settle (whole component)
BOOT = float(E("BOOT", "1.0"))
DEPTH = float(E("DEPTH", "3"))


class Layout:
    def __init__(self, widths):
        s = 0
        walls = []
        for i, w in enumerate(widths):
            s += w
            if i < len(widths) - 1:
                walls.append(s)
                s += 1
        R, o = build(walls)
        # taper: drop middle-diagonal cells of 3-wide bands near the connectors
        TAP = int(E("TAPER", "0"))
        if TAP:
            wallset = set(walls)
            conn = [c for c in R if (c[0] + c[1]) in wallset]
            mids = set()
            sd = 0
            for w in widths:
                if w == 3:
                    mids |= set(c for c in R if c[0] + c[1] == sd + 1)
                sd += w + 1
            dist = {c: 0 for c in conn}
            fr = list(conn)
            while fr:
                nf = []
                for c in fr:
                    for d, m in nb(c, R):
                        if m not in dist:
                            dist[m] = dist[c] + 1
                            nf.append(m)
                fr = nf
            drop = set(c for c in mids if dist.get(c, 99) <= TAP)
            R = set(R) - drop
            o = [c for c in o if c not in drop]
        self.R, self.o = R, o
        self.n = len(o)
        self.pos = {c: i for i, c in enumerate(o)}
        self.lo = {c: [d for d, m in nb(c, R) if d not in UPD] for c in R}
        self.up = {c: [d for d, m in nb(c, R) if d in UPD] for c in R}
        self.M = set(c for c in R if self.lo[c] and self.up[c])
        # junction components: M cells with an M neighbour
        jm = set(c for c in self.M if any(m in self.M for d, m in nb(c, R)))
        self.comp = {}
        self.comps = []
        for c0 in sorted(jm, key=lambda c: self.pos[c]):
            if c0 in self.comp:
                continue
            k = len(self.comps)
            comp = [c0]
            self.comp[c0] = k
            st = [c0]
            while st:
                x = st.pop()
                for d, m in nb(x, R):
                    if m in jm and m not in self.comp:
                        self.comp[m] = k
                        comp.append(m)
                        st.append(m)
            self.comps.append(sorted(comp, key=lambda c: self.pos[c]))
        self.iso = self.M - jm
        import jlazy
        self.net = []
        for comp in ([] if E('NONET') else self.comps):
            cst, order, m, sw, tk = jlazy.best_order(comp, R)
            J, P = jlazy.geom(comp, R)
            self.net.append((comp, order, cst * float(E("JF", "1.15")), J, P))
        # a cut before index q is allowed unless a junction component (with margin) straddles it
        self.cut_ok = [True] * (self.n + 1)
        for comp in self.comps:
            reg = set(comp)
            for _ in range(int(E("JRING", "1"))):
                reg |= set(m for c in list(reg) for d, m in nb(c, R))
            idx = sorted(self.pos[c] for c in reg)
            for q in range(idx[0] + 1, idx[-1] + 1):
                self.cut_ok[q] = False
        print("cells", self.n, "M", len(self.M), "iso", len(self.iso), "comps", len(self.comps),
              "safe cuts", sum(self.cut_ok), file=sys.stderr)

    def pure(self, a, b):
        return a not in self.M and b not in self.M


class Phase:
    """one drone's work in one round over global indices [p, q) walked forward."""

    def __init__(self, lay, p, q, till, K):
        self.lay, self.p, self.q, self.till, self.K = lay, p, q, till, K

    def ops(self, start):
        lay = self.lay
        o, R = lay.o, lay.R
        p, q, K = self.p, self.q, self.K
        n = q - p
        ops = []
        cur = start
        fwd_cost = 0.0
        own = set(range(p, q))
        deferred = {}  # global idx -> list of fix ops
        for t in range(n):
            i = p + t
            c = o[i]
            mv = path_moves(cur, c)
            for m in mv:
                ops.append(("move", int(m)))
            fwd_cost += T_ACT * len(mv)
            cur = c
            if self.till:
                ops.append(("till",))
                fwd_cost += T_ACT
            ops.append(("plant",))
            fwd_cost += T_ACT + 2
            fx = []
            # pure edges to earlier own cells
            for d, m in nb(c, R):
                j = lay.pos[m]
                if j in own and j < i and lay.pure(c, m):
                    fx.append(("cas", d, d in UPD))
            for d, m in nb(c, R):
                j = lay.pos[m]
                if j >= q and lay.pure(c, m):
                    deferred.setdefault(i, []).append(("xcas", d, d in UPD))
            if t >= n - K:
                if fx:
                    deferred.setdefault(i, []).extend(fx)
            else:
                ops += fx
                fwd_cost += C_CAS * len(fx)
            # mixed / junction fixes always deferred, attached to the cell
            if c in lay.iso:
                deferred.setdefault(i, []).append(("fm", lay.lo[c], lay.up[c]))
            if c in lay.comp:
                k = lay.comp[c]
                comp = lay.comps[k]
                if c == comp[-1]:
                    deferred.setdefault(i, []).append(("jx", k))
        ops.append(("LP",))
        back_cost = 0.0
        for i in sorted(deferred, reverse=True):
            c = o[i]
            items = deferred[i]
            # junction fixes are performed from the component's first cell
            mv = path_moves(cur, c)
            for m in mv:
                ops.append(("move", int(m)))
            back_cost += T_ACT * len(mv)
            cur = c
            for it in items:
                if it[0] in ("cas", "xcas"):
                    ops.append(it)
                    back_cost += C_CAS
                elif it[0] == "fm":
                    ops.append(it)
                    back_cost += C_FM
                elif it[0] == "jx":
                    comp, order, cst, J, P = lay.net[it[1]]
                    st = comp[order[0]]
                    for m in path_moves(cur, st):
                        ops.append(("move", int(m)))
                    back_cost += T_ACT * tdist(cur, st)
                    cur = st
                    ops.append(("jf", J, P, order))
                    back_cost += cst
        return ops, cur, fwd_cost, back_cost


def chunk_eval(lay, p, q, till, start):
    """best K for this chunk: returns (finish time from start, K, fwd, back)."""
    import bisect
    o, R = lay.o, lay.R
    n = q - p
    fwd = 0.0
    cur = start
    cas = {}
    alw = {}
    for i in range(p, q):
        c = o[i]
        fwd += T_ACT * tdist(cur, c) + (T_ACT if till else 0) + T_ACT + 2
        cur = c
        k = 0
        a = 0.0
        for d, m in nb(c, R):
            j = lay.pos[m]
            if p <= j < i and lay.pure(c, m):
                k += 1
            if j >= q and lay.pure(c, m):
                a += C_CAS
        if k:
            cas[i] = C_CAS * k
        if c in lay.iso:
            a += C_FM
        if c in lay.comp and c == lay.comps[lay.comp[c]][-1]:
            a += lay.net[lay.comp[c]][2]
        if a:
            alw[i] = a
    inl = sum(cas.values())
    # descending visit list (stored ascending for bisect)
    lst = sorted(alw)
    itc = sum(alw.values())
    def mv(a, b):
        return T_ACT * tdist(o[a], o[b])
    end = q - 1
    moves = 0.0
    if lst:
        moves = mv(end, lst[-1]) + sum(mv(lst[j + 1], lst[j]) for j in range(len(lst) - 1))
    best = None
    for K in range(0, n + 1):
        if K > 0:
            x = q - K
            if x in cas:
                inl -= cas[x]
                itc += cas[x]
                if x not in alw:
                    pos = bisect.bisect_left(lst, x)
                    hi = lst[pos] if pos < len(lst) else None
                    lo = lst[pos - 1] if pos > 0 else None
                    if hi is None:
                        moves += mv(end, x) - (mv(end, lo) if lo is not None else 0) + (mv(x, lo) if lo is not None else 0)
                    else:
                        moves += mv(hi, x) - (mv(hi, lo) if lo is not None else 0) + (mv(x, lo) if lo is not None else 0)
                    lst.insert(pos, x)
        f = fwd + inl
        b = moves + itc
        tot = f + max(GROW_T, b)
        if best is None or tot < best[0] - 1e-9:
            best = (tot, K, f, b)
    return best


def plan(lay):
    o = lay.o
    n = lay.n
    LMAX = int(E("LMAX", "40"))
    cuts = [q for q in range(n + 1) if lay.cut_ok[q]]
    memo = {}

    def cA(p, q):
        key = (p, q)
        if key not in memo:
            memo[key] = chunk_eval(lay, p, q, True, o[p])
        return memo[key]

    def offs_of(p):
        return T_ACT * (tdist((0, 0), o[p]) + DEPTH) * BOOT

    def feas(T, offf):
        # fewest chunks covering [0,n) with offf(p) + cost <= T
        INF = 10 ** 9
        best = {0: (0, None)}
        for p in cuts:
            if p not in best or p == n:
                continue
            k, _ = best[p]
            for q in cuts:
                if q <= p or q - p > LMAX:
                    continue
                if offf(p) + cA(p, q)[0] > T:
                    continue
                if q not in best or best[q][0] > k + 1:
                    best[q] = (k + 1, p)
        if n not in best or best[n][0] > ND:
            return None
        ch = []
        q = n
        while q > 0:
            p = best[q][1]
            ch.append((p, q))
            q = p
        return ch[::-1]

    offf = offs_of
    for it in range(3):
        lo, hi = 0.0, 400000.0
        for _ in range(28):
            T = (lo + hi) / 2
            if feas(T, offf) is not None:
                hi = T
            else:
                lo = T
        ch = feas(hi, offf)
        while len(ch) < ND:
            k = max(range(len(ch)), key=lambda i: ch[i][1] - ch[i][0])
            p, q = ch[k]
            mids = [m for m in cuts if p < m < q]
            m = min(mids, key=lambda m: abs(m - (p + q) / 2))
            ch[k:k + 1] = [(p, m), (m, q)]
        starts = [o[p] for p, q in ch]
        offs, plans = spawn_plan(tuple(starts), (0, 0))
        actual = {ch[k][0]: offs[k] * T_ACT + T_ACT for k in range(ND)}
        fin = [actual[p] + cA(p, q)[0] for p, q in ch]
        print("A iter", it, "T %.0f" % hi, "actual max %.0f (%.3fs)" % (max(fin), max(fin) / 6075), file=sys.stderr)
        offf = (lambda act: (lambda p: act.get(p, offs_of(p))))(dict(actual))
    lay.chA, lay.offs, lay.plans = ch, offs, plans
    lay.TA = max(fin)
    # round B: chunk k starts where drone k ended round A, forward only
    memoB = {}

    def cB(k, p, q):
        key = (k, p, q)
        if key not in memoB:
            endA = lay.endA[k]
            r = chunk_eval(lay, p, q, False, endA)
            memoB[key] = r
        return memoB[key]

    lay.endA = []
    lay.KA = []
    for k, (p, q) in enumerate(ch):
        r = cA(p, q)
        ph = Phase(lay, p, q, True, r[1])
        _, cur, _, _ = ph.ops(o[p])
        lay.endA.append(cur)
        lay.KA.append(r[1])
    # B: DP over cuts, chunk k = [b_k, b_{k+1}); b_0 = 0, b_32 = n
    W = int(E("BWIN", "30"))
    cand = [[0]] + [[c for c in cuts if abs(c - ch[k][0]) <= W] for k in range(1, ND)] + [[n]]
    f = {0: (0.0, None)}
    hist = [f]
    for k in range(ND):
        g = {}
        for b in cand[k + 1]:
            bv = None
            for a, (v, _) in f.items():
                if b <= a or b - a > LMAX:
                    continue
                c = max(v, cB(k, a, b)[0])
                if bv is None or c < bv[0]:
                    bv = (c, a)
            if bv is not None:
                g[b] = bv
        hist.append(g)
        f = g
    TB, _ = f[n]
    bs = [n]
    b = n
    for k in range(ND, 0, -1):
        a = hist[k][b][1]
        bs.append(a)
        b = a
    bs = bs[::-1]
    lay.chB = [(bs[k], bs[k + 1]) for k in range(ND)]
    lay.KB = [cB(k, a, b)[1] for k, (a, b) in enumerate(lay.chB)]
    lay.TB = TB
    print("plan TA %.0f TB %.0f est total %.3fs" % (lay.TA, TB, (lay.TA + TB + 400) / 6075), file=sys.stderr)


def render(name, ops):
    L = ["def %s():" % name]
    for op in ops:
        k = op[0]
        if k == "move":
            L.append("\tmove(%s)" % DN[op[1]])
        elif k == "till":
            L.append("\ttill()")
        elif k == "plant":
            L.append("\tplant(Entities.Cactus)")
        elif k == "LP":
            L.append("\ttl = get_time()")
        elif k == "cas":
            d, up = op[1], op[2]
            L.append("\tif measure() %s measure(%s):" % (">" if up else "<", DN[d]))
            L.append("\t\tswap(%s)" % DN[d])
        elif k == "xcas":
            d, up = op[1], op[2]
            L.append("\txcas(%s, %d)" % (DN[d], 1 if up else 0))
        elif k == "fm":
            L.append("\tfm(%s, %s)" % (lit([Dr(x) for x in op[1]]), lit([Dr(x) for x in op[2]])))
        elif k == "jf":
            L.append("\tjf(%s, %s, %s)" % (lit(op[1]), lit(op[2]), lit(op[3])))
        else:
            raise ValueError(k)
    L.append("\treturn tl")
    L.append("")
    return L


def main():
    widths = [int(x) for x in E("WIDTHS", "2,2,2,2,2,2,2,2,2,2,2,2,3,3,3,3,2,2,2,2").split(",")]
    lay = Layout(widths)
    plan(lay)
    if E("REPORT"): report(lay)
    o = lay.o
    L = []
    from build_entry import DV
    pos_end = {}

    def sim_plan(c, pp):
        for st in lay.plans[c]:
            for m in st[0]:
                dx, dy = DV[int(m)]
                pp = ((pp[0] + dx) % N, (pp[1] + dy) % N)
            sim_plan(st[1], pp)
        pos_end[c] = pp

    sim_plan(0, (0, 0))
    for k in range(ND):
        p, q = lay.chA[k]
        opsA, curA, fa, ba = Phase(lay, p, q, True, lay.KA[k]).ops(pos_end[k])
        L += render("fa%d" % k, opsA)
        a, b = lay.chB[k]
        pre = [("move", int(m)) for m in path_moves(curA, o[a])]
        opsB, curB, fb, bb = Phase(lay, a, b, False, lay.KB[k]).ops(o[a])
        L += render("fb%d" % k, pre + opsB)
    L.append("FA = [%s]" % ", ".join("fa%d" % c for c in range(ND)))
    L.append("FB = [%s]" % ", ".join("fb%d" % c for c in range(ND)))
    L.append("LP = %s" % lit([[[st[0], st[1]] for st in lay.plans[c]] for c in range(ND)]))
    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "t2.py")).read()
    src = tpl.replace("#DATA#", "\n".join(L)).replace("#NSIG#", str(ND - 1))
    open(sys.argv[1], "w").write(src)
    print("A sizes", [q - p for p, q in lay.chA], file=sys.stderr)
    print("B sizes", [q - p for p, q in lay.chB], file=sys.stderr)
    print("KA", lay.KA, "KB", lay.KB, file=sys.stderr)



def report(lay):
    o = lay.o
    for k, (p, q) in enumerate(lay.chA):
        r = chunk_eval(lay, p, q, True, o[p])
        a, b = lay.chB[k]
        rb = chunk_eval(lay, a, b, False, lay.endA[k])
        js = sum(1 for i in range(p, q) if o[i] in lay.comp)
        print("k%2d A n=%2d off=%4.0f fwd=%6.0f back=%6.0f K=%2d | B n=%2d fwd=%6.0f back=%6.0f K=%2d  jcells=%d" % (
            k, q - p, lay.offs[k] * T_ACT, r[2], r[3], r[1], b - a, rb[2], rb[3], rb[1], js), file=sys.stderr)


if __name__ == "__main__":
    main()
