import sys,re
lines=open(sys.argv[1]).read().split('\n')
def owner(ln):
    l=lines[ln-1]; lev=len(l)-len(l.lstrip('\t'))
    for i in range(ln-2,-1,-1):
        m=re.match(r'(\t*)def (w\d+)\(\):',lines[i])
        if m and len(m.group(1))<lev: return m.group(2)
m={}
for line in open(sys.argv[2]):
    p=line.split('\t')
    if p[0]=='E' and p[3] in('till','plant'):
        d=int(p[2])
        if d not in m: m[d]=owner(int(p[8].split(':')[1]))
for d in sorted(m): print(d,m[d])
