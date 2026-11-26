---
name: cactus-diag
description: Find where a cactus leaderboard run (two sorted harvests, many drones) loses time. Traces every action of every drone with a diagnostic copy of the tfwr simulator and reports which drone and routine set each harvest time, what its tail spent its time on, whether a harvest waited on growth or on fixes, per-junction settle times over many seeds, and cells two drones swapped close together. Use before changing cactus_lb_entry.py or its generators, to pick a target.
---

# Cactus run diagnostics

`tfwr_diag.rs` is a copy of `../tfwr-sim/tfwr_sim.rs` at commit b060991 with one addition. When
the environment variable `CACTUS_TRACE` is set, every run writes `$CACTUS_TRACE.<seed>.tsv`:

- `E t drone kind x y dir ticks file:line extra` for every side effect, stamped when it starts. The
  `extra` field holds the value planted (plant), the two cell values before the swap (swap), or
  the cactus gained (harvest).
- `G t - x y` when a cactus finishes growing.

Timing is unchanged; it is the same simulator. Re-copy it (`git show HEAD:.claude/skills/tfwr-sim/tfwr_sim.rs`)
and re-apply the `trace` additions (search for `CACTUS_TRACE`, `trace_before`, `trace_after`) if
the main simulator changes. `cactus_diag.py` analyses the traces.

Run from the save folder:

```
set CACTUS_TRACE=<scratch dir>\run
cargo +nightly -Zscript .claude/skills/cactus-diag/tfwr_diag.rs run_cactus_lb.py --seeds 24 --quiet
python .claude/skills/cactus-diag/cactus_diag.py <scratch dir>\run.<seed>.tsv cactus_lb_entry.py --top 6
python .claude/skills/cactus-diag/cactus_diag.py --summary <scratch dir>\run.*.tsv cactus_lb_entry.py
```

(In Git Bash: `CACTUS_TRACE="$S/run" cargo ...`.) Keep traces in a scratch directory, never in the
save folder. A 24-seed trace is about 24 files of a few MB.

## What the reports say

One run (`TRACE.tsv ENTRY.py`), per round (A = up to the first harvest, B = up to the second):

- the harvest time, the drones' mean and latest work end (last action that is not a read), and
  last plant;
- the time the last cactus grew, and whether the harvest was bound by GROWTH or by FIX WORK (and
  which drone and routine);
- the latest drones: simulator drone id, the `fa<N>`/`fb<N>` routine it ran (the chunk), arrival
  (first plant), last plant, work end, and the tail after the last plant split into move, swap,
  spin (a read repeated on the same line), read and use, and by function (jf, fmc, ...);
- all drones' time booked by kind (drone-seconds), and with `--drone K` one drone's time by function.
  Each gap between a drone's events is booked to the earlier event: an action's own 200 ticks plus
  the compute that follows it.

Also: swaps by two different drones on one cell less than 0.1 s apart (possible races).

`--summary` over many seeds: how often each routine set each harvest, how far the slowest drone
was behind the mean, and every junction settle (`jf` call) with its mean and worst duration.

## Findings for the shipped entry (g3, 7.865 s), 24 seeds

- Neither harvest waits on growth. Both are bound by fix work in one drone's tail. The slowest
  drone finishes 0.23 s (A) and 0.36 s (B) after the mean.
- The drone that sets the harvest changes from seed to seed. That points to variance in tail
  work, not one bad chunk.
- Junction settles take 0.52 s per call (4-cell junctions) and 0.77 s (the two 5-cell junctions,
  chunks 18 and 22), with worst cases near 1.08 s. A one-seed look at chunk 22 found 1.12 s.
- Moves dominate all drones' time: 67 drone-s in round A and 48 in B, against 24 for planting.
