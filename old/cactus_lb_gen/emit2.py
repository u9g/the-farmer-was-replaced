import random, sys, json, os, re, subprocess
from model import build, insert_gates, nbrs, middle, dist, N, simulate_chunk
from gen2 import forbidden, tdist, main as cands_main
ND=32
DIRV={(0,1):0,(1,0):1,(0,-1):2,(-1,0):3}
SIM="C:/Users/Jason/AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/Saves/minerwasreplace/.claude/skills/tfwr-sim/tfwr_sim.rs"

def layout(maxspan, extra=()):
    C,order,junc,cands=cands_main(0)
    gates=[w for sp,w in cands if sp<=maxspan]+list(extra)
    C=set(C)|set(gates)
    order=insert_gates(list(order),gates)
    return C,order

def split_cost(order,forb,cost,start,T):
    # cost[i]: time of cell i (incl. move to it); start(p): offset for a chunk starting at p
    chunks=[];p=0
    while p<len(order):
        c=start(p); q=p; last_ok=None
        while q<len(order):
            c+=cost[q]; q+=1
            if q==len(order) or not forb[q]:
                if c<=T or last_ok is None: last_ok=q
                if c>T: break
        chunks.append((p,last_ok)); p=last_ok
    return chunks
def best_split(order,forb,cost,start):
    lo,hi=0.0,60.0
    for _ in range(40):
        T=(lo+hi)/2
        if len(split_cost(order,forb,cost,start,T))<=ND: hi=T
        else: lo=T
    ch=split_cost(order,forb,cost,start,hi)
    return ch,hi

def chunk_data(C,order,chunks,ci,owner):
    p,q=chunks[ci]; ch=order[p:q]
    xs=[c[0] for c in ch]; ys=[c[1] for c in ch]; nb=[]
    for c in ch:
        e=[]
        for n,up in nbrs(c,C):
            oc,oi=owner[n]
            if oc==ci: e+=[oi,DIRV[(n[0]-c[0],n[1]-c[1])],1 if up else 0]
        nb.append(e)
    def ext(c,other):
        for n,up in nbrs(c,C):
            if owner[n][0]==other: return [DIRV[(n[0]-c[0],n[1]-c[1])],1 if up else 0]
        return []
    ea=ext(ch[-1],ci+1) if ci+1<len(chunks) else []
    eb=ext(ch[0],ci-1) if ci>0 else []
    for k,c in enumerate(ch):
        for n,up in nbrs(c,C):
            oc,oi=owner[n]
            if oc!=ci:
                assert (k==len(ch)-1 and oc==ci+1) or (k==0 and oc==ci-1), (ci,c,n)
                assert not middle(c,C) and not middle(n,C)
                assert not any(middle(m,C) for m,_ in nbrs(c,C)) and not any(middle(m,C) for m,_ in nbrs(n,C))
    return [xs,ys,nb,ea,eb]

def owners(order,chunks):
    owner={}
    for ci,(p,q) in enumerate(chunks):
        for i in range(p,q): owner[order[i]]=(ci,i-p)
    return owner

def emit(C,order,cha,chb,path,template="template2.py",debug=False):
    oa=owners(order,cha); ob=owners(order,chb)
    lines=[]
    for nm,chs,ow in (("a",cha,oa),("b",chb,ob)):
        for ci in range(len(chs)):
            d=chunk_data(C,order,chs,ci,ow)
            lines.append("def d%s%d():\n\treturn %s\n"%(nm,ci,json.dumps(d)))
    lines.append("FA = [%s]\n"%", ".join("da%d"%i for i in range(len(cha))))
    lines.append("FB = [%s]\n"%", ".join("db%d"%i for i in range(len(chb))))
    lines.append("NA = %d\n"%len(order))
    src=open(template).read().replace("#DATA#","\n\n".join(lines))
    if not debug:
        src=re.sub(r"\n[ \t]*quick_print\(.*#DBG", "", src)
    open(path,"w").write(src)
