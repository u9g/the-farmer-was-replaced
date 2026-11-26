# g4: cactus leaderboard generator (see README.md).
#   python g4.py out.py
#
# Round A: drone k plants chunk k = snake[p, q) walking either way, then its tail walks back m
# cells running deferred fixes and stops at u_k. Round B: drone k plants snake[u_k, u_{k+1})
# walking up the snake (u_0 = 0), so it starts where its A tail stopped, then its tail walks back.
from g4_core import *

GROW = TPS * float(E("GW", "1.0")) + float(E("GPAD", "40"))
INL_FM = float(E("INL_FM", "3"))
MINC = int(E("MINC", "8"))     # extra moves to run an fm/jf inline (off the tail)


def cut_type(dl, dr):
    if dl == 0 and dr == 0:
        return "FF"
    if dl == 1 and dr == 1:
        return "RR"
    if dl == 0 and dr == 1:
        return "FR"
    return "RF"


class RoundPlan:
    """chs: [(p, q, d)], tails: per chunk number of walk positions the tail covers (0 = none).
    rf: per R|F cut, how it is handled: 'first' (later arriver xcas after its first plant)."""

    def __init__(self, lay, plan, chs, till, tails, fins, arr=None, wrap=False):
        self.lay, self.plan, self.till = lay, plan, till
        self.chs = chs
        self.tails = tails
        n = lay.n
        owner = [0] * n
        tpos = [0] * n
        for k, ch in enumerate(chs):
            for t, i in enumerate(walk_of(*ch)):
                owner[i] = k
                tpos[i] = t
        self.owner, self.tpos = owner, tpos
        nk = len(chs)
        self.slot = {}
        self.forced = set()
        self.delay = [0.0] * nk        # wait before the first xcas (ticks)
        ops = lay.ops
        own_of = lambda c: owner[lay.pos[c]]
        pairs = [(k, k + 1) for k in range(nk - 1)]
        if wrap:
            pairs.append((nk - 1, 0))
        for l, r in pairs:
            q = chs[l][1]
            t = cut_type(chs[l][2], chs[r][2])
            k = l
            cross = [op["id"] for op in ops if set(own_of(c) for c in op["cells"]) == {l, r}]
            if not cross:
                continue
            if t == "FF":
                H, slot = l, "head"
            elif t == "RR":
                H, slot = r, "head"
            elif t == "FR":
                H, slot = (l if fins[l] >= fins[r] else r), "headw"
            else:
                # both start here: the later arriver CASes right after its first plant
                al, ar = (arr[l], arr[r]) if arr else (0.0, 0.0)
                H = l if al >= ar else r
                slot = "first"
                gap = abs(al - ar) / TA
                if 1.2 <= gap <= 4.8:
                    self.delay[H] = (4.8 - gap) * TA
            if t in ("FR", "RF"):
                assert len(cross) == 1 and ops[cross[0]]["k"] == "cas", (q, t, [ops[i]["k"] for i in cross])
            Nn = r if H == l else l
            hset = set(cross)
            changed = t in ("FR", "RF")
            while changed:
                changed = False
                touched = set(c for i in hset for c in ops[i]["cells"])
                for c in list(touched):
                    for oid in lay.ops_of[c]:
                        if oid in hset or oid in self.forced:
                            continue
                        op = ops[oid]
                        ks = set(own_of(x) for x in op["cells"])
                        if ks != {Nn}:
                            if ks == {l, r}:
                                hset.add(oid)
                                changed = True
                            continue
                        if op["k"] == "cas":
                            self.forced.add(oid)
                        else:
                            assert slot == "head", (q, t, op["k"])
                            hset.add(oid)
                            changed = True
            for oid in hset:
                stand = None
                if oid in cross and slot in ("headw", "first"):
                    a, b = lay.o[q - 1], lay.o[q]
                    stand = a if H == l else b
                self.slot[oid] = (H, slot, stand)
        self.inline = [dict() for _ in range(nk)]
        self.deferred = [[] for _ in range(nk)]
        self.head = [[] for _ in range(nk)]
        self.first = [[] for _ in range(nk)]
        self.back = [dict() for _ in range(nk)]    # inline fm/jf: t -> [(stand, oid)]
        for oid, (H, slot, stand) in self.slot.items():
            if slot in ("head", "headw"):
                self.head[H].append((stand, oid, slot == "headw"))
            else:
                self.first[H].append((stand, oid))
        for op in ops:
            oid = op["id"]
            if oid in self.slot:
                continue
            ks = set(own_of(c) for c in op["cells"])
            assert len(ks) == 1, (op["k"], ks)
            k = ks.pop()
            nn = chs[k][1] - chs[k][0]
            tp = [tpos[lay.pos[c]] for c in op["cells"]]
            ready = max(tp)
            lim = nn - 1 - tails[k]       # tail covers walk positions >= lim
            if op["k"] == "cas":
                later = op["cells"][tp.index(ready)]
                if oid in self.forced or ready < lim or tails[k] == 0:
                    self.inline[k].setdefault(ready, []).append((later, oid))
                else:
                    self.deferred[k].append((later, oid))
            else:
                stand = op["m"] if op["k"] == "fm" else op["start"]
                if tails[k] > 0 and tpos[lay.pos[stand]] >= lim:
                    self.deferred[k].append((stand, oid))
                else:
                    self.back[k].setdefault(ready, []).append((stand, oid))

    def stand_for(self, op, cur):
        if op["k"] == "cas":
            a, b = op["cells"]
            return a if tdist(cur, a) <= tdist(cur, b) else b
        if op["k"] == "fm":
            return op["m"]
        return op["start"]

    def stop_cell(self, k):
        ch = self.chs[k]
        w = walk_of(*ch)
        return self.lay.o[w[len(w) - 1 - self.tails[k]]]

    def chunk_ops(self, k, start_pos):
        lay = self.lay
        ch = self.chs[k]
        w = walk_of(*ch)
        n = len(w)
        fwd = []
        cur = start_pos
        for t, i in enumerate(w):
            c = lay.o[i]
            for m in path_moves(cur, c):
                fwd.append(("move", int(m)))
            cur = c
            if self.till:
                fwd.append(("till",))
            fwd.append(("plant",))
            if t == 0:
                if self.first[k] and self.delay[k] > 0:
                    fwd.append(("wait", self.delay[k]))
                for stand, oid in self.first[k]:
                    fwd.append(("opx", oid, c))
            for stand, oid in self.inline[k].get(t, []):
                assert stand == c
                fwd.append(("op", oid, c))
            for stand, oid in self.back[k].get(t, []):
                for m in path_moves(cur, stand):
                    fwd.append(("move", int(m)))
                fwd.append(("op", oid, stand))
                cur2 = stand
                for m in path_moves(cur2, c):
                    fwd.append(("move", int(m)))
        tail = []
        for stand, oid, wait in self.head[k]:
            op = lay.ops[oid]
            st = stand if stand is not None else self.stand_for(op, cur)
            for m in path_moves(cur, st):
                tail.append(("move", int(m)))
            cur = st
            tail.append(("opw" if wait else "op", oid, st))
        dl = sorted(self.deferred[k], key=lambda x: -self.tpos[lay.pos[x[0]]])
        for stand, oid in dl:
            for m in path_moves(cur, stand):
                tail.append(("move", int(m)))
            cur = stand
            tail.append(("op", oid, stand))
        stop = self.stop_cell(k)
        for m in path_moves(cur, stop):
            tail.append(("move", int(m)))
        cur = stop
        return fwd, tail, cur

    def cost(self, ops):
        t = 0.0
        v = 0.0
        for x in ops:
            if x[0] in ("move", "till", "plant", "water"):
                t += TA + 1
            elif x[0] == "wait":
                t += x[1]
            else:
                op = self.lay.ops[x[1]]
                t += op_cost(op)
                v += op_var(op)
                if x[0] == "opw":
                    t += 320
                if x[0] == "opx":
                    t += 40
        return t, v


