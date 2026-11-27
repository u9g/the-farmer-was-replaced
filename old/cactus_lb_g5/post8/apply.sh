#!/bin/sh
# post8: sh apply.sh IN.py OUT.py   (IN = the post7 entry, git show 2f53be4:cactus_lb_entry.py)
set -e
D=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d)
python3 $D/rev.py "$1" $T/a.py w29 "xcasw(West, 0)" >/dev/null
python3 $D/dropx.py $T/a.py $T/b.py w30 "xcas(East, 1)"
python3 $D/prefix.py $T/b.py $T/c.py w14:West:fsSW_NE
python3 $D/wafter.py $T/c.py $T/d.py w12,w19
python3 $D/early.py $T/d.py $T/e.py 2.6
python3 $D/fopt.py $T/e.py $T/f.py
OUT=$(cd "$(dirname "$2")" && pwd)/$(basename "$2")
(cd $D && python3 mk_tree.py launch_tree_u2b.json "$OUT" $T/f.py)
rm -r $T
