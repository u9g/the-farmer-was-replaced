# Hand the first harvest from the main drone to drone H: the main drone signals like every other
# drone and pre-travels to its round-B start during its round-A slack; H, once at its own round-B
# start (a grown round-A cactus), waits for all 32 signals (its own included) and harvests.
#   python hswap.py IN OUT H
import re, sys

src = open(sys.argv[1]).read().split("\n")
H = int(sys.argv[3])
fstart = {}
for i, l in enumerate(src):
    m = re.match(r"def (w\d+)\(", l)
    if m:
        fstart[int(m.group(1)[1:])] = i


def fend(k):
    return min([v for v in fstart.values() if v > fstart[k]] + [len(src)])


edits = []
# main
a = fstart[0]
w = next(i for i in range(a, fend(0)) if src[i].startswith("\twhile (get_time() // WDT) - num_items(Items.Water) < NSIG:"))
assert src[w + 1] == "\t\tpass" and src[w + 2] == "\tharvest()"
b = w + 3
while re.match(r"\tmove\(\w+\)$", src[b]):
    b += 1
edits.append((w, b, ["\tuse_item(Items.Water)"] + src[w + 3:b] + ["\twhile num_items(Items.Cactus) <= 0:", "\t\tpass"]))
# H
a = fstart[H]
w = next(i for i in range(a, fend(H)) if src[i] == "\twhile num_items(Items.Cactus) <= 0:")
edits.append((w, w, ["\twhile (get_time() // WDT) - num_items(Items.Water) < NSIG + 1:", "\t\tpass", "\tharvest()"]))
out = list(src)
for x, y, L in sorted(edits, reverse=True):
    out[x:y] = L
open(sys.argv[2], "w", newline="\n").write("\n".join(out))
