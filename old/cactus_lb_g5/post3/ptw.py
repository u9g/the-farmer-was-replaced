# pre-travel inside the growth wait: moves between the round-A signal and the round-B wait are
# made before the signal while there is time before the drone's own growth deadline; the rest
# (moves commute on the torus) after the signal.  python ptw.py IN OUT [MARGIN]
import re, sys
src = open(sys.argv[1]).read().split("\n")
MARG = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0331
out = []
i = 0
n = 0
while i < len(src):
    l = src[i]
    m = re.match(r"(\t*)wait_until\(tl \+ ([0-9.]+)\)$", l)
    if m and i + 1 < len(src) and src[i + 1] == m.group(1) + "use_item(Items.Water)":
        ind, g = m.group(1), float(m.group(2))
        j = i + 2
        blk = []
        while not (src[j].startswith(ind + "while num_items(Items.Cactus) <= 0:") or src[j].startswith(ind + "while (get_time() // WDT)")):
            blk.append(src[j])
            j += 1
        assert all(len(b) - len(b.lstrip("\t")) >= len(ind) for b in blk)
        if any("move(" in b for b in blk):
            out.append(ind + "e = tl + %.4f" % (g - MARG))
            out.append(ind + "P = []")
            for b in blk:
                mm = re.match(r"(\t*)move\((\w+)\)$", b)
                if mm:
                    bi = mm.group(1)
                    out += [bi + "if get_time() < e:", bi + "\tmove(%s)" % mm.group(2), bi + "else:", bi + "\tP.append(%s)" % mm.group(2)]
                else:
                    assert "move" not in b, b
                    out.append(b)
            out.append(l)
            out.append(src[i + 1])
            out.append(ind + "for d in P:")
            out.append(ind + "\tmove(d)")
            n += 1
        else:
            out += [l, src[i + 1]] + blk
        i = j
        continue
    out.append(l)
    i += 1
print("pre-travel blocks", n, file=sys.stderr)
open(sys.argv[2], "w", newline="\n").write("\n".join(out))
