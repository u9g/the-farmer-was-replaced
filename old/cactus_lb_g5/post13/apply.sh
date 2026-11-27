#!/bin/sh
# post12 entry -> post13 entry: late drones water their last round-B plant, then drop leaf (10,0)
# usage: sh apply.sh post12_entry.py OUT.py
set -e
D=$(cd "$(dirname "$0")" && pwd)
python3 $D/dynwat.py "$1" "$2.w.py" 6.0
python3 $D/drop10.py "$2.w.py" "$2"
rm -f "$2.w.py"
