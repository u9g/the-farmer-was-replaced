# adaptive lazy settle for a junction component: model + data for the in-game jf()
import random
from lay import nb, UPD, tdist
from build_entry import path_moves, Dr


def geom(comp, R):
    ci = {c: i for i, c in enumerate(comp)}
    J = []
    for c in comp:
        B = [(d, m) for d, m in nb(c, R) if d not in UPD]
        T = [(d, m) for d, m in nb(c, R) if d in UPD]
        J.append([[Dr(d) for d, m in B], [Dr(d) for d, m in T], [ci.get(m, -1) for d, m in B], [ci.get(m, -1) for d, m in T]])
    P = [[[Dr(x) for x in path_moves(a, b)] for b in comp] for a in comp]
    return J, P


def model(comp, R, order, trials=2000, seed=5):
    rng = random.Random(seed)
    cells = set(comp)
    for c in comp:
        for d, m in nb(c, R):
            cells.add(m)
    cells = list(cells)
    lo = {c: [m for d, m in nb(c, R) if d not in UPD and m in cells] for c in cells}
    up = {c: [m for d, m in nb(c, R) if d in UPD and m in cells] for c in cells}
    cs = set(comp)
    tm = ts = tt = 0
    for _ in range(trials):
        v = {c: rng.randrange(10) for c in cells}
        # pure edges among ring/outside assumed already ok: apply CAS on edges not touching comp
        for c in cells:
            for m in up[c]:
                if c not in cs and m not in cs and v[c] > v[m]:
                    v[c], v[m] = v[m], v[c]
        pos = comp[order[0]]
        work = [comp[i] for i in order]
        mv = sw = tk = 0
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
        mv += tdist(pos, comp[order[0]])
        tm += mv; ts += sw; tt += tk
    return tm / trials, ts / trials, tt / trials


def best_order(comp, R, trials=1500):
    n = len(comp)
    cands = [list(range(n)), list(range(n - 1, -1, -1))]
    # by diagonal descending / ascending
    byd = sorted(range(n), key=lambda i: comp[i][0] + comp[i][1])
    cands += [byd, byd[::-1]]
    best = None
    for o in cands:
        m, s, t = model(comp, R, o, trials)
        cost = 201 * (m + s) + float(__import__("os").environ.get("JT", "1")) * t
        if best is None or cost < best[0]:
            best = (cost, o, m, s, t)
    return best
