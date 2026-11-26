# Concurrent tick-level model of the generated program (b9 ops).
import heapq, random, sys
from lay import nb, UPD, N

DV = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}
TPS = 6075.0
GROW = 6075  # ticks
ACT = 200


class World:
    def __init__(self, R, rng):
        self.R = R
        self.val = {}      # pos -> value
        self.pt = {}       # pos -> plant tick
        self.rng = rng
        self.cactus = 0
        self.water_used = 0
        self.pumpkins = 0


def run_drone(w, ph, start, st):
    """generator executing phase ops; yields tick costs. st: dict with pos, t (updated by scheduler)"""
    name, ops, cur, GT = ph
    st["pos"] = start

    def nbpos(d):
        dx, dy = DV[d]
        p = st["pos"]
        return ((p[0] + dx) % N, (p[1] + dy) % N)

    def meas(d=None):
        p = st["pos"] if d is None else nbpos(d)
        return w.val.get(p)

    for op in ops:
        k = op[0]
        if k == "move":
            yield ACT + 1
            st["pos"] = nbpos(op[1])
        elif k == "till":
            yield ACT + 1
        elif k == "plant":
            p = st["pos"]
            if p in w.val:
                st["fail"] = st.get("fail", 0) + 1
                yield 1
            else:
                w.val[p] = w.rng.randrange(10)
                w.pt[p] = st["t"]
                w.pumpkins += 1
                yield ACT + 1
        elif k == "LP":
            st["lp"] = st["t"]
        elif k == "fp":
            d, up = op[1], op[2]
            yield 2
            a, b = meas(), meas(d)
            fr = len(op) > 3 and op[3]
            while b is None and fr:
                st["wait"] = st.get("wait", 0) + 3
                yield 3
                b = meas(d)
            yield 2
            if fr:
                while True:
                    a, b = meas(), meas(d)
                    yield 4
                    if a is not None and b is not None and ((up and a > b) or ((not up) and a < b)):
                        yield from swap_gen(w, st, d)
                    else:
                        break
            elif a is not None and b is not None and ((up and a > b) or ((not up) and a < b)):
                yield from swap_gen(w, st, d)
        elif k == "fm":
            yield from fm_gen(w, st, op[1], op[2])
        elif k == "fmf":
            yield ACT + 1
            st["pos"] = nbpos(op[1])
            yield from fm_gen(w, st, op[2], op[3])
            yield ACT + 1
            st["pos"] = nbpos(op[4])
        elif k == "cc":
            yield from cc_gen(w, st, op[3])
        elif k == "cx":
            yield from cx_gen(w, st, op[1], op[2])
        else:
            raise ValueError(k)


def swap_gen(w, st, d):
    p = st["pos"]
    dx, dy = DV[d]
    q = ((p[0] + dx) % N, (p[1] + dy) % N)
    # swap applies at start of action
    vp, vq = w.val.get(p), w.val.get(q)
    tp, tq = w.pt.get(p), w.pt.get(q)
    if vq is None:
        w.val.pop(p, None)
    else:
        w.val[p] = vq
    if vp is None:
        w.val.pop(q, None)
    else:
        w.val[q] = vp
    if tq is None:
        w.pt.pop(p, None)
    else:
        w.pt[p] = tq
    if tp is None:
        w.pt.pop(q, None)
    else:
        w.pt[q] = tp
    yield ACT + 2


def fm_gen(w, st, B, T):
    def nbpos(d):
        dx, dy = DV[d]
        p = st["pos"]
        return ((p[0] + dx) % N, (p[1] + dy) % N)
    for n in range(12):
        yield 3
        v = w.val.get(st["pos"])
        if v is None:
            return
        bd, bv = None, v
        for d in B:
            yield 3
            x = w.val.get(nbpos(d))
            while x is None:
                st["wait"] = st.get("wait", 0) + 3
                yield 3
                x = w.val.get(nbpos(d))
            if x > bv:
                bv, bd = x, d
        if bd is not None:
            yield from swap_gen(w, st, bd)
            continue
        td, tv = None, v
        for d in T:
            yield 3
            x = w.val.get(nbpos(d))
            while x is None:
                st["wait"] = st.get("wait", 0) + 3
                yield 3
                x = w.val.get(nbpos(d))
            if x < tv:
                tv, td = x, d
        if td is not None:
            yield from swap_gen(w, st, td)
            continue
        return


