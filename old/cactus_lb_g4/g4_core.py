# g4: cactus leaderboard generator.
#
# Model (see README.md):
#   * every fix is a monotone op: a pure-pure CAS, an isolated-mixed settle (fm) or a junction
#     settle (jf). Pure cells only ever move towards their extreme, so ops commute: the final
#     field is sorted as long as every op runs once after all of its cells are planted, and no two
#     drones run ops on a shared cell at the same moment.
#   * chunks are snake segments walked in either direction; the cut between two chunks is one of
#       F|F / R|R  one drone ends at the cut, the other starts there: the ender runs every cross op
#                  at the start of its tail (the starter planted its side long before)
#       R|F        both start at the cut: X runs the cross CAS at the end of its tail, Y runs its
#                  own ops on the shared cell inline at plant time
#       F|R        both end at the cut: X (later finisher) waits for Y's last cell, then runs the
#                  cross CAS; Y runs its ops on the shared cell inline
#   * tails walk back from the chunk end to the start running deferred ops, so round B starts
#     where round A's tail ended.
#   python g4.py out.py
import os, sys, random, math, bisect
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cactus_lb_g2"))
from lay import build, nb, UPD, tdist, N
from build_entry import path_moves, Dr, lit, DV
import jlazy

E = os.environ.get
ND = 32
DN = ["North", "East", "South", "West"]
TA = 200.0                     # ticks per action
TPS = 6075.0
GROW = TPS * 1.0 + 30          # growth window in ticks (+ harvest latency slack)
Z = float(E("Z", "1.6"))       # sigma multiplier for tails
SPW = float(E("SPW", "4"))     # spawn depth estimate (actions) before the first plan


def walls_of(ws):
    s = 0
    w = []
    for i, x in enumerate(ws):
        s += x
        if i < len(ws) - 1:
            w.append(s)
            s += 1
    return w


class Lay:
    def __init__(self, widths):
        if E("TAPERX"):
            os.environ.setdefault("NONET", "1")
            import g2
            L2 = g2.Layout(widths)
            R, o = L2.R, L2.o
        else:
            R, o = build(walls_of(widths))
        self.R, self.o = set(R), list(o)
        self.n = len(o)
        self.pos = {c: i for i, c in enumerate(o)}
        R = self.R
        self.lo = {c: [d for d, m in nb(c, R) if d not in UPD] for c in R}
        self.up = {c: [d for d, m in nb(c, R) if d in UPD] for c in R}
        self.M = set(c for c in R if self.lo[c] and self.up[c])
        jm = set(c for c in self.M if any(m in self.M for d, m in nb(c, R)))
        self.iso = self.M - jm
        comps = []
        seen = set()
        for c0 in sorted(jm, key=lambda c: self.pos[c]):
            if c0 in seen:
                continue
            st = [c0]
            comp = []
            seen.add(c0)
            while st:
                x = st.pop()
                comp.append(x)
                for d, m in nb(x, R):
                    if m in jm and m not in seen:
                        seen.add(m)
                        st.append(m)
            comps.append(sorted(comp, key=lambda c: self.pos[c]))
        self.comps = comps
        self.build_ops()
        print("cells", self.n, "M", len(self.M), "iso", len(self.iso), "comps", [len(c) for c in comps], file=sys.stderr)

    def rotated(self, s):
        """same field and ops, snake order rotated to start at index s (round B wraps)."""
        import copy
        L = copy.copy(self)
        L.o = self.o[s:] + self.o[:s]
        L.pos = {c: i for i, c in enumerate(L.o)}
        return L

    def build_ops(self):
        R, M = self.R, self.M
        ops = []
        for c in R:
            if c in M:
                continue
            for d, m in nb(c, R):
                if d in UPD and m not in M:
                    ops.append({"k": "cas", "lo": c, "hi": m, "cells": [c, m]})
        for c in self.iso:
            cells = [c] + [m for d, m in nb(c, R)]
            ops.append({"k": "fm", "m": c, "cells": cells})
        jm_comp = {}
        for i, comp in enumerate(self.comps):
            cs = set(comp)
            ring = set(m for c in comp for d, m in nb(c, R))
            cost, order, mv, sw, tk = jlazy.best_order(comp, R, trials=int(E("JTR", "1500")))
            J, P = jlazy.geom(comp, R)
            ops.append({"k": "jf", "ci": i, "comp": comp, "cells": sorted(cs | ring, key=lambda c: self.pos[c]),
                        "order": order, "J": J, "P": P, "start": comp[order[0]]})
        # every edge must be covered by exactly one op
        for i, op in enumerate(ops):
            op["id"] = i
        self.ops = ops
        self.ops_of = {c: [] for c in R}
        for op in ops:
            for c in op["cells"]:
                self.ops_of[c].append(op["id"])
        cover = set()
        for op in ops:
            if op["k"] == "cas":
                cover.add(frozenset((op["lo"], op["hi"])))
            elif op["k"] == "fm":
                for d, m in nb(op["m"], R):
                    cover.add(frozenset((op["m"], m)))
            else:
                for c in op["comp"]:
                    for d, m in nb(c, R):
                        cover.add(frozenset((c, m)))
        edges = set(frozenset((c, m)) for c in R for d, m in nb(c, R))
        assert edges <= cover, len(edges - cover)
        self.mc_costs()

    def mc_costs(self, trials=int(E("MCT", "400"))):
        """Monte Carlo: per-op expected swaps and their variance, ops applied in snake order."""
        R, o = self.R, self.o
        rng = random.Random(7)
        ops = self.ops
        # order: cas in order of later cell, then fm/jf at their max position
        key = []
        for op in ops:
            key.append(max(self.pos[c] for c in op["cells"]))
        order = sorted(range(len(ops)), key=lambda i: key[i])
        s1 = [0.0] * len(ops)
        s2 = [0.0] * len(ops)
        tk1 = [0.0] * len(ops)
        for _ in range(trials):
            v = {c: rng.randrange(10) for c in R}
            for i in order:
                op = ops[i]
                sw, tk = self.apply(op, v)
                s1[i] += sw
                s2[i] += sw * sw
                tk1[i] += tk
        for i, op in enumerate(ops):
            m = s1[i] / trials
            op["sw"] = m
            op["var"] = max(0.0, s2[i] / trials - m * m)
            op["tk"] = tk1[i] / trials

    def apply(self, op, v):
        R = self.R
        if op["k"] == "cas":
            a, b = op["lo"], op["hi"]
            if v[a] > v[b]:
                v[a], v[b] = v[b], v[a]
                return 1, 6
            return 0, 6
        if op["k"] == "fm":
            c = op["m"]
            lo = [m for d, m in nb(c, R) if d not in UPD]
            up = [m for d, m in nb(c, R) if d in UPD]
            sw = 0
            tk = 0
            while True:
                tk += 6 + 5 * len(lo)
                bl = max(lo, key=lambda m: v[m])
                if v[bl] > v[c]:
                    v[bl], v[c] = v[c], v[bl]
                    sw += 1
                    continue
                tk += 5 * len(up)
                tu = min(up, key=lambda m: v[m])
                if v[tu] < v[c]:
                    v[tu], v[c] = v[c], v[tu]
                    sw += 1
                    continue
                break
            return sw, tk + 8
        # jf
        comp = op["comp"]
        cs = set(comp)
        lo = {c: [m for d, m in nb(c, R) if d not in UPD] for c in comp}
        up = {c: [m for d, m in nb(c, R) if d in UPD] for c in comp}
        work = [comp[i] for i in op["order"]]
        sw = 0
        tk = 0
        mv = 0
        pos = comp[op["order"][0]]
        while work:
            c = work.pop(0)
            mv += tdist(pos, c)
            pos = c
            while True:
                tk += 12 + 4 * (len(lo[c]) + len(up[c]))
                bl = max(lo[c], key=lambda m: v[m], default=None)
                if bl is not None and v[bl] > v[c]:
                    v[bl], v[c] = v[c], v[bl]
                    sw += 1
                    if bl in cs and bl not in work:
                        work.append(bl)
                    continue
                tu = min(up[c], key=lambda m: v[m], default=None)
                if tu is not None and v[tu] < v[c]:
                    v[tu], v[c] = v[c], v[tu]
                    sw += 1
                    if tu in cs and tu not in work:
                        work.append(tu)
                    continue
                break
        mv += tdist(pos, comp[op["order"][0]])
        return sw + mv, tk  # moves counted as actions too


