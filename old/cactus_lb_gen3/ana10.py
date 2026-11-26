import os, sys, random, statistics as S, heapq
import b9, cmodel
def phase_times(g, seeds=8):
    A=[[] for _ in range(32)]; B=[[] for _ in range(32)]; TA=[]; TB=[]
    for sd in range(seeds):
        rng=random.Random(sd); w=cmodel.World(g.R,rng)
        sts=[];gens=[];heap=[]
        for k in range(32):
            tr=0
            for op in g.PA[k][1]:
                if op[0]!='move': break
                tr+=1
            st={'t':200+(g.offs[k]-tr)*200,'k':k}; sts.append(st)
            gens.append(cmodel.run_drone(w,g.PA[k],g.pos_end[k],st)); heapq.heappush(heap,(st['t'],k))
        done=[0]*32
        while heap:
            t,k=heapq.heappop(heap); sts[k]['t']=t
            try: heapq.heappush(heap,(t+next(gens[k]),k))
            except StopIteration: done[k]=t
        a=[max(done[k], sts[k]['lp']+6076)+200 for k in range(32)]
        tH=max(a)+2
        cmodel.harvest(w,sts[0]['pos'],tH)
        st2=[];gens=[];heap=[]
        for k in range(32):
            st={'t':tH+205,'k':k}; st2.append(st)
            gens.append(cmodel.run_drone(w,g.PB[k],sts[k]['pos'],st)); heapq.heappush(heap,(st['t'],k))
        d2=[0]*32
        while heap:
            t,k=heapq.heappop(heap); st2[k]['t']=t
            try: heapq.heappush(heap,(t+next(gens[k]),k))
            except StopIteration: d2[k]=t
        b=[max(d2[k], st2[k]['lp']+6076)-tH for k in range(32)]
        for k in range(32): A[k].append(a[k]); B[k].append(b[k])
        TA.append(max(a)); TB.append(max(b))
    return A,B,TA,TB
if __name__=="__main__":
    g=b9.Gen(); g.plan(); g.build()
    A,B,TA,TB=phase_times(g)
    print('A max %.0f avg %.0f | B max %.0f avg %.0f'%(S.mean(TA), S.mean(S.mean(x) for x in A), S.mean(TB), S.mean(S.mean(x) for x in B)))
    print('A per', [int(S.mean(x)/100) for x in A])
    print('B per', [int(S.mean(x)/100) for x in B])