# ---------------------------------------------------------------------------------------------
class ChunkModel:
    """chunk cost estimates (own ops exact, ops straddling an end at half cost)."""

    def __init__(self, lay):
        self.lay = lay
        o = lay.o
        n = lay.n
        self.pre = [0] * (n + 1)
        for i in range(1, n):
            self.pre[i + 1] = self.pre[i] + tdist(o[i - 1], o[i])
        self.span = [(min(lay.pos[c] for c in op["cells"]), max(lay.pos[c] for c in op["cells"])) for op in lay.ops]
        self.by_max = [[] for _ in range(n)]
        self.by_min = [[] for _ in range(n)]
        for op in lay.ops:
            a, b = self.span[op["id"]]
            self.by_max[b].append(op["id"])
            self.by_min[a].append(op["id"])
        self.memo = {}

    def walkdist(self, i, j):
        if i > j:
            i, j = j, i
        return self.pre[j + 1] - self.pre[i + 1]

    def items(self, p, q, d):
        """own ops as (ready tpos, stand tpos, cost, var, kind) + cross cost."""
        key = ("it", p, q, d)
        r = self.memo.get(key)
        if r is not None:
            return r
        lay = self.lay
        tp = (lambda i: i - p) if d == 0 else (lambda i: q - 1 - i)
        its = []
        cross_c = 0.0
        for i in range(p, q):
            for oid in self.by_max[i]:
                a, b = self.span[oid]
                op = lay.ops[oid]
                if a >= p:
                    ts = [tp(lay.pos[c]) for c in op["cells"]]
                    ready = max(ts)
                    if op["k"] == "cas":
                        stand = ready
                    else:
                        st = op["m"] if op["k"] == "fm" else op["start"]
                        stand = tp(lay.pos[st])
                    its.append((ready, stand, op_cost(op), op_var(op), op["k"]))
                else:
                    cross_c += 0.5 * op_cost(op)
            for oid in self.by_min[i]:
                a, b = self.span[oid]
                if b >= q:
                    cross_c += 0.5 * op_cost(lay.ops[oid])
        r = (its, cross_c)
        self.memo[key] = r
        return r

    def ev(self, p, q, d, till, m):
        """(finish-from-arrival, fwd, tail) for chunk walked d with a tail covering m positions."""
        key = (p, q, d, till, m)
        r = self.memo.get(key)
        if r is not None:
            return r
        n = q - p
        its, cross_c = self.items(p, q, d)
        base = (TA + 1) * (self.walkdist(p, q - 1) + n * (2 if till else 1))
        lim = n - 1 - m
        fi = base
        fv = 0.0
        tc = cross_c + (TA + 1) * m
        tv = 0.0
        for ready, stand, c, v, kd in its:
            if kd == "cas":
                if m > 0 and ready >= lim:
                    tc += c
                    tv += v
                else:
                    fi += c
                    fv += v
            else:
                if m > 0 and stand >= lim:
                    tc += c
                    tv += v
                else:
                    fi += c + INL_FM * TA
                    fv += v
        fwd = fi + Z * math.sqrt(fv)
        tail = tc + Z * math.sqrt(tv)
        r = (fwd + max(GROW, tail), fwd, tail)
        self.memo[key] = r
        return r

    def best_m(self, p, q, d, till, mmax=None):
        n = q - p
        best = None
        for m in range(0, n if mmax is None else min(n, mmax + 1)):
            r = self.ev(p, q, d, till, m)
            if best is None or r[0] < best[0] - 1e-6:
                best = (r[0], m)
        return best


