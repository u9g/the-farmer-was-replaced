g5: generator for `cactus_lb_entry.py` (Leaderboards.Cactus). 7.445 s over a full 968-run attempt
(g3's entry: 7.87 s on the same seeds). Every run meets the goal.

    WIDTHS=2,2,2,2,2,3,3,3,3,3,3,3,2,2,2,2,2,2,2 TAPERX=4 JMAX=5 DEPTH=8 AITER=5 DIRS=1 python g5.py ../../cactus_lb_entry.py

g5.py needs scipy and numpy (`pip install scipy numpy`): without scipy it quietly skips the free
round-B assignment (`linear_sum_assignment`) and the output no longer matches the shipped entry.
With them the merged command below reproduces the pre-post3 entry byte for byte. The shipped entry
is that output with post3..post7 applied (post7: `post7/apply.sh`).

Merged entry (launch tree + round-B routing + tail post-processing), one command:

    WIDTHS=2,2,2,2,2,3,3,3,3,3,3,3,2,2,2,2,2,2,2 TAPERX=4 JMAX=5 DEPTH=6 AITER=5 DIRS=1 SPOBJ=exp SPTAU=600 CHOICE=2 KA=3 KB=6 KP=6 LEAFPUSH=1 POST=1 python g5.py ../../cactus_lb_entry.py

- `SPOBJ=exp SPTAU=600 DEPTH=6` (spawnx.py): launch tree weighted by each chunk's planned finish.
- `NEST=1` (default, nest.py): each `w<k>` is defined inside its spawner just before its spawn.
- `CHOICE=2 KA KB KP` (g5_cols.py, `pk2` runtime): round-B 3-wide columns route a measured
  value into the far cell or the next column's entry; `LEAFPUSH=1`: dead ends planted by swap.
- `POST=1` (post/post.py, run on the flat entry before nesting): HARVESTER=3 does the first
  harvest (hswap), fm tails forked to free drone slots (fork2, NMIN=3; its geometry check passes
  for every tail with pk2 routing, which runs before `tl` and only in the drone's own chunk),
  free junction exits (fexit), per-site fm/jf code (spec, jspec), fork tables as tuples (tup),
  unused defs dropped (clean). `POSTSTEPS=hswap,fork2,...` keeps only some steps.

It reuses the layout, junction model, spawn plan and race rules of `../cactus_lb_g2` (g2.py,
g3.py, lay.py, jlazy.py, spawnmm.py, build_entry.py) and changes the planner and the code layout.

## What changed against g3

- **Balanced plan** (`plan5` in g5.py). g3 searched for the smallest latest finish and took any
  cut set that met it, so some chunks sat at the limit and others had up to 1 s of slack; with
  the model a little off, the ones at the limit were late in every run. plan5 picks exactly 32
  chunks that minimise the sum of `exp(finish / SOFT)` (SOFT=600 ticks), for round A and round B.
- **Facing cuts counted.** Where two walks end at the same cut, the drone that ends first waits
  for the other's last plant before it starts its tail (`xcasw`). g3's model left that wait out;
  in a balanced plan the two end chunks (two junctions each) waited ~0.6 s there and set the
  first harvest.
- **Costs fitted to the simulator.** The isolated mixed cell fix is 350 ticks, not 230 (C_FM).
  Pre-travel to the round-B start has PTM=300 ticks more slack than the model's balanced finish,
  because the harvest waits for the latest drone of the run.
- **One function per drone** (`w0`..`w31`: launch steps, round A, pre-travel, round B). g3's
  96 fa/fb/pt functions and its FA/FB/PT/LP tables cost the main drone 405 ticks before the first
  spawn (a `def` and a list element are 1 tick each): 0.06 s off every drone's start.
- **Columns planted from two cells in round B.** 3-wide bands are walked column by column in one
  direction (`zig_order5`). With no tilling to do, the drone plants the entry cell, steps to the
  middle, plants, swaps that cactus into the far cell and plants the middle again: 6 actions per
  column instead of 7 (`PUSH=0` turns it off). Worth about 0.08 s.
- **Growth wait from the plant itself.** `tl` is read 200 ticks after the last plant took
  effect, so the wait is 0.9676 s, not 1.0001 (GSUB). 0.9672 passes, 0.96 harvests ungrown cactus.

- **Any drone takes any round-B chunk.** g3 gave round-B chunk k to drone k, so a drone whose
  round-A tail ended far from that chunk's start kept travelling after the first harvest (0.10 s
  per drone on average, 0.68 s for the worst). Now the drones are assigned to the chunks by
  distance over the torus (`linear_sum_assignment` on the planner's own objective) and the
  chunks are cut again for that assignment, a few rounds (`BASSIGN=0` turns it off). About half
  the drones change chunk; 7.473 -> 7.445 s.

Measured in the simulator (mean of the run): first harvest 4.70 -> 4.44 s, second round
3.12 -> 2.94 s.

## Tools

- `calib.py WORKDIR N`: plan, trace the entry over SEEDS seeds with `tfwr_diag.rs`, compare each
  chunk's measured finish with the planner's and feed the difference back as extra ticks per
  cell (`CORR`), N times. With the balanced planner the difference settles at about 120 ticks
  (round A) and 180 (round B) per chunk and the score no longer moves, so the shipped entry uses
  no corrections. `MODEL=file.json python g5.py out.py` dumps the planner's per-chunk figures.
- `python ../../.claude/skills/cactus-diag/cactus_diag.py --chunks TRACES... ENTRY.py`: when
  each chunk's drone is done in each round, mean and sd, and how often it was the latest.
- `mc_col2.py`, `mc_col3.py`: Monte Carlo of the in-place column sort below.
- `junction_sim.py`: the junction settle against the fewest swaps possible (see the last section).

## Tried, not used

- **Sorting a 3-wide column in place right after planting it** (`COLFIX=1`, routines `cmd`/`cmu`
  in g5_cols.py: bubble the three cells from the middle, fix the edge to the previous column,
  detour for the previous middle's edge only when needed). 2.0 actions per column in the forward
  pass against 3.55 in the tail (2 moves and 1.55 swaps), but the tail runs inside the 1 s growth
  wait, which is free. 7.58 s. `MIRROR=1` (backward walks hand the mixed cells at a cut to the
  neighbour, as forward walks do) is needed with it and costs a little alone (7.55 s).
- **Watering the last cells** (`WA`, `WB`): a watered cactus swapped onto a dry cell grows at
  the dry rate again, so a fix swap in the tail puts back most of the second and the shortened
  wait harvests ungrown cactus. Runs fail.
- **Variance terms** (`ZB`, `ZF`): 7.51 s (ZB=0.25) to 7.67 s (ZB=1).
- g3's own knobs (C_FM, C_CAS, JF, DEPTH, PTF, ZB, ZF) with g3's planner: 7.84 s at best, noise.

## Where the time is, and why 6 s is out of reach

At 6075 ticks/s an action is 32.9 ms. The goal is 32 x 1024^2 cactus: one sorted harvest of all
1024 cells, or two of 725.

- Two harvests (this design), per drone: round A move + till + plant for 725 cells is 68 actions
  (2.24 s), round B move + plant is 45 (1.49 s), and each round ends 1 s after its last plant:
  5.73 s. Deploying 32 drones adds 0.3 s at the very least (0.76 s here). That is 6.0 s with no
  sorting at all and every drone finishing at the same instant.
- This entry: drones start planting at 0.76 s on average, plant until about 3.2 s, and the first harvest
  comes at 4.44 s; round B plants for 1.6 s and its harvest comes 2.94 s after the first. In both
  rounds the average drone is done 0.24 to 0.30 s before the harvest: the harvest waits for the
  latest of 32 drones, and tail work is random (sd 0.05 to 0.2 s per drone, junction settles most).
- One harvest of 1024 would need 96 actions per drone and one growth wait (4.5 s), but the whole
  32x32 field must then be sorted in both directions. Going by how far the values have to
  travel, a random field needs 6000 or more adjacent swaps for that, against about 2300 actions
  left before 6 s.

What is left in this design: the spread between drones (0.5 s over both rounds), deployment
(0.76 s average before the first plant), and cheaper junction settles (18 per round, 0.5 to 0.8 s
each, the widest spread of any tail item).

## Looking for 7.25 s: where the 7.47 s goes, and what did not move it

(Written before the free round-B assignment, which took 0.03 s of the travel listed below.)

With the entry's own shapes (4 moves per 3-wide column in round A, 2 actions per cell in round B)
the floor is: 0.76 s average arrival + 2.39 s planting + 1 s growth for round A, 1.56 s planting +
1 s growth for round B, 0.03 s for the last harvest: 6.74 s. The entry is 0.73 s above that:

- round A, 0.29 s: 0.05 s of inline swaps; the latest chunk's mean finish is 0.13 s past the
  rest of the floor (tail work that does not fit the growth wait, planting that ends unevenly);
  the harvest comes 0.11 s after that mean, since it waits for the latest of 32 drones;
- round B, 0.43 s: 0.05 s of inline swaps, 0.07 s of travel left over from the pre-travel, 0.14 s
  for the latest chunk's mean, 0.17 s from that mean to the harvest.
  (The 0.05 s and the two 0.13/0.14 s figures are my split of a measured total.)

Tail work is about 31 drone-seconds per round (my estimate from the action counts) against 32
drone-seconds of growth wait, so the wait is full: fix work moved into the forward pass costs
time there, and fix work left in the tail runs past the wait. Over 40% of the tail work is walking
back (420 moves per round), 30% the junction settles, the rest swaps. Measured against that:

- **Junction settle** (`junction_sim.py`): the shipped work list does 4.7 swaps where the fewest
  possible is 4.4 when the cells around the junction are already settled, and 7.1 against 6.5
  when nothing is, so only its 7 moves can shrink. In the planner's model the best of all 24
  visiting orders is 0.6 action (of 16) better than the shipped one; nearest-cell-first with a
  free exit saves up to 2 of 13; settling while planting costs more (14.8). Not built: about
  0.03 s.
- **Layouts with fewer mixed cells**: 129 to 131 isolated middles instead of 144 (a 3-wide band in
  a corner), or 60 to 86 with 7-cell junctions (four 3-wide bands, JMAX=7): 7.53 to 7.66 s
  against 7.46 s on the same 128 seeds.
- **A margin under the growth wait** (`TM_A`, `TM_B`), alone or with the in-place column sort in
  round B only (`COLFIX_A=0`): 7.46 to 7.58 s. A short run of sorted columns still leaves its
  first middle to the neighbour and its last one to the tail, so the planner hardly uses it.
- **Planting on the way to the chunk start**: a drone crossing a 3-wide band could plant a
  column's end cell and save its owner two moves, but only 43 such cells lie on shortest paths:
  at most 0.09 s, in round A only. Not built.
- **Starting every chunk at its nearer end**: start distances fall from 510 to 417 moves, but
  the chunks that gain sit in the middle of 3-wide bands and would end facing each other there,
  where the first tail fixes of both drones share cells. Not built.
- The interpreter overhead of `fmc` is 23 ticks per call and of `jf` 240: nothing to unroll.

## Flying across the field edges

Moves wrap, sorting does not: a cactus has no neighbour across an edge, so only travel can use
the wrap. All travel is already routed over the torus (`tdist`, `path_moves`):

- deployment in round A crosses an edge 23 times per run and is 272 moves shorter for it (482
  moves instead of 754): the origin is next to all four corners and to both ends of the long
  middle bands;
- the trip from a drone's round-A end to its round-B start never crosses one, with chunk k tied
  to drone k or with the free assignment: no round-B start is nearer across an edge;
- tail walks and junction settles stay inside a chunk, whose cells are neighbours in the field.

What the wrap cannot do is shorten a planting walk: a chunk is a run of field neighbours along
an antidiagonal band, and continuing past the edge lands on a different band that another
drone plants.

## Is there a different structure underneath? (checked, none found)

The run is: deploy, plant 725, wait 1 s, harvest, plant 725, wait 1 s, harvest. Each part against
the game's rules (as ported in `tfwr_sim.rs`):

- **One harvest instead of two.** 1024 sorted cells would be 96 actions per drone and one wait,
  about 4.6 s before sorting. Sorting the whole field: a value sits about 13 cells (along x + y)
  from where a sorted field wants it, so about 6600 swaps, plus the moves to make them, against
  the 2800 actions 32 drones have between 3.6 s and 6.5 s.
- **Uneven rounds.** Cells not planted yet do no harm to a harvest, so round one could skip cells
  that only round two plants (677 then 768 meets the goal). Round one saves 0.20 s, round two
  loses 0.09 s of planting and 0.19 s of extra middle-cell fixes its full growth wait cannot
  take. The reverse (768 then 677) loses the same way in round one.
- **Planting for round two before the first harvest.** A cactus that is not grown makes every
  cactus next to it unsorted, and an unsorted cactus is neither harvested nor passes the harvest
  on. The layout fills the field with walls one cell thick, so there is no cell to plant early
  that is not next to a round-one cell.
- **Tilling** is 725 actions, 0.75 s per drone. The only other thing that turns grassland to
  soil is a dinosaur tail segment, and a tail needs an apple, which costs 64 cactus: none until
  the first harvest, by which time everything is tilled. (One drone only, and its moves cost 400
  ticks.) A cactus cannot be swapped onto grassland either: grass is not swappable and grows
  back at once.
- **Cactus numbers.** A cell keeps its number until the cactus on it is grown, and a swap moves
  the number with the cactus, so a number is used once: no copies, no way to carry round one's
  order into round two, no reroll without growing.
- **The growth waits** hold the fix work. With every fix done while planting instead (half the
  actions, no walking back) the tails are empty and watering becomes safe, but the water supply
  (25.6 per second) covers about three cells per drone in round A and one in round B: 7.38 s by
  the same arithmetic as the floor above, before any spread between drones.
- **Deployment.** The layout's cells are 16.2 moves from the origin on average and the chunk
  starts 15.9. If every drone planted on its way out, ring by ring, about 360 of today's 510
  flying moves would still plant nothing, because the rings near the origin hold fewer cells
  than 32 drones need (`plant as you go` bound; chunks would have to cross bands). At most
  0.15 s.
- **Waiting for the slowest drone** (0.5 s over both rounds). Sharing tail work between
  neighbours needs each to know what the other has fixed; the only signals are actions (200
  ticks each), and two drones fixing next to each other corrupt the order.

