#!/bin/bash
# usage: abt.sh NSEEDS runner...   (trace-based: A, B per seed)
N=$1; shift
W=${WORK:?set WORK to a scratch dir}/abt
for r in "$@"; do
  rm -rf $W; mkdir -p $W
  CACTUS_TRACE=$W/run cargo +nightly -Zscript /home/user/the-farmer-was-replaced/.claude/skills/cactus-diag/tfwr_diag.rs $r --seed ${SEED:-1} --seeds $N --jobs 1 --quiet 2>&1 | grep -i "score\|error" | sed "s/^/$r /"
  for f in $W/run.*.tsv; do s=${f##*/run.}; s=${s%.tsv}; awk -F'\t' -v s=$s '$4=="harvest"{t=$2+0; if(n==0||t-h[n-1]>0.5){h[n++]=t}} END{print s, h[0], h[1]}' $f; done | sort -n > $W/../hv_$r.txt
done
python3 -I - "$@" <<'PY'
import sys,statistics as st
import os; W=os.environ['WORK']+'/'
base=None
for r in sys.argv[1:]:
    d={int(l.split()[0]):tuple(map(float,l.split()[1:])) for l in open(W+'hv_'+r+'.txt')}
    if base is None: base=d
    A=[d[s][0] for s in d]; B=[d[s][1]-d[s][0] for s in d]
    dA=[d[s][0]-base[s][0] for s in d]; dT=[d[s][1]-base[s][1] for s in d]
    se=lambda x: st.pstdev(x)/len(x)**.5
    print('%-14s A %.4f B %.4f end %.4f | dA %+.4f+-%.4f dEnd %+.4f+-%.4f'%(r,st.mean(A),st.mean(B),st.mean(A)+st.mean(B),st.mean(dA),se(dA),st.mean(dT),se(dT)))
PY
