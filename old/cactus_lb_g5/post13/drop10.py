"""Drop leaf (10,0) from w0's round B (2 actions) and w31's fertilizer (frees the cactus margin)."""
import sys
src, dst = sys.argv[1], sys.argv[2]
L = open(src).read().split("\n")


def find(seq, start=0):
    for i in range(start, len(L) - len(seq) + 1):
        if all(L[i + k] == seq[k] for k in range(len(seq))):
            return i
    raise SystemExit("not found: %r" % (seq,))


# 1. w31 fertilizer
i = find(["\t\t\t\t\t\t\tif use_item(Items.Fertilizer):", "\t\t\t\t\t\t\t\ttl = get_time() - 0.0988"])
del L[i:i + 2]
# 2. w0 round B: plant (9,0) once, no swap into (10,0)
i = find(["\tplant(Entities.Cactus)", "\tswap(East)", "\tplant(Entities.Cactus)", "\tmove(North)"], 19000)
del L[i + 1:i + 3]
b0 = i
# 3. junction cell 2 = (9,0): no East neighbour any more
i = find(["\tq2 = False", "\tmove(East)", "\tmove(South)"], b0)
j = i + 3
old_first = [
    "\t\tja = measure(North)",
    "\t\twhile ja == None:",
    "\t\t\tja = measure(North)",
    "\t\tjb = measure(East)",
    "\t\twhile jb == None:",
    "\t\t\tjb = measure(East)",
    "\t\tif ja >= v <= jb:",
    "\t\t\tbreak",
    "\t\tif jb < ja:",
    "\t\t\tswap(East)",
    "\t\telse:",
    "\t\t\tswap(North)",
]
k = find(old_first, j)
assert k - j < 20
L[k:k + len(old_first)] = [
    "\t\tja = measure(North)",
    "\t\twhile ja == None:",
    "\t\t\tja = measure(North)",
    "\t\tif ja >= v:",
    "\t\t\tbreak",
    "\t\tswap(North)",
]
old_inner = [
    "\t\t\tja = measure(North)",
    "\t\t\tjb = measure(East)",
    "\t\t\tif ja >= v <= jb:",
    "\t\t\t\tbreak",
    "\t\t\tif jb < ja:",
    "\t\t\t\tswap(East)",
    "\t\t\telse:",
    "\t\t\t\tswap(North)",
]
k2 = find(old_inner, k)
assert k2 - k < 20
L[k2:k2 + len(old_inner)] = ["\t\t\tja = measure(North)", "\t\t\tif ja >= v:", "\t\t\t\tbreak", "\t\t\tswap(North)"]
# cx == 2 block
c = find(["\t\telif cx == 2:"], k2)
old_cx = [
    "\t\t\t\tja = measure(North)",
    "\t\t\t\tjb = measure(East)",
    "\t\t\t\tif ja >= v <= jb:",
    "\t\t\t\t\tbreak",
    "\t\t\t\tif jb < ja:",
    "\t\t\t\t\tswap(East)",
    "\t\t\t\telse:",
    "\t\t\t\t\tswap(North)",
]
k3 = find(old_cx, c)
assert k3 - c < 25
L[k3:k3 + len(old_cx)] = ["\t\t\t\tja = measure(North)", "\t\t\t\tif ja >= v:", "\t\t\t\t\tbreak", "\t\t\t\tswap(North)"]
open(dst, "w").write("\n".join(L))
