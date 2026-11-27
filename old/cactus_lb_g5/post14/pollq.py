"""Main drone's final num_drones() poll: body q = 0 (0 ticks) instead of pass (1 tick), so the
harvest follows the last drone's end a tick sooner. usage: python pollq.py IN OUT"""
import sys
s = open(sys.argv[1]).read()
o = "\twhile num_drones() > 1:\n\t\tpass\n\tharvest()\n"
assert s.count(o) == 1
open(sys.argv[2], 'w').write(s.replace(o, "\twhile num_drones() > 1:\n\t\tq = 0\n\tharvest()\n"))
