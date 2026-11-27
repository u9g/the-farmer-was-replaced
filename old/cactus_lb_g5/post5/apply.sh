#!/bin/sh
# usage: apply.sh IN OUT   (interpreter-tick rewrites on the post4 entry)
set -e
d=$(dirname "$0"); t=$(mktemp -d)
python3 "$d/rewrite_fix.py" "$1" "$t/b.py" --peel
python3 "$d/rewrite_inline.py" "$t/b.py" "$t/c.py" --peel
sed -e 's/while len(wk) > 0:/while wk:/' -e 's/if h != None:/if h:/' -e 's/if a == None or b == None:/if not a != None != b:/' "$t/c.py" > "$2"
rm -r "$t"
