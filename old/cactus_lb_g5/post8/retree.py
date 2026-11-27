# flatten nested w-functions of the entry, replace launch prefixes, re-nest.
import re,sys
N=32
D={'North':(0,1),'South':(0,-1),'East':(1,0),'West':(-1,0)}
def flatten(text):
    L=text.split('\n')
    i0=next(i for i,l in enumerate(L) if re.match(r'def w0\(\):',l))
    # end of w0: next line at col 0 non-empty
    i1=next(i for i in range(i0+1,len(L)) if L[i] and not L[i][0].isspace())
    head=L[:i0]; tail=L[i1:]
    funcs={}
    def grab(i,ind,name):
        # returns body lines (dedented to one tab) excluding nested w defs; and launch tokens
        body=[];j=i+1;launch=[];inl=True
        while j<i1:
            l=L[j]
            if l.strip()=='':
                j+=1; continue
            d=len(l)-len(l.lstrip('\t'))
            if d<=ind: break
            m=re.match(r'\t*def (w\d+)\(\):$',l)
            if m and d==ind+1:
                j=grab(j,d,m.group(1)); continue
            s=l[ind+1:]
            if inl and d==ind+1:
                mm=re.match(r'move\((\w+)\)$',s); ms=re.match(r'spawn_drone\((w\d+)\)$',s)
                if mm: launch.append(('M',mm.group(1))); j+=1; continue
                if ms: launch.append(('S',ms.group(1))); j+=1; continue
                inl=False
            body.append('\t'+s); j+=1
        funcs[name]=(launch,body)
        return j
    grab(i0,0,'w0')
    return head,funcs,tail
def emit(funcs,launch,name,ind):
    out=[ind+'def %s():'%name]
    for k,a in launch[name]:
        if k=='M': out.append(ind+'\tmove(%s)'%a)
        else:
            out+=emit(funcs,launch,a,ind+'\t')
            out.append(ind+'\tspawn_drone(%s)'%a)
    out+=[ind+l for l in funcs[name][1]]
    return out
def build(head,funcs,tail,launch):
    return '\n'.join(head+emit(funcs,launch,'w0','')+['']+tail)
def path_moves(p,q):
    dx=(q[0]-p[0])%N; dy=(q[1]-p[1])%N
    mv=[]
    mv+=['East']*dx if dx<=16 else ['West']*(N-dx)
    mv+=['North']*dy if dy<=16 else ['South']*(N-dy)
    return mv
def from_goto(glaunch):
    # glaunch: name -> list of ('G',pt) / ('S',child); start at (0,0) for w0
    out={}
    def go(n,p):
        seq=[]
        for k,a in glaunch[n]:
            if k=='G':
                seq+=[('M',d) for d in path_moves(p,a)]; p=a
            else:
                seq.append(('S',a)); go(a,p)
        out[n]=seq
    go('w0',(0,0))
    return out
if __name__=='__main__':
    t=open(sys.argv[1]).read()
    h,f,tl=flatten(t)
    la={k:v[0] for k,v in f.items()}
    o=build(h,f,tl,la)
    open(sys.argv[2],'w').write(o)
