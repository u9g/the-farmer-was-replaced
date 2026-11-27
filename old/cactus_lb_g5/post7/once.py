"""Fix loops that always end after one swap: `while` -> `if`, drop the re-measure.

MODE=reuse : v = (the value swapped in), no sensor read
MODE=meas  : v = measure()
usage: python once.py IN OUT [MODE] [WHICH] [RANGE]  WHICH: 2 (two-neighbour loops), 1 (one-neighbour), 12 (both)
       RANGE: w0 (default: from `def w0():` on) or LO-HI (1-based lines)
"""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else "reuse"
which = sys.argv[4] if len(sys.argv) > 4 else "12"
L = open(src).read().split("\n")
rng = sys.argv[5] if len(sys.argv) > 5 else "w0"
if rng == "w0":
    # only the drone code: from `def w0():` on (the shared fix routines above it race with helper drones)
    lo, hi = L.index("def w0():") + 1, 10 ** 9
else:
    lo, hi = (int(x) for x in rng.split("-"))


def ind(s):
    return len(s) - len(s.lstrip("\t"))


out = []
i = 0
n2 = n1 = 0
while i < len(L):
    line = L[i]
    m2 = re.match(r"^(\t*)while not (\w+) <= v >= (\w+):$", line)
    m1 = re.match(r"^(\t*)while (\w+) > v:$", line)
    if m2 and "2" in which and lo <= i + 1 <= hi:
        t, A, B = m2.group(1), m2.group(2), m2.group(3)
        k = len(t)
        # body: lines with indent > k
        j = i + 1
        while j < len(L) and (L[j].strip() == "" or ind(L[j]) > k):
            j += 1
        body = L[i + 1:j]
        # expect: if B > A: / swap(D1) / ... / else: / swap(D2) / ... / v = measure() / A = measure(D2) / B = measure(D1)
        assert body[0] == t + "\tif %s > %s:" % (B, A), (i, body[0])
        assert body[-3] == t + "\tv = measure()", (i, body[-3])
        assert re.match(r"^\t*%s = measure\(\w+\)$" % A, body[-2]), (i, body[-2])
        assert re.match(r"^\t*%s = measure\(\w+\)$" % B, body[-1]), (i, body[-1])
        ei = body.index(t + "\telse:")
        then_b = body[1:ei]
        else_b = body[ei + 1:-3]
        out.append(t + "if not %s <= v >= %s:" % (A, B))
        out.append(body[0])
        out.extend(then_b)
        out.append(t + "\t\tv = " + (B if mode == "reuse" else "measure()"))
        out.append(body[ei])
        out.extend(else_b)
        out.append(t + "\t\tv = " + (A if mode == "reuse" else "measure()"))
        n2 += 1
        i = j
        continue
    if m1 and "1" in which and lo <= i + 1 <= hi:
        t, A = m1.group(1), m1.group(2)
        k = len(t)
        j = i + 1
        while j < len(L) and (L[j].strip() == "" or ind(L[j]) > k):
            j += 1
        body = L[i + 1:j]
        assert body[-2] == t + "\tv = measure()", (i, body)
        assert re.match(r"^\t*%s = measure\(\w+\)$" % A, body[-1]), (i, body[-1])
        assert body[0].startswith(t + "\tswap("), (i, body[0])
        out.append(t + "if %s > v:" % A)
        out.extend(body[:-2])
        out.append(t + "\tv = " + (A if mode == "reuse" else "measure()"))
        n1 += 1
        i = j
        continue
    out.append(line)
    i += 1
open(dst, "w").write("\n".join(out))
print("two-neighbour loops:", n2, "one-neighbour loops:", n1, file=sys.stderr)
