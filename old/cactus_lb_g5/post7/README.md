post7 on the post6 entry: 7.119 -> 7.088 s on 2 x 2048 paired seeds (1-2048, 300000-302047),
7.090 s on 4096 more (500000-504095), 7.087 s on a full 1016-run attempt; no failed runs.

    sh apply.sh post6_entry.py ../../../cactus_lb_entry.py

reproduces the shipped entry from the post6 one (`git show feac9d5:cactus_lb_entry.py`).
Every pass is a text transform; most find their targets by pattern and assert on shapes they do
not know. Paired 2048-seed means per group, each alone on post6:

- Round A tails (-0.012): `jfree.py`, 14 junction settles that end mid-tail go on from the cell
  they ended on instead of walking back; `dtr.py`, 11 move runs left by earlier passes with
  detours (`WNNEN`) become shortest paths; `wlast.py`, the three always growth-bound chunks
  (w12, w16, w23) water their last cell and count the growth wait from the plant before
  (NSIG += 12 so the water-count signal still adds up). Watering busier chunks costs time.
- Interpreter ticks (-0.012, measured at 4096 seeds x 3 blocks): `once.py`, inline fix loops
  end after one swap and re-read only the drone's own cell (not done in the shared fs* routines:
  the main drone and its helper work side by side there and runs failed); `jstatic.py`, a
  junction's first pass over its work list is straight-line code, the loop handles only
  re-queued cells (keeps the entry at ~88k of 100k syntax nodes); `ownargs.py`, own/hlp get
  their tables as arguments; `wat.py`, water before the last round-B plant of one more
  growth-bound chunk (line number: re-pick after a regeneration).
- Round-B assignment (-0.013): `reassign.py IN OUT MAP` moves round-B blocks between drones
  and regenerates their pre-travel. MAP (chunk=drone) is a 10-drone cycle picked on 280 traced
  seeds to minimise each chunk's measured start lateness after the first harvest
  (`assign.py` on traces, then `hung.py`). Chunk start cells are taken from post6 traces.
  Re-pick MAP after changes to round-A tail ends.

All three together: -0.031 s, so the gains add up.

Tried, not used:
- launch: lazy round-B defs (`lazydefs.py`, first spawn 21 -> 11 ticks, ~0.002 s, under the
  noise); more flight tills / dead-end plants (+0.007); the launch is 0.01 s above its floor.
- round A: harvester polling between moves (`hv1.py`, first harvest -0.001, score no gain).
- round B: pk2 thresholds KA/KB/KP (shipped 3/6/6 are optimal, KP=7 -0.002 noise); w0 in the
  reassignment (+0.010); drones ending without the growth wait (runs fail).
- mechanics: shorter xcasw wait (-0.0004), growth wait 0.9672 (noise), watering before each
  fertilised last plant (+0.006). Compute nearly free (`--tweak compute=0.05`) would give
  7.041 s on post6, so interpreter work had at most 0.075 s in it.
- design: uneven or overlapping rounds, three rounds, rerolling cactus values (a cell keeps its
  ungrown value through destroy and replant), layouts with fewer mixed cells (best 2/3-band
  layout with 4 three-wide bands: +0.264 s, its 7-8 cell junctions cost more than the middles
  save).

Left: chunks that start nearer the origin (needs the planner; ~0.1 s less arrival per drone),
round-A helper forks (no free slots in round A).
