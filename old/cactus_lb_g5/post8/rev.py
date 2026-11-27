"""rev.py IN OUT W [CROSS]
Reverse the round-A planting walk of chunk W (2-wide chain with its junction at the walk's start),
so the walk ends at the junction: the tail settles it there instead of walking back the whole chunk.
CROSS = 'Xw:line_text:dir:up' optional: remove neighbour Xw's xcas on our first cell and do it ourselves."""
import sys, re
OPP={"North":"South","South":"North","East":"West","West":"East"}
D={"North":(0,1),"South":(0,-1),"East":(1,0),"West":(-1,0)}
src,dst,W=sys.argv[1:4]
L=open(src).read().split('\n')
start=[i for i,l in enumerate(L) if re.match(r'\s*def %s\(\):$'%W,l)][0]
ind=L[start+1][:len(L[start+1])-len(L[start+1].lstrip('\t'))]
i=start+1
toks=[]
while True:
    s=L[i].strip()
    if s.startswith('def '): raise SystemExit("nested def inside forward pass at %d"%i)
    m=re.match(r'move\((\w+)\)$',s)
    if m: toks.append(('M',m.group(1))); i+=1; continue
    if s=='till()' and L[i+1].strip()=='plant(Entities.Cactus)': toks.append(('TP',)); i+=2; continue
    m=re.match(r'if measure\(\) ([<>]) measure\((\w+)\):$',s)
    if m and L[i+1].strip()=='swap(%s)'%m.group(2): toks.append(('F',m.group(1),m.group(2))); i+=2; continue
    if s=='tl = get_time()': break
    raise SystemExit("unexpected line %d: %s"%(i+1,s))
tl_line=i
# tail prefix: xcas then moves up to 'wk = '
j=i+1; tailpre=[]
while not L[j].strip().startswith('wk = '):
    tailpre.append(L[j].strip()); j+=1
junction_start=j
# cells
pos=(0,0); cells=[]; incoming=[]; fixes={}; deploy=[]; cur_moves=[]
for t in toks:
    if t[0]=='M':
        dx,dy=D[t[1]]; pos=(pos[0]+dx,pos[1]+dy); cur_moves.append(t[1])
    elif t[0]=='TP':
        cells.append(pos); incoming.append(cur_moves); cur_moves=[]
    else:
        fixes.setdefault(len(cells)-1,[]).append((t[1],t[2]))
assert not cur_moves
idx={c:k for k,c in enumerate(cells)}
# reverse fixes: fix at cell k toward n=k+D, need n planted earlier (j<k); in reverse do it at n toward opp
rfix={}
for k,fl in fixes.items():
    for cmp,d in fl:
        n=(cells[k][0]+D[d][0],cells[k][1]+D[d][1])
        assert n in idx and idx[n]<k, (W,k,d)
        rfix.setdefault(idx[n],[]).append(('<' if cmp=='>' else '>', OPP[d]))
out=[]
def mv(a,b):
    r=[]; dx=b[0]-a[0]; dy=b[1]-a[1]
    r+=['move(%s)'%('East' if dx>0 else 'West')]*abs(dx)
    r+=['move(%s)'%('North' if dy>0 else 'South')]*abs(dy)
    return r
n=len(cells)
out+=mv((0,0),cells[-1])
tailx=[s for s in tailpre if s.startswith('xcas')]
tailm=[s for s in tailpre if s.startswith('move')]
assert len(tailx)+len(tailm)==len(tailpre)
for k in range(n-1,-1,-1):
    if k<n-1:
        # move from cells[k+1] to cells[k]: reverse of incoming[k+1]
        out+=['move(%s)'%OPP[d] for d in reversed(incoming[k+1])]
    out+=['till()','plant(Entities.Cactus)']
    for cmp,d in rfix.get(k,[]):
        out+=['if measure() %s measure(%s):'%(cmp,d),'\tswap(%s)'%d]
    if k==n-1:
        out+=tailx   # cut pair with the neighbour at the old end, now our first cell
out+=['tl = get_time()']
cross=sys.argv[4] if len(sys.argv)>4 else None
if cross:
    out+=[cross]
# junction start position: old end + tail moves
p=cells[-1]
for s in tailm:
    d=re.match(r'move\((\w+)\)',s).group(1); p=(p[0]+D[d][0],p[1]+D[d][1])
out+=mv(cells[0],p)
new=L[:start+1]+[ind+s for s in out]+L[junction_start:]
open(dst,'w').write('\n'.join(new))
print("cells",n,"deploy",len(mv((0,0),cells[-1])),"was",len(incoming[0]),"fixes",sum(len(v) for v in fixes.values()),"junction from c0 moves",len(mv(cells[0],p)))
