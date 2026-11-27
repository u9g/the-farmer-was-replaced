#!/bin/bash
# usage: ab.sh NSEEDS runner1 runner2 ... ; prints per-script mean first harvest, B, total, paired diff
N=$1; shift
cargo +nightly -Zscript /home/user/the-farmer-was-replaced/.claude/skills/tfwr-sim/tfwr_sim.rs "$@" --seed 1 --seeds $N --jobs 1 --quiet 2>/dev/null | python3 -I -c '
import sys,re,statistics as st
runs=[];cur=None;scripts=[];errs=[]
for l in sys.stdin:
    m=re.match(r"seed (\d+): simulated",l)
    if m: cur=int(m.group(1))
    m=re.search(r"([\d.]+)s between harvests.*first at ([\d.]+)s",l)
    if m: runs.append((float(m.group(2)),float(m.group(1))))
    if "ERROR" in l or "error" in l.lower(): errs.append(l.strip())
    m=re.match(r"Leaderboards.cactus with (\S+)",l)
    if m: scripts.append(m.group(1))
    m=re.match(r"\s+score \S+ \(([\d.]+)s\)",l)
    if m: scripts[-1]=(scripts[-1],float(m.group(1)))
n=len(runs)//len(scripts)
base=None
for i,(s,sc) in enumerate(scripts):
    r=runs[i*n:(i+1)*n]; A=[a for a,b in r]; T=[a+b for a,b in r]
    if base is None: base=T
    d=[t-b for t,b in zip(T,base)]
    print("%-22s score %.4f  A %.4f  B %.4f  A+B %.4f  diff %+.4f +- %.4f"%(s,sc,st.mean(A),st.mean(b for a,b in r),st.mean(T),st.mean(d),st.pstdev(d)/len(d)**.5))
print("errors:",len(errs), errs[:3])
'
