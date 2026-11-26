# CAS network for a junction component: verified on all 0-1 inputs (0-1 principle for poset sorting).
import itertools, random
from lay import nb, UPD, tdist
from build_entry import path_moves

DIRV = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}


def dir_to(a, b):
    for d, (dx, dy) in DIRV.items():
        if (a[0] + dx, a[1] + dy) == b:
            return d
    return None


def network(comp, R):
    S = list(comp)
    ring = []
    for c in comp:
        for d, m in nb(c, R):
            if m not in S and m not in ring:
                ring.append(m)
    S += ring
    idx = {c: i for i, c in enumerate(S)}
    E = []
    for c in S:
        for d, m in nb(c, R):
            if d in UPD and m in idx:
                E.append((idx[c], idx[m]))  # need v[lo] <= v[hi]
    k = len(S)
    vecs = [list(v) for v in itertools.product((0, 1), repeat=k)]
    seq = []
    def viol(v):
        return any(v[a] > v[b] for a, b in E)
    live = [v for v in vecs if viol(v)]
    while live:
        best = None
        for e in E:
            a, b = e
            cnt = sum(1 for v in live if v[a] > v[b])
            if cnt and (best is None or cnt > best[0]):
                best = (cnt, e)
        a, b = best[1]
        seq.append(best[1])
        for v in live:
            if v[a] > v[b]:
                v[a], v[b] = v[b], v[a]
        live = [v for v in live if viol(v)]
    # verify
    for v0 in vecs:
        v = list(v0)
        for a, b in seq:
            if v[a] > v[b]:
                v[a], v[b] = v[b], v[a]
        assert not viol(v)
    return S, seq


def route(S, seq, start):
    """choose for each CAS the endpoint to stand on, min moves (DP). returns ops and end pos."""
    n = len(seq)
    INF = 10 ** 9
    # dp over choices
    cand = [[S[a], S[b]] for a, b in seq]
    dp = [{} for _ in range(n)]
    for j, p in enumerate(cand[0]):
        dp[0][j] = (tdist(start, p), None)
    for i in range(1, n):
        for j, p in enumerate(cand[i]):
            best = None
            for jj, (v, _) in dp[i - 1].items():
                c = v + tdist(cand[i - 1][jj], p)
                if best is None or c < best[0]:
                    best = (c, jj)
            dp[i][j] = best
    j = min(dp[n - 1], key=lambda x: dp[n - 1][x][0])
    ch = [0] * n
    for i in range(n - 1, -1, -1):
        ch[i] = j
        j = dp[i][j][1]
    ops = []
    cur = start
    for i, (a, b) in enumerate(seq):
        lo, hi = S[a], S[b]
        p = cand[i][ch[i]]
        for m in path_moves(cur, p):
            ops.append(("move", int(m)))
        cur = p
        if p == lo:
            ops.append(("cas", dir_to(lo, hi), True))
        else:
            ops.append(("cas", dir_to(hi, lo), False))
    return ops, cur


def exp_cost(S, seq, R, trials=3000, T_ACT=201.0):
    idx = {c: i for i, c in enumerate(S)}
    sw = 0
    for _ in range(trials):
        v = [random.randrange(10) for _ in S]
        for a, b in seq:
            if v[a] > v[b]:
                v[a], v[b] = v[b], v[a]
                sw += 1
    return sw / trials


if __name__ == "__main__":
    import g2
    lay = g2.Layout([2] * 12 + [3] * 4 + [2] * 4)
    for k, comp in enumerate(lay.comps):
        S, seq = network(comp, lay.R)
        ops, cur = route(S, seq, comp[-1])
        mv = sum(1 for o in ops if o[0] == "move")
        print(k, "cells", len(S), "cas", len(seq), "moves", mv, "exp swaps %.2f" % exp_cost(S, seq, lay.R))
