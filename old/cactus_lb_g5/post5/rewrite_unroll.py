"""Unroll the junction helpers of cactus_lb_entry.py at their call sites (interpreter op cuts).

usage: python rewrite_unroll.py IN OUT

Every call takes literal arguments, so the generator can evaluate all of own()/hlp()'s control
flow that does not depend on the game:
- `h = spawn_drone(hlp, K, j, lo, e)` becomes `def hq(): <straight-line moves and fix calls>`
  then `h = spawn_drone(hq)`: the helper spends 0 ops instead of the K if-chain (2 per tested K),
  3 tuple builds (1 + 8 + 8), and ~6 ops per loop pass. The def costs the spawner 1 op.
- `own(K, j, e)` is inlined as straight-line code; only `if h != None:` after each spawn stays
  (2 ops), since spawn success depends on the drone count. `FS[j]()` (index + call through a
  variable = 2 ops) becomes a direct call of the global fix routine (free).
The now unused hlp/own defs are left in place (removing them would shift start-up op counts and
so every later random draw; harmless either way).
"""
import re
import sys

src = open(sys.argv[1]).read()
lines = src.split("\n")


def tup(s):
    return [x.strip() for x in s.strip()[1:-1].split(",") if x.strip()]


start = next(i for i, l in enumerate(lines) if l.startswith("def hlp("))
end = next(i for i, l in enumerate(lines) if l.startswith("def own("))
oend = next(i for i in range(end + 1, len(lines)) if lines[i].startswith("def "))
table, k = {}, None
for l in lines[start:end]:
    m = re.match(r"\t(?:el)?if K == (\d+):", l)
    if m:
        k = int(m.group(1))
        table[k] = {}
        continue
    m = re.match(r"\t\t(FS|MS|RS) = (.*)$", l)
    if m:
        table[k][m.group(1)] = m.group(2)
spec = {}
for k, t in table.items():
    ms = re.findall(r"\((\w+), (\w+)\)", t["MS"])
    rs = re.findall(r"\((\w+), (\w+)\)", t["RS"])
    spec[k] = (tup(t["FS"]), ms, rs)
k = None
for l in lines[end:oend]:
    m = re.match(r"\t(?:el)?if K == (\d+):", l)
    if m:
        k = int(m.group(1))
        continue
    m = re.match(r"\t\t(FS|MS) = (.*)$", l)
    if m:
        assert m.group(2) == table[k][m.group(1)]
spl = [l for l in lines[end:oend] if l.strip().startswith("SP = [")][0].strip()
SP = [int(x) for x in spl[len("SP = ["):-1].split(",")]


def hlp_lines(K, j, lo, e, ind):
    FS, MS, RS = spec[K]
    o = [ind + "def hq():"]
    b = ind + "\t"
    while j < e:
        o += [b + f"move({d})" for d in MS[j]]
        j += 1
    while j >= lo:
        o.append(b + f"{FS[j]}()")
        if j > lo:
            o += [b + f"move({d})" for d in RS[j - 1]]
        j -= 1
    o.append(ind + "h = spawn_drone(hq)")
    return o


def own_lines(K, j, e, ind):
    FS, MS, RS = spec[K]

    def step(j, e, ind):
        # the rest of a pass from `FS[j]()`, then the following passes
        o = [ind + f"{FS[j]}()"]
        if j < e:
            o += [ind + f"move({d})" for d in MS[j]]
        return o + loop(j + 1, e, ind)

    def loop(j, e, ind):
        if j > e:
            return []
        if e - j >= 2:
            a = SP[e - j + 1]
            o = hlp_lines(K, j, j + a, e, ind)
            o.append(ind + "if h != None:")
            o += step(j, j + a - 1, ind + "\t")
            o.append(ind + "else:")
            o += step(j, e, ind + "\t")
            return o
        return step(j, e, ind)

    return loop(j, e, ind)


out = []
n_h = n_o = 0
for l in lines:
    m = re.match(r"^(\t+)h = spawn_drone\(hlp, (\d+), (\d+), (\d+), (\d+)\)$", l)
    if m:
        ind, K, j, lo, e = m.group(1), *map(int, m.groups()[1:])
        out += hlp_lines(K, j, lo, e, ind)
        n_h += 1
        continue
    m = re.match(r"^(\t+)own\((\d+), (\d+), (\d+)\)$", l)
    if m:
        ind, K, j, e = m.group(1), *map(int, m.groups()[1:])
        out += own_lines(K, j, e, ind)
        n_o += 1
        continue
    out.append(l)
sys.stderr.write(f"unrolled {n_h} hlp spawns, {n_o} own calls; {len(lines)} -> {len(out)} lines\n")
open(sys.argv[2], "w").write("\n".join(out))
