# for each cell tilled by a non-owner (first till by drone A, first plant by drone B != A), slack = plant_t - till_t
import sys,json
res=json.load(open(sys.argv[1])) if len(sys.argv)>2 and sys.argv[1].endswith('.json') and False else {}
mins={}
bad=0
for f in sys.argv[2:]:
    till={};plant={}
    for l in open(f):
        p=l.split('\t')
        if p[0]!='E':continue
        if p[3]=='harvest': break
        c=(p[4],p[5])
        if p[3]=='till' and c not in till: till[c]=(float(p[1]),p[2])
        if p[3]=='plant' and c not in plant: plant[c]=(float(p[1]),p[2])
    for c,(t,d) in till.items():
        if c in plant and plant[c][1]!=d:
            s=plant[c][0]-t
            mins[c]=min(mins.get(c,9),s)
            if s<0: bad+=1
    for c in plant:
        if c not in till: bad+=1
try: old=json.load(open(sys.argv[1]))
except Exception: old={}
for c,v in mins.items():
    k=','.join(c); old[k]=min(old.get(k,9),v)
old['_bad']=old.get('_bad',0)+bad
json.dump(old,open(sys.argv[1],'w'))
