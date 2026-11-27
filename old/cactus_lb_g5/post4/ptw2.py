# Pre-travel checks (ptw.py output) as nested ifs: once get_time() >= e, the rest of the run of
# deferred moves is appended as one tuple, without a check per move.
#   python3 ptw2.py IN OUT
import sys, re
L = open(sys.argv[1]).read().split("\n")
def ind(s): return len(s) - len(s.lstrip("\t"))
def grp(i):
    if i + 3 < len(L):
        m = re.match(r"(\t*)if get_time\(\) < e:$", L[i])
        if m:
            t = m.group(1)
            m2 = re.match(re.escape(t) + r"\tmove\((\w+)\)$", L[i + 1])
            if m2 and L[i + 2] == t + "else:" and L[i + 3] == t + "\tP.append(%s)" % m2.group(1):
                return t, m2.group(1)
    return None
out = []; i = 0; runs = 0; loops = 0
while i < len(L):
    g = grp(i)
    if g:
        t = g[0]; mv = []
        while True:
            g2 = grp(i)
            if not g2 or g2[0] != t: break
            mv.append(g2[1]); i += 4
        def nest(k, tt):
            if k == len(mv): return []
            return [tt + "if get_time() < e:", tt + "\tmove(%s)" % mv[k]] + nest(k + 1, tt + "\t") + [tt + "else:", tt + "\tP.append((%s,))" % ", ".join(mv[k:])]
        out += nest(0, t)
        runs += 1
        continue
    if L[i].strip() == "for d in P:" and L[i + 1].strip() == "move(d)" and L[i - 1].strip() == "use_item(Items.Water)":
        t = L[i][:ind(L[i])]
        out += [t + "for q in P:", t + "\tfor d in q:", t + "\t\tmove(d)"]
        i += 2; loops += 1
        continue
    out.append(L[i]); i += 1
assert "P.append(" not in "\n".join(x for x in out if not x.strip().startswith("P.append(("))
open(sys.argv[2], "w", newline="\n").write("\n".join(out))
print("runs", runs, "loops", loops, file=sys.stderr)
