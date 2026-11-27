"""Post-process the entry: chosen round-B chunks fertilize their last planted cactus (instantly
grown) and count their growth wait from the plant before it (2 actions earlier).
usage: python fert.py IN OUT LINE[,LINE...]   (LINE = 1-based line of the chunk's last plant in IN)
Each LINE must be 'plant(Entities.Cactus)' followed by 'tl = get_time()'."""
import sys

src = open(sys.argv[1]).read().split("\n")
lines = [int(x) for x in sys.argv[3].split(",") if x]
SUB = sys.argv[4] if len(sys.argv) > 4 else "0.0988"   # 600 ticks
for L in sorted(lines, reverse=True):
    i = L - 1
    assert src[i].strip() == "plant(Entities.Cactus)", (L, src[i])
    assert src[i + 1].strip() == "tl = get_time()", (L, src[i + 1])
    t = src[i + 1][: len(src[i + 1]) - len(src[i + 1].lstrip("\t"))]
    src[i + 2:i + 2] = [t + "if use_item(Items.Fertilizer):", t + "\ttl = get_time() - " + SUB]
open(sys.argv[2], "w").write("\n".join(src))
