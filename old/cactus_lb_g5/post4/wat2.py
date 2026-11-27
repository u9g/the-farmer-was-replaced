"""Round-B growth shortcut by water (stackable post-pass on cactus_lb_entry.py).
In the chosen chunks, the cell of the drone's last round-B cactus gets N=4 water (volume 1.0, growth
5x) just before that cactus is planted, and the growth wait is counted from the plant before it
(as post3/fert.py does with fertilizer: tl = get_time() - 0.0988 right after the plant).
Why it is safe: the plant before it (p2) is at least 3 actions earlier (move/swap, water, plant),
so every other cactus is grown at the shortened wait end; the watered cactus is grown by then as
long as it stays on the wet cell 0.025 s (it grows 5x there); the drone's own next action is
0.033 s later, and the only foreign swap on these cells is xcasw, 0.05 s after the plant.
usage: python wat2.py IN OUT w3,w27,... [N]"""
import re, sys
src = open(sys.argv[1]).read().split("\n")
want = set(sys.argv[3].split(","))
N = sys.argv[4] if len(sys.argv) > 4 else "4"
stack = []; owner = []
for ln in src:
    if ln.strip():
        ind = len(ln) - len(ln.lstrip("\t"))
        while stack and stack[-1][0] >= ind:
            stack.pop()
        m = re.match(r"\s*def (\w+)\(", ln)
        if m:
            stack.append((ind, m.group(1)))
    cur = None
    for _, n in reversed(stack):
        if re.match(r"w\d+$", n):
            cur = n; break
    owner.append(cur)
last = {}
for i in range(len(src)):
    if src[i].strip() == "tl = get_time()" and owner[i] in want:
        last[owner[i]] = i
assert set(last) == want, (want - set(last))
for w, i in sorted(last.items(), key=lambda kv: -kv[1]):
    t = src[i][: len(src[i]) - len(src[i].lstrip("\t"))]
    if "Fertilizer" in src[i + 1]:
        # fertilized chunk: water the cell of the plant before the last one instead, and count
        # the wait from the plant before that one (1200 ticks more than get_time after the fert)
        assert src[i + 1] == t + "if use_item(Items.Fertilizer):" and src[i + 2] == t + "\ttl = get_time() - 0.0988", w
        assert src[i - 1] == t + "plant(Entities.Cactus)" and src[i - 2].startswith(t + "move(") and src[i - 3] == t + "plant(Entities.Cactus)", (w, src[i-3:i])
        src[i + 3:i + 3] = [t + "\tif WW:", t + "\t\ttl = tl - 0.0988"]
        src[i - 3:i - 3] = [t + "WW = use_item(Items.Water, %s)" % N]
        print(w, "fertilized: water before line", i - 2)
        continue
    j = i - 1
    while src[j].strip() != "plant(Entities.Cactus)":
        assert i - j <= 3 and (src[j].strip().startswith("if measure") or src[j].strip().startswith("swap(")), (w, src[j])
        j -= 1
    assert src[j] == t + "plant(Entities.Cactus)", (w, "indent")
    src[i + 1:i + 1] = [t + "if tw:", t + "\ttl = tw"]
    src[j:j + 1] = [t + "if use_item(Items.Water, %s):" % N, t + "\tplant(Entities.Cactus)", t + "\ttw = get_time() - 0.0988",
                    t + "else:", t + "\tplant(Entities.Cactus)", t + "\ttw = 0"]
    print(w, "plant line", j + 1)
open(sys.argv[2], "w").write("\n".join(src))
