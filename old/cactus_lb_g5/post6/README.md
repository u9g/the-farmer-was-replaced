Tills on the launch flight, on the post5 entry: 7.137 -> 7.117 s on 2048 fresh seeds (120000-122047),
7.120 s on a full 1012-run attempt, 4096 more seeds (90000-94095) at 7.119 s without a failure.

A drone's moves to its chunk can be taken in any order for the same cost. A drone with slack
reorders its flight to pass over cells of the binding chunks and tills them there (+1 action for it,
-1 for the owner, whose `till()` for that cell is deleted). 16 tills moved, picked greedily in two
rounds on 256 traced seeds against a per-seed model of the whole run (harvest A, each drone's
readiness for round B, its round-B end), not round A alone: a round-A-only pick gave its gain back
in round B. Excluded: the w19 harvester, the round-B-critical drones (w18, w2, w13, w12) and the
ten cells post4's apply_preplant already tills and plants (a second till turns soil back to grass).

Safety: for every moved cell the tiller must be there before the owner's earliest possible arrival
(its path with no swaps) by a margin; the trace check (`safe2.py`) over 4096 seeds found no cell
planted before it was tilled and no cell tilled twice, tightest gap 0.165 s.

Pipeline (traces from `.claude/skills/cactus-diag/tfwr_diag.rs`, `WORK` a scratch dir):

- `parse.py`: the nested entry's launch tree and each drone's flight;
- `arr2.py`, `full.py`: per-drone, per-seed stats from traces (round-A done counts the last
  drone's self-harvest as its signal);
- `tillopt.py ENTRY STATS.json TILLS.json OUT.py [MARGIN MAXN EPS]`, with `FULL=stats` for the
  two-round model and `EXCELLS="x,y;x,y"` for cells to leave alone;
- `safe2.py`: the trace safety check; `abt.sh` / `ab.sh`: paired A/B on traces.

The picks are tied to this entry's chunk code: re-run after any regeneration.

Tried, not used (launch phase): a re-optimised launch tree from measured chunk times (+0.008 s);
any drone or the harvester mid-flight doing the first harvest (A earlier by 0.006-0.012 s, given
back in round B); off-path detours to till (nothing worth it). Mean arrival is 0.713 s against a
floor of 0.703 s. Not built: chunks starting nearer the origin (start distances 520 -> 419 moves,
~0.1 s less arrival per drone), which needs the planner.
