g5: generator for `cactus_lb_entry.py` (Leaderboards.Cactus). 7.473 s over a full 964-run attempt
(g3's entry: 7.87 s on the same seeds). Every run meets the goal.

    WIDTHS=2,2,2,2,2,3,3,3,3,3,3,3,2,2,2,2,2,2,2 TAPERX=4 JMAX=5 DEPTH=8 AITER=5 DIRS=1 python g5.py ../../cactus_lb_entry.py

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

Measured in the simulator (mean of the run): first harvest 4.70 -> 4.44 s, second round
3.12 -> 2.99 s.

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
  comes at 4.44 s; round B plants for 1.6 s and its harvest comes 2.99 s after the first. In both
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

With the entry's own shapes (4 moves per 3-wide column in round A, 2 actions per cell in round B)
the floor is: 0.76 s average arrival + 2.39 s planting + 1 s growth for round A, 1.56 s planting +
1 s growth for round B, 0.03 s for the last harvest: 6.74 s. The entry is 0.73 s above that:

- round A, 0.29 s: 0.05 s of inline swaps, about 0.10 s of tail work that does not fit the
  growth wait, and 0.14 s because the harvest waits for the latest of 32 drones;
- round B, 0.43 s: 0.05 s of inline swaps, 0.07 s of travel left over from the pre-travel, 0.12 s
  of tail work over the wait, and 0.19 s for the latest drone.

Tail work is about 31.5 drone-seconds per round against 32 drone-seconds of growth wait, so the
wait is full: fix work moved into the forward pass costs time there, and fix work left in the
tail runs past the wait. A third of the tail work is walking back (420 moves per round), a third
is the junction settles, the rest swaps. Measured against that:

- **Junction settle** (`junction_sim.py`): the shipped work list does 5.9 swaps where the fewest
  possible is 5.5 (7.1 against 6.5 with nothing settled around it), so only its 7 moves can
  shrink. Every visiting order is within 0.3 action of the shipped one; nearest-cell-first with a
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

