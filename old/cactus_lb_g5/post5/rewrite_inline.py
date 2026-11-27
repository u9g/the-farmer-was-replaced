"""Rewrite the inline junction fix loops (`while True:` blocks in the chunk functions) into the
cheaper op form used by rewrite_fix.py.

usage: python rewrite_inline.py IN OUT

Each block is parsed into (low dirs, high dirs, bookkeeping lines after each swap), the original
text is regenerated from that parse and must match exactly, else the block is left alone.
New form: the low-side bubble is `while not ja <= v >= jb:` (or `while ja > v:`), with no
`while ja == None` polls inside it (a neighbour that read non-None stays planted), and the high
side exits on one chained comparison.
"""
import re
import sys

PEEL = "--peel" in sys.argv[3:]

T = "\t"


def ind(l):
    return len(l) - len(l.lstrip(T))


def orig(lo, hi, bk):
    o = ["v = measure()"]
    for n, d in zip(("ja", "jb"), lo):
        o += [f"{n} = measure({d})", f"while {n} == None:", f"\t{n} = measure({d})"]

    def sw(d, k):
        return [T * k + f"swap({d})"] + [T * k + x for x in bk[d]]

    def hipart(k):
        h = []
        for n, d in zip(("ja", "jb"), hi):
            h += [T * k + x for x in (f"{n} = measure({d})", f"while {n} == None:", f"\t{n} = measure({d})")]
        if len(hi) == 2:
            h += [T * k + "if ja < v:", T * (k + 1) + "if jb < ja:"] + sw(hi[1], k + 2) + [T * (k + 1) + "else:"] + sw(hi[0], k + 2)
            h += [T * k + "elif jb < v:"] + sw(hi[1], k + 1)
        else:
            h += [T * k + "if ja < v:"] + sw(hi[0], k + 1)
        h += [T * k + "else:", T * (k + 1) + "break"]
        return h

    if len(lo) == 2:
        o += ["if ja > v:", "\tif jb > ja:"] + sw(lo[1], 2) + ["\telse:"] + sw(lo[0], 2)
        o += ["elif jb > v:"] + sw(lo[1], 1)
    else:
        o += ["if ja > v:"] + sw(lo[0], 1)
    o += ["else:"] + hipart(1)
    return o


def new(lo, hi, bk, polls=True):
    if PEEL and polls:
        # first pass with the None polls, up to its first high-side swap; then the loop without
        return new(lo, hi, bk, True, ) if False else (_new(lo, hi, bk, True) + ["while True:"] + ["\t" + x for x in _new(lo, hi, bk, False)] + ["break"])
    return _new(lo, hi, bk, polls)


def _new(lo, hi, bk, polls):
    o = ["v = measure()"]
    for n, d in zip(("ja", "jb"), lo):
        o += [f"{n} = measure({d})"] + ([f"while {n} == None:", f"\t{n} = measure({d})"] if polls else [])

    def sw(d, k):
        return [T * k + f"swap({d})"] + [T * k + x for x in bk[d]]

    if len(lo) == 2:
        o += ["while not ja <= v >= jb:", "\tif jb > ja:"] + sw(lo[1], 2) + ["\telse:"] + sw(lo[0], 2)
        o += ["\tv = measure()", f"\tja = measure({lo[0]})", f"\tjb = measure({lo[1]})"]
    else:
        o += ["while ja > v:"] + sw(lo[0], 1) + ["\tv = measure()", f"\tja = measure({lo[0]})"]
    for n, d in zip(("ja", "jb"), hi):
        o += [f"{n} = measure({d})"] + ([f"while {n} == None:", f"\t{n} = measure({d})"] if polls else [])
    if len(hi) == 2:
        o += ["if ja >= v <= jb:", "\tbreak", "if jb < ja:"] + sw(hi[1], 1) + ["else:"] + sw(hi[0], 1)
    else:
        o += ["if ja >= v:", "\tbreak"] + sw(hi[0], 0)
    return o


def parse(blk):
    reads = [re.match(r"\t*j[ab] = measure\((\w+)\)$", l) for l in blk]
    dirs = []
    for m in reads:
        if m and m.group(1) not in dirs:
            dirs.append(m.group(1))
    bk = {}
    for i, l in enumerate(blk):
        m = re.match(r"^(\t*)swap\((\w+)\)$", l)
        if m:
            k = len(m.group(1))
            b = []
            for x in blk[i + 1:]:
                if ind(x) < k or x.strip() in ("else:",) and ind(x) == k:
                    break
                b.append(x[k:])
            bk.setdefault(m.group(2), b)
    for nlo in (1, 2):
        lo, hi = dirs[:nlo], dirs[nlo:]
        if not (1 <= len(hi) <= 2) or any(d not in bk for d in lo + hi):
            continue
        if orig(lo, hi, bk) == blk:
            return lo, hi, bk
    return None


src = open(sys.argv[1]).read().split("\n")
out, i, n_ok, n_bad = [], 0, 0, 0
while i < len(src):
    l = src[i]
    if l.strip() == "while True:" and i > 528 and ind(l) > 1:
        k = ind(l)
        j = i + 1
        while j < len(src) and ind(src[j]) > k and src[j].strip():
            j += 1
        blk = [x[k + 1:] for x in src[i + 1:j]]
        p = parse(blk)
        if p and src[i + 1].strip() == "v = measure()":
            out.append(l)
            out += [T * (k + 1) + x for x in new(*p)]
            n_ok += 1
            i = j
            continue
        n_bad += 1
        sys.stderr.write(f"left alone: line {i + 1}\n")
    out.append(l)
    i += 1
sys.stderr.write(f"rewrote {n_ok} inline fix loops, left {n_bad}\n")
open(sys.argv[2], "w").write("\n".join(out))
