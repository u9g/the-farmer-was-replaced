# Offline planner for run_reset.py's cactus bands: the snake of 2-wide antidiagonal bands (the
# same construction as bd_path in run_reset.py), its mixed cells, and the cut of the snake into one
# stretch per drone with the number of cells each drone fixes on its walk back, minimising the
# latest finish under a cost model of the round. Prints the bd_cuts() table.
#
#     python bands.py
import sys

import sys
def band_cells(n,s):
    r=[]
    for i in range(n):
        if 0<=s+1-i<n: r.append((i,s+1-i))
        if 0<=s-i<n: r.append((i,s-i))
    return r
def build(n,o):
    path=[]; j=0; prev_s=None
    s=o-3
    while s<=2*n-2:
        b=band_cells(n,s)
        if b:
            if j%2: b=b[::-1]
            if not path:
                path=b[:]
            else:
                best=None
                for da in range(3):
                    for db in range(3):
                        if da>=len(path) or db>=len(b): continue
                        E=path[-1-da]; F=b[db]
                        if E[0]+E[1]!=prev_s+1 or F[0]+F[1]!=prev_s+3: continue
                        for C in [(E[0]+1,E[1]),(E[0],E[1]+1)]:
                            if C[0]<n and C[1]<n and abs(C[0]-F[0])+abs(C[1]-F[1])==1:
                                if best is None or da+db<best[0]: best=(da+db,da,db,C)
                if best is None:
                    break
                _,da,db,C=best
                for _ in range(da): path.pop()
                path.append(C); path+=b[db:]
            prev_s=s; j+=1
        s+=3
    return path

def plan(n, o=0):
    p = build(n, o)
    idx = {c:k for k,c in enumerate(p)}
    NB=[];MX=[]
    for k,(x,y) in enumerate(p):
        nb=[]; lo=up=0
        for (dx,dy,low) in [(0,-1,True),(-1,0,True),(0,1,False),(1,0,False)]:
            q=(x+dx,y+dy)
            if q in idx:
                nb.append((idx[q],low)); lo+=low; up+= (not low)
        NB.append(nb); MX.append(lo>0 and up>0)
    near=list(MX)
    for k in range(len(p)):
        if MX[k]:
            for e in NB[k]: near[e[0]]=True
    return p, NB, MX, near

A = 200/6075
# cost constants (seconds); calibrated against the simulator
C = dict(travel=A*1.05, fwd=2*A+0.008, inl=0.33*A+0.006, dfr=1.33*A+0.010, jx=0.45, grow=1.0, start=0.135, bnd=0.004)
def dist(p, q, n):
    dx = (q[0]-p[0]) % n; dx = min(dx, n-dx)
    dy = (q[1]-p[1]) % n; dy = min(dy, n-dy)
    return dx+dy
def junction_ids(p, MX, NB):
    # group mixed cells into junctions (connected through neighbours)
    L=len(p); g=[-1]*L; ng=0
    for k in range(L):
        if MX[k] and g[k]<0:
            st=[k]; g[k]=ng
            while st:
                c=st.pop()
                for q,_ in NB[c]:
                    if MX[q] and g[q]<0: g[q]=ng; st.append(q)
            ng+=1
    return g, ng
JL = {}
def chunk_cost(a, b, m, p, MX, g, P, n, C):
    # returns (finish time, tail time); a junction counts where its last mixed cell is
    f = b - m
    arrive = C['start'] + dist(P, p[a], n)*C['travel']
    fwd = (b-a-1)*C['fwd'] + 1.5*A
    inl = max(0, f-a-1)*C['inl']
    dfr = m*C['dfr']
    for last in JL['last']:
        if a <= last < b:
            if last < f: inl += C['jx']
            else: dfr += C['jx']
    tail = C['bnd'] + dfr
    return arrive + fwd + inl + max(C['grow'], tail), tail
def best_m(a, b, p, MX, g, P, n, C):
    best=None
    for m in range(0, max(0, b-JL['minl'][a])+1):
        fin, tail = chunk_cost(a, b, m, p, MX, g, P, n, C)
        if best is None or fin < best[0]-1e-9: best=(fin, m)
    return best
def solve(n, d, C, P=None, iters=6):
    p,NB,MX,near = plan(n)
    L=len(p); g,ng=junction_ids(p,MX,NB)
    JL['last']=[max(k for k in range(L) if g[k]==j) for j in range(ng)]
    allowed=[k for k in range(1,L) if not MX[k] and not MX[k-1]]
    # the first cell of a chunk is touched by its own drone only while that drone inserts it and
    # the cells next to it: those must not be deferred (minimum inline length from a chunk start)
    MINL={}
    for k in allowed:
        lim=k+2
        for q,_ in NB[k]:
            if MX[q]:
                lim=max(lim, JL['last'][g[q]]+1)
        MINL[k]=lim
    MINL[0]=2
    JL['minl']=MINL
    if P is None: P = p[0]
    for _ in range(iters):
        lo, hi = 0.5, 20.0
        res=None
        for _ in range(22):
            T=(lo+hi)/2
            cuts=[0]; ms=[]; ok=True
            for i in range(d):
                a=cuts[-1]
                if a>=L: ok=False; break
                if i==d-1:
                    fin,m=best_m(a,L,p,MX,g,P,n,C)
                    if fin>T: ok=False
                    cuts.append(L); ms.append(m); break
                bestb=None
                for j,b in enumerate(allowed):
                    if b<=a: continue
                    if len(allowed)-1-j < d-2-i: break
                    fin,m=best_m(a,b,p,MX,g,P,n,C)
                    if fin<=T: bestb=(b,m)
                    elif b-a>4 and bestb is not None: break
                if bestb is None: ok=False; break
                cuts.append(bestb[0]); ms.append(bestb[1])
            if ok: hi=T; res=(cuts,ms)
            else: lo=T
        cuts,ms=res
        # drone 0 ends where its walk back ends: index cuts[1]-ms[0] (or its last cell)
        e0 = cuts[1]-ms[0] if ms[0]>0 else cuts[1]-1
        P = p[e0]
    fins=[chunk_cost(cuts[i],cuts[i+1],ms[i],p,MX,g,P,n,C) for i in range(d)]
    return cuts, ms, P, hi, fins

# the constants behind run_reset.py's bd_cuts(): connector cost (jx), fix per cell planting
# forwards (inl) and on the walk back (dfr), growth budget for the walk back (grow); picked by
# a sweep in the simulator (12x12 and 16x16 rounds with 4 and 16 drones)
C12 = dict(C); C12.update(jx=0.6, inl=0.017, dfr=0.07, grow=1.0)
C16 = dict(C); C16.update(jx=0.45, inl=0.035, dfr=0.054, grow=0.9)
if __name__ == '__main__':
    out = {}
    for n, d, Cx in [(12, 4, C12), (12, 8, C12), (16, 8, C16), (16, 16, C16)]:
        cuts, ms, P, T, f = solve(n, d, Cx)
        out[n * 1000 + d] = (cuts, ms)
        print('%dx%d, %d drones: predicted %.2f s to the last finish' % (n, n, d, T), file=sys.stderr)
    print(repr(out))
