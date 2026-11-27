# Post-process a g5 cactus entry: tails made only of fm() calls on 3-wide middles and moves get
# checkpoints. At each checkpoint the drone tries spawn_drone(hlp, ...): that fails in 1 tick while
# 32 drones run; once one has returned it succeeds, the helper walks to the far end of the
# remaining fixes and works back, the owner keeps the near part (and may split it again).
# Why it is safe: in a 3-wide band every fm swaps its middle with a bottom (which only ever gets
# smaller) or a top (only ever larger), and bottoms and tops are shared only between middles, so
# fixes on different middles never undo each other, and a swap made on a stale read (a few
# ticks between read and swap) is always followed by a fresh read of the drone whose swap made
# it stale (its next read is 200 ticks after its own swap). Two drones never work on the same
# middle. The geometry is checked below for every forked tail.
#   python fork2.py IN OUT [NMIN] [CF] [CM]
import re, sys, os

src = open(sys.argv[1]).read().split("\n")
NMIN = int(sys.argv[3]) if len(sys.argv) > 3 else 4
CF = float(sys.argv[4]) if len(sys.argv) > 4 else 365.0   # ticks per fix
CM = float(sys.argv[5]) if len(sys.argv) > 5 else 200.0   # ticks per move
ROUNDS = os.environ.get("ROUNDS", "B")
NEST = os.environ.get("FORKNEST", "1") == "1"  # owners split their share again (was env NEST; renamed: g5.py uses NEST)
OPP = {"North": "South", "South": "North", "East": "West", "West": "East"}
DV = {"North": (0, 1), "South": (0, -1), "East": (1, 0), "West": (-1, 0)}

funcs = []
cur = None
for i, l in enumerate(src):
    m = re.match(r"def (w\d+)\(", l)
    if m:
        cur = int(m.group(1)[1:])
    if l.startswith("\ttl = get_time()") and cur is not None:
        funcs.append((cur, i))


def safe(FS, MS):
    """middles distinct, no middle is a neighbour of another fix, no cell both a bottom and a top"""
    p = (0, 0)
    mids = []
    bs, ts = set(), set()
    for t, (B, T) in enumerate(FS):
        mids.append(p)
        for d in re.findall(r"\w+", B):
            bs.add((p[0] + DV[d][0], p[1] + DV[d][1]))
        for d in re.findall(r"\w+", T):
            ts.add((p[0] + DV[d][0], p[1] + DV[d][1]))
        if t < len(MS):
            for m in MS[t]:
                p = (p[0] + DV[m][0], p[1] + DV[m][1])
    return len(set(mids)) == len(mids) and not (bs & ts) and not (set(mids) & (bs | ts))


def split(n):
    """owner's share of n fixes left (owner at the first, helper walks to the last)"""
    best = None
    for a in range(1, n):
        to = CM + a * CF + (a - 1) * 2 * CM
        th = CM + 2 * CM * (n - 1) + (n - a) * CF + (n - a - 1) * 2 * CM
        t = max(to, th)
        if best is None or t < best[0]:
            best = (t, a)
    return best[1]


SP = [0] * 40
for n in range(NMIN, 40):
    SP[n] = split(n)

tables = {}
out = list(src)
edits = []
skipped = []
for k, i in funcs:
    rnd = sum(1 for kk, ii in funcs if kk == k and ii < i)
    rn = "AB"[rnd]
    if rn not in ROUNDS:
        continue
    j = i + 1
    lead = []
    FS = []
    MS = []
    ok = True
    while not src[j].startswith("\twait_until("):
        l = src[j].strip()
        mm = re.match(r"move\((\w+)\)$", l)
        mf = re.match(r"fm\((\[.*?\]), (\[.*?\])\)$", l)
        if mm:
            if FS:
                MS[-1].append(mm.group(1))
            else:
                lead.append(mm.group(1))
        elif mf:
            FS.append((mf.group(1), mf.group(2)))
            MS.append([])
        else:
            ok = False
            break
        j += 1
    if not ok or len(FS) < NMIN or MS[-1]:
        continue
    MS = MS[:-1]
    if not safe(FS, MS):
        skipped.append(k)
        continue
    r = len(FS)
    key = k * 2 + rnd
    tables[key] = (FS, MS)
    L = []
    for m in lead:
        L.append("move(%s)" % m)
    depth = 0
    for t in range(r):
        n = r - t
        if n >= NMIN:
            a = SP[n]
            L.append("\t" * depth + "h = spawn_drone(hlp, %d, %d, %d, %d)" % (key, t, t + a, r - 1))
            L.append("\t" * depth + "if h != None:")
            L.append("\t" * (depth + 1) + "own(%d, %d, %d)" % (key, t, t + a - 1))
            L.append("\t" * depth + "else:")
            depth += 1
        L.append("\t" * depth + "fm(%s, %s)" % FS[t])
        if t < r - 1:
            for m in MS[t]:
                L.append("\t" * depth + "move(%s)" % m)
    edits.append((i + 1, j, ["\t" + x for x in L]))

