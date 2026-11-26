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
            if push:
                if emit:
                    ops.append(("plant",))
                    ops.append(("push", 2 if col["down"] else 0))
                    ops.append(("plant",))
                st["fwd"] += 2 * PLANT_B + T_ACT
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
        _, _, f, vf, b, vb = walk_plan(lay, p, q, d, till, K, start)
        f += ZF * max(vf, 0) ** 0.5
        b += ZB * vb ** 0.5
        tot = f + max(GW, b + ((TM_A if till else TM_B) if b > 0 else 0))
        if best is None or tot < best[0] - 1e-9:
            best = (tot, K, f, b, GW)
    c = corr(till, p, q)
    out = (best[0] + c, best[1], best[2] + c, best[3], best[4])
    _ce_memo[key] = out
    return out


def phase_ops(lay, p, q, d, till, K, start, xstart=None, hx=True, nolast=False, xw=False):
    r = walk_plan(lay, p, q, d, till, K, start, xstart, hx, nolast, xw, emit=True)
    return r[0], r[1]


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
