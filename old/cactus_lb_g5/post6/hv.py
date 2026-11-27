import sys,statistics as st
a=[];b=[]
for f in sys.argv[1:]:
    hs=[]
    last=None
    for line in open(f):
        p=line.split('\t')
        if p[0]=='E' and p[3]=='harvest':
            t=float(p[1])
            if not hs or t-hs[-1]>0.5: hs.append(t)
    a.append(hs[0]); b.append(hs[1]-hs[0])
print('A %.4f B %.4f tot %.4f n=%d'%(st.mean(a),st.mean(b),st.mean(a)+st.mean(b),len(a)))