def dp_A(lay, plan, cm, arrival, T, LMAX):
    n = lay.n
    cuts = [q for q in range(n + 1) if plan.cut_ff[q]]
    best = {(0, -1): (0, None)}
    for p in cuts:
        for dp_ in (-1, 0, 1):
            if (p, dp_) not in best or p == n:
                continue
            k = best[(p, dp_)][0]
            for q in cuts:
                if q <= p:
                    continue
                if q - p > LMAX:
                    break
                if q - p < MINC:
                    continue
                for d in (0, 1):
                    if p > 0:
                        t = cut_type(dp_, d)
                        if t in ("RF", "FR") and not plan.cut_clean[p]:
                            continue
                    st = lay.o[p] if d == 0 else lay.o[q - 1]
                    if arrival(st) + cm.best_m(p, q, d, True)[0] > T:
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


def plan_A(lay, plan, cm, arrival, LMAX):
    lo, hi = 1.0 * TPS, 6.0 * TPS
    assert dp_A(lay, plan, cm, arrival, hi, LMAX) is not None
    for _ in range(18):
        mid = (lo + hi) / 2
        if dp_A(lay, plan, cm, arrival, mid, LMAX) is not None:
            hi = mid
        else:
            lo = mid
    ch = dp_A(lay, plan, cm, arrival, hi, LMAX)
    while len(ch) < ND:
        k = max(range(len(ch)), key=lambda i: ch[i][1] - ch[i][0])
        p, q, d = ch[k]
        mids = [x for x in range(p + 3, q - 2) if plan.cut_ff[x]]
        x = min(mids, key=lambda x: abs(x - (p + q) / 2))
        ch[k:k + 1] = [(p, x, d), (x, q, d)]
    return ch, hi


