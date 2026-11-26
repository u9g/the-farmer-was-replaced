# lazy cross: sort the column, fix the side edge, then only if H[j] < M[j-1] go up, swap West, come back
import random

def fmc(k, L, M, H, ncol):
    sw = 0
    while True:
        lows = [(L[k], 0)] + ([(L[k - 1], 1)] if k > 0 else [])
        bv, bd = max(lows)
        if bv > M[k]:
            if bd == 0: L[k], M[k] = M[k], L[k]
            else: L[k - 1], M[k] = M[k], L[k - 1]
            sw += 1; continue
        highs = [(H[k], 0)] + ([(H[k + 1], 1)] if k + 1 < ncol and H[k + 1] is not None else [])
        tv, td = min(highs)
        if tv < M[k]:
            if td == 0: H[k], M[k] = M[k], H[k]
            else: H[k + 1], M[k] = M[k], H[k + 1]
            sw += 1; continue
        return sw

def run(ncol, rng):
    L, M, H = [None] * ncol, [None] * ncol, [None] * ncol
    sw = mv = det = rep = 0
    LM = -1
    for j in range(ncol):
        H[j] = rng.randrange(10); M[j] = rng.randrange(10); L[j] = rng.randrange(10)
        if L[j] > M[j]:
            L[j], M[j] = M[j], L[j]; sw += 1
        if M[j] > H[j]:
            M[j], H[j] = H[j], M[j]; sw += 1
            if L[j] > M[j]:
                L[j], M[j] = M[j], L[j]; sw += 1
        if j > 0 and L[j - 1] > M[j]:
            L[j - 1], M[j] = M[j], L[j - 1]; sw += 1
            if M[j] > H[j]:
                M[j], H[j] = H[j], M[j]; sw += 1
        if j > 0 and H[j] < M[j - 1]:
            det += 1; mv += 2; sw += 1
            H[j], M[j - 1] = M[j - 1], H[j]
            if M[j - 1] < LM:
                rep += 1; mv += 2
                sw += fmc(j - 1, L, M, H, ncol)
        LM = max(L[j], L[j - 1]) if j > 0 else L[j]
    for j in range(ncol):
        assert L[j] <= M[j] <= H[j], (j, L[j], M[j], H[j])
        if j > 0:
            assert L[j - 1] <= M[j] and M[j - 1] <= H[j], j
    return sw, mv, det, rep

rng = random.Random(1)
T = 20000; n = 8
a = [run(n, rng) for _ in range(T)]
f = lambda i: sum(x[i] for x in a) / T / n
print("lazy: swaps/col %.3f moves/col %.3f detours/col %.3f repairs/col %.4f -> actions/col %.3f" % (f(0), f(1), f(2), f(3), f(0) + f(1)))
import statistics
tot = [x[0] + x[1] for x in a]
print("per 8 columns: mean %.2f sd %.2f" % (statistics.mean(tot), statistics.pstdev(tot)))
