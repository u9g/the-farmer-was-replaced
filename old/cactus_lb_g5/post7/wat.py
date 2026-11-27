"""Water (4) the cell of a chunk's last round-B plant before planting it, and count the growth wait
from the plant before (as old/cactus_lb_g5/post4 wat2 does).

usage: python wat.py IN OUT LINE[,LINE...]   (LINE: 1-based line of the `tl = get_time()` that
follows the chunk's last plant, in IN)
"""
import sys

src, dst, lines = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")]
L = open(src).read().split("\n")
for ln in sorted(lines, reverse=True):
    i = ln - 1
    t = L[i]
    k = len(t) - len(t.lstrip("\t"))
    assert t.strip() == "tl = get_time()", (ln, t)
    assert L[i - 1] == "\t" * k + "plant(Entities.Cactus)", (ln, L[i - 1])
    assert L[i - 2].strip().startswith("move("), (ln, L[i - 2])
    assert L[i - 3].strip() == "plant(Entities.Cactus)", (ln, L[i - 3])
    p = "\t" * k
    new = [
        p + "if use_item(Items.Water, 4):",
        p + "\tplant(Entities.Cactus)",
        p + "\ttw = get_time() - 0.0988",
        p + "else:",
        p + "\tplant(Entities.Cactus)",
        p + "\ttw = 0",
        p + "tl = get_time()",
        p + "if tw:",
        p + "\ttl = tw",
    ]
    L[i - 1:i + 1] = new
open(dst, "w").write("\n".join(L))
