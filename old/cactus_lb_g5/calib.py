# Calibrate the g5 planner against the simulator: generate an entry, trace it over SEEDS seeds,
# compare the measured finish of each chunk (mean + Z sd over seeds) with the planner's figure,
# spread the difference over the cells of the chunk as extra ticks (CORR), and plan again.
#   python calib.py WORKDIR ITERATIONS [first seed]
# Environment: the g5/g3 variables, plus SEEDS (48), Z (1.0), ETA (0.7), START (a corr json).
import os, sys, json, subprocess, glob, re, statistics as st, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DIAG = os.path.join(ROOT, ".claude", "skills", "cactus-diag", "tfwr_diag.rs")
work = os.path.abspath(sys.argv[1])
NIT = int(sys.argv[2])
SEED0 = int(sys.argv[3]) if len(sys.argv) > 3 else 1
SEEDS = int(os.environ.get("SEEDS", "48"))
Z = float(os.environ.get("Z", "1.0"))
ETA = float(os.environ.get("ETA", "0.7"))
TICK = 6075.0
ACT = 200 / TICK
os.makedirs(work, exist_ok=True)


def measure(entry, tdir):
    names = {}
    cur = "?"
    for i, ln in enumerate(open(entry), 1):
        m = re.match(r"def (\w+)\(", ln)
        if m:
            cur = m.group(1)
        names[i] = cur
    finA = {k: [] for k in range(32)}
    finB = {k: [] for k in range(32)}
    tot = []
    hA = []
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
        use = {}
        la = {}
        lp = {}
        lb = {}
        lpb = {}
        for t, d, k, l in ev:
            if d not in dn or k not in ("move", "swap", "plant", "till", "use"):
                continue
            if t < h[0]:
                if k == "use" and names.get(int(l.split(":")[1]), "?") != "?" and d not in use and d in lp and t > lp[d] + 0.5:
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
    return finA, finB, st.mean(tot), st.mean(hA)


def run(it, corr):
    cj = os.path.join(work, "corr%d.json" % it)
    json.dump(corr, open(cj, "w"))
    out = os.path.join(work, "e%d.py" % it)
    mj = os.path.join(work, "model%d.json" % it)
    env = dict(os.environ, CORR=cj, MODEL=mj)
    r = subprocess.run([sys.executable, os.path.join(HERE, "g5.py"), out], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise SystemExit(1)
    tdir = os.path.join(work, "tr%d" % it)
    shutil.rmtree(tdir, ignore_errors=True)
    os.makedirs(tdir)
    env2 = dict(os.environ, CACTUS_TRACE=os.path.join(tdir, "run"))
    r2 = subprocess.run(["cargo", "+nightly", "-Zscript", DIAG, os.path.basename(out), "--leaderboard", "cactus",
                         "--seed", str(SEED0), "--seeds", str(SEEDS), "--quiet"], env=env2, cwd=work, capture_output=True, text=True)
    sc = re.search(r"score \S+ \(([\d.]+)s\)", r2.stdout)
    fail = re.search(r"FAILED[^\n]*", r2.stdout)
    model = json.load(open(mj))
    m = measure(out, tdir)
    shutil.rmtree(tdir, ignore_errors=True)
    return out, model, m, (float(sc.group(1)) if sc else None), (fail.group(0) if fail else None)


corr = json.load(open(os.environ["START"])) if os.environ.get("START") else {"A": [0.0] * 800, "B": [0.0] * 800}
best = None
for it in range(NIT):
    out, model, m, score, fail = run(it, corr)
    if m is None or score is None:
        print("iter", it, "FAILED", fail)
        break
    finA, finB, tot, hA = m
    rows = model["chunks"]
    eA = []
    eB = []
    for k in range(32):
        ma = st.mean(finA[k]) + Z * st.pstdev(finA[k])
        mb = st.mean(finB[k]) + Z * st.pstdev(finB[k])
        eA.append(ma * TICK - rows[k]["finA"])
        eB.append(mb * TICK - rows[k]["finB"])
    mnA = [st.mean(finA[k]) for k in range(32)]
    mnB = [st.mean(finB[k]) for k in range(32)]
    print("iter %d score %.3f | A harvest %.3f, chunk means avg %.3f max %.3f | B %.3f, avg %.3f max %.3f | model %.3f + %.3f | err sd A %.0f B %.0f ticks" % (
        it, score, hA, st.mean(mnA), max(mnA), tot - hA, st.mean(mnB), max(mnB),
        model["TA"] / TICK, model["TB"] / TICK, st.pstdev(eA), st.pstdev(eB)), flush=True)
    if best is None or score < best[0]:
        best = (score, out)
    new = {"A": list(corr["A"]), "B": list(corr["B"])}
    for k in range(32):
        p, q, d = rows[k]["A"]
        for i in range(p, q):
            new["A"][i] += ETA * eA[k] / (q - p)
        p, q, d = rows[k]["B"]
        for i in range(p, q):
            new["B"][i] += ETA * eB[k] / (q - p)
    corr = new
print("best", best)
