# Tail post-processing for a g5 entry (run after g5.py):
#   python post.py IN OUT
# 1. hswap.py   drone H (default 3) does the first harvest; the main drone signals and pre-travels
# 2. fork2.py   round-B fm tails get spawn checkpoints: a free drone slot becomes a helper that
#               takes the far end of the remaining fixes (NMIN=3)
# 3. fexit.py   a junction settle that ends a tail does not walk back to its first cell
# 4. spec.py    fm(B, T) calls become routines written out per direction list
# 5. jspec.py   junction settles written out in place
# 6. tup.py     the fork helpers' tables as tuple literals (1 tick each instead of 1 per element)
# 7. clean.py   drop the defs nothing calls any more
# g5.py runs this itself with POST=1 (before nesting the drone defs, NEST=1).
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
src, dst = sys.argv[1], sys.argv[2]
H = os.environ.get("HARVESTER", "3")
NMIN = os.environ.get("NMIN", "3")
steps = []
if H != "0":
    steps.append(["hswap.py", H])
steps += [["fork2.py", NMIN], ["fexit.py"], ["spec.py"], ["jspec.py"], ["tup.py"], ["clean.py", "fmc,fm,jf,jfx"]]
# POSTSTEPS=hswap,fork2,... keeps only those steps (for measuring the layers one by one)
keep = os.environ.get("POSTSTEPS")
if keep:
    keep = keep.split(",")
    steps = [st for st in steps if st[0][:-3] in keep or st[0] == "clean.py"]
cur = src
for k, st in enumerate(steps):
    nxt = dst + ".step%d" % k
    subprocess.run([sys.executable, os.path.join(HERE, st[0]), cur, nxt] + st[1:], check=True)
    if cur != src:
        os.remove(cur)
    cur = nxt
os.replace(cur, dst)
