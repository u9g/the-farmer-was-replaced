import random, statistics
from mc_col2 import fmc

def run(ncol, rng, early):
    L, M, H = [None] * ncol, [None] * ncol, [None] * ncol
    sw = mv = det = rep = 0
    LM = -1
    for j in range(ncol):
        H[j] = rng.randrange(10)
        if early and j > 0 and LM <= H[j] < M[j - 1]:
            H[j], M[j - 1] = M[j - 1], H[j]; sw += 1
        M[j] = rng.randrange(10); L[j] = rng.randrange(10)
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
        assert L[j] <= M[j] <= H[j]
        if j > 0:
            assert L[j - 1] <= M[j] and M[j - 1] <= H[j]
    return sw, mv, det, rep

for early in (0, 1):
    rng = random.Random(1)
    T = 20000; n = 8
    a = [run(n, rng, early) for _ in range(T)]
    f = lambda i: sum(x[i] for x in a) / T / n
    tot = [x[0] + x[1] for x in a]
    print("early=%d swaps/col %.3f moves/col %.3f detours %.3f repairs %.4f -> %.3f /col; per 8 cols sd %.2f" % (early, f(0), f(1), f(2), f(3), f(0) + f(1), statistics.pstdev(tot)))
