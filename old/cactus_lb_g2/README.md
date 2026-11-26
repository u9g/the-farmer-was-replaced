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
