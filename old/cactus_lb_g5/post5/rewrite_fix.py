"""Rewrite the top-level fix routines (f[s]<low>_<high>) into cheaper op forms.

usage: python rewrite_fix.py IN OUT [--cachev]

Costs (tfwr_sim.rs): `if` 1 + each comparison step 1; `or`/`and` 1; a chained comparison
`a <= v >= b` costs only its steps (1 per link evaluated, stops at the first false link);
`not` is free; a `while` charges 1 when the statement starts and then only its condition per pass.

Form: the low-side bubble is an inner `while not <chain>:` (no per-pass `if`), the high-side exit
test is one chained comparison, and the None checks of the s-variants run once per outer pass
instead of on every swap pass (a planted neighbour never reads None again).
--cachev: after own swap, take v from the value swapped in instead of measure() (saves 1 read).
"""
import re
import sys

src = open(sys.argv[1]).read()
cachev = "--cachev" in sys.argv[3:]
peel = "--peel" in sys.argv[3:]
D = {"S": "South", "W": "West", "N": "North", "E": "East"}


def gen(name):
    m = re.match(r"f(s?)([SW]+)_([NE]+)$", name)
    safe, lo, hi = m.group(1) == "s", [D[c] for c in m.group(2)], [D[c] for c in m.group(3)]
    if safe and peel:
        # first pass (None checks, `continue` restarts it) up to its first high-side swap, then
        # the unchecked loop: once every neighbour has read non-None it stays planted
        a = body(lo, hi, True)
        b = body(lo, hi, False)
        return [f"def {name}():", "\twhile True:"] + ["\t" + x for x in a] + ["\t\tbreak"] + ["\twhile True:"] + ["\t" + x for x in b]
    return [f"def {name}():", "\twhile True:"] + ["\t" + x for x in body(lo, hi, safe)]


def body(lo, hi, safe):
    o = ["\t\tv = measure()"]
    names = ["a", "b"]
    for n, d in zip(names, lo):
        o.append(f"\t\t{n} = measure({d})")
    if safe:
        o.append("\t\tif " + " or ".join(f"{n} == None" for n in names[: len(lo)]) + ":")
        o.append("\t\t\tcontinue")
    if len(lo) == 2:
        o.append("\t\twhile not a <= v >= b:")
        o.append("\t\t\tif b > a:")
        o.append(f"\t\t\t\tswap({lo[1]})")
        if cachev:
            o.append("\t\t\t\tv = b")
        o.append("\t\t\telse:")
        o.append(f"\t\t\t\tswap({lo[0]})")
        if cachev:
            o.append("\t\t\t\tv = a")
        if not cachev:
            o.append("\t\t\tv = measure()")
        o.append(f"\t\t\ta = measure({lo[0]})")
        o.append(f"\t\t\tb = measure({lo[1]})")
    else:
        o.append("\t\twhile a > v:")
        o.append(f"\t\t\tswap({lo[0]})")
        o.append("\t\t\tv = a" if cachev else "\t\t\tv = measure()")
        o.append(f"\t\t\ta = measure({lo[0]})")
    for n, d in zip(names, hi):
        o.append(f"\t\t{n} = measure({d})")
    if safe:
        o.append("\t\tif " + " or ".join(f"{n} == None" for n in names[: len(hi)]) + ":")
        o.append("\t\t\tcontinue")
    if len(hi) == 2:
        o.append("\t\tif a >= v <= b:")
        o.append("\t\t\treturn")
        o.append("\t\tif b < a:")
        o.append(f"\t\t\tswap({hi[1]})")
        o.append("\t\telse:")
        o.append(f"\t\t\tswap({hi[0]})")
    else:
        o.append("\t\tif a >= v:")
        o.append("\t\t\treturn")
        o.append(f"\t\tswap({hi[0]})")
    return [x[1:] for x in o]


lines = src.split("\n")
out = []
i = 0
done = []
while i < len(lines):
    m = re.match(r"def (fs?[SW]+_[NE]+)\(\):$", lines[i])
    if m:
        out += gen(m.group(1))
        done.append(m.group(1))
        i += 1
        while i < len(lines) and (lines[i].startswith("\t") or lines[i] == "" and i + 1 < len(lines) and lines[i + 1].startswith("\t")):
            i += 1
        continue
    out.append(lines[i])
    i += 1
sys.stderr.write("rewrote %s\n" % done)
open(sys.argv[2], "w").write("\n".join(out))
