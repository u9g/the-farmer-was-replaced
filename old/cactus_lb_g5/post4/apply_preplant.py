"""Round-A pre-planting of dead-end cells by passing drones (deployment researcher, -0.014 s).

A 3-wide column's end cell is a dead end in its owner's round-A walk:
    move(D); till(); plant(Entities.Cactus); move(opposite D)
Ten such cells lie on another drone's launch flight (after that drone's last spawn) well
before (>= 6 actions) the owner gets there. The flyer tills and plants the cell as it passes
(+2 actions for it); the owner drops those 4 lines (-4 actions). Picks chosen with an
empirical model of both rounds (round-A done times, round-B pre-travel and work per drone,
256 traced seeds) so that late round-B drones are not made later.

usage: python apply_preplant.py IN_ENTRY.py OUT_ENTRY.py
Works on the nested g5 entry (w0..w31). Every pick is checked against the code; a pick whose
flight cell or dead-end pattern is missing is skipped with a warning.
"""
import re, sys

PICKS = [("w19", (10, 0)), ("w20", (24, 0)), ("w11", (3, 22)), ("w12", (13, 12)), ("w8", (17, 2)),
         ("w25", (16, 0)), ("w18", (4, 0)), ("w23", (21, 31)), ("w5", (4, 13)), ("w16", (16, 19))]
DV = {'North': (0, 1), 'South': (0, -1), 'East': (1, 0), 'West': (-1, 0)}
OPP = {'North': 'South', 'South': 'North', 'East': 'West', 'West': 'East'}
N = 32


def indent(l):
    return len(l) - len(l.lstrip('\t'))


def unnest(text):
    src = text.split('\n')
    i0 = next(i for i, l in enumerate(src) if re.match(r"def w\d+\(\):", l))
    funcs, order = {}, []

    def parse(i, lvl):
        name = re.match(r"\t*def (w\d+)\(\):$", src[i]).group(1)
        order.append(name)
        body = []
        i += 1
        while i < len(src) and (src[i] == '' or indent(src[i]) > lvl):
            l = src[i]
            if l == '':
                i += 1
                continue
            if indent(l) == lvl + 1 and re.match(r"\t*def w\d+\(\):$", l):
                i = parse(i, lvl + 1)
                continue
            body.append('\t' + l[lvl + 1:])
            i += 1
        funcs[name] = body
        return i

    i = parse(i0, 0)
    return src[:i0], funcs, order, src[i:]


def nest(head, funcs, tail):
    def emit(name, ind):
        out = [ind + "def %s():" % name]
        for l in funcs[name]:
            m = re.match(r"\tspawn_drone\((w\d+)\)$", l)
            if m:
                out += emit(m.group(1), ind + "\t")
            out.append(ind + l)
        return out
    return "\n".join(head + emit("w0", "") + [""] + tail)


def prefix(body):
    pre = []
    for l in body:
        m = re.match(r"\tmove\((\w+)\)$", l)
        s = re.match(r"\tspawn_drone\((w\d+)\)$", l)
        if m:
            pre.append(('m', m.group(1)))
        elif s:
            pre.append(('s', s.group(1)))
        else:
            break
    return pre


def step(p, d):
    return ((p[0] + DV[d][0]) % N, (p[1] + DV[d][1]) % N)


def main(src, dst):
    head, f, order, tail = unnest(open(src).read())
    pres, starts, flight = {}, {}, {}

    def go(name, p):
        pre = prefix(f[name])
        pres[name] = pre
        last = max([j for j, (k, v) in enumerate(pre) if k == 's'], default=-1)
        cells = {}
        for j, (k, v) in enumerate(pre):
            if k == 'm':
                p = step(p, v)
                if j > last:
                    cells[p] = j
            else:
                go(v, p)
        flight[name], starts[name] = cells, p
    go('w0', (0, 0))
    dead = {}
    for n in order:
        b, p = f[n], starts[n]
        for i in range(len(pres[n]), len(b)):
            l = b[i]
            if l == '\ttl = get_time()':
                break
            m = re.match(r"\tmove\((\w+)\)$", l)
            if m:
                p = step(p, m.group(1))
                if b[i + 1:i + 3] == ['\ttill()', '\tplant(Entities.Cactus)'] and b[i + 3] == '\tmove(%s)' % OPP[m.group(1)]:
                    dead[p] = (n, i)
    ins, rm = {}, {}
    for fl, c in PICKS:
        if fl not in flight or c not in flight[fl] or c not in dead or dead[c][0] == fl:
            print('skipped pick', fl, c, file=sys.stderr)
            continue
        ins.setdefault(fl, []).append(flight[fl][c])
        rm.setdefault(dead[c][0], []).append(dead[c][1])
    for n in order:
        b = f[n]
        for i in sorted(rm.get(n, []), reverse=True):
            del b[i:i + 4]
        for j in sorted(ins.get(n, []), reverse=True):
            b[j + 1:j + 1] = ['\ttill()', '\tplant(Entities.Cactus)']
    open(dst, 'w', newline='\n').write(nest(head, f, tail))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
