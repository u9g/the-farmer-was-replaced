import sys
R={}
for f in sys.argv[1:]:
    till={};sw={};res={}
    for l in open(f):
        p=l.split('\t')
        if p[0]!='E':continue
        if p[3]=='harvest': break
        c=(p[4],p[5]); d=p[2]; t=float(p[1])
        if p[3]=='till' and c not in till: till[c]=(t,d)
        if p[3]=='swap': sw[d]=sw.get(d,0)+1
        if p[3]=='plant' and c in till and till[c][1]!=d and c not in res:
            res[c]=(t-till[c][0],sw.get(d,0))
    for c,v in res.items():
        R.setdefault(c,[]).append(v)
for c,L in sorted(R.items(),key=lambda kv:min(kv[1])[0]):
    print(c,'min slack %.3f'%min(L)[0],'min swaps before',min(s for _,s in L),'slack at 0 swaps',sorted(set(round(a,3) for a,s in L if s==0))[:3])
