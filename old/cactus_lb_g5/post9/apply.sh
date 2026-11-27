#!/bin/sh
# post8 entry -> post9 entry: forward tail helper (old splits) + deadline-gated helper spawns
# usage: sh apply.sh post8_entry.py OUT.py   (run from this folder)
K=0 python3 fwd.py "$1" "$2.k0.py" && python3 gate.py "$2.k0.py" "$2" 0.09 && rm -f "$2.k0.py"
