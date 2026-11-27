# python apply.py IN.py OUT.py : every post4 pass, in order (see README.md)
import os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__))
src, dst = sys.argv[1], sys.argv[2]
a, b = dst + ".a", dst + ".b"
run = lambda *c: subprocess.run([sys.executable, *c], check=True)
run(os.path.join(D, "apply_preplant.py"), src, a)
run(os.path.join(D, "apply_sync.py"), a, b, "19")
run(os.path.join(D, "wat2.py"), b, dst, "w3,w27,w15,w20")
os.remove(a); os.remove(b)
