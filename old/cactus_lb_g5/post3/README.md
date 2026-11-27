Post-passes on the g5 entry (7.207 -> 7.177 s on 1024 seeds, faster on 723), applied in this order:

    python fert.py IN.py a.py 12116,9131,8224,2339   # fertilize the last round-B plant of the 4 growth-bound chunks
    python ptw.py a.py b.py                          # fly toward the round-B start inside the round-A growth wait
    python jrw.py b.py c.py                          # junction-settle blocks without bi/bv/ti/tv bookkeeping
    python pkrw.py c.py OUT.py                       # pk2 specialised per call site (constants folded)

- fert.py: Fertilizer is unlocked and never used. Four weird cactus cost 4 x 11,600 of the 85,568
  cactus margin. The chunk's wait is then counted from the plant before the last, but only if
  use_item returned True. The line numbers are each chunk's last round-B `plant(...)`, followed by
  `tl = get_time()`, in the g5 entry at commit c45a645. After
  regenerating, pick the chunks again from cactus-diag `--chunks` (the latest growth-bound ones). (-0.012 s)
- ptw.py: pre-travel moves that fit before the drone's own growth time run before the water
  signal. The rest wait until after it. (-0.005 s)
- jrw.py, pkrw.py: interpreter-tick cuts. (-0.010 s together)

Tried, no gain: launch-tree SPTAU/SPOBJ variants, early exit of round-B drones, fork2 forward helpers,
6 fertilized chunks, a shorter xcasw wait.
