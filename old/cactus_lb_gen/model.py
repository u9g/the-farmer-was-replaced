import random, sys
N=32
def strip_of(x,y): return (x+y)//3 if (x+y)%3 else None
def build(extra_gates=()):
    C=set((x,y) for x in range(N) for y in range(N) if (x+y)%3)
    C.add((0,0))
    # serpentine: strip k traversed increasing t if k even
    order=[(0,0)]
    junctions=[]
    for k in range(21):
        cells=sorted([c for c in C if (c[0]+c[1])%3 and (c[0]+c[1])//3==k], key=lambda c:c[0]-c[1])
        inc = (k%2==0)
        if not inc: cells=cells[::-1]
        if k>0:
            s=3*k
            wall=sorted([(x,s-x) for x in range(N) if 0<=s-x<N], key=lambda c:c[0]-c[1])
            # previous strip k-1 traversed inc if (k-1) even -> ended at max t -> gate max t
            g = wall[-1] if (k-1)%2==0 else wall[0]
            C.add(g); order.append(g); junctions.append(g)
        order+=cells
    for g in extra_gates:
        C.add(g)
    return C,order,junctions
def insert_gates(order,gates):
    for g in gates:
        best=None
        for i in range(len(order)-1):
            a,b=order[i],order[i+1]
            d=abs(a[0]-g[0])+abs(a[1]-g[1])+abs(b[0]-g[0])+abs(b[1]-g[1])-abs(a[0]-b[0])-abs(a[1]-b[1])
            if best is None or d<best[0]: best=(d,i)
        order.insert(best[1]+1,g)
    return order
def nbrs(c,C):
    x,y=c
    out=[]
    for dx,dy,up in ((0,1,True),(1,0,True),(0,-1,False),(-1,0,False)):
        n=(x+dx,y+dy)
        if n in C: out.append((n,up))
    return out
def middle(c,C):
    ns=nbrs(c,C); return any(u for _,u in ns) and any(not u for _,u in ns)
def dist(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])
def simulate_chunk(chunk,C,rng,till=True):
    inchunk=set(chunk)
    vals={}
    pos=chunk[0]; moves=0; swaps=0; acts=0
    for c in chunk:
        moves+=dist(pos,c); pos=c
        acts+= 2 if till else 1
        vals[c]=rng.randrange(10)
        work=[c]
        while work:
            a=work.pop()
            for n,up in nbrs(a,C):
                if n not in inchunk or n not in vals: continue
                lo,hi=(a,n) if up else (n,a)
                if vals[lo]>vals[hi]:
                    st = lo if dist(pos,lo)<=dist(pos,hi) else hi
                    moves+=dist(pos,st); pos=st
                    vals[lo],vals[hi]=vals[hi],vals[lo]; swaps+=1
                    work.append(lo); work.append(hi)
    return moves,swaps,acts,vals
if __name__=="__main__":
    C,order,j=build()
    print(len(C),len(order),len(set(order)))
    tot=sum(dist(order[i],order[i+1]) for i in range(len(order)-1))
    print("path moves",tot)
    mids=[c for c in C if middle(c,C)]
    print("middle nodes",len(mids))
    rng=random.Random(1)
    m,s,a,v=simulate_chunk(order,C,rng)
    print("whole path as one chunk: moves",m,"swaps",s,"acts",a)
    # verify sorted
    bad=sum(1 for c in C for n,up in nbrs(c,C) if up and v[c]>v[n])
    print("bad",bad)
