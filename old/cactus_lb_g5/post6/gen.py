import os
import sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from parse import parse, starts
def emit(pre,W,post,plan):
    # plan: name -> list of ('move',dir) / ('spawn',child)
    out=list(pre)
    def blk(name,lev):
        out.append('\t'*lev+'def %s():'%name)
        for s in plan[name]:
            if s[0]=='move': out.append('\t'*(lev+1)+'move(%s)'%s[1])
            else:
                blk(s[1],lev+1); out.append('\t'*(lev+1)+'spawn_drone(%s)'%s[1])
        for l in W[name][1]:
            out.append(('\t'*(lev+1)+l) if l else '')
    blk('w0',0)
    # parse() strips trailing blank lines into work; keep post
    out.extend(post)
    return out
if __name__=='__main__':
    lines=open(sys.argv[1]).read().split('\n')
    pre,W,post=parse(lines)
    plan={n:[s for s in W[n][0] if s[0]!='def'] for n in W}
    out=emit(pre,W,post,plan)
    open(sys.argv[2],'w').write('\n'.join(out))
