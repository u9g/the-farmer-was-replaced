import json, re
from model import nbrs, middle, dist
DIRV={(0,1):0,(1,0):1,(0,-1):2,(-1,0):3}
def owners(order,chunks):
    owner={}
    for ci,(p,q) in enumerate(chunks):
        for i in range(p,q): owner[order[i]]=ci
    return owner
def pass_data(C,cells,owner,ci,nextci):
    pos={c:i for i,c in enumerate(cells)}
    xs=[c[0] for c in cells]; ys=[c[1] for c in cells]
    nb=[];mv=[];pj=[];pd=[];pu=[]
    for i,c in enumerate(cells):
        e=[]
        for n,up in nbrs(c,C):
            if owner[n]==ci: e+=[pos[n],DIRV[(n[0]-c[0],n[1]-c[1])],1 if up else 0]
        nb.append(e)
        if i>0 and dist(cells[i-1],c)==1: mv.append(DIRV[(c[0]-cells[i-1][0],c[1]-cells[i-1][1])])
        else: mv.append(-1)
        before=[(n,up) for n,up in nbrs(c,C) if owner[n]==ci and pos[n]<i]
        simple = not middle(c,C) and all(not middle(n,C) for n,_ in before)
        if simple and len(before)==0: pj.append(-2);pd.append(0);pu.append(0)
        elif simple and len(before)==1:
            n,up=before[0]; pj.append(pos[n]); pd.append(DIRV[(n[0]-c[0],n[1]-c[1])]); pu.append(1 if up else 0)
        else: pj.append(-1);pd.append(0);pu.append(0)
    ext=[]
    if nextci is not None:
        c=cells[-1]
        for n,up in nbrs(c,C):
            if owner[n]==nextci: ext=[DIRV[(n[0]-c[0],n[1]-c[1])],1 if up else 0]
    # validate cross edges
    for k,c in enumerate(cells):
        for n,up in nbrs(c,C):
            if owner[n]!=ci:
                assert owner[n] in (ci-1,ci+1)
                assert not middle(c,C) and not middle(n,C)
                assert not any(middle(m,C) for m,_ in nbrs(c,C)) and not any(middle(m,C) for m,_ in nbrs(n,C))
    return [xs,ys,nb,ext,mv,pj,pd,pu]
def emit(C,order,cha,chb,path,template="template3.py",debug=False):
    oa=owners(order,cha); ob=owners(order,chb)
    lines=[]
    for ci,(p,q) in enumerate(cha):
        nxt=ci+1 if ci+1<len(cha) else None
        lines.append("def da%d():\n\treturn %s\n"%(ci,json.dumps(pass_data(C,order[p:q],oa,ci,nxt))))
    for ci,(p,q) in enumerate(chb):
        nxt=ci-1 if ci>0 else None
        lines.append("def db%d():\n\treturn %s\n"%(ci,json.dumps(pass_data(C,order[p:q][::-1],ob,ci,nxt))))
    lines.append("FA = [%s]\n"%", ".join("da%d"%i for i in range(len(cha))))
    lines.append("FB = [%s]\n"%", ".join("db%d"%i for i in range(len(chb))))
    lines.append("NA = %d\n"%len(order))
    src=open(template).read().replace("#DATA#","\n\n".join(lines))
    if not debug:
        src=re.sub(r"\n[ \t]*quick_print\(.*#DBG", "", src)
    open(path,"w").write(src)
