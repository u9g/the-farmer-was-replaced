# Greedy search on a g6 plan, scored by the simulator itself. Each step traces the current plan
# (TSEEDS seeds) to find the chunks that finish latest in each round, builds candidates that
# shrink one of them by one or two cells at either of its cuts, scores them all against the
# current plan on the same SEEDS seeds (paired), and keeps the best one if it beats the current
# plan by more than KSE standard errors.
#   python search.py PLAN.json WORKDIR STEPS
# Environment: the g5 variables (WIDTHS, ...), SEEDS (128), SEED0 (1000), TSEEDS (48),
# TOP (4 latest chunks per round), STEPS_ (1,2), KSE (1.5), ROUNDS ("AB").
import os, sys, json, subprocess, re, shutil, statistics as st
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SIM = os.path.join(ROOT, ".claude", "skills", "tfwr-sim", "tfwr_sim.rs")
import tune  # noqa: E402

E = os.environ.get
SEEDS = int(E("SEEDS", "128"))
SEED0 = int(E("SEED0", "1000"))
TSEEDS = int(E("TSEEDS", "48"))
TOP = int(E("TOP", "4"))
STEPS = [int(x) for x in E("STEPS_", "1,2").split(",")]
KSE = float(E("KSE", "1.5"))
ROUNDS = E("ROUNDS", "AB")
ND = 32


def score_many(work, names):
    """scores of names[1:] against names[0], paired by seed: list of (mean diff, se)"""
    r = subprocess.run(["cargo", "+nightly", "-Zscript", SIM] + names + ["--leaderboard", "cactus", "--seed", str(SEED0),
                       "--seeds", str(SEEDS), "--quiet"], cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = {}
    for m in re.finditer(r"^\s+([+-][\d.]+)s ± ([\d.]+)s\s+\(faster on (\d+) of (\d+) seeds\)\s+(\S+)", r.stdout, re.M):
        out[os.path.basename(m.group(5).replace("\\", "/"))] = (float(m.group(1)), float(m.group(2)))
    base = re.search(r"with \S*%s\n(?:.*\n)??\s+score \S+ \(([\d.]+)s\)" % re.escape(names[0]), r.stdout)
    fails = re.findall(r"FAILED[^\n]*", r.stdout)
    return out, (float(base.group(1)) if base else None), fails


def shrink(plan, rnd, c, side, k):
    """copy of plan with chunk c of round rnd shrunk by k cells at its low (side 0) or high cut"""
    p2 = json.loads(json.dumps(plan))
    ch = p2[rnd]
    if side == 0:
        j = c
        if j == 0:
            return None
        q = ch[j][0] + k
    else:
        j = c + 1
        if j == ND:
            return None
        q = ch[j][0] - k
    if not (0 < q < plan["n"]) or not tune.valid(p2, rnd, j, q):
        return None
    ch[j - 1][1] = q
    ch[j][0] = q
    return p2


def main():
    plan = json.load(open(sys.argv[1]))
    work = os.path.abspath(sys.argv[2])
    nsteps = int(sys.argv[3])
    os.makedirs(work, exist_ok=True)
    for step in range(nsteps):
        cur = os.path.join(work, "s%d_cur.py" % step)
        tune.build(plan, cur)
        _, _, m = tune.trace(cur, os.path.join(work, "tr"), 1, TSEEDS)
        finA, finB, tot, hA = m
        fa = [st.mean(finA[k]) + st.pstdev(finA[k]) for k in range(ND)]
        dr = plan["dr"]
        fb = [st.mean(finB[dr[c]]) + st.pstdev(finB[dr[c]]) for c in range(ND)]
        cands = []
        for rnd, f in (("A", fa), ("B", fb)):
            if rnd not in ROUNDS:
                continue
            for c in sorted(range(ND), key=lambda c: -f[c])[:TOP]:
                for side in (0, 1):
                    for k in STEPS:
                        p2 = shrink(plan, rnd, c, side, k)
                        if p2 is not None:
                            cands.append(("%s%d%s%d" % (rnd, c, "lh"[side], k), p2))
        names = []

        def mk(i_c):
            i, (tag, p2) = i_c
            nm = "s%d_c%d_%s.py" % (step, i, tag)
            tune.build(p2, os.path.join(work, nm))
            return nm
        with ThreadPoolExecutor(8) as ex:
            names = list(ex.map(mk, enumerate(cands)))
        res, base, fails = score_many(work, [os.path.basename(cur)] + names)
        rows = sorted(((res[n][0], res[n][1], n, cands[i][1]) for i, n in enumerate(names) if n in res), key=lambda r: r[0])
        print("step %d base %.4f; %d candidates; best %s" % (step, base or -1, len(rows),
              ", ".join("%s %+.4f±%.4f" % (r[2].split("_", 2)[2][:-3], r[0], r[1]) for r in rows[:5])), flush=True)
        if fails:
            print("   failures:", fails[:3], flush=True)
        for n in names:
            if not rows or n != rows[0][2]:
                os.remove(os.path.join(work, n))
                pj = os.path.join(work, n + ".plan.json")
                if os.path.exists(pj):
                    os.remove(pj)
        if not rows or rows[0][0] > -KSE * rows[0][1]:
            print("no candidate clearly better; stopping", flush=True)
            break
        plan = rows[0][3]
        json.dump(plan, open(os.path.join(work, "plan_s%d.json" % step), "w"))
    json.dump(plan, open(os.path.join(work, "plan_final.json"), "w"))


if __name__ == "__main__":
    main()
