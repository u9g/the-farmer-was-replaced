# Layout + order + Monte-Carlo cost model for the cactus leaderboard.
import random
N = 32
DV = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}  # N E S W
UPD = (0, 1)


def diag_strips(walls):
    """walls: sorted list of wall diagonals. returns list of strips (list of diagonals)."""
    strips = []
    cur = []
    for d in range(63):
        if d in walls:
            if cur:
                strips.append(cur)
            cur = []
        else:
            cur.append(d)
    if cur:
        strips.append(cur)
    return strips


def strip_cells(ds):
    return [(x, d - x) for d in ds for x in range(N) if 0 <= d - x < N]


def zig_order(ds, inc):
    """order of the cells of a strip (2 or 3 diagonals) walked SE (inc) or NW."""
    cells = strip_cells(ds)
    if len(ds) <= 2:
        cells.sort(key=lambda c: (c[0] - c[1]))
        return cells if inc else cells[::-1]
    # width 3: columns by x, snake within columns
    cols = {}
    for c in cells:
        cols.setdefault(c[0], []).append(c)
    xs = sorted(cols)
    if not inc:
        xs = xs[::-1]
    out = []
    up = True
    for x in xs:
        col = sorted(cols[x], key=lambda c: c[1])
        if not up:
            col = col[::-1]
        # choose direction that starts nearest to the last cell
        if out:
            a, b = col[0], col[-1]
            l = out[-1]
            if abs(b[0] - l[0]) + abs(b[1] - l[1]) < abs(a[0] - l[0]) + abs(a[1] - l[1]):
                col = col[::-1]
        out += col
        up = not up
    return out


def build(walls, extra=(), drop=()):
    """serpentine through strips; connector on the wall between consecutive strips at the turn."""
    walls = sorted(walls)
    strips = diag_strips(set(walls))
    R = set()
    order = []
    for k, ds in enumerate(strips):
        inc = (k % 2 == 0)
        cells = zig_order(ds, inc)
        if k > 0:
            w = max(d for d in walls if d < ds[0])
            wall = sorted([(x, w - x) for x in range(N) if 0 <= w - x < N], key=lambda c: c[0] - c[1])
            # previous strip ended at max t if it was inc
            g = wall[-1] if ((k - 1) % 2 == 0) else wall[0]
            R.add(g)
            order.append(g)
        R |= set(cells)
        order += cells
    for g in extra:
        if g not in R:
            R.add(g)
            # insert near closest
            best = None
            for i in range(len(order) - 1):
                a, b = order[i], order[i + 1]
                dd = abs(a[0] - g[0]) + abs(a[1] - g[1]) + abs(b[0] - g[0]) + abs(b[1] - g[1])
                if best is None or dd < best[0]:
                    best = (dd, i)
            order.insert(best[1] + 1, g)
    for c in drop:
        R.discard(c)
        order.remove(c)
    return R, order


def nb(c, R):
    x, y = c
    out = []
    for d, (dx, dy) in DV.items():
        n = (x + dx, y + dy)
        if n in R:
            out.append((d, n))
    return out


def is_mid(c, R):
    ds = [d for d, _ in nb(c, R)]
    return any(d in UPD for d in ds) and any(d not in UPD for d in ds)


def has_up(c, R):
    return any(d in UPD for d, _ in nb(c, R))


def has_dn(c, R):
    return any(d not in UPD for d, _ in nb(c, R))


def mdist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def tdist(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return min(dx, N - dx) + min(dy, N - dy)


class Drone:
    def __init__(self, pos):
        self.pos = pos
        self.moves = 0
        self.swaps = 0
        self.acts = 0

    def go(self, c):
        self.moves += tdist(self.pos, c)
        self.pos = c


def settle(dr, c, R, vals):
    """runtime settle at cell c (drone is at c). mirrors the game code."""
    again = True
    while again:
        again = False
        for d, n in nb(c, R):
            if n not in vals:
                continue
            v, w = vals[c], vals[n]
            up = d in UPD
            if (up and v > w) or ((not up) and v < w):
                vals[c], vals[n] = w, v
                dr.swaps += 1
                # neighbour n got v: if it went up (n above c) its up-neighbours may break
                if (up and has_up(n, R)) or ((not up) and has_dn(n, R)):
                    back = dr.pos
                    dr.go(n)
                    settle(dr, n, R, vals)
                    dr.go(back)
                again = True
                break


def check_sorted(R, vals):
    bad = 0
    for c in R:
        for d, n in nb(c, R):
            if d in UPD and vals[c] > vals[n]:
                bad += 1
    return bad


def sim_chunks(R, order, chunks, rng, till):
    """chunks: list of (p,q) over order. simulated last-to-first. returns per-cell action costs."""
    vals = {}
    cost = [0.0] * len(order)
    for ci in range(len(chunks) - 1, -1, -1):
        p, q = chunks[ci]
        dr = Drone(order[p])
        for i in range(p, q):
            c = order[i]
            m0, s0 = dr.moves, dr.swaps
            dr.go(c)
            vals[c] = rng.randrange(10)
            settle(dr, c, R, vals)
            cost[i] = (dr.moves - m0) + (dr.swaps - s0) + 1 + (1 if till else 0)
    return cost, vals


if __name__ == "__main__":
    walls = [d for d in range(63) if d % 3 == 0]
    R, order = build(walls)
    print("A size", len(R), len(order), len(set(order)))
    gaps = sum(1 for i in range(len(order) - 1) if mdist(order[i], order[i + 1]) != 1)
    print("non-adjacent steps", gaps)
    print("middles", sum(1 for c in R if is_mid(c, R)))
    rng = random.Random(1)
    tot = []
    for s in range(20):
        cost, vals = sim_chunks(R, order, [(0, len(order))], rng, True)
        assert check_sorted(R, vals) == 0
        tot.append(sum(cost))
    print("A cost/cell", sum(tot) / len(tot) / len(order))
