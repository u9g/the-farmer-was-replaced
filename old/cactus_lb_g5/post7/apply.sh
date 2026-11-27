#!/bin/sh
# post7: text passes on the post6 entry, in this order (see README.md).
#   sh apply.sh IN.py OUT.py
set -e
D=$(dirname "$0")
T=$(mktemp -d)
cp "$1" $T/a.py
# water before the last round-B plant of the chunk whose `tl = get_time()` is at this line of the
# post6 entry (line-number based: must run first)
python3 $D/wat.py $T/a.py $T/a.py ${WATLINES:-8571}
python3 $D/jfree.py $T/a.py $T/b.py
python3 $D/dtr.py $T/b.py $T/c.py
WL=${WL:-w12,w16,w23} python3 $D/wlast.py $T/c.py $T/d.py
python3 $D/once.py $T/d.py $T/e.py meas 12 w0
DYN=1 python3 $D/jstatic.py $T/e.py $T/f.py
python3 $D/ownargs.py $T/f.py $T/g.py
python3 $D/reassign.py $T/g.py "$2" "${REASSIGN:-w1=w3,w2=w4,w3=w2,w4=w5,w5=w26,w14=w1,w26=w27,w27=w29,w29=w31,w31=w14}"
rm -rf $T
