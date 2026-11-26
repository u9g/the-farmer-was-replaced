# optimal (swaps+moves) to settle the bottom-edge T junction, drone starts at X3
import random, heapq, collections
cells = {"A":(6,0),"B":(7,0),"G":(8,0),"C":(9,0),"D":(8,1),"X1":(9,1),"X2":(10,0),"X3":(8,2)}
names=list(cells); idx={n:i for i,n in enumerate(names)}
rel=[("A","B"),("B","G"),("G","C"),("G","D"),("C","X1"),("C","X2"),("D","X1"),("D","X3")]
rel=[(idx[a],idx[b]) for a,b in rel]
pure_lo={idx["A"]}; pure_hi={idx["X1"],idx["X2"],idx["X3"]}
adj=collections.defaultdict(list)
for a,b in rel: adj[a].append(b); adj[b].append(a)
pos=[cells[n] for n in names]
def md(a,b): return abs(pos[a][0]-pos[b][0])+abs(pos[a][1]-pos[b][1])
def ok(v): return all(v[a]<=v[b] for a,b in rel)
def solve(v, start):
    v=tuple(v)
    if ok(v): return 0
    dist={(v,start):0}; pq=[(0,v,start)]
    while pq:
        d,x,p=heapq.heappop(pq)
        if dist.get((x,p),1e9)<d: continue
        if ok(x): return d
        # swap from p with a related neighbour (fix-direction only, keeps pure cells monotone)
        for q in adj[p]:
            a,b=(p,q) if (p,q) in rel else (q,p)
            if x[a]>x[b]:
                y=list(x); y[a],y[b]=y[b],y[a]; y=tuple(y)
                if d+1<dist.get((y,p),1e9): dist[(y,p)]=d+1; heapq.heappush(pq,(d+1,y,p))
        for q in range(len(names)):
            if q!=p:
                nd=d+md(p,q)
                if nd<dist.get((x,q),1e9): dist[(x,q)]=nd; heapq.heappush(pq,(nd,x,q))
R=random.Random(1); T=600
for label,gen in [("random",lambda R:[R.randrange(10) for _ in names]),
                  ("ring ext2",lambda R:[min(R.randrange(10),R.randrange(10))]+[R.randrange(10) for _ in range(4)]+[max(R.randrange(10),R.randrange(10)) for _ in range(3)])]:
    tot=0
    for _ in range(T):
        tot+=solve(gen(R), idx["X3"])
    print(label,"optimal swaps+moves %.2f"%(tot/T))