def cx_gen(w, st, BS, CS):
    def nbpos(d, p=None):
        dx, dy = DV[d]
        p = st["pos"] if p is None else p
        return ((p[0] + dx) % N, (p[1] + dy) % N)

    def step(d):
        yield ACT + 1
        st["pos"] = nbpos(d)
    for d, tops, od, pre in CS:
        if pre:
            yield from step(d)
            yield from fm_gen(w, st, [], tops)
            yield from step(od)
    for d, lows, od, pre in BS:
        if pre:
            yield from step(d)
            yield from fm_gen(w, st, lows, [])
            yield from step(od)
    for n in range(10):
        yield 20
        g = w.val.get(st["pos"])
        hit = False
        for d, tops, od, pre in CS:
            x = w.val.get(nbpos(d))
            if x is not None and g > x:
                yield from swap_gen(w, st, d)
                yield from step(d)
                yield from fm_gen(w, st, [], tops)
                yield from step(od)
                hit = True
                break
        if not hit:
            for d, lows, od, pre in BS:
                x = w.val.get(nbpos(d))
                if x is not None and g < x:
                    yield from swap_gen(w, st, d)
                    yield from step(d)
                    yield from fm_gen(w, st, lows, [])
                    yield from step(od)
                    hit = True
                    break
        if not hit:
            return


def cc_gen(w, st, args):
    RD, EDG, NS, AX, AY = args

    def goto(x, y):
        while st["pos"][0] < x:
            yield ACT + 3
            st["pos"] = (st["pos"][0] + 1, st["pos"][1])
        while st["pos"][0] > x:
            yield ACT + 3
            st["pos"] = (st["pos"][0] - 1, st["pos"][1])
        while st["pos"][1] < y:
            yield ACT + 3
            st["pos"] = (st["pos"][0], st["pos"][1] + 1)
        while st["pos"][1] > y:
            yield ACT + 3
            st["pos"] = (st["pos"][0], st["pos"][1] - 1)

    V = [0] * NS
    yield 10 + NS
    for i, e in enumerate(RD):
        yield from goto(e[0], e[1])
        V[i] = w.val.get(st["pos"])
        yield 4
        for d, s in e[2]:
            dx, dy = DV[d]
            V[s] = w.val.get(((st["pos"][0] + dx) % N, (st["pos"][1] + dy) % N))
            yield 4
    S = []
    ch = True
    n = 0
    while ch and n < 40:
        ch = False
        n += 1
        for e in EDG:
            if V[e[0]] is not None and V[e[1]] is not None and V[e[0]] > V[e[1]]:
                V[e[0]], V[e[1]] = V[e[1]], V[e[0]]
                S.append(e)
                ch = True
        yield 8 * len(EDG)
    for e in S:
        yield 8
        if e[5] >= 0:
            px, py = st["pos"]
            if abs(px - e[5]) + abs(py - e[6]) < abs(px - e[2]) + abs(py - e[3]):
                yield from goto(e[5], e[6])
                yield from swap_gen(w, st, e[7])
                continue
        yield from goto(e[2], e[3])
        yield from swap_gen(w, st, e[4])
    yield from goto(AX, AY)


def sorted_cell(w, c, t):
    v = w.val.get(c)
    if v is None or w.pt.get(c, 1e18) + GROW > t:
        return False
    x, y = c
    for d, (dx, dy) in DV.items():
        m = (x + dx, y + dy)
        if not (0 <= m[0] < N and 0 <= m[1] < N):
            continue
        u = w.val.get(m)
        if u is None:
            continue
        if w.pt.get(m, 1e18) + GROW > t:
            return False
        if d in UPD and v > u:
            return False
        if d not in UPD and v < u:
            return False
    return True


