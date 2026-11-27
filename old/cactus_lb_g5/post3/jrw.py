# Rewrite junction-settle (jspec) blocks of cactus_lb_entry.py into cheaper equivalent code.
import sys, re
L = open(sys.argv[1]).read().split('\n')
def ind(s): return len(s) - len(s.lstrip('\t'))

def parse(blk):
    # blk: list of dedented lines, blk[0]=='while True:'
    s = [x.strip() for x in blk]
    i = 1
    assert s[i] == 'v = measure()'; i += 1
    assert s[i] == 'bi = -1'; i += 1
    assert s[i] == 'bv = v'; i += 1
    D = []
    while s[i].startswith('w = measure('):
        d = s[i][len('w = measure('):-1]
        assert s[i+1] == 'while w == None:' and s[i+2] == 'w = measure(%s)' % d
        assert s[i+3] == 'if w > bv:' and s[i+4] == 'bv = w' and s[i+5] == 'bi = %d' % len(D)
        D.append(d); i += 6
    def swaps(i, var, n, endkw):
        out = []
        for k in range(n):
            kw = 'if' if k == 0 else 'elif'
            assert s[i] == '%s %s == %d:' % (kw, var, k), (s[i], var, k)
            assert s[i+1] == 'swap(%s)' % (D if var == 'bi' else U)[k]
            i += 2
            extra = []
            while s[i].startswith('if not (') :
                m = re.match(r'if not \((\d+) in wk\):$', s[i]); assert m
                assert s[i+1] == 'wk.append(%s)' % m.group(1)
                extra.append(int(m.group(1))); i += 2
            out.append(extra)
        return i, out
    U = []
    i, DW = swaps(i, 'bi', len(D), None)
    if D:
        assert s[i] == 'else:'; i += 1
    assert s[i] == 'ti = -1'; i += 1
    assert s[i] == 'tv = v'; i += 1
    while s[i].startswith('w = measure('):
        d = s[i][len('w = measure('):-1]
        assert s[i+1] == 'while w == None:' and s[i+2] == 'w = measure(%s)' % d
        assert s[i+3] == 'if w < tv:' and s[i+4] == 'tv = w' and s[i+5] == 'ti = %d' % len(U)
        U.append(d); i += 6
    i, UW = swaps(i, 'ti', len(U), None)
    assert s[i] == 'else:' and s[i+1] == 'break', s[i:i+2]
    i += 2
    assert i == len(s), (i, len(s))
    return D, DW, U, UW

def emit(D, DW, U, UW, t):
    o = []
    def sw(d, wk, t):
        r = [t + 'swap(%s)' % d]
        for n in wk:
            r += [t + 'if not (%d in wk):' % n, t + '\twk.append(%d)' % n]
        return r
    def meas(var, d, t):
        return [t + '%s = measure(%s)' % (var, d), t + 'while %s == None:' % var, t + '\t%s = measure(%s)' % (var, d)]
    o.append(t + 'while True:')
    t1 = t + '\t'
    o.append(t1 + 'v = measure()')
    def part(dirs, wks, op, t, tail):
        # op '>' for D (swap with max), '<' for U (swap with min); first wins ties
        r = []
        for k, d in enumerate(dirs):
            r += meas('ja' if k == 0 else 'jb', d, t)
        if len(dirs) == 1:
            r += [t + 'if ja %s v:' % op] + sw(dirs[0], wks[0], t + '\t')
        elif len(dirs) == 2:
            r += [t + 'if ja %s v:' % op, t + '\tif jb %s ja:' % op] + sw(dirs[1], wks[1], t + '\t\t') + [t + '\telse:'] + sw(dirs[0], wks[0], t + '\t\t')
            r += [t + 'elif jb %s v:' % op] + sw(dirs[1], wks[1], t + '\t')
        else:
            raise Exception('len %d' % len(dirs))
        r += [t + 'else:'] + tail(t + '\t')
        return r
    def upart(t):
        if not U:
            return [t + 'break']
        return part(U, UW, '<', t, lambda tt: [tt + 'break'])
    if D:
        o += part(D, DW, '>', t1, upart)
    else:
        o += upart(t1)
    return o

out = []
i = 0; n = 0
while i < len(L):
    s = L[i]
    if s.strip() == 'while True:' and i + 2 < len(L) and L[i+1].strip() == 'v = measure()' and L[i+2].strip() == 'bi = -1':
        k = ind(s); j = i + 1
        while j < len(L) and (L[j].strip() == '' or ind(L[j]) > k):
            j += 1
        while L[j-1].strip() == '':
            j -= 1
        D, DW, U, UW = parse(L[i:j])
        out += emit(D, DW, U, UW, '\t' * k)
        n += 1
        i = j
    else:
        out.append(s); i += 1
open(sys.argv[2], 'w').write('\n'.join(out))
print('rewrote', n, 'blocks', file=sys.stderr)
