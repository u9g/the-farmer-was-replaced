# The fork helpers' tables (FS, MS, RS in hlp/own, written by fork2.py, FS renamed by spec.py)
# become tuple literals: a list literal costs a tick per element, a tuple literal one tick, and
# hlp/own only index and iterate them. A one-element move list is written (d,).
#   python tup.py IN OUT
import re, sys

src = open(sys.argv[1]).read().split("\n")


def conv(s):
    s = s.strip()
    if s.startswith("["):
        assert s.endswith("]")
        inner = s[1:-1]
        parts = []
        depth = 0
        cur = ""
        for ch in inner:
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
            if ch == "," and depth == 0:
                parts.append(cur)
                cur = ""
            else:
                cur += ch
        if cur.strip():
            parts.append(cur)
        parts = [conv(p) for p in parts]
        if not parts:
            return "[]"
        if len(parts) == 1:
            return "(" + parts[0] + ",)"
        return "(" + ", ".join(parts) + ")"
    return s


out = []
infn = False
n = 0
for l in src:
    m = re.match(r"def (\w+)\(", l)
    if m:
        infn = m.group(1) in ("hlp", "own")
    m = re.match(r"(\s*)(FS|MS|RS) = (\[.*\])$", l)
    if infn and m:
        l = m.group(1) + m.group(2) + " = " + conv(m.group(3))
        n += 1
    out.append(l)
open(sys.argv[2], "w", newline="\n").write("\n".join(out))
print("tuple tables:", n, file=sys.stderr)
