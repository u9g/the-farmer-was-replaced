import re,sys
# parse nested launch tree of cactus entry
def ind(l): return len(l)-len(l.lstrip('\t'))
def parse(lines):
    # returns: prefix lines (before 'def w0'), dict name->(launch steps, work lines), postfix
    i0=next(i for i,l in enumerate(lines) if l.startswith('def w0():'))
    end=next(i for i in range(len(lines)-1,-1,-1) if lines[i].strip()=='w0()')
    W={}
    def block(i,lev):
        # lines[i] is 'def wK():' at indent lev; returns end index
        name=re.match(r'\s*def (w\d+)\(\):',lines[i]).group(1)
        j=i+1; steps=[]
        while j<len(lines) and (lines[j].strip()=='' or ind(lines[j])>lev):
            l=lines[j]; s=l.strip()
            if ind(l)!=lev+1: j+=1; continue
            m=re.match(r'def (w\d+)\(\):$',s)
            if m and (not steps or steps[-1][0]!='work'):
                child=m.group(1); j=block(j,lev+1); steps.append(('def',child)); continue
            m=re.match(r'spawn_drone\((w\d+)\)$',s)
            if m and (not steps or steps[-1][0]!='work'):
                steps.append(('spawn',m.group(1))); j+=1; continue
            m=re.match(r'move\((North|South|East|West)\)$',s)
            if m and (not steps or steps[-1][0]!='work'):
                steps.append(('move',m.group(1))); j+=1; continue
            # work starts
            k=j
            while k<len(lines) and (lines[k].strip()=='' or ind(lines[k])>lev): k+=1
            work=[l[lev+1:] if l.strip() else '' for l in lines[j:k]]
            steps.append(('work',work)); j=k
        launch=[s for s in steps if s[0]!='work']
        work=[s for s in steps if s[0]=='work']
        assert len(work)==1,(name,len(work))
        W[name]=(launch,work[0][1])
        return j
    e=block(i0,0)
    return lines[:i0],W,lines[e:]
D={'North':(0,1),'South':(0,-1),'East':(1,0),'West':(-1,0)}
def starts(W,N=32):
    S={}
    def go(name,pos):
        for s in W[name][0]:
            if s[0]=='move':
                dx,dy=D[s[1]]; pos=((pos[0]+dx)%N,(pos[1]+dy)%N)
            elif s[0]=='spawn': go(s[1],pos)
        S[name]=pos
    go('w0',(0,0)); return S
if __name__=='__main__':
    lines=open(sys.argv[1]).read().split('\n')
    pre,W,post=parse(lines)
    S=starts(W)
    for n in sorted(W,key=lambda x:int(x[1:])):
        print(n,S[n],len(W[n][1]),[ (s[0],s[1]) for s in W[n][0]])
    print('post',post[:3])
