# Specialised fix routines: every fm(B, T) in a tail becomes a call to a routine written out for
# its direction lists (no list arguments, no loops over directions, no swap counter). The first
# and last fix of a tail keep the wait for an unplanted neighbour (measure() returning None);
# fixes inside a tail only see cells their own drone planted before the tail began.
#   python spec.py IN OUT
import re, sys

src = open(sys.argv[1]).read().split("\n")
AB = {"North": "N", "South": "S", "East": "E", "West": "W"}
need = {}


def name(B, T, safe):
    return "f%s%s_%s" % ("s" if safe else "", "".join(AB[d] for d in B), "".join(AB[d] for d in T))


def gen(B, T, safe):
    L = ["def %s():" % name(B, T, safe), "\twhile True:", "\t\tv = measure()"]
    vs = "ab"

    def side(D, cmp, ind):
        out = []
        for k, d in enumerate(D):
            out.append(ind + "%s = measure(%s)" % (vs[k], d))
        if safe:
            out.append(ind + "if " + " or ".join("%s == None" % vs[k] for k in range(len(D))) + ":")
            out.append(ind + "\tcontinue")
        return out

    L += side(B, ">", "\t\t")
    # B: swap the largest that is above v (first on ties)
    if len(B) == 1:
        L += ["\t\tif a > v:", "\t\t\tswap(%s)" % B[0]]
    else:
        L += ["\t\tif a > v:", "\t\t\tif b > a:", "\t\t\t\tswap(%s)" % B[1], "\t\t\telse:", "\t\t\t\tswap(%s)" % B[0],
              "\t\telif b > v:", "\t\t\tswap(%s)" % B[1]]
    L += ["\t\telse:"]
    if not T:
        L += ["\t\t\treturn"]
        return L
    L += side(T, "<", "\t\t\t")
    if len(T) == 1:
        L += ["\t\t\tif a < v:", "\t\t\t\tswap(%s)" % T[0], "\t\t\telse:", "\t\t\t\treturn"]
    else:
        L += ["\t\t\tif a < v:", "\t\t\t\tif b < a:", "\t\t\t\t\tswap(%s)" % T[1], "\t\t\t\telse:", "\t\t\t\t\tswap(%s)" % T[0],
              "\t\t\telif b < v:", "\t\t\t\tswap(%s)" % T[1], "\t\t\telse:", "\t\t\t\treturn"]
    return L


out = list(src)
i = 0
n = 0
while i < len(src):
    if src[i].startswith("\ttl = get_time()"):
        j = i + 1
        while not src[j].startswith("\twait_until(") and not src[j].startswith("\tif tl - hs"):
            j += 1
        idx = [k for k in range(i + 1, j) if re.match(r"\s*fm\(", src[k])]
        for k in idx:
            m = re.match(r"(\s*)fm\(\[(.*?)\], \[(.*?)\]\)$", src[k])
            ind, B, T = m.group(1), [x for x in m.group(2).split(", ") if x], [x for x in m.group(3).split(", ") if x]
            safe = k == idx[0] or k == idx[-1]
            need[(tuple(B), tuple(T), safe)] = 1
            out[k] = ind + name(B, T, safe) + "()"
            n += 1
        i = j
    i += 1
# the fork helpers' tables: [[B], [T]] pairs become the safe routines themselves
for k, l in enumerate(out):
    m = re.match(r"(\s*)FS = \[(.*)\]$", l)
    if not m:
        continue
    pairs = re.findall(r"\[\[([^\[\]]*)\], \[([^\[\]]*)\]\]", m.group(2))
    names = []
    for B, T in pairs:
        B = [x for x in B.split(", ") if x]
        T = [x for x in T.split(", ") if x]
        need[(tuple(B), tuple(T), True)] = 1
        names.append(name(B, T, True))
    out[k] = m.group(1) + "FS = [%s]" % ", ".join(names)
for k, l in enumerate(out):
    if "fmc(FS[j][0], FS[j][1])" in l:
        out[k] = l.replace("fmc(FS[j][0], FS[j][1])", "FS[j]()")
defs = []
for (B, T, safe) in sorted(need):
    if not B:
        raise SystemExit("empty B list")
    defs += gen(list(B), list(T), safe) + ["", ""]
for idx, l in enumerate(out):
    if re.match(r"def w\d+\(", l):
        break
out[idx:idx] = defs
open(sys.argv[2], "w", newline="\n").write("\n".join(out))
print("specialised %d fixes, %d routines" % (n, len(need)), file=sys.stderr)
