"""Mechanical tick-saving rewrites of cactus_lb_entry.py.
python3 rw.py IN OUT PASSES   (PASSES: comma list of wait,xcas,inl,pk,end,tfs,tfsl,nitems,hlp,own)"""
import sys, re

src_path, out_path, passes = sys.argv[1], sys.argv[2], set(sys.argv[3].split(','))
L = open(src_path).read().split('\n')
ind = lambda l: len(l) - len(l.lstrip('\t'))


def top_def(name):
    """(start, end) line indexes of a top-level def, end exclusive (blank lines after dropped)"""
    s = next(i for i, l in enumerate(L) if l.startswith('def %s(' % name))
    e = s + 1
    while e < len(L) and (L[e] == '' or L[e].startswith('\t')):
        e += 1
    return s, e


def body_of(name):
    s, e = top_def(name)
    b = L[s + 1:e]
    while b and b[-1] == '':
        b.pop()
    return [l[1:] for l in b]  # dedent one level


def drop_def(name):
    s, e = top_def(name)
    del L[s:e]


def rename(lines, names, pre):
    out = []
    for l in lines:
        for n in names:
            l = re.sub(r'\b%s\b' % n, pre + n, l)
        out.append(l)
    return out


def inline_calls(pattern, make):
    """replace each statement line matching pattern (full line) with make(match) lines"""
    global L
    out = []
    for l in L:
        m = re.fullmatch(r'(\t*)' + pattern, l)
        if m and not l.lstrip().startswith('def '):
            t = m.group(1)
            out += [t + x for x in make(m)]
        else:
            out.append(l)
    L = out


# 1. wait_until(X) -> wuT = X; while get_time() < wuT: pass   (drops one def at startup)
if 'wait' in passes:
    drop_def('wait_until')
    inline_calls(r'wait_until\((.*)\)', lambda m: ['wuT = ' + m.group(2), 'while get_time() < wuT:', '\tpass'])

# 2. xcas / xcasw inlined and specialised on their literal `up` (saves the `if up` tick per call)
if 'xcas' in passes:
    def mk(wait):
        def f(m):
            d, up = m.group(2), m.group(3) not in ('0', 'False')
            r = ['xw = measure(%s)' % d, 'while xw == None:', '\txw = measure(%s)' % d]
            if wait:
                r += ['xt = get_time() + 0.05', 'while get_time() < xt:', '\tpass', 'xw = measure(%s)' % d]
            r += ['if measure() %s xw:' % ('>' if up else '<'), '\tswap(%s)' % d]
            return r
        return f
    drop_def('xcasw')
    drop_def('xcas')
    inline_calls(r'xcasw\((\w+), (\w+)\)', mk(True))
    inline_calls(r'xcas\((\w+), (\w+)\)', mk(False))

# 3. inline the two return-free fix routines called from only a few places
if 'inl' in passes:
    for name in ('fS_NE', 'fSW_E'):
        b = rename(body_of(name), ['v', 's', 'w', 'a', 'b', 'q'], 'i_')
        assert not any('return' in x for x in b)
        drop_def(name)
        inline_calls(name + r'\(\)', lambda m, b=b: b)

# 4. merge the pk_* pairs that differ only in one direction into parameterised functions
if 'pk' in passes:
    pairs = [('pkA', 'pk_East_North_None_0_0', 'pk_West_South_None_1_0', {'East': 'x', 'North': 'y'}, {'West': 'x', 'South': 'y'}),
             ('pkB', 'pk_East_North_West_0_1', 'pk_None_North_West_0_1', None, None),
             ('pkC', 'pk_West_South_East_1_1', 'pk_None_South_East_1_1', None, None)]
    for new, a, b, ma, mb in pairs:
        ba, bb = body_of(a), body_of(b)
        if ma is None:
            # differ in one direction token; find it
            diffs = [(x, y) for x, y in zip(ba, bb) if x != y]
            ta = {re.search(r'swap\((\w+)\)', x).group(1) for x, y in diffs}
            tb = {re.search(r'swap\((\w+)\)', y).group(1) for x, y in diffs}
            assert len(ta) == 1 and len(tb) == 1 and len(ba) == len(bb), (a, b, diffs)
            ta, tb = ta.pop(), tb.pop()
            nb = [x if x == y else x.replace('swap(%s)' % ta, 'swap(x)') for x, y in zip(ba, bb)]
            ca, cb = '%s(%s)' % (new, ta), '%s(%s)' % (new, tb)
            hdr = 'def %s(x):' % new
        else:
            sub = lambda body, m: [re.sub(r'\b(%s)\b' % '|'.join(m), lambda q: m[q.group(1)], l) for l in body]
            nb = sub(ba, ma)
            assert nb == sub(bb, mb), (a, b)
            ca = '%s(%s)' % (new, ', '.join(k for k in ma))
            cb = '%s(%s)' % (new, ', '.join(k for k in mb))
            hdr = 'def %s(x, y):' % new
        s, _ = top_def(a)
        drop_def(a)
        L[s:s] = [hdr] + ['\t' + x if x else x for x in nb] + ['', '']
        drop_def(b)
        L = [l.replace(a + '()', ca).replace(b + '()', cb) for l in L]

