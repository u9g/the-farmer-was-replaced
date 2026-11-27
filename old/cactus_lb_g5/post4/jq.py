# Junction worklists (wk = [...]; cur = s; while len(wk) > 0: cx = wk.pop(0) ...) rewritten with a
# read index and pending flags: same FIFO order and same dedup, fewer interpreter ticks.
#   python3 jq.py IN OUT
import sys, re
L = open(sys.argv[1]).read().split("\n")
def ind(s): return len(s) - len(s.lstrip("\t"))
out = []; i = 0; n = 0
while i < len(L):
    s = L[i]
    m = re.match(r"(\t*)wk = \[([\d, ]+)\]$", s)
    if not (m and L[i + 2].strip() == "while len(wk) > 0:" and L[i + 3].strip() == "cx = wk.pop(0)" and L[i + 1].strip().startswith("cur = ")):
        out.append(s); i += 1; continue
    t = m.group(1); k = len(t)
    order = [int(x) for x in m.group(2).split(",")]
    out += [s, L[i + 1], t + "qi = 0", t + "qn = %d" % len(order)] + [t + "q%d = True" % c for c in order]
    out += [t + "while qi < qn:", t + "\tcx = wk[qi]", t + "\tqi += 1"]
    j = i + 4
    body = []
    while j < len(L) and (L[j].strip() == "" or ind(L[j]) > k):
        body.append(L[j]); j += 1
    # top-level cx dispatch lines
    tops = [b for b, x in enumerate(body) if ind(x) == k + 1 and re.match(r"(if|elif) cx == \d+:$", x.strip())]
    assert len(tops) == len(order), (i, tops)
    nb = []
    for b, x in enumerate(body):
        st = x.strip()
        mm = re.match(r"(if|elif) cx == (\d+):$", st)
        if ind(x) == k + 1 and mm:
            if b == tops[-1]:
                nb.append(t + "\telse:")
            else:
                nb.append(x)
            nb.append(t + "\t\tq%s = False" % mm.group(2))
            continue
        mm = re.match(r"if not \((\d+) in wk\):$", st)
        if mm:
            nb.append(x[:ind(x)] + "if not q%s:" % mm.group(1)); continue
        mm = re.match(r"wk\.append\((\d+)\)$", st)
        if mm:
            tt = x[:ind(x)]
            nb += [x, tt + "qn += 1", tt + "q%s = True" % mm.group(1)]; continue
        assert "wk" not in st, st
        nb.append(x)
    out += nb
    n += 1
    i = j
open(sys.argv[2], "w", newline="\n").write("\n".join(out))
print("worklists rewritten:", n, file=sys.stderr)