EARLY = os.environ.get("EARLY", "0") == "1"
if EARLY:
    # Round B: a drone that was already waiting at its start when the first harvest came, and
    # whose last plant is no later than the main drone's earliest possible last plant, returns
    # as soon as its fixes are done (its cactus grow before the main drone's own growth wait
    # ends), so its drone slot frees sooner for helpers.
    fstart = {}
    for i, l in enumerate(src):
        m = re.match(r"def (w\d+)\(", l)
        if m:
            fstart[int(m.group(1)[1:])] = i
    # main's unconditional actions from its harvest to its last round-B plant
    i0 = fstart[0]
    h = next(i for i in range(i0, len(src)) if src[i] == "\tharvest()")
    tl2 = next(i for i in range(h + 1, len(src)) if src[i] == "\ttl = get_time()")
    n0 = sum(1 for l in src[h + 1:tl2] if re.match(r"\t(move|plant|swap)\(", l))
    C = (200 * n0 + 200 - float(os.environ.get("EMARGIN", "40"))) / 6075.0
    print("main round-B actions before its last plant:", n0, "C = %.4f s" % C, file=sys.stderr)
    for k, st in fstart.items():
        if k == 0:
            continue
        en = fstart.get(k - 1, len(src)) if k - 1 in fstart and fstart[k - 1] > st else len(src)
        en = min([v for v in fstart.values() if v > st] + [len(src)])
        w = next(i for i in range(st, en) if src[i] == "\twhile num_items(Items.Cactus) <= 0:")
        tls = [i for i in range(st, en) if src[i] == "\ttl = get_time()"]
        wu = next(i for i in range(tls[1], en) if src[i].startswith("\twait_until(tl + "))
        edits.append((wu, wu + 1, ["\tif tl - hs > %.4f:" % C, "\t" + src[wu]]))
        edits.append((w + 2, w + 2, ["\ths = get_time()", "\tif ew:", "\t\ths = -9"]))
        edits.append((w, w, ["\tew = num_items(Items.Cactus) > 0"]))

for a, b, L in sorted(edits, key=lambda e: (e[0], e[1]), reverse=True):
    out[a:b] = L


def tab_code(ind, rs):
    L = []
    first = True
    for key, (FS, MS) in sorted(tables.items()):
        L.append(ind + ("if" if first else "elif") + " K == %d:" % key)
        first = False
        L.append(ind + "\tFS = [%s]" % ", ".join("[%s, %s]" % f for f in FS))
        if rs:
            L.append(ind + "\tMS = [%s]" % ", ".join("[%s]" % ", ".join(m) for m in MS))
            L.append(ind + "\tRS = [%s]" % ", ".join("[%s]" % ", ".join(OPP[x] for x in m[::-1]) for m in MS))
        else:
            L.append(ind + "\tMS = [%s]" % ", ".join("[%s]" % ", ".join(m) for m in MS))
    return L


rt = ["", "def hlp(K, j, lo, e):"] + tab_code("\t", True) + [
    "\twhile j < e:",
    "\t\tfor d in MS[j]:",
    "\t\t\tmove(d)",
    "\t\tj += 1",
    "\twhile j >= lo:",
    "\t\tfmc(FS[j][0], FS[j][1])",
    "\t\tif j > lo:",
    "\t\t\tfor d in RS[j - 1]:",
    "\t\t\t\tmove(d)",
    "\t\tj -= 1",
    "",
    "",
    "def own(K, j, e):"] + tab_code("\t", False)
if NEST:
    rt += ["\tSP = [%s]" % ", ".join(str(x) for x in SP[:30])]
rt += [
    "\twhile j <= e:"]
if NEST:
    rt += [
        "\t\tif e - j >= %d:" % (NMIN - 1),
        "\t\t\ta = SP[e - j + 1]",
        "\t\t\th = spawn_drone(hlp, K, j, j + a, e)",
        "\t\t\tif h != None:",
        "\t\t\t\te = j + a - 1"]
rt += [
    "\t\tfmc(FS[j][0], FS[j][1])",
    "\t\tif j < e:",
    "\t\t\tfor d in MS[j]:",
    "\t\t\t\tmove(d)",
    "\t\tj += 1",
    "",
    ""]

for idx, l in enumerate(out):
    if re.match(r"def w\d+\(", l):
        break
out[idx:idx] = rt
open(sys.argv[2], "w", newline="\n").write("\n".join(out))
print("forked tails:", sorted((k // 2, "AB"[k % 2], len(v[0])) for k, v in tables.items()), "unsafe:", skipped, "SP", SP[NMIN:12], file=sys.stderr)