def u_of(lay, ch, m):
    """snake index where chunk ch's tail stops (tail covering m walk positions)."""
    p, q, d = ch
    w = walk_of(p, q, d)
    return w[len(w) - 1 - m]


def plan_B(lay, plan, cm, chs, arr, TA_lim, cands=None):
    """round B is cyclic: drone k plants [u_k, u_k+1) going up the snake, the last segment wraps
    from the snake's end to its start. returns (drone order, rotated lay, B chunks, A tail depths,
    est max B)."""
    nk = len(chs)
    n = lay.n
    opts = []
    for k, ch in enumerate(chs):
        p, q, d = ch
        allo = []
        for m in range(0, q - p):
            fA = arr[k] + cm.ev(p, q, d, True, m)[0]
            allo.append((u_of(lay, ch, m), m, fA))
        o_ = [x for x in allo if x[2] <= TA_lim]
        if len(o_) < 3:
            o_ = sorted(allo, key=lambda x: x[2])[:max(3, len(o_))]
        opts.append(o_)
        opts[-1] = (o_, allo)
    best = None
    js = cands if cands is not None else [int(x) for x in E("BJ", "0,8,16,24").split(",")]
    for j in js:
        for u_j, m_j, fa_j in sorted(opts[j][0], key=lambda x: x[2])[:int(E("BJM", "2"))]:
            s = u_j
            lr = lay.rotated(s)
            pr = Plan(lr)
            cr = ChunkModel(lr)
            order = list(range(j, nk)) + list(range(0, j))
            rot = lambda u: (u - s) % n
            f = {0: (0.0, None)}
            hist = [f]
            for t in range(1, nk):
                k = order[t]
                g = {}
                cand = [x for x in opts[k][0] if pr.cut_ff[rot(x[0])]]
                if not cand:
                    cand = [x for x in sorted(opts[k][1], key=lambda x: x[2]) if pr.cut_ff[rot(x[0])]][:3]
                for u, m, fa in cand:
                    ur = rot(u)
                    bv = None
                    for u0, (v, _) in f.items():
                        if ur - u0 < MINC:
                            continue
                        c = max(v, cr.best_m(u0, ur, 0, False)[0])
                        if bv is None or c < bv[0]:
                            bv = (c, u0)
                    if bv is not None and (ur not in g or bv[0] < g[ur][0]):
                        g[ur] = bv
                f = g
                hist.append(f)
            bestv = None
            for u, (v, _) in f.items():
                if n - u < MINC:
                    continue
                c = max(v, cr.best_m(u, n, 0, False)[0])
                if bestv is None or c < bestv[0]:
                    bestv = (c, u)
            if bestv is None:
                continue
            us = [bestv[1]]
            u = bestv[1]
            for t in range(nk - 1, 0, -1):
                u = hist[t][u][1]
                us.append(u)
            us = us[::-1]
            ms = [None] * nk
            for t in range(nk):
                k = order[t]
                for uu, m, fa in opts[k][1]:
                    if rot(uu) == us[t]:
                        ms[k] = m
                        break
            HA = max(arr[k] + cm.ev(*chs[k], True, ms[k])[0] for k in range(nk))
            tot = HA + bestv[0]
            print("    B rot j=%d s=%d: HA %.3f HB %.3f" % (j, s, HA / TPS, bestv[0] / TPS), file=sys.stderr)
            if best is None or tot < best[0]:
                chB = [None] * nk
                for t in range(nk):
                    chB[order[t]] = (us[t], us[t + 1] if t + 1 < nk else n, 0)
                best = (tot, lr, pr, cr, chB, ms, HA, bestv[0])
    return best


