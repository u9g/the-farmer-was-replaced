import sys,json,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from parse import parse,starts
from gen import emit
from tree import plan_tree
ACT=201/6075
entry,stats,out=sys.argv[1:4]; tau=float(sys.argv[4]); var=float(sys.argv[5]) if len(sys.argv)>5 else 1.0
hanan=int(os.environ.get('HANAN','0'))
lines=open(entry).read().split('\n'); pre,W,post=parse(lines); S=starts(W)
J=json.load(open(stats))
order=sorted(W,key=lambda x:int(x[1:]))
# rest in actions, plus variance correction
taua=tau/ACT
R={n:(J[n]['done']-J[n]['arr'])/ACT + var*(J[n]['sd']/ACT)**2/(2*taua) for n in order}
plan,arr,pred=plan_tree(order,S,R,taua,hanan=hanan)
cur={n:J[n]['arr']/ACT for n in order}
print('pred softmax(s)',pred*ACT,'mean arr',sum(arr.values())/32*ACT, 'cur mean arr', sum(cur.values())/32*ACT)
print('max pred done', max(arr[n]+R[n] for n in order)*ACT, 'cur', max(cur[n]+R[n] for n in order)*ACT)
for n in sorted(order,key=lambda n:-(arr[n]+R[n]))[:6]: print(n, round(arr[n]*ACT,3), round(cur[n]*ACT,3), round((arr[n]+R[n])*ACT,3))
open(out,'w').write('\n'.join(emit(pre,W,post,plan)))
