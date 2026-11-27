Cactus for the fastest reset (`run_reset.py`, `cactus_round`): 2-wide antidiagonal bands
instead of a sorted field. `bands.py` prints the `bd_cuts()` table (where each drone's stretch of
the snake starts and how many of its cells it fixes on the walk back).

## Layout

Cells with x + y = s or s + 1 (s = 0, 3, 6, ...) hold cactus; the diagonals in between stay empty
except one connector cell each, at the field edge, which joins the bands into one snake. A band
cell's only cactus neighbours are on the other diagonal of its band, so every cell on s only has
to be no bigger than its neighbours and every cell on s + 1 no smaller ("pure" cells): one
compare-and-swap per edge, never undone by another. Only the connectors and the cells next to
them are "mixed" (a chain over five diagonals), settled by a small work list. 97 of 144 cells on
12x12, 172 of 256 on 16x16, so 45% of a full field's yield per harvest.

## Measured (simulator, speed 5 with power, Cactus 2, rounds back to back)

| field, drones | old full sort | bands | cactus/min |
|---|---|---|---|
| 12x12, 4 | 16.9 s, 41.3k | 4.36 s, 18.8k | 147k -> 259k |
| 12x12, 8 | 9.45 s, 40.6k | 2.91 s, 18.8k | 259k -> 387k |
| 16x16, 8 | 18.2 s, 130k | 3.61 s, 59.2k | 430k -> 984k |
| 16x16, 16 | 10.3 s, 128k | 2.66 s, 59.2k | 748k -> 1.34M |

The old sort also left cells unsorted on some harvests (16x16: 113k to 131k); the bands harvest
every cell in every round over 16 seeds.

Whole fastest reset, 32 seeds paired: -24.6 s ± 5.6 s (faster on 25 of 32), 32:16 -> 31:51 mean.
Cactus rounds take 1:24 instead of 2:17 a run, but a band round plants more cells per cactus
(2 pumpkins x Cactus multiplier per cell; 0.0116 against 0.0078 pumpkins per cactus at 16x16), so
pumpkin and carrot rounds take about 26 s more. Weird rounds turn about 86% of the cactus weird
(43% of the yield as weird substance, against 50% before), and `weird_early` now makes a round
weird whenever that does not add a round.

## How a round runs

Drones are spawned per round (`fan`). Each walks to its stretch, plants it forwards fixing each
cell against the ones planted before it (pure cells: one compare with the previous cell), fixes
the edge to the next stretch's first cell (planted when that drone arrived), then walks back over
its last cells fixing them while the cactus grow, and waits for its last cactus to grow. Cuts are
only between two pure cells, so a mixed cell's neighbours are always in its own stretch. The plan
balances walk to the stretch, planting, fixes, connectors and the walk back against the 1 s
growth wait.

## Tried, not kept

- **Fixing by sweeps** (the old cactus_job rule, restricted to band cells, swept until a whole pass
  was clean): drones swapped the same cell at once at the connectors and left cells unsorted.
- **Cuts kept away from every mixed cell and its neighbours**: too few places to cut on 16x16
  (stretches of 1 cell).
- **Drones kept alive between rounds** (each walks back to its start in the growth wait; drone 0
  harvests 1 s after the pumpkin count shows every cell planted; the others start when the
  cactus count rises): 2.69 s on 16x16 against 2.66 s, 4.79 s on 12x12 against 4.36 s, and a
  harvest is short whenever a walk back runs past the wait. A connector settled on the walk back
  has an sd of 0.2 to 0.3 s.
- **Weird substance on every second cell**: swaps move the weird flags, 76% weird. Tracking the
  flags and only using it where it gains: 82%. Using it whenever the cell before is still plain
  (shipped): 86%.

## Where the time is

A connector costs about 0.5 to 0.75 s for the drone that settles it (6.8 swaps and 10 moves in
`jsim`-style counts, plus interpreter work). The fewest actions for one connector window, sorted
after planting and ending at its last cell, is 13.5 on average (breadth-first search), against
about 15 for the work list. What is left is mostly the pumpkin cost per cactus: a layout with more
cells per round (3-wide bands, whose middle cells are mixed but each fixed standing on it) would
cut it, and has fewer connectors.
