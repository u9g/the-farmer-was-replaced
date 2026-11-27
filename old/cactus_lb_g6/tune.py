# Rebalance a g6 plan against the simulator. The chunk structure stays (directions, round-B drone
# assignment); each iteration traces the entry over SEEDS seeds, takes every chunk's measured
# finish (mean + Z sd), and moves the cuts so that late chunks give cells to their neighbours
# along the snake.
#   python tune.py PLAN.json WORKDIR ITERATIONS
# Environment: the g5 variables (WIDTHS, ...), SEEDS (48), SEED0 (1), Z (1.0), ETA (0.6),
# ROUNDS ("AB"), CA / CB (ticks one cell is worth in round A / B: 600 / 420), LMIN/LMAX (6/40).
import os, sys, json, subprocess, re, glob, shutil, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DIAG = os.path.join(ROOT, ".claude", "skills", "cactus-diag", "tfwr_diag.rs")
E = os.environ.get
SEEDS = int(E("SEEDS", "48"))
SEED0 = int(E("SEED0", "1"))
Z = float(E("Z", "1.0"))
ETA = float(E("ETA", "0.6"))
ROUNDS = E("ROUNDS", "AB")
CA = float(E("CA", "600"))
CB = float(E("CB", "420"))
LMIN = int(E("LMIN", "6"))
LMAX = int(E("LMAX", "40"))
TICK = 6075.0
ACT = 200 / TICK
ND = 32


def measure(entry, tdir):
    """per drone (w<k>): round-A done times and round-B done times (from the first harvest)"""
    names = {}
    cur = "?"
    for i, ln in enumerate(open(entry), 1):
        m = re.match(r"def (\w+)\(", ln)
        if m:
            cur = m.group(1)
        names[i] = cur
    finA = {k: [] for k in range(ND)}
    finB = {k: [] for k in range(ND)}
    tot, hA = [], []
    for f in sorted(glob.glob(os.path.join(tdir, "run.*.tsv"))):
        ev = []
        for ln in open(f):
            x = ln.split("\t")
            if x[0] == "E":
                ev.append((float(x[1]), int(x[2]), x[3], x[8]))
        h = [t for t, d, k, l in ev if k == "harvest"]
        if len(h) != 2:
            return None
        tot.append(h[1] + ACT)
        hA.append(h[0])
        dn = {}
        for t, d, k, l in ev:
            if k in ("plant", "till") and d not in dn:
                fn = names.get(int(l.split(":")[1]), "?")
                if re.match(r"w\d+$", fn):
                    dn[d] = int(fn[1:])
        use, la, lp, lb, lpb = {}, {}, {}, {}, {}
        for t, d, k, l in ev:
            if d not in dn or k not in ("move", "swap", "plant", "till", "use"):
                continue
            if t < h[0]:
                if k == "use" and d not in use and d in lp and t > lp[d] + 0.5:
                    use[d] = t
                elif d not in use:
                    la[d] = t
                    if k == "plant":
                        lp[d] = t
            elif t < h[1]:
                if k == "plant":
                    lpb[d] = t
                if d in lpb:
                    lb[d] = t
        for d, k in dn.items():
            a = use[d] if d in use else max(la[d] + ACT, lp[d] + 1.0)
            finA[k].append(a)
            finB[k].append(max(lb[d] + ACT, lpb[d] + 1.0) - h[0])
    return finA, finB, tot, hA


def build(plan, out):
    pj = out + ".plan.json"
    json.dump(plan, open(pj, "w"))
    r = subprocess.run([sys.executable, os.path.join(HERE, "g6.py"), out], env=dict(os.environ, OVR=pj),
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        raise SystemExit(1)


def trace(entry, tdir, seed0, seeds):
    shutil.rmtree(tdir, ignore_errors=True)
    os.makedirs(tdir)
    env = dict(os.environ, CACTUS_TRACE=os.path.join(tdir, "run"))
    r = subprocess.run(["cargo", "+nightly", "-Zscript", DIAG, os.path.basename(entry), "--leaderboard", "cactus",
                        "--seed", str(seed0), "--seeds", str(seeds), "--quiet"], env=env, cwd=os.path.dirname(entry),
                       capture_output=True, text=True)
    sc = re.search(r"score \S+ \(([\d.]+)s\)", r.stdout)
    fail = re.search(r"FAILED[^\n]*|failed[^\n]*", r.stdout)
    m = measure(entry, tdir)
    shutil.rmtree(tdir, ignore_errors=True)
    return (float(sc.group(1)) if sc else None), (fail.group(0) if fail else None), m


def valid(plan, rnd, j, q):
    """may cut j (between chunk j-1 and chunk j) of round rnd sit at position q?"""
    ch = plan[rnd]
    if not plan["cut_ok"][q]:
        return False
    if q - ch[j - 1][0] < LMIN or ch[j][1] - q < LMIN or q - ch[j - 1][0] > LMAX or ch[j][1] - q > LMAX:
        return False
    da, d = ch[j - 1][2], ch[j][2]
    if da != d and not plan["clean"][q]:
        return False
    return True


def rebalance(plan, rnd, fin, cost):
    """fin[c]: measured finish of chunk c (ticks). Move the cuts toward equal finishes."""
    ch = plan[rnd]
    tgt = st.mean(fin)
    delta = [-(f - tgt) / cost for f in fin]
    m = st.mean(delta)
    delta = [ETA * (x - m) for x in delta]
    s = 0.0
    moved = 0
    for j in range(1, ND):
        s += delta[j - 1]
        want = ch[j][0] + int(round(s))
        cur = ch[j][0]
        if want == cur:
            continue
        step = 1 if want > cur else -1
        best = cur
        q = cur
        while q != want:
            q += step
            if 0 < q < plan["n"] and valid(plan, rnd, j, q):
                best = q
        if best != cur:
            ch[j - 1][1] = best
            ch[j][0] = best
            moved += abs(best - cur)
    return moved


def main():
    plan = json.load(open(sys.argv[1]))
    work = os.path.abspath(sys.argv[2])
    nit = int(sys.argv[3])
    os.makedirs(work, exist_ok=True)
    best = None
    for it in range(nit):
        out = os.path.join(work, "t%d.py" % it)
        build(plan, out)
        shutil.copy(os.path.join(ROOT, "run_cactus_lb.py"), work)
        score, fail, m = trace(out, os.path.join(work, "tr"), SEED0, SEEDS)
        if m is None or score is None:
            print("iter", it, "FAILED", fail, score, flush=True)
            break
        finA, finB, tot, hA = m
        fa = [(st.mean(finA[k]) + Z * st.pstdev(finA[k])) * TICK for k in range(ND)]
        dr = plan["dr"]
        fb = [(st.mean(finB[dr[c]]) + Z * st.pstdev(finB[dr[c]])) * TICK for c in range(ND)]
        print("iter %d score %.4f | A harvest %.3f chunk max %.3f avg %.3f | B %.3f max %.3f avg %.3f" % (
            it, score, st.mean(hA), max(fa) / TICK, st.mean(fa) / TICK, st.mean(tot) - st.mean(hA),
            max(fb) / TICK, st.mean(fb) / TICK), flush=True)
        json.dump(plan, open(os.path.join(work, "plan%d.json" % it), "w"))
        if best is None or score < best[0]:
            best = (score, it)
        mv = 0
        if "A" in ROUNDS:
            mv += rebalance(plan, "A", fa, CA)
        if "B" in ROUNDS:
            mv += rebalance(plan, "B", fb, CB)
        print("   moved %d cells" % mv, flush=True)
        if mv == 0:
            break
    print("best", best)


if __name__ == "__main__":
    main()
