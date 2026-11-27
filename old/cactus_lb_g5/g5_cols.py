# Chunk evaluation and code generation for g5: push-planted columns (round B), columns sorted
# in place right after planting, and the mixed cells at a cut left to the drone whose walk ends
# there in both walk directions. Imported by g5.py.
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cactus_lb_g2"))
import g2, g3
from g2 import T_ACT, GROW_T, C_CAS
from g3 import walk_of, item_cost, item_var, water_n, grow_window, TILL_A, PLANT_B, ZB, ZF, is_foreign_end
from lay import nb, tdist, UPD
from build_entry import path_moves

E = os.environ.get
PUSH = E("PUSH", "1") == "1"
CHOICE = int(E("CHOICE", "0"))   # round B: a push column's far cell may be filled from the next column's middle instead
KT = int(E("KT", "5"))
KA = int(E("KA", "2"))
KB = int(E("KB", "6"))
KP = int(E("KP", "6"))
PK_T = float(E("PK_T", "0"))  # model: interpreter ticks of a pk2 call
FMB_SAVE = float(E("FMB_SAVE", "0"))  # model: ticks a routed (CHOICE) middle fix saves in round B
COLFIX = E("COLFIX", "0") == "1"   # sort a 3-wide column in place right after planting it
COLFIX_A = E("COLFIX_A", "1") == "1"  # ... in round A (with COLFIX)
TM_A = float(E("TM_A", "0"))          # ticks of the growth wait kept clear of tail work, round A
TM_B = float(E("TM_B", "0"))          # ... round B
MIRROR = E("MIRROR", "0") == "1"   # R walks too: the drone whose walk ends at a cut fixes the mixed cells just past it
C_CM = float(E("C_CM", "290"))     # column sort at the middle cell: ticks + expected swaps
C_SD = float(E("C_SD", "55"))      # its edge to the previous column
C_CX = float(E("C_CX", "95"))      # the previous middle's edge to this column (detour when needed)
V_CM = float(E("V_CM", "87000"))

CORR = {}
if E("CORR"):
    import json
    for _r, _v in json.load(open(E("CORR"))).items():
        _p = [0.0]
        for _x in _v:
            _p.append(_p[-1] + _x)
        CORR[_r] = _p


def corr(till, p, q):
    """measured-minus-modelled time of the cells [p, q), from calib.py"""
    pre = CORR.get("A" if till else "B")
    if not pre or q >= len(pre):
        return 0.0
    return pre[q] - pre[p]


_ci_memo = {}


def cell_items5(lay, w, p, q, d, hx=True):
    """g3.cell_items, except that in both directions a mixed cell with a neighbour in the chunk
    before the walk start is left to that chunk's drone (g3: forward walks only)."""
    key = (p, q, d, hx)
    if key in _ci_memo:
        return _ci_memo[key]
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
        if c in lay.iso:
            if d == 0:
                skip = any(lay.pos[m] < p for dd, m in nb(c, R))
            else:
                skip = MIRROR and any(lay.pos[m] >= q for dd, m in nb(c, R))
            if not skip:
                alw.append(("fm", lay.lo[c], lay.up[c]))
        if t == len(w) - 1:
            if d == 0:
                for i2 in range(q, min(lay.n, q + 12)):
                    c2 = o[i2]
                    if c2 in lay.iso and any(lay.pos[m] < q for dd, m in nb(c2, R)):
                        alw.append(("fmx", c2, lay.lo[c2], lay.up[c2]))
            elif MIRROR:
                for i2 in range(p - 1, max(-1, p - 13), -1):
                    c2 = o[i2]
                    if c2 in lay.iso and any(lay.pos[m] >= p for dd, m in nb(c2, R)):
                        alw.append(("fmx", c2, lay.lo[c2], lay.up[c2]))
        if c in lay.comp:
            k = lay.comp[c]
            comp = lay.comps[k]
            last = max(comp, key=lambda x: tpos.get(lay.pos[x], -1))
            if c == last:
                alw.append(("jx", k))
        out.append((cas, alw))
    _ci_memo[key] = out
    return out


_an_memo = {}


