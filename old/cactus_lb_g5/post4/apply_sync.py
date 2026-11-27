# Apply this corner's wins to a cactus entry:  python3 apply_sync.py IN OUT [H]
#   hmove.py H (first-harvest role to drone H, default 19), jq.py (cheaper junction worklists),
#   ptw2.py (nested pre-travel checks), lh.py (last round-A drone harvests itself)
import sys, subprocess, os
D = os.path.dirname(os.path.abspath(__file__))
src, dst = sys.argv[1], sys.argv[2]; H = sys.argv[3] if len(sys.argv) > 3 else "19"
steps = [["hmove.py", H], ["jq.py"], ["ptw2.py"], ["lh.py"]]
cur = src
for k, st in enumerate(steps):
    nxt = dst + ".s%d" % k
    subprocess.run([sys.executable, os.path.join(D, st[0]), cur, nxt] + st[1:], check=True)
    if cur != src: os.remove(cur)
    cur = nxt
os.replace(cur, dst)
