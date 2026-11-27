# Specialise pk2(dp, df, de, lo, nx) per call-site constant tuple (same behaviour, fewer ticks).
import sys, re
src = open(sys.argv[1]).read()
KA, KB, KP = 3, 6, 6
assert 'KA = 3\nKB = 6\nKP = 6\n' in src
P = 'plant(Entities.Cactus)'
def gen(dp, df, de, lo, nx):
    name = 'pk_%s_%s_%s_%d_%d' % (dp, df, de, lo, nx)
    # thresholds on the raw measure m: v = m if lo else 9 - m
    if lo:
        ka, kb, kp = 'v <= %d' % KA, 'v >= %d' % KB, 'measure() >= %d' % KP
    else:
        ka, kb, kp = 'v >= %d' % (9 - KA), 'v <= %d' % (9 - KB), 'measure() <= %d' % (9 - KP)
    o = ['def %s():' % name, '\tglobal PD', '\t' + P]
    if nx:
        # PD branch
        o += ['\tif PD:',
              '\t\tif %s:' % kp,
              '\t\t\tswap(%s)' % de, '\t\t\t' + P,
              '\t\t\tswap(%s)' % dp, '\t\t\t' + P,
              '\t\t\tPD = False',
              '\t\t\tmove(%s)' % df, '\t\t\t' + P, '\t\t\tmove(%s)' % de,
              '\t\t\treturn',
              '\t\tswap(%s)' % dp, '\t\t' + P, '\t\tPD = False']
        o += ['\tv = measure()',
              '\tif %s:' % ka,
              '\t\tswap(%s)' % df, '\t\t' + P,
              '\t\tmove(%s)' % de, '\t\t' + P, '\t\tmove(%s)' % df,
              '\telif %s:' % kb,
              '\t\tswap(%s)' % de, '\t\t' + P,
              '\t\tmove(%s)' % df, '\t\t' + P, '\t\tmove(%s)' % de,
              '\telse:',
              '\t\tmove(%s)' % de, '\t\t' + P, '\t\tmove(%s)' % df,
              '\t\tPD = True']
    else:
        o += ['\tif PD:', '\t\tswap(%s)' % dp, '\t\t' + P, '\t\tPD = False',
              '\tswap(%s)' % df, '\t' + P]
    return name, '\n'.join(o) + '\n\n\n'
calls = sorted(set(re.findall(r'pk2\((\w+), (\w+), (\w+), (\d), (\d)\)', src)))
defs = ''
for c in calls:
    if c == ('dp', 'df', 'de', 'lo', 'nx'):
        continue
    name, d = gen(c[0], c[1], c[2], int(c[3]), int(c[4]))
    defs += d
    src = src.replace('pk2(%s, %s, %s, %s, %s)' % c, name + '()')
# replace the pk2 definition with the specialised ones
i = src.index('def pk2(dp, df, de, lo, nx):')
j = src.index('\ndef hlp(')
src = src[:i] + defs + src[j + 1:]
open(sys.argv[2], 'w').write(src)
print(len(calls), file=sys.stderr)
