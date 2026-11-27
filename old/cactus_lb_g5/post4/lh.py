# The last drone to finish round A harvests itself instead of signalling; the harvester H only
# harvests if nobody did (two drones that finish together both signal).
#   python3 lh.py IN OUT
import sys, re
L = open(sys.argv[1]).read().split("\n")
C = "(get_time() // WDT) - num_items(Items.Water)"
out = []; n = 0; h = 0; i = 0
while i < len(L):
    l = L[i]
    t = l[:len(l) - len(l.lstrip("\t"))]
    if l.strip() == "use_item(Items.Water)" and L[i - 1].strip().startswith("wait_until(tl + "):
        out += [t + "if %s >= NSIG:" % C, t + "\tif get_entity_type() == Entities.Cactus:", t + "\t\tharvest()",
                t + "\telse:", t + "\t\tuse_item(Items.Water)", t + "else:", t + "\tuse_item(Items.Water)"]
        n += 1; i += 1; continue
    if l.strip() == "while %s < NSIG + 1:" % C:
        assert L[i + 1].strip() == "pass" and L[i + 2].strip() == "harvest()"
        out += [t + "while num_items(Items.Cactus) <= 0:", t + "\tif %s >= NSIG + 1:" % C, t + "\t\tharvest()"]
        h += 1; i += 3; continue
    out.append(l); i += 1
assert h == 1, h
open(sys.argv[2], "w", newline="\n").write("\n".join(out))
print("signals", n, file=sys.stderr)