def render_ops(lay, ops):
    L = []
    for x in ops:
        k = x[0]
        if k == "move":
            L.append("\tmove(%s)" % DN[x[1]])
        elif k == "till":
            L.append("\ttill()")
        elif k == "water":
            L.append("\tuse_item(Items.Water)")
        elif k == "plant":
            L.append("\tplant(Entities.Cactus)")
        elif k == "wait":
            L.append("\twait_until(get_time() + %.4f)" % (x[1] / TPS))
        else:
            op = lay.ops[x[1]]
            stand = x[2]
            if op["k"] == "cas":
                lo, hi = op["lo"], op["hi"]
                other = hi if stand == lo else lo
                d = dir_to(stand, other)
                up = stand == lo
                if k == "opw":
                    L.append("\txcasw(%s, %d)" % (DN[d], 1 if up else 0))
                elif k == "opx":
                    L.append("\txcas(%s, %d)" % (DN[d], 1 if up else 0))
                else:
                    L.append("\tif measure() %s measure(%s):" % (">" if up else "<", DN[d]))
                    L.append("\t\tswap(%s)" % DN[d])
            elif op["k"] == "fm":
                c = op["m"]
                L.append("\tfm(%s, %s)" % (lit([Dr(d) for d in lay.lo[c]]), lit([Dr(d) for d in lay.up[c]])))
            else:
                L.append("\tjf(%s, %s, %s)" % (lit(op["J"]), lit(op["P"]), lit(op["order"])))
    return L


def dir_to(a, b):
    for d, (dx, dy) in DV.items():
        if (a[0] + dx, a[1] + dy) == b:
            return d
    raise ValueError((a, b))


def spawn(lay, chs, rest):
    from spawnmm import spawn_plan_mm
    starts = [start_of(lay, c) for c in chs]
    offs, plans, mk = spawn_plan_mm(tuple(starts), tuple(rest), (0, 0))
    return offs, plans