def analyse(lay, p, q, d, hx=True):
    """columns of the walk: three consecutive walk cells in a vertical line. 'reg' ones have an
    isolated mixed middle between two pure cells; for those: whether the side edge (middle to
    the previous column's pure cell) and the cross edge (first cell to the previous column's
    middle) can be fixed from inside this walk."""
    key = (p, q, d, hx)
    if key in _an_memo:
        return _an_memo[key]
    o, R = lay.o, lay.R
    w = walk_of(p, q, d)
    n = len(w)
    ci = cell_items5(lay, w, p, q, d, hx)
    tpos = {o[i]: t for t, i in enumerate(w)}
    cols = {}
    t = 0
    prev = None
    while t + 2 < n:
        a, b, c = o[w[t]], o[w[t + 1]], o[w[t + 2]]
        dy = b[1] - a[1]
        if a[0] == b[0] == c[0] and abs(dy) == 1 and c[1] - b[1] == dy:
            col = {"t0": t, "down": dy == -1, "reg": False, "push": not ci[t + 2][0]}
            if b in lay.iso and a not in lay.M and c not in lay.M:
                # the previous column is west of a top-down column, east of a bottom-up one
                sx = b[0] - 1 if dy == -1 else b[0] + 1
                side = (sx, b[1])
                nxtc = (2 * b[0] - sx, b[1])
                mprev = (sx, a[1])
                col["reg"] = True
                col["plain"] = not ci[t][0] and not ci[t + 1][0] and not ci[t + 2][0]
                col["side_ex"] = side in R
                col["side_en"] = side in R and side not in lay.M and tpos.get(side, n) < t
                col["next_ex"] = nxtc in R
                col["full"] = sorted(lay.lo[b]) == [2, 3] and sorted(lay.up[b]) == [0, 1]
                col["cross_en"] = (prev is not None and prev["reg"] and prev["plain"] and prev["t0"] == t - 3
                                   and o[w[t - 2]] == mprev and prev["side_en"] and prev["full"] and col["plain"])
            cols[t] = col
            prev = col
            t += 3
        else:
            prev = None
            t += 1
    out = (w, n, ci, cols)
    _an_memo[key] = out
    return out


