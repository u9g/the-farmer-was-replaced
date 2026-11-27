# Free exit for a junction settle that ends a tail: jfx() does not walk back to the junction's
# first cell; it returns the cell it ended on. Round B: nothing follows, the walk is dropped.
# Round A: the moves after the signal (pre-travel to the round-B start; for the main drone the
# moves after its harvest) are replaced by one shortest torus path per possible end cell.
#   python fexit.py IN OUT
import re, sys, ast

N = 32
src = open(sys.argv[1]).read().split("\n")
DV = {"North": (0, 1), "South": (0, -1), "East": (1, 0), "West": (-1, 0)}


def parse_P(call):
    # jf(J, P, order) with direction names: make them strings and eval
    s = re.sub(r"\b(North|South|East|West)\b", r"'\1'", call)
    args = ast.literal_eval("(" + s[s.index("(") + 1:s.rindex(")")] + ")")
    return args


def path(dx, dy):
    dx %= N
    dy %= N
    if dx > N // 2:
        dx -= N
    if dy > N // 2:
        dy -= N
    mv = []
    mv += ["East"] * dx if dx > 0 else ["West"] * (-dx)
    mv += ["North"] * dy if dy > 0 else ["South"] * (-dy)
    return mv


out = list(src)
edits = []
nA = nB = 0
for i, l in enumerate(src):
    if not l.startswith("\tjf("):
        continue
    if not src[i + 1].startswith("\twait_until(tl + "):
        continue
    J, P, order = parse_P(l.strip())
    st = order[0]
    # which round: is there a use_item / harvest loop right after the wait?
    nxt = src[i + 2]
    if nxt.startswith("\tuse_item(Items.Water)") or nxt.startswith("\twhile (get_time() // WDT)"):
        # round A
        if nxt.startswith("\tuse_item"):
            a = i + 3
        else:
            a = next(k for k in range(i + 2, len(src)) if src[k] == "\tharvest()") + 1
        b = a
        while re.match(r"\tmove\(\w+\)$", src[b]):
            b += 1
        pre = [re.match(r"\tmove\((\w+)\)$", src[k]).group(1) for k in range(a, b)]
        vx = sum(DV[m][0] for m in pre)
        vy = sum(DV[m][1] for m in pre)
        L = []
        for c in range(len(J)):
            bx = sum(DV[m][0] for m in P[c][st])
            by = sum(DV[m][1] for m in P[c][st])
            mv = path(bx + vx, by + vy)
            L.append("\t%s c == %d:" % ("if" if c == 0 else "elif", c))
            L += ["\t\tmove(%s)" % m for m in mv] or ["\t\tpass"]
        edits.append((a, b, L))
        edits.append((i, i + 1, ["\tc = jfx" + l.strip()[2:]]))
        nA += 1
    else:
        edits.append((i, i + 1, ["\tjfx" + l.strip()[2:]]))
        nB += 1

for a, b, L in sorted(edits, reverse=True):
    out[a:b] = L

txt = "\n".join(out)
# jfx: jf without the walk back
jf0 = txt.index("def jf(J, P, order):")
jf1 = txt.index("\n\n\n", jf0)
body = txt[jf0:jf1]
assert body.rstrip().endswith("for m in P[cur][st]:\n\t\tmove(m)")
jfx = body.replace("def jf(", "def jfx(").rstrip()
jfx = jfx[:jfx.rindex("\tfor m in P[cur][st]:")] + "\treturn cur"
txt = txt[:jf1] + "\n\n\n" + jfx + txt[jf1:]
open(sys.argv[2], "w", newline="\n").write(txt)
print("free exits: round A %d, round B %d" % (nA, nB), file=sys.stderr)
