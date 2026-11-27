"""own/hlp get their tables as arguments instead of a chain on K; SP becomes a tuple.

usage: python ownargs.py IN OUT
"""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
L = s.split("\n")


def ind(x):
    return len(x) - len(x.lstrip("\t"))


def func_range(name):
    i = L.index("def %s:" % name) if ("def %s:" % name) in L else None
    if i is None:
        i = [p for p, x in enumerate(L) if x.startswith("def %s(" % name)][0]
    j = i + 1
    while j < len(L) and (L[j].strip() == "" or ind(L[j]) > 0):
        j += 1
    return i, j


def tables(i, j):
    T = {}
    K = None
    for x in L[i + 1:j]:
        m = re.match(r"^\t(?:if|elif) K == (\d+):$", x)
        if m:
            K = int(m.group(1))
            T[K] = {}
            continue
        m = re.match(r"^\t\t(FS|MS|RS) = (.*)$", x)
        if m and K is not None:
            T[K][m.group(1)] = m.group(2)
            continue
        if ind(x) == 1:
            K = None
    return T


hi, hj = func_range("hlp")
oi, oj = func_range("own")
TH = tables(hi, hj)
TO = tables(oi, oj)
assert set(TH) == set(TO), (set(TH), set(TO))
for K in TH:
    assert TH[K]["FS"] == TO[K]["FS"] and TH[K]["MS"] == TO[K]["MS"], K

# new hlp: body after the chain
hb = [x for x in L[hi + 1:hj]]
p = [q for q, x in enumerate(hb) if x.startswith("\twhile ")][0]
new_hlp = ["def hlp(FS, MS, RS, j, lo, e):"] + hb[p:]
ob = L[oi + 1:oj]
p = [q for q, x in enumerate(ob) if x.startswith("\tSP = ")][0]
rest = ob[p:]
assert rest[0].startswith("\tSP = [") and rest[0].endswith("]")
rest[0] = "\tSP = (" + rest[0][len("\tSP = ["):-1] + ")"
rest = [x.replace("spawn_drone(hlp, K, j, j + a, e)", "spawn_drone(hlp, FS, MS, RS, j, j + a, e)") for x in rest]
assert any("spawn_drone(hlp, FS, MS, RS," in x for x in rest)
new_own = ["def own(FS, MS, RS, j, e):"] + rest

out = L[:hi] + new_hlp + L[hj:oi] + new_own + L[oj:]
t = "\n".join(out)


lines = t.split("\n")
seen = {}
o = []
n1 = n2 = 0
for x in lines:
    m = re.search(r"spawn_drone\(hlp, (\d+), ", x)
    if m:
        K = int(m.group(1))
        k = ind(x)
        # first spawn of this K in this drone: define the tables here (all later uses are nested below)
        key = K
        if key not in seen or not any(ind(y) <= k for y in []):
            pass
        if seen.get(K) is None or k <= seen[K]:
            T = TH[K]
            o.append("\t" * k + "TFS = " + T["FS"])
            o.append("\t" * k + "TMS = " + T["MS"])
            o.append("\t" * k + "TRS = " + T["RS"])
            seen[K] = k
        x, c = re.subn(r"spawn_drone\(hlp, (\d+), ", "spawn_drone(hlp, TFS, TMS, TRS, ", x)
        n2 += c
    x, c = re.subn(r"\bown\((\d+), ", "own(TFS, TMS, TRS, ", x)
    n1 += c
    o.append(x)
t = "\n".join(o)
print("own calls", n1, "hlp spawns", n2, file=sys.stderr)
open(dst, "w").write(t)