def harvest(w, c, t):
    """returns popped count; removes popped cells"""
    if w.val.get(c) is None or w.pt[c] + GROW > t:
        w.val.pop(c, None)
        return 0
    popped = set()
    stack = [c]
    while stack:
        x = stack.pop()
        if x in popped or w.val.get(x) is None or w.pt[x] + GROW > t:
            continue
        popped.add(x)
        nbrs = []
        for d, (dx, dy) in DV.items():
            m = (x[0] + dx, x[1] + dy)
            if 0 <= m[0] < N and 0 <= m[1] < N and w.val.get(m) is not None:
                nbrs.append(m)
        if all(sorted_cell(w, m, t) for m in nbrs):
            stack.extend(nbrs)
    for x in popped:
        del w.val[x]
        del w.pt[x]
    return len(popped)


def simulate(g, seed, BOOT=200):
    """full run: A phase, water-signal sync, harvest, B phase, final harvest. returns (time_s, nA, nB)"""
    rng = random.Random(seed)
    w = World(g.R, rng)
    ND = len(g.PA)
    # A phase
    states = []
    gens = []
    heap = []
    for k in range(ND):
        tr = 0
        for op in g.PA[k][1]:
            if op[0] != "move":
                break
            tr += 1
        st = {"t": BOOT + (g.offs[k] - tr) * 200, "k": k}
        states.append(st)
        gens.append(run_drone(w, g.PA[k], g.pos_end[k], st))
        heapq.heappush(heap, (st["t"], k))
    done = [None] * ND
    while heap:
        t, k = heapq.heappop(heap)
        st = states[k]
        st["t"] = t
        try:
            dt = next(gens[k])
            heapq.heappush(heap, (t + dt, k))
        except StopIteration:
            done[k] = t
    # each drone: wait own growth, signal (1 action), harvester waits all signals
    sig = []
    for k in range(ND):
        tt = max(done[k], states[k]["lp"] + GROW + 1)
        sig.append(tt + ACT)
    tH = max(sig) + 2
    hv = int(getattr(g, "hv", 0))
    nA = harvest(w, states[hv]["pos"], tH)
    # B phase
    states2 = []
    gens = []
    heap = []
    for k in range(ND):
        st = {"t": tH + ACT + 5, "k": k}
        states2.append(st)
        gens.append(run_drone(w, g.PB[k], states[k]["pos"], st))
        heapq.heappush(heap, (st["t"], k))
    done2 = [None] * ND
    while heap:
        t, k = heapq.heappop(heap)
        st = states2[k]
        st["t"] = t
        try:
            dt = next(gens[k])
            heapq.heappush(heap, (t + dt, k))
        except StopIteration:
            done2[k] = t
    ends = [max(done2[k], states2[k]["lp"] + GROW + 1) for k in range(ND)]
    tE = max(ends) + 2
    nB = harvest(w, states2[hv]["pos"], tE)
    ok = 32 * (nA * nA + nB * nB) >= 33554432
    return tE / TPS, nA, nB, ok, max(done) / TPS, tH / TPS, (max(done2) - tH) / TPS


if __name__ == "__main__":
    import os
    import b9
    g = b9.Gen()
    g.plan()
    g.build()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    res = [simulate(g, s) for s in range(n)]
    import statistics as S
    fails = [r for r in res if not r[3]]
    print("cmodel: mean time %.3f  fails %d/%d  nA %s nB %s" % (S.mean(r[0] for r in res), len(fails), n,
          sorted(set(r[1] for r in res))[:5], sorted(set(r[2] for r in res))[:5]))
    print("A done %.3f harvest %.3f B dur %.3f" % (S.mean(r[4] for r in res), S.mean(r[5] for r in res), S.mean(r[6] for r in res)))
