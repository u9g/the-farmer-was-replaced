# drop top-level defs nothing calls any more (of the names given; a name still called outside its
# own def is kept, so a partial post.py run, POSTSTEPS=..., stays valid)
import re, sys
src = open(sys.argv[1]).read().split("\n")
names = sys.argv[3].split(",")


def strip(src, drop):
    out = []
    skip = False
    for l in src:
        m = re.match(r"def (\w+)\(", l)
        if m:
            skip = m.group(1) in drop
        elif l and not l.startswith(("\t", " ")):
            skip = False
        if not skip:
            out.append(l)
    return out


drop = set(names)
while True:
    rest = "\n".join(strip(src, drop))
    used = {n for n in drop if re.search(r"\b%s\(" % n, rest)}
    if not used:
        break
    drop -= used
txt = "\n".join(strip(src, drop))
txt = re.sub(r"\n{4,}", "\n\n\n", txt)
open(sys.argv[2], "w", newline="\n").write(txt)
