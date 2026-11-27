# per seed per chunk: Adone(use), ready (end of last move before first B plant), Bfp, Bend; hA, hB
import sys,re,json
entry=sys.argv[1]; out=sys.argv[2]; files=sys.argv[3:]
lines=open(entry).read().split('\n'); cache={}
TA=200/6075
def owner(ln):
    if ln in cache: return cache[ln]
    l=lines[ln-1]; lev=len(l)-len(l.lstrip('\t'))
    for i in range(ln-2,-1,-1):
        m=re.match(r'(\t*)def (w\d+)\(\):',lines[i])
        if m and len(m.group(1))<lev: cache[ln]=m.group(2); return m.group(2)
R={'_hA':[],'_hB':[]}
for f in files:
    ev=[l.rstrip('\n').split('\t') for l in open(f)]
    ev=[p for p in ev if p[0]=='E']
    hv=[]
    for p in ev:
        if p[3]=='harvest':
            t=float(p[1])
            if not hv or t-hv[-1]>0.5: hv.append(t)
    hA,hB=hv[0],hv[1]
    nm={};use={};lastmv={};bfp={};bend={}
    for p in ev:
        t=float(p[1]);d=int(p[2]);k=p[3]
        if k in('till','plant') and d not in nm and t<hA: nm[d]=owner(int(p[8].split(':')[1]))
        if t<hA+0.3 and (k=='use' or (k=='harvest' and t==hA)) and d not in use: use[d]=t
        if d in use and d not in bfp and k=='move': lastmv[d]=t+TA
        if t>=hA and k=='plant' and d not in bfp: bfp[d]=t
        if t>=hA and t<hB and k not in('measure','items','time','harvest'): bend[d]=t
    for d,n in nm.items():
        r=R.setdefault(n,{'A':[],'ready':[],'bfp':[],'bend':[]})
        r['A'].append(use[d]); r['ready'].append(max(lastmv.get(d,use[d]+TA),use[d]+TA)); r['bfp'].append(bfp[d]); r['bend'].append(bend.get(d,bfp[d]))
    R['_hA'].append(hA); R['_hB'].append(hB)
json.dump(R,open(out,'w'))
import statistics as st
print('hA',st.mean(R['_hA']),'hB',st.mean(R['_hB']))
