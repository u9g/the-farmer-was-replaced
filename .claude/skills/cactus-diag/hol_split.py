"""The N latest drones per round (rank 0 = the one the harvest waits for): finish, arrival,
planting phase action counts, and how far the tail ran past the growth wait.
Round A finish is the drone's done signal (water / harvest); later moves are pre-travel.
    python3 hol_split.py TRACES..."""
import sys, statistics as st, collections
ACT=200/6075.0; GROW=0.9676
R={0:collections.defaultdict(lambda: collections.defaultdict(list)),1:collections.defaultdict(lambda: collections.defaultdict(list))}
for fn in sys.argv[1:]:
    ev=[]
    for l in open(fn):
        p=l.rstrip('\n').split('\t')
        if p[0]=='E': ev.append((float(p[1]),int(p[2]),p[3],int(p[7]),int(p[4]),int(p[5]),p[9] if len(p)>9 else ''))
    hv=[e[0] for e in ev if e[2]=='harvest' and e[6] and float(e[6])>1e6]
    for r,(lo,hi) in enumerate(((0,hv[0]),(hv[0],hv[1]))):
        la,lp={},{}
        for e in ev:
            if not (lo<=e[0]<hi and e[3]==200): continue
            if e[2]=='plant': lp[e[1]]=max(lp.get(e[1],0),e[0]+ACT)
            if e[2]!='end' and (r==1 and e[2]!='harvest' or r==0 and e[2] in ('use','harvest')):
                la[e[1]]=max(la.get(e[1],0),e[0]+ACT)
        fin={d:max(la[d],lp[d]+GROW) for d in la if d in lp}
        for rank,h in enumerate(sorted(fin,key=fin.get,reverse=True)[:5]):
            es=[e for e in ev if e[1]==h and lo<=e[0]<hi and e[3]==200 and e[2] not in ('end',)]
            pl=[e for e in es if e[2]=='plant']
            fp,lpt=pl[0][0],pl[-1][0]
            mid=[e for e in es if fp<=e[0]<=lpt]
            c=collections.Counter(e[2] for e in mid)
            # cells planted (distinct) vs moves in planting phase
            cells=len({(e[4],e[5]) for e in pl})
            d=R[r][rank]
            d['arrive'].append(fp-lo); d['plantspan'].append(lpt+ACT-fp); d['tailover'].append(max(0,la[h]-(lp[h]+GROW)))
            d['finish'].append(fin[h]-lo); d['cells'].append(cells); d['plants'].append(c['plant'])
            for k in ('move','till','swap','use','spawn'): d[k].append(c[k])
            d['pre_moves'].append(sum(1 for e in es if e[0]<fp and e[2]=='move'))
for r in (0,1):
    print(f'round {"AB"[r]}: the 5 latest drones (rank 0 = the one everyone waits for)')
    for rank in range(5):
        d=R[r][rank]; m=lambda k: st.mean(d[k])
        print(f'  #{rank}: finish {m("finish"):.3f}  arrives {m("arrive"):.3f} ({m("pre_moves"):.1f} moves before 1st plant)  planting {m("plantspan"):.3f} s: {m("plants"):.1f} plants on {m("cells"):.1f} cells, {m("move"):.1f} moves, {m("till"):.1f} tills, {m("swap"):.1f} swaps, {m("use"):.1f} water, {m("spawn"):.1f} spawns  tail past growth {m("tailover")*1000:.0f} ms')