def walk_plan(lay, p, q, d, till, K, start, xstart=None, hx=True, nolast=False, xw=False, emit=False):
    """one drone's work in one round. Returns (ops or None, end cell, forward ticks, forward
    variance, tail ticks, tail variance)."""
    o = lay.o
    w, n, ci, cols = analyse(lay, p, q, d, hx)
    zone = n - K
    Wn = min(water_n(till), n)
    ops = [] if emit else None
    st = {"cur": start, "fwd": 0.0, "vf": 0.0}
    deferred = {}
    act = TILL_A if till else PLANT_B

    def goto(c):
        if emit:
            for m in path_moves(st["cur"], c):
                ops.append(("move", int(m)))
        st["fwd"] += T_ACT * tdist(st["cur"], c)
        st["cur"] = c

    def fixes(t, drop_fm=False):
        cas, alw = ci[t]
        if cas:
            if t >= zone and t >= 2 and not (nolast and t == n - 1):  # a chunk never defers its first two cells
                deferred.setdefault(t, []).extend(cas)
            else:
                if emit:
                    ops.extend(cas)
                st["fwd"] += C_CAS * len(cas)
                st["vf"] += 8400.0 * len(cas)
        for it in alw:
            if drop_fm and it[0] == "fm":
                continue
            deferred.setdefault(t, []).append(it)

    def inline_ok(col, t):
        return (col is not None and COLFIX and (COLFIX_A or not till) and col["reg"] and col["plain"] and t + 2 < zone
                and not (t + 2 >= n - Wn) and (till or (PUSH and col["push"])))

    def elig(t):
        col = cols.get(t)
        return (col is not None and not till and PUSH and col["push"] and not (t + 2 >= n - Wn)
                and col["reg"] and not ci[t][0] and not ci[t + 1][0] and not ci[t + 2][0])

    def link(t):
        if not (CHOICE and elig(t) and elig(t + 3)):
            return False
        a = o[w[t + 2]]
        b = o[w[t + 4]]
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            return False
        if CHOICE >= 2:
            c1, f0 = o[w[t + 1]], o[w[t + 3]]
            # c1 -> far -> next middle and c1 -> next entry -> next middle are both 2 moves
            if abs(c1[0] - f0[0]) + abs(c1[1] - f0[1]) != 1 or (a[0] + f0[0] - c1[0], a[1] + f0[1] - c1[1]) != b:
                return False
        return True

    def dirto(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        return {(0, 1): 0, (1, 0): 1, (0, -1): 2, (-1, 0): 3}[(dx, dy)]

    chm = set()
    if CHOICE and not till:
        for t0 in cols:
            if link(t0) or (t0 >= 3 and link(t0 - 3)):
                chm.add(t0 + 1)
    t = 0
    while t < n:
        col = cols.get(t)
        watered = t + 2 >= n - Wn
        push = col is not None and not till and PUSH and col["push"] and not watered
        fix = inline_ok(col, t)
        if push or fix:
            c0, c1, c2 = o[w[t]], o[w[t + 1]], o[w[t + 2]]
            complete = False
            if fix:
                nx = cols.get(t + 3)
                nxt_inline = inline_ok(nx, t + 3) and nx["cross_en"]
                complete = (col["side_en"] or not col["side_ex"]) and (not col["next_ex"] or nxt_inline)
            k0 = len(ops) if emit else 0
            goto(c0)
            if emit:
                if till:
                    ops.append(("till",))
                ops.append(("plant",))
                if t == 0 and xstart is not None:
                    ops.append(("xcas", xstart[0], xstart[1]))
            st["fwd"] += act
            fixes(t)
            goto(c1)
            if emit and push and CHOICE >= 2 and t >= 3 and link(t - 3):
                del ops[k0:]   # the previous column's pk2 walked here and planted on the way
            if push:
                if emit:
                    nx = link(t)
                    pv = t >= 3 and link(t - 3)
                    if CHOICE >= 2 and (nx or pv):
                        dp = dirto(c1, o[w[t - 1]]) if pv else -1
                        de = dirto(c1, o[w[t + 3]]) if nx else -1
                        ops.append(("pk2", dp, 2 if col["down"] else 0, de, col["down"], nx))
                    elif nx or pv:
                        dp = dirto(c1, o[w[t - 1]]) if pv else -1
                        ops.append(("pk", dp, 2 if col["down"] else 0, col["down"], nx))
                    else:
                        ops.append(("plant",))
                        ops.append(("push", 2 if col["down"] else 0))
                        ops.append(("plant",))
                st["fwd"] += 2 * PLANT_B + T_ACT + (PK_T if (t + 1) in chm else 0.0)
                fixes(t + 1, drop_fm=complete)
                fixes(t + 2)
            else:
                if emit:
                    if till:
                        ops.append(("till",))
                    ops.append(("plant",))
                st["fwd"] += act
                fixes(t + 1, drop_fm=complete)
                goto(c2)
                if emit:
                    if till:
                        ops.append(("till",))
                    ops.append(("plant",))
                st["fwd"] += act
                fixes(t + 2)
            if fix:
                if not push:
                    goto(c1)
                if emit:
                    ops.append(("cm", col["down"], col["side_en"], col["cross_en"]))
                st["fwd"] += C_CM + (C_SD if col["side_en"] else 0) + (C_CX if col["cross_en"] else 0)
                st["vf"] += V_CM
            t += 3
            continue
        goto(o[w[t]])
        if emit:
            if till:
                ops.append(("till",))
            if t >= n - Wn:
                ops.append(("water",))
            ops.append(("plant",))
            if t == 0 and xstart is not None:
                ops.append(("xcas", xstart[0], xstart[1]))
        st["fwd"] += act + (T_ACT if t >= n - Wn else 0)
        fixes(t)
        t += 1
    if emit:
        ops.append(("LP",))
    cur = st["cur"]
    tail = 0.0
    vb = 0.0
    for t in sorted(deferred, reverse=True):
        c = o[w[t]]
        tail += T_ACT * tdist(cur, c)
        if emit:
            for m in path_moves(cur, c):
                ops.append(("move", int(m)))
        cur = c
        for it in deferred[t]:
            tail += item_cost(lay, it)
            if it[0] == "fm" and t in chm:
                tail -= FMB_SAVE
            vb += item_var(lay, it)
            if it[0] == "jx":
                comp, order, cst, J, P = lay.net[it[1]]
                s0 = comp[order[0]]
                tail += T_ACT * tdist(cur, s0)
                if emit:
                    for m in path_moves(cur, s0):
                        ops.append(("move", int(m)))
                    ops.append(("jf", J, P, order))
                cur = s0
            elif not emit:
                continue
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
    return ops, cur, st["fwd"], st["vf"], tail, vb


_ce_memo = {}


def chunk_eval(lay, p, q, d, till, start):
    key = (p, q, d, till, start)
    if key in _ce_memo:
        return _ce_memo[key]
    w, n, ci, cols = analyse(lay, p, q, d)
    Wn = min(water_n(till), n)
    GW = grow_window(lay, w, start, till, Wn) if Wn else GROW_T
    # deferral zones worth trying: from a column start, from a cell with an inline CAS, or none
    zs = {n} | set(cols) | {t for t in range(2, n) if ci[t][0]}
    best = None
    for z in sorted(zs, reverse=True):
        K = n - z
        em = LEAFPUSH and not till and LPMODEL
        ops, _, f, vf, b, vb = walk_plan(lay, p, q, d, till, K, start, emit=em)
        if em:
            k = ops.index(("LP",))
            leaf_push(ops[:k])
            f -= T_ACT * leaf_push.n
        f += ZF * max(vf, 0) ** 0.5
        b += ZB * vb ** 0.5
        tot = f + max(GW, b + ((TM_A if till else TM_B) if b > 0 else 0))
        if best is None or tot < best[0] - 1e-9:
            best = (tot, K, f, b, GW)
    c = corr(till, p, q)
    out = (best[0] + c, best[1], best[2] + c, best[3], best[4])
    _ce_memo[key] = out
    return out


LEAFPUSH = E("LEAFPUSH", "0") == "1"
LPMODEL = E("LPMODEL", "0") == "1"


def leaf_push(ops):
    """round B: 'move d, plant, move back, plant' (a dead end planted before the cell it hangs
    off) becomes 'plant, swap d, plant': one action less."""
    out = []
    i = 0
    n = 0
    def back(a, b):
        return a[0] == "move" and b[0] == "move" and b[1] == (a[1] + 2) % 4

    while i < len(ops):
        # here unplanted: go to the leaf, plant it, come back, plant here
        if (i + 3 < len(ops) and back(ops[i], ops[i + 2]) and ops[i + 1] == ("plant",)
                and (ops[i + 3] == ("plant",) or ops[i + 3][0] in ("pk", "pk2"))):
            out += [("plant",), ("push", ops[i][1])]
            i += 3
            n += 1
            continue
        # here planted with nothing to check: plant the leaf from here instead
        if (i + 3 < len(ops) and ops[i] == ("plant",) and back(ops[i + 1], ops[i + 3]) and ops[i + 2] == ("plant",)):
            out += [("plant",), ("push", ops[i + 1][1]), ("plant",)]
            i += 4
            n += 1
            continue
        out.append(ops[i])
        i += 1
    leaf_push.n = n
    return out


def phase_ops(lay, p, q, d, till, K, start, xstart=None, hx=True, nolast=False, xw=False):
    r = walk_plan(lay, p, q, d, till, K, start, xstart, hx, nolast, xw, emit=True)
    ops = r[0]
    if LEAFPUSH and not till:
        k = ops.index(("LP",))
        ops = leaf_push(ops[:k]) + ops[k:]
    return ops, r[1]


PKRT = '''PD = False


def pk(dp, df, lo, nx):
	global PD
	plant(Entities.Cactus)
	if PD:
		swap(dp)
		plant(Entities.Cactus)
		PD = False
	if nx:
		v = measure()
		if lo:
			k = v >= KT
			if k and dp != None:
				k = v >= measure(dp)
		else:
			k = v <= 9 - KT
			if k and dp != None:
				k = v <= measure(dp)
		if k:
			PD = True
			return
	swap(df)
	plant(Entities.Cactus)


'''

PK2RT = '''PD = False


def pk2(dp, df, de, lo, nx):
	global PD
	plant(Entities.Cactus)
	f = 0
	if PD:
		if nx:
			v = measure()
			if not lo:
				v = 9 - v
			if v >= KP:
				swap(de)
				plant(Entities.Cactus)
				f = 2
		swap(dp)
		plant(Entities.Cactus)
		PD = False
	if not nx:
		swap(df)
		plant(Entities.Cactus)
		return
	if f == 0:
		v = measure()
		if not lo:
			v = 9 - v
		if v <= KA:
			swap(df)
			plant(Entities.Cactus)
			f = 1
		elif v >= KB:
			swap(de)
			plant(Entities.Cactus)
			f = 2
	if f == 2:
		move(df)
		plant(Entities.Cactus)
		move(de)
	else:
		move(de)
		plant(Entities.Cactus)
		move(df)
		if f == 0:
			PD = True


'''

RUNTIME = '''BL = [South, West]
TU = [North, East]
PM = 0
LM = 0
HM = 0


def cmd(sd, cx):
	global PM
	global LM
	m = measure()
	l = measure(South)
	h = measure(North)
	if l > m:
		swap(South)
		t = l
		l = m
		m = t
	if m > h:
		swap(North)
		t = h
		h = m
		m = t
		if l > m:
			swap(South)
			t = l
			l = m
			m = t
	w = -1
	if sd:
		w = measure(West)
		if w > m:
			swap(West)
			t = w
			w = m
			m = t
			if m > h:
				swap(North)
				t = h
				h = m
				m = t
	if cx:
		if h < PM:
			move(North)
			swap(West)
			if h < LM:
				move(West)
				fmc(BL, TU)
				move(East)
			move(South)
	PM = m
	LM = l
	if w > l:
		LM = w


def cmu(sd, cx):
	global PM
	global HM
	m = measure()
	l = measure(South)
	h = measure(North)
	if l > m:
		swap(South)
		t = l
		l = m
		m = t
	if m > h:
		swap(North)
		t = h
		h = m
		m = t
		if l > m:
			swap(South)
			t = l
			l = m
			m = t
	e = 99
	if sd:
		e = measure(East)
		if e < m:
			swap(East)
			t = e
			e = m
			m = t
			if m < l:
				swap(South)
				t = l
				l = m
				m = t
	if cx:
		if l > PM:
			move(South)
			swap(East)
			if l > HM:
				move(East)
				fmc(BL, TU)
				move(West)
			move(North)
	PM = m
	HM = h
	if e < h:
		HM = e


'''