# 5. main drone's end: wait on the clocks first, then the drone count, so harvest follows the
#    last drone's end with only the count poll in between
if 'end' in passes:
    s = '\n'.join(L)
    old_w = '\twait_until(tl + 0.9676)\n\twhile num_drones() > 1:\n\t\tpass\n\twait_until(hm + 2.6)\n\tharvest()'
    old_i = ('\twuT = tl + 0.9676\n\twhile get_time() < wuT:\n\t\tpass\n\twhile num_drones() > 1:\n\t\tpass\n'
             '\twuT = hm + 2.6\n\twhile get_time() < wuT:\n\t\tpass\n\tharvest()')
    if old_w in s:
        s = s.replace(old_w, '\twait_until(tl + 0.9676)\n\twait_until(hm + 2.6)\n\twhile num_drones() > 1:\n\t\tpass\n\tharvest()')
    else:
        assert old_i in s
        s = s.replace(old_i, '\twuT = tl + 0.9676\n\twhile get_time() < wuT:\n\t\tpass\n\twuT = hm + 2.6\n'
                      '\twhile get_time() < wuT:\n\t\tpass\n\twhile num_drones() > 1:\n\t\tpass\n\tharvest()')
    L = s.split('\n')

# 6. hoist the constant TFS/TMS/TRS tuples of round B into round A's growth wait
#    (tfs: before the wait; tfsl: before the harvest-detect loop)
if 'tfs' in passes or 'tfsl' in passes:
    loop = 'tfsl' in passes
    mv = []
    for i, l in enumerate(L):
        if l.strip().startswith('TFS ='):
            j = i
            if loop:
                while 'while num_items(Items.Cactus)' not in L[j]:
                    j -= 1
                if L[j - 1].strip() == 'hb = 0':
                    j -= 1
            else:
                while not (L[j].strip().startswith('wait_until(tl + 0.9676)') or L[j].strip() == 'wuT = tl + 0.9676'):
                    j -= 1
            assert ind(L[j]) == ind(l) and all(ind(L[k]) >= ind(l) for k in range(j, i) if L[k].strip())
            mv.append((j, i))
    for j, i in sorted(mv, reverse=True):
        blk = L[i:i + 3]
        del L[i:i + 3]
        L[j:j] = blk

# 7. harvest-detect polls: `<= 0` -> `not` (one op less per pass)
if 'nitems' in passes:
    L = [l.replace('while num_items(Items.Cactus) <= 0:', 'while not num_items(Items.Cactus):') for l in L]

# 8. hlp: RS shifted by one (RS[j] instead of RS[j - 1]) and the back loop without the inner if
if 'hlp' in passes:
    s, e = top_def('hlp')
    L[s:e] = ['def hlp(FS, MS, RS, j, lo, e):',
              '\twhile j < e:',
              '\t\tfor d in MS[j]:',
              '\t\t\tmove(d)',
              '\t\tj += 1',
              '\tFS[j]()',
              '\twhile j > lo:',
              '\t\tfor d in RS[j]:',
              '\t\t\tmove(d)',
              '\t\tj -= 1',
              '\t\tFS[j]()',
              '', '']
    L = [re.sub(r'^(\t*TRS = \()', r'\1(), ', l) for l in L]

# 9. own: one subtraction for the spawn test, SP pre-shifted, no loop test per step
if 'own' in passes:
    s, e = top_def('own')
    sp = re.search(r'SP = \((.*)\)', '\n'.join(L[s:e])).group(1).split(', ')
    L[s:e] = ['def own(FS, MS, RS, j, e):',
              '\tSP = (%s)' % ', '.join(sp[1:]),
              '\twhile True:',
              '\t\tk = e - j',
              '\t\tif k >= 2:',
              '\t\t\tlo = j + SP[k]',
              '\t\t\th = spawn_drone(hlp, FS, MS, RS, j, lo, e)',
              '\t\t\tif h:',
              '\t\t\t\te = lo - 1',
              '\t\tFS[j]()',
              '\t\tif j == e:',
              '\t\t\treturn',
              '\t\tfor d in MS[j]:',
              '\t\t\tmove(d)',
              '\t\tj += 1',
              '', '']


# 10. diagonal fix chains: fSW_NE leaves its four neighbour values in globals (free stores); the
#     next fSW_NE of the chain, one diagonal step on, takes two of them instead of measuring
if 'kc' in passes:
    s, e = top_def('fSW_NE')
    body = L[s + 1:e]
    while body and body[-1] == '':
        body.pop()
    body = ['\tglobal KS', '\tglobal KW', '\tglobal KN', '\tglobal KE'] + body + ['\tKS = s', '\tKW = w', '\tKN = a', '\tKE = b']
    L[s + 1:e] = body + ['', '']
    def variant(name, sub):
        b = [l for l in body]
        for old, new in sub:
            k = b.index(old)
            b[k] = new
        return ['def %s():' % name] + b + ['', '']
    s, _ = top_def('fSW_NE')
    L[s:s] = ['KS = 0', 'KW = 0', 'KN = 0', 'KE = 0', '', ''] + variant('fSW_NEp', [('\ts = measure(South)', '\ts = KW'), ('\tb = measure(East)', '\tb = KN')]) + \
             variant('fSW_NEm', [('\tw = measure(West)', '\tw = KS'), ('\ta = measure(North)', '\ta = KE')])
    for i in range(len(L)):
        if L[i].strip() == 'fSW_NE()' and L[i - 3].strip() in ('fSW_NE()', 'fSW_NEp()', 'fSW_NEm()') and ind(L[i - 3]) == ind(L[i - 2]) == ind(L[i - 1]) == ind(L[i]):
            mv = (L[i - 2].strip(), L[i - 1].strip())
            t = L[i][:ind(L[i])]
            if mv == ('move(West)', 'move(North)'):
                L[i] = t + 'fSW_NEp()'
            elif mv == ('move(East)', 'move(South)'):
                L[i] = t + 'fSW_NEm()'

open(out_path, 'w').write('\n'.join(L))
