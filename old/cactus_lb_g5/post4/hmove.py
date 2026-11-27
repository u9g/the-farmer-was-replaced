# Move the first-harvest role (hswap's drone H) to drone NEW in a finished (nested) entry.
#   python3 hmove.py IN OUT NEW
import sys, re
L = open(sys.argv[1]).read().split("\n"); NEW = int(sys.argv[3])
POLL = "while (get_time() // WDT) - num_items(Items.Water) < NSIG + 1:"
def ind(s): return len(s) - len(s.lstrip("\t"))
i = next(k for k, l in enumerate(L) if l.strip() == POLL)
assert L[i + 1].strip() == "pass" and L[i + 2].strip() == "harvest()"
blk = L[i:i + 3]; t0 = ind(L[i])
del L[i:i + 3]
d = next(k for k, l in enumerate(L) if re.match(r"\t*def w%d\(\):$" % NEW, l))
bi = ind(L[d]) + 1
j = d + 1
while True:
    l = L[j]
    if l.strip() and ind(l) < bi: raise SystemExit("not found")
    if ind(l) == bi and l.strip() == "while num_items(Items.Cactus) <= 0:": break
    j += 1
L[j:j] = ["\t" * bi + b[t0:] for b in blk]
open(sys.argv[2], "w", newline="\n").write("\n".join(L))