def main():
    widths = [int(x) for x in E("WIDTHS", "2,2,2,2,2,2,2,2,2,2,2,2,3,3,2,2,3,3,2,2").split(",")]
    lay = Lay(widths)
    plan = Plan(lay)
    cm = ChunkModel(lay)
    LMAX = int(E("LMAX", "36"))
    arr_of = {}

    def arrival(c):
        if c in arr_of:
            return arr_of[c]
        return (SPW + tdist((0, 0), c)) * TA
    for it in range(int(E("AITER", "3"))):
        ch, TA_ = plan_A(lay, plan, cm, arrival, LMAX)
        rest = [cm.best_m(*c, True)[0] for c in ch]
        offs, plans = spawn(lay, ch, rest)
        arr = [offs[k] * TA + TA for k in range(ND)]
        fin = [arr[k] + rest[k] for k in range(ND)]
        print("A it %d  plan TA %.3f  spawned max %.3f  mean arr %.1f" % (
            it, TA_ / TPS, max(fin) / TPS, sum(arr) / ND / TA), file=sys.stderr)
        arr_of = {start_of(lay, c): arr[k] for k, c in enumerate(ch)}
    pos_end = {}

    def sim_plan(c, pp):
        for st in plans[c]:
            for m in st[0]:
                dx, dy = DV[int(m)]
                pp = ((pp[0] + dx) % N, (pp[1] + dy) % N)
            sim_plan(st[1], pp)
        pos_end[c] = pp
    sim_plan(0, (0, 0))
    HA0 = max(fin)
    best = None
    for slack in [float(x) for x in E("SLK", "0,0.05,0.1,0.2").split(",")]:
        r = plan_B(lay, plan, cm, ch, arr, HA0 + slack * TPS)
        if r is None:
            continue
        print("  slack %.2f: HA %.3f HB %.3f" % (slack, r[6] / TPS, r[7] / TPS), file=sys.stderr)
        if best is None or r[0] < best[0]:
            best = r
    _, layB, planB, cmB, chB, ms, _, _ = best
    mB = [cmB.best_m(p, q, d, False)[1] for p, q, d in chB]
    finA = [arr[k] + cm.ev(*ch[k], True, ms[k])[0] for k in range(ND)]
    finB = [cmB.ev(*chB[k], False, mB[k])[0] for k in range(ND)]
    rA = RoundPlan(lay, plan, ch, True, ms, finA, arr=arr)
    # round B: drones in cyclic order on the rotated snake
    orderB = sorted(range(ND), key=lambda k: chB[k][0])
    chBs = [chB[k] for k in orderB]
    rBs = RoundPlan(layB, planB, chBs, False, [mB[k] for k in orderB], [finB[k] for k in orderB], arr=[0.0] * ND, wrap=True)
    slotB = {k: i for i, k in enumerate(orderB)}
    L = []
    resA, resB = [], []
    for k in range(ND):
        fwd, tail, cur = rA.chunk_ops(k, pos_end[k])
        f, fv = rA.cost(fwd)
        t, tv = rA.cost(tail)
        trav = TA * tdist(pos_end[k], start_of(lay, ch[k]))
        resA.append((arr[k], f - trav, t))
        L.append("def fa%d():" % k)
        L += render_ops(lay, fwd)
        L.append("\ttl = get_time()")
        L += render_ops(lay, tail)
        L.append("\treturn tl")
        L.append("")
        assert cur == layB.o[chB[k][0]], (k, cur, layB.o[chB[k][0]])
        fwd, tail, cur2 = rBs.chunk_ops(slotB[k], cur)
        f2, fv2 = rBs.cost(fwd)
        t2, tv2 = rBs.cost(tail)
        resB.append((f2, t2))
        L.append("def fb%d():" % k)
        L += render_ops(lay, fwd)
        L.append("\ttl = get_time()")
        L += render_ops(lay, tail)
        L.append("\treturn tl")
        L.append("")
    HA = max(a + f + max(GROW, t) for a, f, t in resA)
    HB = max(f + max(GROW, t) for f, t in resB)
    print("exact est: HA %.3f HB %.3f total %.3f" % (HA / TPS, HB / TPS, (HA + HB + 3 * TA) / TPS), file=sys.stderr)
    if E("DUMP"):
        for k in range(ND):
            a, f, t = resA[k]
            f2, t2 = resB[k]
            print("k%2d A n=%2d d=%d m=%2d arr %.2f fwd %.2f tail %.2f fin %.2f | B n=%2d m=%2d fwd %.2f tail %.2f fin %.2f" % (
                k, ch[k][1] - ch[k][0], ch[k][2], ms[k], a / TPS, f / TPS, t / TPS, (a + f + max(GROW, t)) / TPS,
                chB[k][1] - chB[k][0], mB[k], f2 / TPS, t2 / TPS, (f2 + max(GROW, t2)) / TPS), file=sys.stderr)
    L.append("FA = [%s]" % ", ".join("fa%d" % c for c in range(ND)))
    L.append("FB = [%s]" % ", ".join("fb%d" % c for c in range(ND)))
    L.append("GA = [%s]" % ", ".join("1.0001" for c in range(ND)))
    L.append("GB = [%s]" % ", ".join("1.0001" for c in range(ND)))
    L.append("LP = %s" % lit([[[st[0], st[1]] for st in plans[c]] for c in range(ND)]))
    tpl = open(os.path.join(HERE, "t4.py")).read()
    src = tpl.replace("#DATA#", "\n".join(L)).replace("#NSIG#", str(ND - 1))
    open(sys.argv[1], "w").write(src)


if __name__ == "__main__":
    main()
