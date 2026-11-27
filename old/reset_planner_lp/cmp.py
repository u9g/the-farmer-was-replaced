# per-stretch predicted (schedule) vs executed (profile) times
import pickle, re, sys
b, (t, sb), (t0, sc) = pickle.load(open(sys.argv[1], 'rb'))
use = sb if sys.argv[3] == 'best' else sc
ex = {}
for l in open(sys.argv[2]):
    m = re.match(r'\s+[\d:.]+s?\s+([\d:.]+s?)\s+(\w+(?: \d+)?)\s+(\S+)', l)
    if m:
        x = m.group(1).rstrip('s').split(':'); ex[m.group(2)] = float(x[0]) * 60 + float(x[1]) if len(x) == 2 else float(x[0])
def lab(u):
    n = u[0].capitalize(); return n if u[0] in ('plant', 'sunflowers') or (u[0] == 'polyculture') else f'{n} {u[1]}'
tp = te = 0
for u, acts, used in use:
    L = sum(x for x, _ in used); E = ex.get(lab(u), ex.get(u[0].capitalize() + ' ' + str(u[1]), 0))
    tp += L; te += E
    print(f"{lab(u):15} pred {L:6.1f} exec {E:6.1f} {E - L:+6.1f}  {[(k[1] if k[0] in ('hwc', 'mix') else k[0], round(float(x), 1)) for x, k in used]}  {({k: round(v) for k, v in acts.items()})}")
print(f'total pred {tp:.0f} exec {te:.0f}')
