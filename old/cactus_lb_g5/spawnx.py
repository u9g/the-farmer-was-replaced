# launch-tree variants over consecutive chunk ranges.
#   obj="exp": minimise sum_k exp((arrival_k + rest_k) / TAU) (matches plan5's objective)
#   obj="sum": minimise sum of arrival offsets
# extra candidate spawn points: EXTRA = list of cells
import math, os
from functools import lru_cache
from lay import tdist
from build_entry import path_moves


def spawn_plan_x(starts, rest, origin, obj="exp", TAU=600.0, T_ACT=201.0, extra=()):
    n = len(starts)
    restA = [r / T_ACT for r in rest]
    tau = TAU / T_ACT
    ref = max(restA)
    extra = tuple(extra)

    @lru_cache(None)
    def h(i, j, p):
        if j - i == 1:
            a = tdist(p, starts[i])
            if obj == "exp":
                return (math.exp((a + restA[i] - ref) / tau), None)
            return (a, None)
        best = None
        cand = {p} | {starts[k] for k in range(i, j)} | set(extra)
        for q in cand:
            dq = tdist(p, q)
            for m in range(i + 1, j):
                a = h(i, m, q)[0]
                b = h(m, j, q)[0]
                if obj == "exp":
                    v = math.exp((dq + 1) / tau) * (a + b)
                else:
                    v = (j - i) * (dq + 1) + a + b
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
