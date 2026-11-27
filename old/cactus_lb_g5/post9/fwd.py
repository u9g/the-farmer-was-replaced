"""fwd.py IN OUT [F] [MODE]: forked helper walks only to its first cell and fixes forward.
MODE=plain: helper fixes lo..e itself. MODE=own: helper calls own(lo, e) (can fork again)."""
import sys, re
src=open(sys.argv[1]).read(); F=float(sys.argv[3]) if len(sys.argv)>3 else 1.5
MODE=sys.argv[4] if len(sys.argv)>4 else 'plain'; M=2
def best(n):
    return min(range(1,n),key=lambda a:(max(a*F+(a-1)*M,a*M+(n-a)*F+(n-a-1)*M),-a))
import os
OLD=(0, 0, 0, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10, 10, 11, 12, 13, 13, 14, 15, 16, 16, 17, 18, 19, 20, 20, 21, 22)
K=int(os.environ.get('K','-99'))
SPN=[0,0,0]+[best(n) for n in range(3,30)] if K==-99 else [0,0,0]+[max(1,min(n-1,OLD[n]+K)) for n in range(3,30)]
old_h=re.search(r'def hlp\(FS, MS, RS, j, lo, e\):\n(\t.*\n)+',src).group(0)
if MODE=='own':
    new_h='def hlp(FS, MS, RS, j, lo, e):\n\twhile j < lo:\n\t\tfor d in MS[j]:\n\t\t\tmove(d)\n\t\tj += 1\n\town(FS, MS, RS, j, e)\n'
else:
    new_h='def hlp(FS, MS, RS, j, lo, e):\n\twhile j < lo:\n\t\tfor d in MS[j]:\n\t\t\tmove(d)\n\t\tj += 1\n\twhile j <= e:\n\t\tFS[j]()\n\t\tif j < e:\n\t\t\tfor d in MS[j]:\n\t\t\t\tmove(d)\n\t\tj += 1\n'
src=src.replace(old_h,new_h)
src,k=re.subn(r'SP = \((\d+, )+\d+\)','SP = ('+', '.join(map(str,SPN))+')',src); assert k==1
cnt=[0]
def rep(m):
    J,LO,E=int(m.group(2)),int(m.group(3)),int(m.group(4))
    NL=J+SPN[E-J+1]; cnt[0]+=1
    s=m.group(0)
    s=s.replace(f'spawn_drone(hlp, TFS, TMS, TRS, {J}, {LO}, {E})',f'spawn_drone(hlp, TFS, TMS, TRS, {J}, {NL}, {E})')
    s=s.replace(f'own(TFS, TMS, TRS, {J}, {LO-1})',f'own(TFS, TMS, TRS, {J}, {NL-1})')
    return s
src=re.sub(r'(h = spawn_drone\(hlp, TFS, TMS, TRS, (\d+), (\d+), (\d+)\)\n\t*if h:\n\t*own\(TFS, TMS, TRS, \d+, \d+\))',rep,src)
print('SPN',SPN,'inline',cnt[0],file=sys.stderr)
assert src.count('spawn_drone(hlp')==cnt[0]+1
open(sys.argv[2],'w').write(src)
