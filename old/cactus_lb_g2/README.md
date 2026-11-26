Generator for `cactus_lb_entry.py` (Leaderboards.Cactus), 7.996 s over a full 901-run attempt.

    WIDTHS=2,2,2,2,2,2,2,2,3,3,2,2,2,2,2,3,2,2,2,3 TAPER=1 python g2.py ../../cactus_lb_entry.py

Layout: a snake of antidiagonal bands (mostly 2 wide, four 3 wide with the middle diagonal
dropped next to the connectors), one connector cell per wall at the snake's turns: 726 cells,
harvested twice.

Fixes:
- every edge between a pure-low cell (no lower neighbours) and a pure-high cell (no upper
  neighbours) is one compare-and-swap, done inline while planting or in the back-walk; such a
  swap only ever improves both cells' other edges, so these never cascade and order is free;
- an isolated mixed cell (3-wide band middle) is fixed standing on it (`fm`);
- each junction component (mixed cells touching mixed cells, at the connectors) is settled
  adaptively by `jf` during the growth wait; its expected cost comes from a Monte Carlo
  (`jlazy.py`) and feeds the chunk planner.

`plan()` picks chunk cuts and, per chunk, how many trailing cells defer their fixes into the
1 s growth wait, balancing start offset + forward pass + max(growth, back-walk).

`ilp/`: scipy MILP (HiGHS) models used to bound the design: `ilp_types.py` shows a 725-cell
layout needs at least 125 mixed cells; `span.py` shows a connected layout with no two mixed
cells adjacent cannot span more than 3 antidiagonals (so junction chains are unavoidable).

## g3 (7.86 s over a full 916-run attempt)

    WIDTHS=2,2,2,2,2,3,3,3,3,3,3,3,2,2,2,2,2,2,2 TAPERX=4 JMAX=5 DEPTH=8 AITER=5 DIRS=1 python g3.py ../../cactus_lb_entry.py

- Layout: seven 3-wide bands; next to each connector the far diagonal of a 3-wide band is dropped
  (`TAPERX`, adaptive radius) so every junction component has at most 5 cells (725 cells).
- Chunks may run in either direction. Race-free boundary rules: F|F and R|R as before; at a
  facing cut (F|R) the predicted earlier finisher waits for the other's last plant plus 300
  ticks before fixing the shared edge (`xcasw`), the other fixes its last cell inline; at a
  back-to-back cut (R|F, round A only) the handler is chosen from the exact spawn arrival times
  so its fix never coincides with the other drone's next swap. A mixed cell just past a cut is
  fixed by the drone whose walk ends at that cut; a chunk never defers its first two cells.
- Round-B travel happens in the drone's round-A slack (`PT`), before it waits for the harvest.
