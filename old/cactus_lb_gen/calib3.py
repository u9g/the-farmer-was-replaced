import sys, re, subprocess, json, random
from emit2 import *
import emit3
def split_c(order,forb,cost,start,T):
    chunks=[];p=0
    while p<len(order):
        c=start(len(chunks),p); q=p; last_ok=None
        while q<len(order):
            c+=cost[q]; q+=1
            if q==len(order) or not forb[q]:
                if c<=T or last_ok is None: last_ok=q
                if c>T: break
        chunks.append((p,last_ok)); p=last_ok
    return chunks
def best(order,forb,cost,start):
    lo,hi=0.0,60.0
    for _ in range(40):
        T=(lo+hi)/2
        if len(split_c(order,forb,cost,start,T))<=ND: hi=T
        else: lo=T
    return split_c(order,forb,cost,start,hi),hi
def layout_g(gates):
    C,order,junc,cands=cands_main(0)
    gates=[tuple(g) for g in gates if tuple(g) not in C]
    C=set(C)|set(gates)
    order=insert_gates(list(order),gates)
    return C,order
def runsim(path,seeds,seed=1):
    out=subprocess.run(["cargo","+nightly","-Zscript",SIM,path,"--leaderboard","cactus","--seeds",str(seeds),"--seed",str(seed)],capture_output=True,text=True).stdout
    return out
def parse(out,order,cha,chb):
    runs=out.split("seed ")[1:]
    ca=[[] for _ in order]; cb=[[] for _ in order]; S={}
    for r in runs:
        seq={}
        for m in re.finditer(r"\[\s*([\d.]+)s\] (\w) (.*)",r):
            t=float(m.group(1)); k=m.group(2); rest=m.group(3).split()
            if k=="S": S.setdefault(int(rest[0]),[]).append(t)
            elif k=="C":
                c=int(rest[0]); fw=rest[1]=="True"; i=int(rest[2])
                seq.setdefault((c,fw),[]).append((i,t))
            elif k=="X":
                c=int(rest[0]); fw=rest[1]=="True"
                seq.setdefault((c,fw),[]).append((-1,t))
        for (c,fw),lst in seq.items():
            # only first pass of each direction
            n=len(lst)
            chs=cha if fw else chb
            p,q=chs[c]
            L=q-p
            lst=lst[:L+1]
            for k in range(min(L,len(lst)-1)):
                i,t=lst[k]; t2=lst[k+1][1]
                gi = p+i if fw else q-1-i
                (ca if fw else cb)[gi].append(t2-t)
    return ca,cb,S
def main():
    L=json.load(open(sys.argv[1])); out=sys.argv[2]; iters=int(sys.argv[3])
    C,order=layout_g(L["gates"])
    for d in L["drop"]:
        d=tuple(d); C.discard(d); order.remove(d)
    forb=forbidden(order,C)
    costA=[0.11]*len(order); costB=[0.075]*len(order)
    Sd={c:0.25 for c in range(ND)}
    MV=0.034
    for it in range(iters):
        cha,TA=best(order,forb,costA,lambda c,p:Sd.get(c,0.3)+tdist((0,0),order[p])*MV)
        chb,TB=best(order,forb,costB,lambda c,p:0.0)
        print("iter",it,"TA",round(TA,3),"TB",round(TB,3),len(cha),len(chb),file=sys.stderr)
        emit3.emit(C,order,cha,chb,"v/calib_dbg.py",debug=True)
        o=runsim("v/calib_dbg.py",8,seed=it*100+1)
        m=re.search(r"score .*",o); print(" ",m.group(0) if m else o[-2000:],file=sys.stderr)
        ca,cb,S=parse(o,order,cha,chb)
        for i in range(len(order)):
            if ca[i]: costA[i]=0.5*costA[i]+0.5*sum(ca[i])/len(ca[i])
            if cb[i]: costB[i]=0.5*costB[i]+0.5*sum(cb[i])/len(cb[i])
        for c,v in S.items(): Sd[c]=sum(v)/len(v)
    emit3.emit(C,order,cha,chb,out,debug=False)
    json.dump({"costA":costA,"costB":costB,"Sd":Sd},open(out+".json","w"))
main()
