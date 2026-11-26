# T junction on the bottom edge (type S): row 0 = l M N O h, P above N, h2 above O (east of P),
# h1 above P.  Constraints: l<=M<=N<=O<=h, O<=h2, N<=P<=h1, P<=h2.
# Ring cells are pure: l may only go down, h/h1/h2 only up.
# Compare: the shipped greedy work list (jf), the fewest swaps possible, and candidate procedures.
import random, statistics as st, itertools, sys

CELLS = ["l", "M", "N", "O", "h", "P", "h1", "h2"]
POS = {"l": (0, 0), "M": (1, 0), "N": (2, 0), "O": (3, 0), "h": (4, 0), "P": (2, 1), "h1": (2, 2), "h2": (3, 1)}
EDGES = [("l", "M"), ("M", "N"), ("N", "O"), ("O", "h"), ("O", "h2"), ("N", "P"), ("P", "h1"), ("P", "h2")]  # (lower, upper)
LO = {c: [a for a, b in EDGES if b == c] for c in CELLS}
UP = {c: [b for a, b in EDGES if a == c] for c in CELLS}
COMP = ["M", "N", "O", "P"]


def dist(a, b):
    return abs(POS[a][0] - POS[b][0]) + abs(POS[a][1] - POS[b][1])


def ok(v):
    return all(v[a] <= v[b] for a, b in EDGES)


def draw(rng, mode):
    v = {c: rng.randrange(10) for c in CELLS}
    if mode == "settled":  # ring cells already compared with their neighbours outside the junction
        v["l"] = min(v["l"], rng.randrange(10))
        for c in ("h", "h1", "h2"):
            v[c] = max(v[c], rng.randrange(10))
        v["h1"] = max(v["h1"], rng.randrange(10))
        v["h2"] = max(v["h2"], rng.randrange(10))
    return v


def greedy(v, order, start=None):
    """the shipped jf: work list, at each cell swap with the largest lower neighbour above it, else
    the smallest upper neighbour below it. Returns (moves, swaps)."""
    pos = start or order[0]
    work = list(order)
    mv = sw = 0
    while work:
        c = work.pop(0)
        mv += dist(pos, c)
        pos = c
        while True:
            bl = max(LO[c], key=lambda m: v[m], default=None)
            if bl is not None and v[bl] > v[c]:
                v[bl], v[c] = v[c], v[bl]
                sw += 1
                if bl in COMP and bl not in work:
                    work.append(bl)
                continue
            tu = min(UP[c], key=lambda m: v[m], default=None)
            if tu is not None and v[tu] < v[c]:
                v[tu], v[c] = v[c], v[tu]
                sw += 1
                if tu in COMP and tu not in work:
                    work.append(tu)
                continue
            break
    mv += dist(pos, order[0])
    return mv, sw


def minswaps(v0):
    """fewest swaps along edges that end sorted, ring cells moving only in their safe direction."""
    key = tuple(v0[c] for c in CELLS)
    if ok(v0):
        return 0
    seen = {key}
    fr = [key]
    d = 0
    idx = {c: i for i, c in enumerate(CELLS)}
    while fr:
        d += 1
        nf = []
        for s in fr:
            for a, b in EDGES:
                i, j = idx[a], idx[b]
                if s[i] <= s[j]:
                    continue  # only swaps that fix their own edge (keeps ring cells monotone)
                t = list(s)
                t[i], t[j] = t[j], t[i]
                t = tuple(t)
                if t in seen:
                    continue
                if all(t[idx[x]] <= t[idx[y]] for x, y in EDGES):
                    return d
                seen.add(t)
                nf.append(t)
        fr = nf
    return None


def run(mode, T=4000, seed=3):
    rng = random.Random(seed)
    res = {"greedy PONM": [], "greedy NMOP": [], "min swaps": []}
    for _ in range(T):
        v = draw(rng, mode)
        a = dict(v); m, s = greedy(a, ["P", "O", "N", "M"]); assert ok(a); res["greedy PONM"].append((m, s))
        a = dict(v); m, s = greedy(a, ["N", "M", "O", "P"]); assert ok(a); res["greedy NMOP"].append((m, s))
        res["min swaps"].append((0, minswaps(v)))
    print(mode)
    for k, r in res.items():
        tot = [m + s for m, s in r]
        print("  %-12s moves %.2f swaps %.2f  total %.2f  sd %.2f  p90 %d max %d" % (k, st.mean(m for m, s in r), st.mean(s for m, s in r), st.mean(tot), st.pstdev(tot), sorted(tot)[int(0.9 * len(tot))], max(tot)))


if __name__ == "__main__":
    run("random")
    run("settled")
