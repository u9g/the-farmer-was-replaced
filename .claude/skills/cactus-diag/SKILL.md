---
name: cactus-diag
description: Find where a cactus leaderboard run (two sorted harvests, many drones) loses time, including head-of-line tools (which drone every other waits for, and what its chain spent time on) and a linter for repeated or unnecessary work (detour walks, undone or useless swaps, visits whose values were already known). Traces every action of every drone with a diagnostic copy of the tfwr simulator and reports which drone and routine set each harvest time, what its tail spent its time on, whether a harvest waited on growth or on fixes, when each chunk's drone is done over many seeds (which chunks are late every run, which only vary), per-junction settle times, and cells two drones swapped close together. Use before changing cactus_lb_entry.py or its generators, to pick a target.
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
- the latest drones: simulator drone id, the routine it ran (the chunk: `w<N>` in a g5 entry,
  `fa<N>`/`fb<N>` in a g3 one), arrival
  (first plant), last plant, work end, and the tail after the last plant split into move, swap,
  spin (a read repeated on the same line), read and use, and by function (jf, fmc, ...);
- all drones' time booked by kind (drone-seconds), and with `--drone K` one drone's time by function.
  Each gap between a drone's events is booked to the earlier event: an action's own 200 ticks plus
  the compute that follows it.

Also: swaps by two different drones on one cell less than 0.1 s apart (possible races).

`--summary` over many seeds: how often each routine set each harvest, how far the slowest drone
was behind the mean, and every junction settle (`jf` call) with its mean and worst duration.

`--chunks` over many seeds, per round and per chunk: the drone's last plant, when it is done (fix
work finished and its last cactus grown; in round A the moment it signals), the sd of that over
the seeds, and in how many runs it was the latest. A harvest waits for the latest drone, so read
it two ways:

- a chunk whose mean is above the others (marked) is late in every run: the planner's cost for it
  is wrong, or it waits on another drone. Look at that chunk with the one-run report.
- a chunk with a wide sd is late only sometimes; many of those push the harvest past every mean.

Start here. On the g3 entry it showed three chunks done 1 s before the rest and six always late,
and in a balanced plan the two end chunks stuck 0.35 s behind a neighbour's last plant, which
`--summary` (slowest drone minus mean) reports as a single number. `old/cactus_lb_g5/calib.py`
does the same comparison against the planner's own figures.

## Head-of-line tools: the work every other drone waits for

Totals over all drones mostly show work that runs while a drone would be waiting anyway. A
harvest waits only for the drone that finishes last, so these tools look at that drone. Each drone
in a round finishes at max(its done time, its last plant + 0.968 s growth). In round A the done
time is its done signal, the `use_item(Items.Water)` (or harvest) after `wait_until`; the moves
after it are pre-travel to round B, which the harvest does not wait for. In round B it is the
drone's last action. All four tools read the same traces as `cactus_diag.py`.

- `hol_split.py TRACES...`: the five latest drones of each round, with their finish time, arrival,
  planting-phase action counts, and how far the tail ran past the growth wait. The gaps between
  them are the most that trimming any one drone can save.
- `hol_chain.py ENTRY.py TRACES...`: which drone is head of line in how many runs, and its chain
  time (start of the round to last plant, or to the tail end when the tail outlasts growth) by
  function, action kind and line.
- `hol_tail.py ENTRY.py N TRACES...`: what the N latest drones did after their growth wait
  ended, which is the only tail work the harvest waits for.
- `cactlint.py ENTRY.py TRACES... [--top N]`: a linter for repeated or unnecessary work. It
  checks the source for move runs a shorter run would cover (cancelling moves, or the long way
  round the 32-wide torus) and for back-to-back swaps that undo each other. It then replays every
  drone's cells and values from the traces and flags:
  - walks longer than the torus distance between two side effects (D1) or two work actions (D2);
  - swaps of equal values (D3), swaps undone later (D4), and swaps that move both cacti away from
    every cell their value ends in (D5);
  - double tills (D6) and water on a cactus that is swapped away (D7);
  - moves after a drone's last work (D8) and repeated reads (D9);
  - read-only visits whose every value the drone already knew, unchanged since (D10). D10u is
    the same visit with a value another drone changed since, where a value cache would be wrong;
  - read-only visits whose reads could be made from the stop before or after (D11);
  - walks onto a cell only to swap back toward where the drone came from (D12).

  Each finding is reported three ways: actions per run over all drones; head-of-line ms, meaning
  waste on the drone the harvest waits for, capped by its lead over the next drone and by its
  growth wait; and the harvest saved if the pattern were removed on every drone at once.

Both growth and the round-A harvester are handled in `growth.py`, which all four tools (and
`cactus_diag.py --chunks`) use:
- A drone's growth finish is when the last cactus it planted actually grew. The cactus is followed
  through swaps, because growth belongs to the cactus, not the cell.
- The round-A harvester's `harvest()` lands exactly on the harvest time, and it counts as that
  drone's done event. An earlier version dropped it and made round A look balanced to 8 ms.

On the post8 entry (7.057 s, 128 seeds):
- **Lead of the head drone over the next:** round A 39 ms (60 to the 3rd), round B 37 ms. In
  224 of 256 rounds the head drone is bound by its tail rather than its growth.
- **Round A:** the head drone runs 182 ms past its growth wait. That tail is mostly moves and
  `fSW_NE`/`fsSW_NE` swaps.
- **Round B:** the head runs 226 ms past its growth wait, mostly `hlp` walking and `fsSW_NE`
  swaps.
- **Oracle:** with `fSW_NE` swaps costing 1 tick in a copy of the simulator, the score improves
  by -0.084 ± 0.006 s (256 paired seeds). So tail fix work is the hot path everyone waits for.
- **Linter:** no static findings, no equal or undone swaps, no double tills. Removing each
  pattern on every drone would save 20 ms (detours, D2), 12 ms (known-value visits, D10) and
  11 ms (moves after the last work, D8).

## Findings for the shipped entry (g5, 7.44 s), 48 seeds

- First harvest 4.44 s, second 2.94 s later. In round A no chunk's mean is more than 0.13 s
  above the average (the two end chunks are 0.3 s below it); in round B the latest chunk's mean
  is 0.22 s above. The latest chunk changes from run to run: what is left is mostly spread.
- The harvest still comes 0.24 s (A) and 0.32 s (B) after the average chunk is done. Chunks that
  only wait for growth have an sd near 0; junction chunks 0.10 to 0.20 s.
- Junction settles take 0.5 to 0.8 s per call, worst cases 1.1 s.
- Moves take most of the drones' time: 64 drone-s in round A and 39 in B, against 24 for planting.
- Round B starts 0.025 s after the harvest on average (first plant), down from 0.07 s when drone
  k always took chunk k.