KMUL = {"cas": float(E("KC", "1.0")), "fm": float(E("KF", "1.0")), "jf": float(E("KJ", "1.0"))}


def op_cost(op):
    return (op["tk"] + TA * op["sw"]) * KMUL[op["k"]]


def op_var(op):
    return (TA ** 2) * op["var"]


# ---------------------------------------------------------------------------------------------
class Plan:
    """chunks: list of (p, q, d) over the snake; d=0 walks p..q-1, d=1 walks q-1..p."""

    def __init__(self, lay):
        self.lay = lay
        n = lay.n
        o = lay.o
        # snake position of the chunk owning each op cell is decided per plan
        # cut classification: for cut q (between q-1 and q) the ops that straddle it if the
        # chunks are [.., q) and [q, ..): ops with cells on both sides within a window
        self.cross = {}
        W = 40
        for q in range(1, n):
            xs = []
            for op in lay.ops:
                ps = [lay.pos[c] for c in op["cells"]]
                if max(ps) - min(ps) > n // 2:
                    continue   # wraps the rotated snake's ends: handled as the wrap cut
                if min(ps) < q <= max(ps):
                    xs.append(op["id"])
            self.cross[q] = xs
        self.cut_ff = [False] * (n + 1)   # allowed as F|F / R|R
        self.cut_clean = [False] * (n + 1)  # allowed as R|F / F|R
        for q in range(1, n):
            xs = [lay.ops[i] for i in self.cross[q]]
            # no op may span more than 12 snake positions across a cut (keeps cross work local)
            if any(max(lay.pos[c] for c in op["cells"]) - min(lay.pos[c] for c in op["cells"]) > 12 for op in xs):
                continue
            self.cut_ff[q] = True
            if len(xs) == 1 and xs[0]["k"] == "cas":
                a, b = xs[0]["cells"]
                pa, pb = sorted((lay.pos[a], lay.pos[b]))
                if pa == q - 1 and pb == q:
                    # the shared cells' other ops must be CAS (inline-able)
                    ok = True
                    for c in (o[q - 1], o[q]):
                        for oid in lay.ops_of[c]:
                            if lay.ops[oid]["k"] != "cas":
                                ok = False
                    if ok:
                        self.cut_clean[q] = True
        self.cut_ff[0] = self.cut_ff[n] = True
        self.cut_clean[0] = self.cut_clean[n] = True
        print("cuts ff", sum(self.cut_ff), "clean", sum(self.cut_clean), file=sys.stderr)


def walk_of(p, q, d):
    return list(range(p, q)) if d == 0 else list(range(q - 1, p - 1, -1))


def start_of(lay, ch):
    p, q, d = ch
    return lay.o[p] if d == 0 else lay.o[q - 1]


def end_of(lay, ch):
    p, q, d = ch
    return lay.o[q - 1] if d == 0 else lay.o[p]


