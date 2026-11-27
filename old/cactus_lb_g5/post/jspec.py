# Junction settles written out in place: every jf(J, P, order) / jfx(...) call in a drone's code
# becomes the same worklist algorithm with the junction's cells, paths and directions as code
# instead of nested list arguments (88 ticks just to build those) walked by generic loops.
#   python jspec.py IN OUT
import re, sys, ast

src = open(sys.argv[1]).read().split("\n")


def parse(call):
    s = re.sub(r"\b(North|South|East|West)\b", r"'\1'", call)
    return ast.literal_eval("(" + s[s.index("(") + 1:s.rindex(")")] + ")")


def settle(c, e, ind):
    Bd, Td, kB, kT = e
    L = [ind + "while True:", ind + "\tv = measure()"]
    I = ind + "\t"

    def side(D, K, gt, elsepart):
        out = []
        if not D:
            return elsepart(I)
        out.append(I + "bi = -1")
        out.append(I + "bv = v")
        for i, d in enumerate(D):
            out.append(I + "w = measure(%s)" % d)
            out.append(I + "while w == None:")
            out.append(I + "\tw = measure(%s)" % d)
            out.append(I + "if w %s bv:" % gt)
            out.append(I + "\tbv = w")
            out.append(I + "\tbi = %d" % i)
        for i, d in enumerate(D):
            out.append(I + ("if" if i == 0 else "elif") + " bi == %d:" % i)
            out.append(I + "\tswap(%s)" % d)
            if K[i] >= 0:
                out.append(I + "\tif not (%d in wk):" % K[i])
                out.append(I + "\t\twk.append(%d)" % K[i])
        out.append(I + "else:")
        inner = elsepart(I + "\t")
        return out + inner

    def tside(I2):
        if not Td:
            return [I2 + "break"]
        out = [I2 + "ti = -1", I2 + "tv = v"]
        for i, d in enumerate(Td):
            out.append(I2 + "w = measure(%s)" % d)
            out.append(I2 + "while w == None:")
            out.append(I2 + "\tw = measure(%s)" % d)
            out.append(I2 + "if w < tv:")
            out.append(I2 + "\ttv = w")
            out.append(I2 + "\tti = %d" % i)
        for i, d in enumerate(Td):
            out.append(I2 + ("if" if i == 0 else "elif") + " ti == %d:" % i)
            out.append(I2 + "\tswap(%s)" % d)
            if kT[i] >= 0:
                out.append(I2 + "\tif not (%d in wk):" % kT[i])
                out.append(I2 + "\t\twk.append(%d)" % kT[i])
        out.append(I2 + "else:")
        out.append(I2 + "\tbreak")
        return out

    if Bd:
        L += side(Bd, kB, ">", tside)
    else:
        L += tside(I)
    return L


def moves_from(P, c, ind, n):
    """moves from the current cell (variable cur) to cell c"""
    L = []
    first = True
    for x in range(n):
        if x == c or not P[x][c]:
            continue
        L.append(ind + ("if" if first else "elif") + " cur == %d:" % x)
        first = False
        L += [ind + "\tmove(%s)" % m for m in P[x][c]]
    return L


N = 32
DV = {"North": (0, 1), "South": (0, -1), "East": (1, 0), "West": (-1, 0)}


def tpath(dx, dy):
    dx %= N
    dy %= N
    if dx > N // 2:
        dx -= N
    if dy > N // 2:
        dy -= N
    return (["East"] * dx if dx > 0 else ["West"] * (-dx)) + (["North"] * dy if dy > 0 else ["South"] * (-dy))


FUSE = __import__("os").environ.get("FUSE", "0") == "1"
out = []
n = 0
skip = 0
for li, l in enumerate(src):
    if skip:
        skip -= 1
        continue
    m = re.match(r"(\s*)(c = )?(jfx?)\((.*)\)$", l)
    if not m or not l.strip().startswith(("jf(", "jfx(", "c = jfx(")):
        out.append(l)
        continue
    ind, asg, fn, _ = m.groups()
    J, P, order = parse(l.strip()[len(asg or ""):])
    st = order[0]
    nc = len(J)
    L = [ind + "wk = [%s]" % ", ".join(str(x) for x in order), ind + "cur = %d" % st, ind + "while len(wk) > 0:", ind + "\tcx = wk.pop(0)"]
    for k, c in enumerate(range(nc)):
        L.append(ind + "\t" + ("if" if k == 0 else "elif") + " cx == %d:" % c)
        L += moves_from(P, c, ind + "\t\t", nc)
        L.append(ind + "\t\tcur = %d" % c)
        L += settle(c, J[c], ind + "\t\t")
    if fn == "jf":
        after = []
        j = li + 1
        while FUSE and re.match(re.escape(ind) + r"move\((\w+)\)$", src[j]):
            after.append(re.match(re.escape(ind) + r"move\((\w+)\)$", src[j]).group(1))
            j += 1
        if after:
            skip = len(after)
            vx = sum(DV[m][0] for m in after)
            vy = sum(DV[m][1] for m in after)
            first = True
            for x in range(nc):
                mv = tpath(sum(DV[m][0] for m in P[x][st]) + vx, sum(DV[m][1] for m in P[x][st]) + vy)
                L.append(ind + ("if" if first else "elif") + " cur == %d:" % x)
                first = False
                L += [ind + "	move(%s)" % m for m in mv] or [ind + "	pass"]
        else:
            L += moves_from(P, st, ind, nc)
    if asg:
        L.append(ind + "c = cur")
    out += L
    n += 1
open(sys.argv[2], "w", newline="\n").write("\n".join(out))
print("junction settles written out:", n, file=sys.stderr)
