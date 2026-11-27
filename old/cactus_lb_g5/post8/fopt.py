"""Plain fix routines f<LO>_<HI> (not the shared fs* ones): measure each of the five cells once and
track every swap in variables. One swap settles the lower side (the larger lower value moves in) and
one swap settles the upper side, so the loops become ifs and the upper cells are never re-read.
usage: python fopt.py IN OUT"""
import re, sys
D = {"N": "North", "S": "South", "E": "East", "W": "West"}
def low_fix(lo, t):
    if len(lo) == 2:
        return [t + "if not s <= v >= w:", t + "\tif w > s:", t + "\t\tswap(West)", t + "\t\tq = w", t + "\t\tw = v", t + "\t\tv = q",
                t + "\telse:", t + "\t\tswap(South)", t + "\t\tq = s", t + "\t\ts = v", t + "\t\tv = q"]
    x = {"S": "s", "W": "w"}[lo]
    return [t + "if %s > v:" % x, t + "\tswap(%s)" % D[lo], t + "\tq = %s" % x, t + "\t%s = v" % x, t + "\tv = q"]
def body(lo, hi):
    assert lo in ("SW", "S", "W") and hi in ("NE", "N", "E"), (lo, hi)
    o = ["\tv = measure()"] + ["\t%s = measure(%s)" % (d.lower(), D[d]) for d in lo]
    o += low_fix(lo, "\t")
    if len(hi) == 2:
        o += ["\ta = measure(North)", "\tb = measure(East)", "\twhile not a >= v <= b:",
              "\t\tif b < a:", "\t\t\tswap(East)", "\t\t\tq = b", "\t\t\tb = v", "\t\t\tv = q",
              "\t\telse:", "\t\t\tswap(North)", "\t\t\tq = a", "\t\t\ta = v", "\t\t\tv = q"]
    else:
        o += ["\ta = measure(%s)" % D[hi], "\twhile a < v:", "\t\tswap(%s)" % D[hi], "\t\tq = a", "\t\ta = v", "\t\tv = q"]
    o += low_fix(lo, "\t\t")
    return o
L = open(sys.argv[1]).read().split("\n")
out = []; i = 0; cnt = 0
while i < len(L):
    m = re.match(r"^def f([NSWE]+)_([NSWE]+)\(\):$", L[i])
    if not m:
        out.append(L[i]); i += 1; continue
    lo, hi = m.groups()
    j = i + 1
    while j < len(L) and (L[j] == "" or L[j].startswith("\t")):
        j += 1
    blk = L[i:j]
    k = len(blk)
    while blk[k - 1] == "": k -= 1
    out.append(L[i]); out += body(lo, hi); out += L[i + k:j]; cnt += 1
    i = j
open(sys.argv[2], "w").write("\n".join(out))
print("fopt:", cnt, "routines", file=sys.stderr)
