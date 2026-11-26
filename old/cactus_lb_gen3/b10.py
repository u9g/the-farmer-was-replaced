# Full-deferral generator: deterministic forward passes, fixes in a back-walk during growth.
#   python b9.py out.py
import os, random, sys
from lay import build, nb, UPD, tdist, mdist, N
from evalb_lib import dp_walls
from build_entry import path_moves, spawn_plan, Dr, lit, pidx, DV

ND = 32
DN = ["North", "East", "South", "West"]
OPP = [2, 3, 0, 1]
E = os.environ.get
GROW_T = 6075.0
TK = {"move": 1, "till": 1, "plant": 1, "fp": 6, "fm": 40, "sf": 40, "swap": 2}


def has_up(c, R):
    return any(d in UPD for d, _ in nb(c, R))


def has_dn(c, R):
    return any(d not in UPD for d, _ in nb(c, R))


class Gen:
    def __init__(self, walls=None):
        self.KL = int(E("KL", "3"))
        if walls is not None:
            self.walls = list(walls)
        elif E("WALLS"):
            self.walls = [int(x) for x in E("WALLS").split(",")]
        elif E("WSPEC"):
            off, pos = E("WSPEC").split(":")
            pos = set(int(x) for x in pos.split(",") if x)
            ws = []
            d = int(off)
            i = 0
            while d <= 62:
                ws.append(d)
                d += (3 if i in pos else 2) + 1
                i += 1
            self.walls = ws
        else:
            self.walls = dp_walls(self.KL)
        self.R, self.o = build(self.walls)
        R, o = self.R, self.o
        self.NL = len(o)
        self.pos_of = {c: i for i, c in enumerate(o)}
        conn = [c for c in R if (c[0] + c[1]) in set(self.walls)]
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
        self.corrA = [0.0] * len(o)
        self.corrB = [0.0] * len(o)
        self.adj_ok = [True] + [mdist(o[q - 1], o[q]) == 1 for q in range(1, self.NL)] + [True]
        mids = set(c for c in R if has_up(c, R) and has_dn(c, R))
        self.complex = set(c for c in mids if any(m in mids for d, m in nb(c, R)))
        self.mid = mids - self.complex
        wallset = set(self.walls)
        self.cxG = {}     # G -> (lows, ups) for simple connector components
        self.cxB = set()  # b cells handled by their G
        self.cxC = {}     # c cell -> its pure top dirs
        for g in [c for c in self.complex if (c[0] + c[1]) in wallset]:
            lows = [(d, m) for d, m in nb(g, R) if d not in UPD]
            ups = [(d, m) for d, m in nb(g, R) if d in UPD]
            ok = True
            for d, b in lows:
                if any(dd in UPD and mm != g for dd, mm in nb(b, R)) or any(dd not in UPD and mm in mids for dd, mm in nb(b, R)):
                    ok = False
            for d, c in ups:
                if any(dd not in UPD and mm != g for dd, mm in nb(c, R)) or any(dd in UPD and mm in mids for dd, mm in nb(c, R)):
                    ok = False
            if ok and E("USECX") == "1":
                self.cxG[g] = (lows, ups)
                for d, b in lows:
                    self.cxB.add(b)
                for d, c in ups:
                    self.cxC[c] = [dd for dd, mm in nb(c, R) if dd in UPD]
        # complex components -> cc
        self.comp_of = {}
        self.comps = []
        for c0 in self.complex:
            if c0 in self.comp_of or c0 in self.cxG or c0 in self.cxB or c0 in self.cxC:
                continue
            comp = [c0]
            self.comp_of[c0] = len(self.comps)
            stk = [c0]
            while stk:
                x = stk.pop()
                for d, m in nb(x, R):
                    if m in self.complex and m not in self.comp_of:
                        self.comp_of[m] = len(self.comps)
                        comp.append(m)
                        stk.append(m)
            self.comps.append(comp)
        # forbid cuts inside the path interval of each component's 2-ring
        for comp in self.comps + [[g] + [m for d, m in nb(g, R)] for g in self.cxG]:
            reg = set(comp)
            for _ in range(2):
                reg |= set(m for c in list(reg) for d, m in nb(c, R))
            idxs = sorted(self.pos_of[c] for c in reg)
            lo, hi = idxs[0], idxs[-1]
            if hi - lo < 60:
                for q in range(lo + 1, hi + 1):
                    self.adj_ok[q] = False
        # forbid cuts near complex cells
        for q in range(1, self.NL):
            a, b2 = o[q - 1], o[q]
            for c in (a, b2):
                if c in self.complex or any(m in self.complex for d, m in nb(c, R)):
                    self.adj_ok[q] = False
        self.ring1 = {}
        if E("RELAX") == "2":
            # junction owner fixes every edge touching its 1-ring; cuts only forbidden inside
            # the path interval of 1-ring + mids of the 2-ring
            self.adj_ok = [True] + [mdist(o[q - 1], o[q]) == 1 for q in range(1, self.NL)] + [True]
            for ci, comp in enumerate(self.comps):
                r1 = set(comp)
                r1 |= set(m for c in comp for d, m in nb(c, R))
                for x in r1:
                    self.ring1.setdefault(x, set()).add(ci)
                reg = set(r1)
                r2 = set(m for c in r1 for d, m in nb(c, R)) - r1
                reg |= set(x for x in r2 if x in self.mid or x in self.complex)
                idxs = sorted(self.pos_of[c] for c in reg)
                lo, hi = idxs[0], idxs[-1]
                if hi - lo < 60:
                    for q in range(lo + 1, hi + 1):
                        self.adj_ok[q] = False
                else:
                    print("WARN wide ring", ci, file=sys.stderr)
        if E("RELAX") == "1":
            # only forbid cuts inside the path interval of each component's 1-ring
            self.adj_ok = [True] + [mdist(o[q - 1], o[q]) == 1 for q in range(1, self.NL)] + [True]
            for comp in self.comps:
                reg = set(comp)
                reg |= set(m for c in list(reg) for d, m in nb(c, R))
                idxs = sorted(self.pos_of[c] for c in reg)
                lo, hi = idxs[0], idxs[-1]
                if hi - lo < 60:
                    for q in range(lo + 1, hi + 1):
                        self.adj_ok[q] = False
            for c in (self.mid if E("RELAXMID") == "1" else []):
                reg = set([c]) | set(m for d, m in nb(c, R))
                idxs = sorted(self.pos_of[x] for x in reg)
                if idxs[-1] - idxs[0] < 12:
                    for q in range(idxs[0] + 1, idxs[-1] + 1):
                        self.adj_ok[q] = False
        print("L", self.NL, "complex", len(self.complex), "mid", len(self.mid), file=sys.stderr)

    # ---- ops
    def is_pure2(self, c):
        return c not in self.mid and c not in self.complex and not self.in3(c)

    def in3(self, c):
        # pure b/t cell of a 3-wide strip: all its neighbours are mids
        R = self.R
        return any(m in self.mid for d, m in nb(c, R))

    def cross_ok(self, c, m, own_k):
        """may the drone owning c (chunk own_k) fix the cross-chunk edge (c, m)?"""
        wp = getattr(self, "walkpos", None)
        if wp is None:
            return True
        kc, tc, nc = wp[c]
        km, tm, nm = wp[m]
        if self.ring1:
            rc = self.ring1.get(c)
            rm = self.ring1.get(m)
            if rc and not rm:
                return True
            if rm and not rc:
                return False
        ce = tc == nc - 1
        me = tm == nm - 1
        if ce and not me:
            return True
        if me and not ce:
            return False
        return kc < km

    def items_of(self, cells):
        """forced fix items in a chunk: list of dict(cells=[t...], first, last, kind, key)"""
        o, R = self.o, self.R
        idx = {o[i]: t for t, i in enumerate(cells)}
        out = []
        seen = set()
        for t, i in enumerate(cells):
            c = o[i]
            if c in self.comp_of:
                if E("INLCC", "1") == "0":
                    continue
                key = ("cc", self.comp_of[c])
                if key in seen:
                    continue
                seen.add(key)
                cs = self.comps[self.comp_of[c]]
            elif c in self.mid and E("INLFM", "1") == "1":
                key = ("fm", c)
                cs = [c]
            else:
                continue
            ring = set(cs)
            for x in cs:
                for d, m in nb(x, R):
                    ring.add(m)
            if any(x not in idx for x in ring):
                last = 10 ** 9
            else:
                last = max(idx[x] for x in ring)
            ts = [idx[x] for x in cs if x in idx]
            out.append({"key": key, "cs": cs, "first": min(ts), "last": last})
        return out

    def phase_ops(self, cells, till, start_pos, K=None):
        o, R = self.o, self.R
        n = len(cells)
        if K is None:
            K = n
        own = set(o[i] for i in cells)
        idx = {o[i]: t for t, i in enumerate(cells)}
        ops = []
        cur = start_pos
        inline = set()
        INL = E("INL") == "1"
        items = self.items_of(cells) if INL else []
        for t, i in enumerate(cells):
            c = o[i]
            for mm in path_moves(cur, c):
                ops.append(("move", int(mm)))
            cur = c
            if till:
                ops.append(("till",))
            ops.append(("plant",))
            if t < n - K and self.is_pure2(c) and not (self.ring1 and c in self.ring1 and any(m not in own for d, m in nb(c, R))):
                inline.add(c)
                for d, m in nb(c, R):
                    if m in self.mid or m in self.complex:
                        continue
                    if (m in own and idx[m] < t) or (m not in own and self.cross_ok(c, m, None)):
                        ops.append(("fp", d, d in UPD, m not in own))
            if INL:
                for it in items:
                    if it["last"] == t and t < n - K:
                        for x in it["cs"]:
                            inline.add(x)
                        if it["key"][0] == "cc":
                            ci = it["key"][1]
                            ops.append(("cc", ci, c, self.cc_data(ci, c)))
                        else:
                            mcell = it["cs"][0]
                            for mm in path_moves(c, mcell):
                                ops.append(("move", int(mm)))
                            B = [d for d, m in nb(mcell, R) if d not in UPD]
                            T = [d for d, m in nb(mcell, R) if d in UPD]
                            ops.append(("fm", B, T))
                            for mm in path_moves(mcell, c):
                                ops.append(("move", int(mm)))
        ops.append(("LP",))
        # back-walk
        gt = set()
        border = [cells[t] for t in range(len(cells) - 1, -1, -1)]
        bpos = {o[i]: r for r, i in enumerate(border)}
        handled = set()
        for r, i in enumerate(border):
            c = o[i]
            fx = []
            if c in handled or c in inline:
                continue
            if c in self.cxG:
                lows, ups = self.cxG[c]
                BS = []
                for d, b in lows:
                    pre = (b not in bpos) or bpos[b] > r
                    BS.append((d, [dd for dd, mm in nb(b, R) if dd not in UPD], OPP[d], pre))
                    if pre:
                        handled.add(b)
                CS = []
                for d, cc in ups:
                    pre = (cc not in bpos) or bpos[cc] > r
                    CS.append((d, self.cxC[cc], OPP[d], pre))
                    if pre:
                        handled.add(cc)
                fx.append(("cx", BS, CS))
            elif c in self.cxB:
                fx.append(("fm", [dd for dd, mm in nb(c, R) if dd not in UPD], []))
            elif c in self.cxC:
                fx.append(("fm", [], self.cxC[c]))
            elif c in self.comp_of:
                ci = self.comp_of[c]
                if ("cc", ci) in handled:
                    continue
                handled.add(("cc", ci))
                fx.append(("cc", ci, c, self.cc_data(ci, c)))
            elif c in self.mid:
                B = [d for d, m in nb(c, R) if d not in UPD]
                T = [d for d, m in nb(c, R) if d in UPD]
                fx.append(("fm", B, T))
            elif self.in3(c) and E("FMF") == "1":
                for d, m in nb(c, R):
                    if m in self.mid and m not in own:
                        B = [dd for dd, mm in nb(m, R) if dd not in UPD]
                        T = [dd for dd, mm in nb(m, R) if dd in UPD]
                        fx.append(("fmf", d, B, T, OPP[d]))
            else:
                for d, m in nb(c, R):
                    if m in self.mid or m in self.complex:
                        continue
                    if (m in own and (bpos[m] < r or m in inline)) or (m not in own and self.cross_ok(c, m, None)):
                        fx.append(("fp", d, d in UPD, m not in own))
            if not fx:
                continue
            for mm in path_moves(cur, c):
                ops.append(("move", int(mm)))
            cur = c
            ops += fx
        # GT closure
        GT = {}
        fr = set(gt)
        seen = set(gt)
        for depth in range(int(E("TDEPTH", "4"))):
            nf = set()
            for c in fr:
                L = []
                for d, m in nb(c, R):
                    up = d in UPD
                    casc = has_up(m, R) if up else has_dn(m, R)
                    L += [d, 1 if up else 0, 1 if casc else 0, OPP[d], pidx(m)]
                    if casc and m not in seen:
                        seen.add(m)
                        nf.add(m)
                GT[pidx(c)] = L
            fr = nf
        return ops, cur, GT

    # ---- cost (actions) of a phase (deterministic part) and expected back
    def costs(self, cells, till, start_pos):
        ops, cur, GT = self.phase_ops(cells, till, start_pos)
        f = 0.0
        b = 0.0
        inb = False
        for op in ops:
            k = op[0]
            if k == "LP":
                inb = True
                continue
            if k in ("move", "till", "plant"):
                x = 200 + TK[k]
            elif k == "fp":
                x = float(E("CFP", "75"))
            elif k == "fm":
                x = float(E("CFM", "330"))
            elif k == "sf":
                x = float(E("CSF", "1300"))
            elif k == "cx":
                x = float(E("CCX", "3900"))
            else:
                x = 0
            if inb:
                b += x
            else:
                f += x
        return f, b, cur

    def bcells(self, b0, b1):
        if b1 > b0:
            return list(range(b0, b1))
        return list(range(b0, self.NL)) + list(range(0, b1))

    def percell(self):
        o, R = self.o, self.R
        NL = self.NL
        C = {"fp": float(E("CFP", "75")), "fpi": float(E("CFPI", "95")), "fm": float(E("CFM", "330")),
             "sf": float(E("CSF", "1300")), "cx": float(E("CCX", "3900"))}
        self.kind = []
        self.fix = []
        self.fvar = []
        self.fixB_over = {}
        csz = {}
        for comp in getattr(self, "comps", []):
            for c in comp:
                csz[c] = len(comp)
        for i, c in enumerate(o):
            if c in self.cxG:
                k, f, v = "cx", C["cx"], 1000.0 ** 2
            elif c in self.cxB or c in self.cxC or c in self.mid:
                k, f, v = "fm", C["fm"], 200.0 ** 2
            elif c in self.complex:
                n = csz.get(c, 4)
                tot = {4: 4400, 7: 9000, 8: 11600}.get(n, 1400 * n) if not E("CCFLAT") else float(E("CCFLAT")) * n
                if E("CCA"):
                    tot = float(E("CCA")) * n - float(E("CCB", "0"))
                k, f, v = "sf", tot / n, (2000.0 ** 2) / n
                self.fixB_over[i] = tot / n if not E("CCFLATB") else float(E("CCFLATB"))
            elif self.in3(c):
                k, f, v = "in3", 0.0, 0.0
            else:
                k, f, v = "p2", C["fp"], 90.0 ** 2
            self.kind.append(k)
            self.fix.append(f)
            self.fvar.append(v)
        self.CFPI = C["fpi"]
        self.step = [201 * tdist(o[i - 1], o[i]) for i in range(NL)]  # step into i from i-1 (cyclic)

    def chunk_cost(self, cells, till, G):
        """cells: global indices in walk order. returns (forward, inline, back, K)"""
        n = len(cells)
        f = 0.0
        corr = self.corrA if till else self.corrB
        for i in cells:
            f += corr[i]
        stp = [0.0] * n
        for t in range(n):
            i = cells[t]
            f += (402 if till else 201) + 3
            if t > 0:
                j = cells[t - 1]
                s = 201 * tdist(self.o[j], self.o[i])
                stp[t] = s
                f += s
        forced = [t for t in range(n) if self.kind[cells[t]] in ("cx", "fm", "sf")]
        if self.ring1:
            cset = set(cells)
            pi_ = self.pos_of
            for t in range(n):
                c = self.o[cells[t]]
                if c in self.ring1 and any(pi_[m] not in cset for d, m in nb(c, self.R)):
                    forced.append(t)
        e0 = min(forced) if forced else n
        # back cost if deferring everything from index e (walk back from n-1 to e)
        # fixed part from forced cells
        inl_total = sum(self.CFPI for t in range(n) if self.kind[cells[t]] == "p2")
        best = None
        back = 0.0
        inl = inl_total
        # K = number of trailing cells deferred; iterate e = n-1 down to 0
        bk = 0.0
        bv = 0.0
        Z = float(E("ZB", "1.5"))
        ZBX = float(E("ZBB", E("ZB", "0.5"))) if not till else Z
        lastpos = self.o[cells[n - 1]]
        exact = E("BEXACT") == "1"
        INL = E("INL") == "1"
        e0cc = n
        if INL and (E("INLCC", "1") == "0" or E("INLFM", "1") == "0"):
            kk = []
            if E("INLCC", "1") == "0":
                kk += ["cx", "sf"]
            if E("INLFM", "1") == "0":
                kk += ["fm"]
            fc = [t for t in range(n) if self.kind[cells[t]] in kk]
            e0cc = min(fc) if fc else n
        if INL:
            items = self.items_of(cells)
            icost = []
            pi = {c: i for i, c in enumerate(self.o)}
            for it in items:
                cst = 0.0
                for x in it["cs"]:
                    i = pi[x]
                    cst += self.fixB_over[i] if (not till and i in self.fixB_over) else self.fix[i]
                if it["key"][0] == "fm" and it["last"] < 10 ** 8 and cells[it["last"]] != pi[it["cs"][0]]:
                    cst += 2 * 201 * tdist(self.o[cells[it["last"]]], it["cs"][0])
                icost.append(cst)
        for K in range(0, n + 1):
            e = n - K
            if K > 0:
                t = e
                i = cells[t]
                if not till and i in self.fixB_over:
                    bk += self.fixB_over[i]
                else:
                    bk += self.fix[i] if self.kind[i] != "in3" else 0.0
                bv += self.fvar[i]
                if self.kind[i] == "p2":
                    inl -= self.CFPI
                if exact:
                    if self.kind[i] != "in3":
                        bk += 201 * tdist(lastpos, self.o[i])
                        lastpos = self.o[i]
                elif t < n - 1:
                    bk += stp[t + 1]
            if INL:
                ok = e <= e0cc
                iadd = 0.0
                for it, ic in zip(items, icost):
                    if it["last"] < e:
                        iadd += ic
                    elif it["first"] < e:
                        ok = False
                        break
                if not ok:
                    continue
                total = f + inl + iadd + max(G, bk + ZBX * bv ** 0.5)
                if best is None or total < best[0] - 1e-9:
                    best = (total, f, inl + iadd, bk, K)
                continue
            if K < n - e0:
                continue
            total = f + inl + max(G, bk + ZBX * bv ** 0.5)
            if best is None or total < best[0] - 1e-9:
                best = (total, f, inl, bk, K)
        return best

    def plan(self):
        if E("BMODE") == "4":
            return self.plan4()
        o = self.o
        NL = self.NL
        self.percell()
        BOOT = float(E("BOOT", "200"))
        DEPTH = float(E("DEPTH", "5"))
        LMAX = int(E("LMAX", "40"))
        G = GROW_T + 30
        sc = lambda s: 200 * (tdist((0, 0), s) + DEPTH)
        segA = {}
        for p in range(NL):
            for q in range(p + 4, min(NL, p + LMAX) + 1):
                if not (self.adj_ok[p] and self.adj_ok[q]):
                    continue
                fw = self.chunk_cost(list(range(p, q)), True, G)
                bw = self.chunk_cost(list(range(q - 1, p - 1, -1)), True, G)
                c0 = sc(o[p]) + fw[0]
                c1 = sc(o[q - 1]) + bw[0]
                segA[(p, q, 0)] = (c0, 0, fw[4])
                if E("AFWD") != "1":
                    segA[(p, q, 1)] = (c1, 1, bw[4])

        def feas(T):
            INF = 10 ** 9
            # state (q, d): d = direction of the chunk ending at q (0 fwd ends at q-1 side, 1 bwd starts at q-1)
            reach = {(0, 1): 0}
            prev = {}
            for p in range(NL):
                for dp_ in (0, 1):
                    if (p, dp_) not in reach:
                        continue
                    r = reach[(p, dp_)]
                    for q in range(p + 4, min(NL, p + LMAX) + 1):
                        for d in (0, 1):
                            if dp_ == 0 and d == 1 and E("FACE") != "1":
                                continue  # facing at cut p
                            v = segA.get((p, q, d))
                            if v is None or BOOT + v[0] > T:
                                continue
                            if r + 1 < reach.get((q, d), INF):
                                reach[(q, d)] = r + 1
                                prev[(q, d)] = (p, dp_)
            ends = [(reach[(NL, d)], d) for d in (0, 1) if (NL, d) in reach]
            if not ends or min(ends)[0] > ND:
                return None
            d = min(ends)[1]
            ch = []
            q = NL
            while q > 0:
                p, dp_ = prev[(q, d)]
                ch.append((p, q, d))
                q, d = p, dp_
            return ch[::-1]

        lo, hi = 0.0, 200000.0
        for _ in range(30):
            T = (lo + hi) / 2
            if feas(T) is not None:
                hi = T
            else:
                lo = T
        ch3 = feas(hi)
        while len(ch3) < ND:
            k = max(range(len(ch3)), key=lambda i: ch3[i][1] - ch3[i][0])
            p, q, d = ch3[k]
            m = (p + q) // 2
            while not self.adj_ok[m]:
                m += 1
            ch3[k:k + 1] = [(p, m, d), (m, q, d)]
        ch = [(p, q) for p, q, d in ch3]
        dirs = [d for p, q, d in ch3]
        self.KA = [segA[(p, q, d)][2] for p, q, d in ch3]
        starts = [o[p] if d == 0 else o[q - 1] for (p, q), d in zip(ch, dirs)]
        offs_, plans = spawn_plan(tuple(starts), (0, 0))
        self.chA, self.dirA, self.offs, self.plans, self.TA = ch, dirs, list(offs_), plans, hi
        self.cellsA = [list(range(p, q)) if d == 0 else list(range(q - 1, p - 1, -1)) for (p, q), d in zip(ch, dirs)]
        tA = [BOOT + self.offs[k] * 200 + segA[ch3[k]][0] - sc(starts[k]) for k in range(ND)]
        self.slackA = []
        for k in range(ND):
            r = self.chunk_cost(self.cellsA[k], True, G)
            t1 = BOOT + self.offs[k] * 200 + r[1] + r[2] + r[3]
            self.slackA.append(max(0.0, hi - t1 - float(E("PMARG", "800"))))
        print("KA", self.KA, file=sys.stderr)
        print("A plan T %.0f actual-off max %.0f avg off %.1f" % (hi, max(tA), sum(self.offs) / ND), file=sys.stderr)
        # ---- B: consecutive chunks, chunk k to drone k, direction choice, travel from A start
        apos = starts
        W = int(E("BWIN", "16"))

        bmemo = {}

        def bcost(k, p, q):
            key = (k, p, q)
            if key in bmemo:
                return bmemo[key]
            cl = [x % NL for x in range(p, q)]
            fw = self.chunk_cost(cl, False, G)
            bw = self.chunk_cost(cl[::-1], False, G)
            t0 = tdist(apos[k], o[p % NL]) * 200 + fw[0]
            t1 = tdist(apos[k], o[(q - 1) % NL]) * 200 + bw[0]
            r = ((t0, 0, fw[4]), (t1, 1, bw[4]))
            bmemo[key] = r
            return r

        # B boundaries b_0..b_31 (b_32 = b_0 + NL); candidates near A boundaries
        # drone k ends A at its tail start (walk index n-K)
        endidx = []
        for k in range(ND):
            p, q = ch[k]
            n = q - p
            K = self.KA[k]
            wl = list(range(p, q)) if dirs[k] == 0 else list(range(q - 1, p - 1, -1))
            endidx.append(wl[n - K] if K > 0 else wl[n - 1])
        apos = [o[e] for e in endidx]
        cen = endidx if E("BCEN") == "1" else [ch[k][0] for k in range(ND)]
        cand = [sorted(set(x for x in range(cen[k] - W, cen[k] + W + 1) if self.adj_ok[x % NL])) for k in range(ND)]
        if E("BCEN") == "1":
            # keep candidates increasing in k
            for k in range(1, ND):
                lo_ = min(cand[k - 1]) + 1
                cand[k] = [x for x in cand[k] if x >= lo_] or cand[k]
        best = None
        best = None
        for b0 in cand[0]:
            for d0 in (0, 1):
                # f[(b, d)] : max cost so far, chunk ending at b has direction d
                f = {}
                hist = []
                # chunk 0 from b0
                g = {}
                for b in cand[1]:
                    if b - b0 < 4 or b - b0 > LMAX:
                        continue
                    c = bcost(0, b0, b)[d0][0]
                    g[(b, d0)] = (c, None)
                hist.append(g)
                f = g
                for k in range(2, ND + 1):
                    g = {}
                    cs = cand[k] if k < ND else [b0 + NL]
                    for b in cs:
                        for d in (0, 1):
                            if k == ND and d == 0 and d0 == 1 and E("FACE") != "1":
                                continue  # chunk 31 fwd ends at b0+NL, chunk 0 bwd ends at b0: facing
                            bv = None
                            for (bp, dp_), (v, _) in f.items():
                                if b - bp < 4 or b - bp > LMAX:
                                    continue
                                if dp_ == 0 and d == 1 and E("FACE") != "1":
                                    continue
                                c = max(v, bcost(k - 1, bp, b)[d][0])
                                if bv is None or c < bv[0]:
                                    bv = (c, (bp, dp_))
                            if bv is not None:
                                g[(b, d)] = bv
                    hist.append(g)
                    f = g
                for (b, d), (v, _) in f.items():
                    if best is None or v < best[0]:
                        best = (v, b0, d0, d, hist)
        TB, b0, d0, dl, hist = best
        bs = [0] * (ND + 1)
        ds = [0] * ND
        bs[ND] = b0 + NL
        ds[ND - 1] = dl
        key = (b0 + NL, dl)
        for k in range(ND, 1, -1):
            pb = hist[k - 1][key][1]
            bs[k - 1] = pb[0]
            ds[k - 2] = pb[1]
            key = pb
        bs[0] = b0
        ds[0] = d0
        self.TB = TB
        self.cellsB = []
        self.KB = []
        for k in range(ND):
            p, q = bs[k], bs[k + 1]
            r = bcost(k, p, q)[ds[k]]
            cl = [x % NL for x in range(p, q)]
            self.cellsB.append(cl if r[1] == 0 else cl[::-1])
            self.KB.append(r[2])
        self.bch = self.cellsB
        if E("BSA") == "1":
            self.plan_bsa(apos, G, LMAX)
            TB = self.TB
        self.gB = None
        if E("WALLSB"):
            gB = Gen(walls=[int(x) for x in E("WALLSB").split(",")])
            gB.percell()
            gB.slackA = self.slackA
            gB.plan_b2(apos, G, LMAX)
            self.gB = gB
            self.TB = TB = gB.TB
        elif E("BMODE") == "2":
            self.plan_b2(apos, G, LMAX)
            TB = self.TB
        if E("BMODE") == "3":
            self.plan_b3(ch, G)
            TB = self.TB
        if E("BMODE") == "5":
            self.plan_b5(ch, dirs, G)
            TB = self.TB
        print("plan TA %.0f TB %.0f est %.3f s" % (max(tA), TB, (max(tA) + TB + 600) / 6075.0), file=sys.stderr)

    def chain_a_cost(self, p, q, t, G):
        """A chunk [p,q) forward with deferred tail [t,q) (K = q - t)."""
        cl = list(range(p, q))
        n = q - p
        K = q - t
        f = 0.0
        corr = self.corrA
        stp = [0.0] * n
        for j in range(n):
            i = cl[j]
            f += corr[i] + 405
            if j > 0:
                stp[j] = 201 * tdist(self.o[cl[j - 1]], self.o[i])
                f += stp[j]
        inl = sum(self.CFPI for j in range(n - K) if self.kind[cl[j]] == "p2")
        bk = 0.0
        bv = 0.0
        forced = [j for j in range(n) if self.kind[cl[j]] in ("cx", "fm", "sf")]
        e0 = min(forced) if forced else n
        if n - K > e0:
            return None
        for j in range(n - K, n):
            i = cl[j]
            bk += self.fix[i] if self.kind[i] != "in3" else 0.0
            bv += self.fvar[i]
            if j < n - 1:
                bk += stp[j + 1]
        Z = float(E("ZB", "0.5"))
        return f + inl + max(G, bk + Z * bv ** 0.5), K

    def chain_a_cost_cells(self, cl, K, G):
        n = len(cl)
        f = 0.0
        stp = [0.0] * n
        for j in range(n):
            i = cl[j]
            f += self.corrA[i] + 405
            if j > 0:
                stp[j] = 201 * tdist(self.o[cl[j - 1]], self.o[i])
                f += stp[j]
        forced = [j for j in range(n) if self.kind[cl[j]] in ("cx", "fm", "sf")]
        e0 = min(forced) if forced else n
        if n - K > e0:
            return None
        inl = sum(self.CFPI for j in range(n - K) if self.kind[cl[j]] == "p2")
        bk = 0.0
        bv = 0.0
        for j in range(n - K, n):
            i = cl[j]
            bk += self.fix[i] if self.kind[i] != "in3" else 0.0
            bv += self.fvar[i]
            if j < n - 1:
                bk += stp[j + 1]
        Z = float(E("ZB", "0.5"))
        return f + inl + max(G, bk + Z * bv ** 0.5)

    def plan_b5(self, ch, dirs, G):
        o = self.o
        NL = self.NL
        BOOT = float(E("BOOT", "200"))
        Acand = []
        for k, ((p, q), d) in enumerate(zip(ch, dirs)):
            cl = list(range(p, q)) if d == 0 else list(range(q - 1, p - 1, -1))
            n = len(cl)
            opts = {}
            for K in range(1, n + 1):
                e = cl[n - K]  # drone ends at walk index n-K
                # B chunk boundary at e must be an allowed cut
                if not self.adj_ok[e]:
                    continue
                r = self.chain_a_cost_cells(cl, K, G)
                if r is None:
                    continue
                opts[e] = (BOOT + self.offs[k] * 200 + r, K)
            if not opts:
                opts[cl[0]] = (BOOT + self.offs[k] * 200 + self.chain_a_cost_cells(cl, n, G), n)
            Acand.append(opts)
        TAmin = max(min(v[0] for v in a.values()) for a in Acand)
        slack = float(E("ASLACK", "600"))
        allowed = [[e for e, v in Acand[k].items() if v[0] <= TAmin + slack] for k in range(len(ch))]
        bmemo = {}

        def bcost(t0, t1):
            key = (t0, t1)
            if key not in bmemo:
                cl = [x % NL for x in range(t0, t1 if t1 > t0 else t1 + NL)]
                bmemo[key] = self.chunk_cost(cl, False, G) if len(cl) >= 2 else (1e9, 0, 0, 0, 0)
            return bmemo[key]
        ND_ = len(ch)
        best = None
        for t0 in allowed[0]:
            f = {t0: (0.0, None)}
            hist = []
            for k in range(1, ND_):
                g = {}
                for t in allowed[k]:
                    bv = None
                    for tp, (v, _) in f.items():
                        if (t - tp) % NL < 2:
                            continue
                        c = max(v, bcost(tp, t)[0])
                        if bv is None or c < bv[0]:
                            bv = (c, tp)
                    if bv is not None:
                        g[t] = bv
                hist.append(g)
                f = g
            for t, (v, _) in f.items():
                c = max(v, bcost(t, t0)[0])
                if best is None or c < best[0]:
                    best = (c, t0, t, hist)
        TB, t0, tl, hist = best
        ts = [0] * ND_
        ts[ND_ - 1] = tl
        for k in range(ND_ - 1, 0, -1):
            ts[k - 1] = hist[k - 1][ts[k]][1]
        ts[0] = t0
        self.KA = [Acand[k][ts[k]][1] for k in range(ND_)]
        self.cellsB = []
        self.KB = []
        for k in range(ND_):
            t1 = ts[(k + 1) % ND_]
            cl = [x % NL for x in range(ts[k], t1 if t1 > ts[k] else t1 + NL)]
            self.cellsB.append(cl)
            self.KB.append(bcost(ts[k], t1)[4])
        self.bch = self.cellsB
        self.TB = TB
        TA = max(Acand[k][ts[k]][0] for k in range(ND_))
        print("B5: TAmin %.0f TA %.0f TB %.0f" % (TAmin, TA, TB), file=sys.stderr)

    def plan_b3(self, ch, G):
        """B chunks chained: B chunk k = [t_k, t_{k+1}) where t_k is drone k's A tail start."""
        o = self.o
        NL = self.NL
        BOOT = float(E("BOOT", "200"))
        # A costs per candidate t
        Acand = []
        for k, (p, q) in enumerate(ch):
            opts = {}
            for t in range(p, q):
                if t > p and not self.adj_ok[t]:
                    continue
                r = self.chain_a_cost(p, q, t, G)
                if r is None:
                    continue
                opts[t] = BOOT + self.offs[k] * 200 + r[0]
            Acand.append(opts)
        TAmin = max(min(v.values()) for v in Acand)
        slack = float(E("ASLACK", "600"))
        allowed = [[t for t, v in Acand[k].items() if v <= TAmin + slack] for k in range(len(ch))]
        bmemo = {}

        def bcost(t0, t1):
            key = (t0, t1)
            if key not in bmemo:
                cl = [x % NL for x in range(t0, t1 if t1 > t0 else t1 + NL)]
                bmemo[key] = self.chunk_cost(cl, False, G)
            return bmemo[key]
        best = None
        ND_ = len(ch)
        for t0 in allowed[0]:
            f = {t0: (0.0, None)}
            hist = []
            for k in range(1, ND_):
                g = {}
                for t in allowed[k]:
                    bv = None
                    for tp, (v, _) in f.items():
                        c = max(v, bcost(tp, t)[0])
                        if bv is None or c < bv[0]:
                            bv = (c, tp)
                    if bv is not None:
                        g[t] = bv
                hist.append(g)
                f = g
            for t, (v, _) in f.items():
                c = max(v, bcost(t, t0)[0])
                if best is None or c < best[0]:
                    best = (c, t0, t, hist)
        TB, t0, tl, hist = best
        ts = [0] * ND_
        ts[ND_ - 1] = tl
        for k in range(ND_ - 1, 0, -1):
            ts[k - 1] = hist[k - 1][ts[k]][1]
        ts[0] = t0
        self.KA = [q - ts[k] for k, (p, q) in enumerate(ch)]
        self.cellsB = []
        self.KB = []
        for k in range(ND_):
            t1 = ts[(k + 1) % ND_]
            cl = [x % NL for x in range(ts[k], t1 if t1 > ts[k] else t1 + NL)]
            self.cellsB.append(cl)
            self.KB.append(bcost(ts[k], t1)[4])
        self.bch = self.cellsB
        self.TB = TB
        TA = max(Acand[k][ts[k]] for k in range(ND_))
        print("B3: TAmin %.0f TA %.0f TB %.0f" % (TAmin, TA, TB), file=sys.stderr)

    def plan4(self):
        """B chunks balanced first (all forward, cyclic); A chunks each contain one B start b_k and
        defer the tail [b_k, q_k) so the drone ends A where its B chunk starts."""
        o = self.o
        NL = self.NL
        self.percell()
        G = GROW_T + 30
        BOOT = float(E("BOOT", "200"))
        LMAX = int(E("LMAX", "40"))
        # ---- B split (cyclic, forward)
        bc = {}

        def bcost(t0, t1):
            key = (t0, t1)
            if key not in bc:
                cl = [x % NL for x in range(t0, t1)]
                bc[key] = self.chunk_cost(cl, False, G)
            return bc[key]

        def bsplit(T, b0):
            INF = 10 ** 9
            reach = {b0: 0}
            prev = {}
            for pos in range(b0, b0 + NL):
                if pos not in reach:
                    continue
                for L in range(4, LMAX + 1):
                    q = pos + L
                    if q > b0 + NL:
                        break
                    if q < b0 + NL and not self.adj_ok[q % NL]:
                        continue
                    if bcost(pos, q)[0] > T:
                        continue
                    if reach[pos] + 1 < reach.get(q, INF):
                        reach[q] = reach[pos] + 1
                        prev[q] = pos
            if reach.get(b0 + NL, INF) > ND:
                return None
            ch = []
            q = b0 + NL
            while q > b0:
                p = prev[q]
                ch.append(p)
                q = p
            return ch[::-1]

        b0s = [x for x in range(0, 30) if self.adj_ok[x]][:int(E("B0N", "6"))]
        lo, hi = 0.0, 40000.0
        bestb = None
        for _ in range(22):
            T = (lo + hi) / 2
            got = None
            for b0 in b0s:
                r = bsplit(T, b0)
                if r is not None:
                    got = r
                    break
            if got is not None:
                hi = T
                bestb = got
            else:
                lo = T
        bs = bestb
        while len(bs) < ND:
            # split longest
            ext = bs + [bs[0] + NL]
            k = max(range(len(bs)), key=lambda i: ext[i + 1] - ext[i])
            m = (ext[k] + ext[k + 1]) // 2
            while not self.adj_ok[m % NL]:
                m += 1
            bs.insert(k + 1, m)
        bs = sorted(x % NL for x in bs)
        self.TB = hi
        # ---- A DP: chunk k = [p_k, p_{k+1}) contains bs[k]; p_0 = 0, p_ND = NL
        # rotate so that bs[0] is the smallest >= 0 (already sorted); chunk k gets bs[k]
        offs = [12.0] * ND
        for it in range(4):
            def acost(k, p, q):
                t = bs[k]
                r = self.chain_a_cost(p, q, t, G) if p <= t < q else None
                if r is None:
                    return None
                return BOOT + offs[k] * 200 + r[0]

            # DP over k: state p_k in (bs[k-1], bs[k]]
            INF = 10 ** 18
            f = {0: 0.0}
            back = []
            for k in range(ND):
                g = {}
                nexts = [NL] if k == ND - 1 else [q for q in range(bs[k] + 1, bs[k + 1] + 1) if self.adj_ok[q]]
                for q in nexts:
                    bv = None
                    for p, v in f.items():
                        c = acost(k, p, q)
                        if c is None:
                            continue
                        c = max(v, c)
                        if bv is None or c < bv[0]:
                            bv = (c, p)
                    if bv is not None:
                        g[q] = bv
                back.append(g)
                f = {q: v[0] for q, v in g.items()}
            TA = f[NL]
            ps = [0] * (ND + 1)
            ps[ND] = NL
            for k in range(ND - 1, -1, -1):
                ps[k] = back[k][ps[k + 1]][1]
            ch = [(ps[k], ps[k + 1]) for k in range(ND)]
            starts = [o[p] for p, q in ch]
            offs_, plans = spawn_plan(tuple(starts), (0, 0))
            offs = list(offs_)
        self.chA, self.offs, self.plans, self.TA = ch, offs, plans, TA
        self.dirA = [0] * ND
        self.cellsA = [list(range(p, q)) for p, q in ch]
        self.KA = [q - bs[k] for k, (p, q) in enumerate(ch)]
        self.cellsB = []
        self.KB = []
        ext = bs + [bs[0] + NL]
        for k in range(ND):
            cl = [x % NL for x in range(ext[k], ext[k + 1])]
            self.cellsB.append(cl)
            self.KB.append(bcost(ext[k], ext[k + 1])[4])
        self.bch = self.cellsB
        print("plan4 TA %.0f TB %.0f est %.3f s; avg off %.1f" % (TA, self.TB, (TA + self.TB + 600) / 6075.0, sum(offs) / ND), file=sys.stderr)

    def plan_bsa(self, apos, G, LMAX):
        """simulated annealing over cyclic B boundaries, directions and drone assignment."""
        import math, random as rnd
        o = self.o
        NL = self.NL
        rng = rnd.Random(int(E("SASEED", "1")))
        # initial from current cellsB (chunk k -> drone k)
        bnd = []
        dirs = []
        for cl in self.cellsB:
            # chunk covers a cyclic interval; recover start index in path order
            if len(cl) > 1 and (cl[1] - cl[0]) % NL == 1:
                bnd.append(cl[0]); dirs.append(0)
            else:
                bnd.append(cl[-1]); dirs.append(1)
        order = sorted(range(32), key=lambda k: bnd[k])
        b = [bnd[k] for k in order]
        dd = [dirs[k] for k in order]
        asg = list(order)  # chunk j (in cyclic order) -> drone asg[j]
        memo = {}

        def ccost(p, q, d):
            key = (p, q, d)
            if key not in memo:
                cl = [x % NL for x in range(p, q)]
                if d == 1:
                    cl = cl[::-1]
                r = self.chunk_cost(cl, False, G)
                memo[key] = (r[0], o[cl[0]], r[4], cl)
            return memo[key]

        def chunk(j):
            p = b[j]
            q = b[(j + 1) % 32] + (NL if j == 31 else 0)
            return p, q

        def jcost(j):
            p, q = chunk(j)
            if q - p < 4 or q - p > LMAX:
                return 1e9
            c, st, K, cl = ccost(p, q, dd[j])
            return c + tdist(apos[asg[j]], st) * 200

        def valid_cut(x):
            return self.adj_ok[x % NL]

        def facing_ok():
            if E("FACE") == "1":
                return True
            for j in range(32):
                if dd[j] == 0 and dd[(j + 1) % 32] == 1:
                    return False
            return True
        costs = [jcost(j) for j in range(32)]
        cur = max(costs)
        best = (cur, list(b), list(dd), list(asg))
        T0 = float(E("SAT0", "800"))
        NIT = int(E("SAIT", "60000"))
        for it in range(NIT):
            temp = T0 * (1 - it / NIT) + 1
            mv = rng.random()
            saved = (list(b), list(dd), list(asg))
            if mv < 0.5:
                j = rng.randrange(32)
                delta = rng.choice([-3, -2, -1, 1, 2, 3])
                nb_ = b[j] + delta
                lo = b[j - 1] if j > 0 else b[31] - NL
                hi = b[j + 1] if j < 31 else b[0] + NL
                if not (lo + 4 <= nb_ <= hi - 4) or not valid_cut(nb_):
                    continue
                b[j] = nb_
                if j == 0:
                    pass
                if b[0] >= NL or b[0] < 0:
                    b[:] = saved[0]
                    continue
            elif mv < 0.8:
                j1, j2 = rng.randrange(32), rng.randrange(32)
                asg[j1], asg[j2] = asg[j2], asg[j1]
            else:
                j = rng.randrange(32)
                dd[j] = 1 - dd[j]
                if not facing_ok():
                    dd[j] = 1 - dd[j]
                    continue
            new = [jcost(j) for j in range(32)]
            nc = max(new)
            if nc <= cur or rng.random() < math.exp(-(nc - cur) / temp):
                cur = nc
                costs = new
                if nc < best[0]:
                    best = (nc, list(b), list(dd), list(asg))
            else:
                b[:], dd[:], asg[:] = saved
        cur, b, dd, asg = best
        cellsB = [None] * 32
        KB = [None] * 32
        for j in range(32):
            p, q = chunk(j)
            c, st, K, cl = ccost(p, q, dd[j])
            cellsB[asg[j]] = cl
            KB[asg[j]] = K
        self.cellsB = cellsB
        self.KB = KB
        self.bch = cellsB
        self.TB = cur
        print("BSA: TB %.0f" % cur, file=sys.stderr)

    def plan_b2(self, apos, G, LMAX):
        import numpy as np
        from scipy.optimize import linear_sum_assignment
        o = self.o
        NL = self.NL
        TRAV = float(E("TRAV0", "600"))
        segc = {}
        for p in range(NL):
            if not self.adj_ok[p]:
                continue
            for L in range(4, LMAX + 1):
                q = p + L
                if not self.adj_ok[q % NL] and q % NL != 0:
                    continue
                cl = [x % NL for x in range(p, q)]
                fw = self.chunk_cost(cl, False, G)
                bw = self.chunk_cost(cl[::-1], False, G)
                segc[(p, L)] = ((fw[0], fw[4]), (bw[0], bw[4]))
        b0s = [x for x in range(0, 60) if self.adj_ok[x]][:12]

        def feas(T, b0):
            INF = 10 ** 9
            reach = {(b0, 1): 0}
            prev = {}
            for pos in range(b0, b0 + NL):
                for dp_ in (0, 1):
                    if (pos, dp_) not in reach:
                        continue
                    r = reach[(pos, dp_)]
                    for L in range(4, LMAX + 1):
                        q = pos + L
                        if q > b0 + NL:
                            break
                        v = segc.get((pos % NL, L))
                        if v is None:
                            continue
                        for d in (0, 1):
                            if dp_ == 0 and d == 1 and E("BFACE") != "1":
                                continue
                            if q == b0 + NL and d == 0 and first_d[0] == 1:
                                pass
                            if v[d][0] + TRAV > T:
                                continue
                            if r + 1 < reach.get((q, d), INF):
                                reach[(q, d)] = r + 1
                                prev[(q, d)] = (pos, dp_, d)
            best = None
            for d in (0, 1):
                if (b0 + NL, d) in reach and reach[(b0 + NL, d)] <= 32:
                    best = d
                    break
            if best is None:
                return None
            ch = []
            key = (b0 + NL, best)
            while key[0] > b0:
                p, dp_, d = prev[key]
                ch.append((p, key[0], d))
                key = (p, dp_)
            return ch[::-1]

        first_d = [0]
        lo, hi = 0.0, 60000.0
        bestch = None
        for _ in range(26):
            T = (lo + hi) / 2
            got = None
            for b0 in b0s:
                ch = feas(T, b0)
                if ch is not None:
                    got = ch
                    break
            if got is not None:
                hi = T
                bestch = got
            else:
                lo = T
        ch = bestch
        while len(ch) < 32:
            k = max(range(len(ch)), key=lambda i: ch[i][1] - ch[i][0])
            p, q, d = ch[k]
            m = (p + q) // 2
            while not self.adj_ok[m % NL]:
                m += 1
            ch[k:k + 1] = [(p, m, d), (m, q, d)]
        # chunk starts/costs
        starts = []
        costs = []
        cells = []
        Ks = []
        for p, q, d in ch:
            cl = [x % NL for x in range(p, q)]
            if d == 1:
                cl = cl[::-1]
            v = segc.get((p % NL, q - p))
            if v is None:
                fw = self.chunk_cost(cl, False, G)
                c, K = fw[0], fw[4]
            else:
                c, K = v[d]
            starts.append(o[cl[0]])
            costs.append(c)
            cells.append(cl)
            Ks.append(K)
        if E("PRET") == "1":
            C = np.array([[max(0.0, tdist(apos[k], starts[j]) * 201 - self.slackA[k]) + costs[j] for j in range(32)] for k in range(32)])
        else:
            C = np.array([[tdist(apos[k], starts[j]) * 200 + costs[j] for j in range(32)] for k in range(32)])
        # bottleneck assignment
        vals = sorted(set(C.flatten()))
        lo, hi = 0, len(vals) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            M = (C > vals[mid]).astype(float)
            r, a = linear_sum_assignment(M)
            if M[r, a].sum() == 0:
                hi = mid
            else:
                lo = mid + 1
        thr = vals[lo]
        M = np.where(C > thr, 1e9, C)
        r, a = linear_sum_assignment(M)
        self.cellsB = [cells[a[k]] for k in range(32)]
        self.KB = [Ks[a[k]] for k in range(32)]
        self.bch = self.cellsB
        self.TB = thr
        print("B2: T %.0f thr %.0f" % (hi, thr), file=sys.stderr)

    def build(self):
        o = self.o
        pos_end = {}

        def sim_plan(c, p):
            for st in self.plans[c]:
                for m in st[0]:
                    dx, dy = DV[int(m)]
                    p = ((p[0] + dx) % N, (p[1] + dy) % N)
                sim_plan(st[1], p)
            pos_end[c] = p

        sim_plan(0, (0, 0))
        self.pos_end = pos_end
        self.PA, self.PB = [], []
        def wpos(chs):
            wp = {}
            for k, cl in enumerate(chs):
                for t, i in enumerate(cl):
                    wp[o[i]] = (k, t, len(cl))
            return wp
        gB = self.gB if self.gB is not None else self
        WPA = wpos(self.cellsA)
        WPB = {}
        for kk, cl in enumerate(gB.bch):
            for t, i in enumerate(cl):
                WPB[gB.o[i]] = (kk, t, len(cl))
        for k in range(ND):
            self.walkpos = WPA
            opsA, curA, GTA = self.phase_ops(self.cellsA[k], True, pos_end[k], self.KA[k])
            if E("PRET") == "1":
                pm = path_moves(curA, gB.o[gB.bch[k][0]])
                npre = min(len(pm), int(self.slackA[k] // 201))
                if k == int(E("HV", "0")) and npre < len(pm):
                    npre = 0
                for mm in pm[:npre]:
                    opsA.append(("move", int(mm)))
                    dx, dy = DV[int(mm)]
                    curA = ((curA[0] + dx) % N, (curA[1] + dy) % N)
            self.walkpos = None
            self.PA.append(("fa%d" % k, opsA, curA, GTA))
            gB.walkpos = WPB
            opsB, curB, GTB = gB.phase_ops(gB.bch[k], False, curA, gB.KB[k])
            gB.walkpos = None
            self.PB.append(("fb%d" % k, opsB, curB, GTB))

    def render(self, ph, L):
        name, ops, cur, GT = ph
        L.append("def %s():" % name)
        if any(op[0] == "sf" for op in ops):
            L.append("\tGT = %s" % lit({k2: [Dr(e) if i % 5 in (0, 3) else e for i, e in enumerate(v2)] for k2, v2 in GT.items()}))
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
            elif k == "fp":
                d, up = op[1], op[2]
                fr = op[3] if len(op) > 3 else False
                if fr:
                    L.append("	w = measure(%s)" % DN[d])
                    L.append("	while w == None:")
                    L.append("		w = measure(%s)" % DN[d])
                    L.append("	while measure() %s measure(%s):" % (">" if up else "<", DN[d]))
                    L.append("		swap(%s)" % DN[d])
                else:
                    L.append("	if measure() %s measure(%s):" % (">" if up else "<", DN[d]))
                    L.append("		swap(%s)" % DN[d])
            elif k == "fm":
                _, B, T = op
                L.append("\tfm(%s, %s)" % (lit([Dr(d) for d in B]), lit([Dr(d) for d in T])))
            elif k == "sf":
                L.append("\tsf(%d, GT)" % op[1])
            elif k == "fmf":
                _, d, B, T, od = op
                L.append("	move(%s)" % DN[d])
                L.append("	fm(%s, %s)" % (lit([Dr(x) for x in B]), lit([Dr(x) for x in T])))
                L.append("	move(%s)" % DN[od])
            elif k == "cx":
                _, BS, CS = op
                L.append("\tcx(%s, %s)" % (lit([[Dr(a), [Dr(x) for x in b], Dr(c2), 1 if pr else 0] for a, b, c2, pr in BS]), lit([[Dr(a), [Dr(x) for x in b], Dr(c2), 1 if pr else 0] for a, b, c2, pr in CS])))
            elif k == "cc":
                RD, EDG, NS, AX, AY = op[3]
                L.append("\tcc(%s, %s, %d, %d, %d)" % (lit([[a, b, [[Dr(x), y] for x, y in cl]] for a, b, cl in RD]), lit([[a, b, x, y, Dr(z), x2, y2, Dr(z2)] for a, b, x, y, z, x2, y2, z2 in EDG]), NS, AX, AY))
            else:
                raise ValueError("unrendered op " + k)
        L.append("\treturn tl")
        L.append("")

    def cc_data(self, ci, anchor, ret=None):
        R = self.R
        comp = self.comps[ci]
        if ret is None:
            ret = anchor
        if anchor not in comp:
            anchor = min(comp, key=lambda x: mdist(x, anchor))
        # tour: DFS order from anchor
        order = []
        seen = set()
        stk = [anchor]
        while stk:
            x = stk.pop()
            if x in seen:
                continue
            seen.add(x)
            order.append(x)
            for d, m in nb(x, R):
                if m in comp and m not in seen:
                    stk.append(m)
        slots = {c: i for i, c in enumerate(order)}
        pure = []
        for c in order:
            for d, m in nb(c, R):
                if m not in slots and m not in pure:
                    pure.append(m)
        for m in pure:
            slots[m] = len(slots)
        RD = []
        for c in order:
            RD.append([c[0], c[1], [[d, slots[m]] for d, m in nb(c, R)]])
        EDG = []
        seen_e = set()
        for c in order:
            for d, m in nb(c, R):
                lo, hi = (c, m) if d in UPD else (m, c)
                if (lo, hi) in seen_e:
                    continue
                seen_e.add((lo, hi))
                # stand on a component cell (alternative: the other endpoint if it is a component cell)
                st, dd = c, d
                if m in comp:
                    EDG.append([slots[lo], slots[hi], st[0], st[1], dd, m[0], m[1], OPP[d]])
                else:
                    EDG.append([slots[lo], slots[hi], st[0], st[1], dd, -1, -1, dd])
        return (RD, EDG, len(slots), ret[0], ret[1])

    def write(self, out):
        L = []
        for k in range(ND):
            self.render(self.PA[k], L)
            self.render(self.PB[k], L)
        L.append("FA = [%s]" % ", ".join("fa%d" % c for c in range(ND)))
        L.append("FB = [%s]" % ", ".join("fb%d" % c for c in range(ND)))
        L.append("BA = [%s]" % ", ".join("nop" for c in range(ND)))
        L.append("BB = BA")
        L.append("TB = BA")
        L.append("LP = %s" % lit([[[st[0], st[1]] for st in self.plans[c]] for c in range(ND)]))
        tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "t9.py")).read()
        tpl = tpl.replace("#DATA#", "def nop():\n\tpass\n\n" + "\n".join(L))
        src = tpl.replace("#HV#", str(int(E("HV", "0")))).replace("#NSIG#", str(ND - 1))
        open(out, "w").write(src)


def main():
    g = Gen()
    g.plan()
    g.build()
    if E("MODEL"):
        import model9
        model9.run(g, int(E("MODEL")))
    g.write(sys.argv[1])
    print("A sizes", [q - p for p, q in g.chA], "dirs", g.dirA, file=sys.stderr)
    print("B sizes", [len(x) for x in g.bch], "avg off %.1f" % (sum(g.offs) / ND), file=sys.stderr)


if __name__ == "__main__":
    main()
