# min-max launch tree over consecutive chunk ranges: minimise max_k(arrival_k + rest_k)
from functools import lru_cache
from lay import tdist
from build_entry import path_moves


def spawn_plan_mm(starts, rest, origin, T_ACT=201.0):
    n = len(starts)
    rest = [r / T_ACT for r in rest]  # in actions
    pts = list(dict.fromkeys(list(starts)))

    @lru_cache(None)
    def h(i, j, p):
        # drone at p (time 0) handles chunks i..j-1; returns (makespan, choice)
        if j - i == 1:
            return (tdist(p, starts[i]) + rest[i], None)
        best = None
        cand = {p} | {starts[k] for k in range(i, j)}
        for q in cand:
            dq = tdist(p, q)
            for m in range(i + 1, j):
                a = h(i, m, q)[0]
                b = h(m, j, q)[0]
                v = dq + 1 + max(a, b)
                if best is None or v < best[0]:
                    best = (v, (q, m))
        return best

    offs = [0.0] * n
    plans = [[] for _ in range(n)]

    def walk(i, j, p, t, owner):
        if j - i == 1:
            offs[i] = t + tdist(p, starts[i])
            return
        q, m = h(i, j, p)[1]
        # owner keeps the range containing its own index
        if owner < m:
            plans[owner].append([path_moves(p, q), m, j])
            t2 = t + tdist(p, q) + 1
            walk(m, j, q, t2, m)
            walk(i, m, q, t2, owner)
        else:
            plans[owner].append([path_moves(p, q), i, m])
            t2 = t + tdist(p, q) + 1
            walk(i, m, q, t2, i)
            walk(m, j, q, t2, owner)

    walk(0, n, origin, 0, 0)
    return offs, plans, h(0, n, origin)[0]
