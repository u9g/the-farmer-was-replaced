"""gate.py IN OUT C [M]: spawn a tail helper only when the drone's remaining fix work
(C s per cell) would run past its deadline DL = max(tl + 0.9676, hb + M) (M default 2.6)."""
import sys, re
src=open(sys.argv[1]).read(); C=float(sys.argv[3]); M=sys.argv[4] if len(sys.argv)>4 else '2.6'
L=src.split('\n'); out=[]
for l in L:
    m=re.match(r'(\t*)TFS = \(',l)
    if m:
        ind=m.group(1)
        out+= [f'{ind}DL = tl + 0.9676', f'{ind}if DL < hb + {M}:', f'{ind}\tDL = hb + {M}']
    out.append(l)
src='\n'.join(out)
def sp(m):
    J,LO,E=int(m.group(1)),int(m.group(2)),int(m.group(3))
    return f'h = get_time() + {C*(E-J+1):.4f} > DL and spawn_drone(hlp, TFS, TMS, TRS, {J}, {LO}, {E})'
src,k=re.subn(r'h = spawn_drone\(hlp, TFS, TMS, TRS, (\d+), (\d+), (\d+)\)',sp,src); print('inline',k,file=sys.stderr)
src,k=re.subn(r'own\(TFS, TMS, TRS, (\d+), (\d+)\)',r'own(TFS, TMS, TRS, \1, \2, DL)',src); print('own calls',k,file=sys.stderr)
a='def own(FS, MS, RS, j, e):'; assert a in src; src=src.replace(a,'def own(FS, MS, RS, j, e, DL):')
a='\t\tif e - j >= 2:\n\t\t\ta = SP'; assert a in src
src=src.replace(a,f'\t\tif e - j >= 2 and get_time() + {C} * (e - j + 1) > DL:\n\t\t\ta = SP')
open(sys.argv[2],'w').write(src)
