import random, sys
from model import build, insert_gates, nbrs, middle, dist, N
ND=32
DIRV={(0,1):0,(1,0):1,(0,-1):2,(-1,0):3}
def tdist(a,b):
    dx=abs(a[0]-b[0]); dy=abs(a[1]-b[1])
    return min(dx,N-dx)+min(dy,N-dy)

def forbidden(order,C):
    idx={c:i for i,c in enumerate(order)}
    forb=[False]*(len(order)+1)  # forb[q]: boundary before order[q] not allowed
    for c in C:
        if middle(c,C):
            for n,_ in nbrs(c,C):
                a,b=sorted((idx[c],idx[n]))
                for q in range(a+1,b+1): forb[q]=True
    for q in range(1,len(order)):
        a,b=order[q-1],order[q]
        if dist(a,b)!=1 or middle(a,C) or middle(b,C): forb[q]=True
        if any(middle(n,C) for n,_ in nbrs(a,C)) or any(middle(n,C) for n,_ in nbrs(b,C)): forb[q]=True
        # every edge crossing must be this boundary edge: neighbors of a/b other than each other must be on own side
    # any non-consecutive edge crossing q is forbidden
    for c in C:
        for n,up in nbrs(c,C):
            i,j=sorted((idx[c],idx[n]))
            if j-i>1:
                for q in range(i+1,j+1): forb[q]=True
    return forb

def split(order,C,cellcost,startdelay,T):
    forb=forbidden(order,C)
    chunks=[];p=0
    while p<len(order):
        cost=startdelay+tdist((0,0),order[p])
        q=p
        last_ok=None
        while q<len(order):
            cost+=cellcost[q]+(dist(order[q-1],order[q]) if q>p else 0)
            q+=1
            if q==len(order) or not forb[q]:
                if cost<=T or last_ok is None: last_ok=q
                if cost>T: break
        chunks.append((p,last_ok)); p=last_ok
    return chunks

def main(ngates, seeds=16, out="cand.py"):
    C,order,junc=build()
    order=list(order)
    # candidate interior gates: wall cells whose closure interval in order is short
    idx={c:i for i,c in enumerate(order)}
    cands=[]
    for x in range(N):
        for y in range(N):
            w=(x,y)
            if (x+y)%3 or w in C: continue
            ns=[n for n in [(x,y+1),(x+1,y),(x,y-1),(x-1,y)] if n in C]
            if len(ns)<2: continue
            ups=[n for n in ns if n[0]+n[1]>x+y]; dns=[n for n in ns if n[0]+n[1]<x+y]
            if not ups or not dns: continue
            span=[idx[n] for n in ns]
            cl=set(span)
            for n in ns:
                for m,_ in nbrs(n,C): cl.add(idx[m])
            cands.append((max(cl)-min(cl),w))
    cands.sort()
    return C,order,junc,cands
if __name__=="__main__":
    C,order,junc,cands=main(0)
    print(len(cands)); print(cands[:40])
