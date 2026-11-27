"""When each drone's own cacti finished growing, from a CACTUS_TRACE file.

Growth belongs to the cactus, not the cell: a swap moves a cactus with its growth progress, so a
drone's cacti can grow on cells it never planted. `plants_grown(path)` follows every planted
cactus through swaps and harvests and returns (planter drone, plant time, grown time or None).
`grown_by(rows, lo, hi)` gives, for each drone, when the last cactus it planted in [lo, hi) grew.
"""

DX = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}  # North East South West
N = 32


def plants_grown(path):
    rows = []      # [drone, plant time, grown time]
    at = {}        # cell -> index into rows of the cactus standing there
    for ln in open(path):
        f = ln.rstrip("\n").split("\t")
        if f[0] == "G":
            c = (int(f[3]), int(f[4]))
            i = at.get(c)
            if i is not None and rows[i][2] is None:
                rows[i][2] = float(f[1])
            continue
        if f[0] != "E" or f[7] != "200":
            continue
        t, d, k = float(f[1]), int(f[2]), f[3]
        c = (int(f[4]), int(f[5]))
        if k == "plant":
            at[c] = len(rows)
            rows.append([d, t, None])
        elif k == "swap":
            dx, dy = DX[int(f[6])]
            o = ((c[0] + dx) % N, (c[1] + dy) % N)
            a, b = at.pop(c, None), at.pop(o, None)
            if b is not None:
                at[c] = b
            if a is not None:
                at[o] = a
        elif k == "harvest":
            if len(f) > 9 and f[9] and float(f[9]) > 1e6:
                at.clear()  # a sorted harvest takes the whole field
            else:
                at.pop(c, None)
    return rows


def grown_by(rows, lo, hi):
    out = {}
    for d, t, g in rows:
        if lo <= t < hi and g is not None and g <= hi + 1e-9:
            out[d] = max(out.get(d, 0.0), g)
    return out
