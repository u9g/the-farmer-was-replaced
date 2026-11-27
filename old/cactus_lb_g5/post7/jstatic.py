"""Junction work lists: run the first pass over the cells (wk = [0..N-1], visited in order from
cur = 0) as straight-line code, then the work-list loop for what was queued again (qi = N).

usage: python jstatic.py IN OUT [MAXJ]   (MAXJ: transform at most this many junction blocks)
Same visiting order and same queueing as the loop, so the same actions in the same order; only
the dispatch ticks (while / index / += / cx and cur compare chains) of the first N visits go.
"""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
maxj = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
L = open(src).read().split("\n")


def ind(s):
    return len(s) - len(s.lstrip("\t"))


def block_end(i, k):
    """first line after i whose indent <= k (blank lines belong to the block)"""
    j = i + 1
    while j < len(L) and (L[j].strip() == "" or ind(L[j]) > k):
        j += 1
    return j


def dedent(lines, n):
    out = []
    for s in lines:
        assert s.strip() == "" or s.startswith("\t" * n), s
        out.append(s[n:])
    return out


def check_breaks(lines, base):
    """every break/continue in lines must sit inside a while/for that is also inside lines"""
    stack = []  # indents of open loops
    for s in lines:
        if not s.strip():
            continue
        k = ind(s)
        while stack and stack[-1] >= k:
            stack.pop()
        t = s.strip()
        if t in ("break", "continue"):
            assert stack, ("loose", t)
        if t.startswith("while ") or t.startswith("for "):
            stack.append(k)


out = []
i = 0
nj = 0
while i < len(L):
    line = L[i]
    m = re.match(r"^(\t*)while qi < qn:$", line)
    if not m or nj >= maxj:
        out.append(line)
        i += 1
        continue
    t = m.group(1)
    k0 = len(t)
    # header check (look back in out)
    hdr = out[-(1 + 3 + 0):]
    qn_line = [s for s in out[-12:] if s.strip().startswith("qn = ")]
    wk_line = [s for s in out[-12:] if s.strip().startswith("wk = [")]
    assert qn_line and wk_line, i
    N = int(qn_line[-1].split("=")[1])
    wk = eval(wk_line[-1].split("=", 1)[1])
    assert sorted(wk) == list(range(N)), (i, wk)
    cur_line = [x for x in out[-12:] if x.strip().startswith("cur = ")]
    cur0 = int(cur_line[-1].split("=")[1])
    end = block_end(i, k0)
    body = L[i + 1:end]
    assert body[0] == t + "\tcx = wk[qi]", (i, body[0])
    assert body[1] == t + "\tqi += 1", (i, body[1])
    # branches
    br = []  # (k, lines of branch body)
    j = 2
    while j < len(body):
        s = body[j]
        assert ind(s) == k0 + 1, (i, j, s)
        mm = re.match(r"^\t*(?:if|elif) cx == (\d+):$", s)
        if mm:
            kk = int(mm.group(1))
        else:
            assert s.strip() == "else:", (i, s)
            kk = None
        e = j + 1
        while e < len(body) and (body[e].strip() == "" or ind(body[e]) > k0 + 1):
            e += 1
        br.append((kk, body[j + 1:e]))
        j = e
    ks = [kk for kk, _ in br]
    assert ks[-1] is None and ks[:-1] == list(range(N - 1)), (i, ks)
    br[-1] = (N - 1, br[-1][1])
    static = []
    bmap = dict(br)
    prev = cur0
    for kk in wk:
        lines = bmap[kk]
        b = k0 + 2
        assert lines[0] == "\t" * b + "q%d = False" % kk, (i, lines[0])
        # cur chain
        p = 1
        moves = {}
        while True:
            s = lines[p]
            mm = re.match(r"^\t*(?:if|elif) cur == (\d+):$", s)
            if not mm or ind(s) != b:
                break
            if s.strip().startswith("if"):
                assert not moves
            e = p + 1
            while e < len(lines) and ind(lines[e]) > b:
                e += 1
            moves[int(mm.group(1))] = lines[p + 1:e]
            p = e
        assert lines[p] == "\t" * b + "cur = %d" % kk, (i, lines[p])
        fix = lines[p + 1:]
        check_breaks(fix, b)
        static.append("\t" * k0 + "q%d = False" % kk)
        if prev != kk:
            static.extend(dedent(moves[prev], 3))
        else:
            assert kk not in moves
        prev = kk
        static.extend(dedent(fix, 2))
    static.append("\t" * k0 + "cur = %d" % prev)
    static.append("\t" * k0 + "qi = %d" % N)
    out.extend(static)
    out.extend(L[i:end])
    nj += 1
    i = end
open(dst, "w").write("\n".join(out))
print("junction blocks:", nj, file=sys.stderr)


# ---- second step (DYN=1 env): drop the None-waiting first pass in the work-list loop's blocks
import os
if os.environ.get("DYN"):
    L = open(dst).read().split("\n")
    out = []
    i = 0
    nd = 0
    in_loop_end = -1
    while i < len(L):
        line = L[i]
        if re.match(r"^\t*while qi < qn:$", line):
            in_loop_end = block_end(i, ind(line))
        if i < in_loop_end and line.strip() == "while True:":
            k = ind(line)
            e = block_end(i, k)
            body = L[i + 1:e]
            if body and body[-1] == "\t" * (k + 1) + "break":
                # find the nested while True at k+1
                ws = [p for p, s in enumerate(body) if s == "\t" * (k + 1) + "while True:"]
                if len(ws) == 1:
                    p = ws[0]
                    pre = body[:p]
                    inner_end = p + 1
                    while inner_end < len(body) and (body[inner_end].strip() == "" or ind(body[inner_end]) > k + 1):
                        inner_end += 1
                    inner = body[p + 1:inner_end]
                    assert inner_end == len(body) - 1, (i, inner_end, len(body))
                    # pre without None waits
                    q = []
                    a = 0
                    while a < len(pre):
                        s = pre[a]
                        if re.match(r"^\t*while \w+ == None:$", s):
                            a += 2
                            continue
                        q.append(s)
                        a += 1
                    if dedent(inner, 1) == q:
                        out.append(line)
                        out.extend(dedent(inner, 1))
                        nd += 1
                        i = e
                        continue
                    else:
                        print("no match at", i, file=sys.stderr)
        out.append(line)
        i += 1
    open(dst, "w").write("\n".join(out))
    print("dynamic blocks unpeeled:", nd, file=sys.stderr)
