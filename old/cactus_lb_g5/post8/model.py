import re,json,sys
N=32
D={'North':(0,1),'South':(0,-1),'East':(1,0),'West':(-1,0)}
def parse(path):
    L=open(path).read().split('\n')
    defs={}
    for i,l in enumerate(L):
        m=re.match(r'(\t*)def (w\d+)\(\):',l)
        if m: defs[m.group(2)]=(i,len(m.group(1)))
    launch={}
    for n,(i,ind) in defs.items():
        seq=[]; j=i+1
        while j<len(L):
            l=L[j]
            if l.strip()=='': j+=1; continue
            d=len(l)-len(l.lstrip('\t'))
            if d<=ind: break
            if d==ind+1:
                s=l.strip()
                if s.startswith('def w'): j+=1; continue
                m=re.match(r'spawn_drone\((w\d+)\)$',s)
                if m: seq.append(('S',m.group(1)))
                else:
                    m=re.match(r'move\((\w+)\)$',s)
                    if m: seq.append(('M',m.group(1)))
                    else: break
            j+=1
        launch[n]=seq
    return L,defs,launch
def arrivals(launch,root='w0'):
    arr={};pos={}
    def go(n,p,t):
        x,y=p
        for k,a in launch[n]:
            if k=='M':
                dx,dy=D[a];x=(x+dx)%N;y=(y+dy)%N;t+=1
            else:
                t+=1; go(a,(x,y),t)
        arr[n]=t;pos[n]=(x,y)
    go(root,(0,0),0)
    return arr,pos
if __name__=='__main__':
    L,defs,launch=parse(sys.argv[1])
    arr,pos=arrivals(launch)
    for n in sorted(arr,key=lambda s:int(s[1:])): print(n,arr[n],pos[n])
    print(sum(arr.values())/32)
