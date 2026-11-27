post8 on the post7 entry: 7.087 -> 7.057 s on a full 1021-run attempt; -0.0376 ± 0.0010 s paired on
8192 fresh seeds (1100000-1108191, faster on 5524); 7.087 -> 7.052 s on seeds 1-256; no failed runs.

    sh apply.sh post7_entry.py ../../../cactus_lb_entry.py

reproduces the shipped entry from the post7 one (`git show 2f53be4:cactus_lb_entry.py`). Found by
five agents each searching one part of the run (launch, rules/harvest, tails, interpreter, round B),
then stacked. Passes, in order:

- Tails. `rev.py`: w29 plants its round-A chain in reverse and ends at its edge junction, settling
  it there instead of walking 15 moves back and 9 to its round-B start; it takes over the cross pair
  with w30's last cell (`xcasw West`; plain `xcas` raced on seed 660), so `dropx.py` removes w30's
  `xcas(East, 1)`. `prefix.py`: w14 settles w13's cut middle next to it right after its last plant.
  (-0.008 and -0.004; the same prefix trick on other chunk pairs was worse or crashed.)
- Round B. `early.py 2.6`: each drone records the last time it saw no cactus before the first
  harvest (`hb`) and skips its own growth wait when `tl + 0.9676 <= hb + 2.6`; the main drone never
  harvests before `hb + 2.6`. Provably safe, and it frees drone slots so `hlp` forks start sooner
  (-0.006). `wafter.py w12,w19`: 4 water on the last round-B plant of those chunks, growth wait
  counted 0.0988 s earlier; only pays with the early exit (-0.005). `unearly.py` / `unwater.py`
  undo them (reassign.py needs the early exit removed first).
- Interpreter. `fopt.py`: the single-owner fix routines `fSW_NE`, `fSW_E`, `fS_NE` read each cell
  once and track their swaps in variables; loops become ifs (-0.010). Not safe in the shared `fs*`
  routines or the junction code (runs failed).
- Launch. `mk_tree.py launch_tree_u2b.json`: spawn tree re-fitted (spawnx-style interval search)
  against each chunk's measured round-A time on 144 traced seeds, tau 1.5 (-0.004). Refit after any
  change to a chunk's start cell or round-A tail: the post7-era tree on this entry was +0.083.

Tried, not used: the post7 round-B MAP re-picked on fresh traces (every MAP worse, the old w27/w29
swap +0.007 once w29 is reversed); early-exit cutoffs 2.56-2.64 (2.6 best); watering more chunks;
moving w31's never-useful fertilizer to w12 (-0.003 alone, 0 once w12 is watered); fertilizer on a
round-A last plant; caching values in junction loops, chain passing, hoisting round-B tables;
lazy defs / spawning at tick 3 (-0.001, over the node limit if applied to all); 0.9672 growth wait.
Run end is within ~1 ms of what the rules allow; the launch is ~0.3 action above its spawn-depth floor.

Tool fixes made alongside: `post7/assign.py` read w12/w16/w23's water as the round-A signal and
crashed; `cactus_diag.py` now names lines by the innermost `def` (the nested entry made every drone
w0); `tfwr_sim.rs` prints paired deltas to 4 decimals.
