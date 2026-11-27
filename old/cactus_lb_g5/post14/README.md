post14 on the post13 entry: the main drone's final `num_drones()` poll has the free body `q = 0`
(0 ticks) instead of `pass` (1 tick). -0.0001 s ± 0.0000 paired on 4096 fresh seeds
(6000000-6004095, faster on 2024, the rest equal); no failed runs.

    python pollq.py post13_entry.py ../../../cactus_lb_entry.py

Five agents each hunted for out-of-the-box ideas in one corner (launch, game rules, interpreter,
sorting strategy, round B / run end), measured against the post8 entry. Their two wins (forward
round-B helper, main's floor wait before its poll) had meanwhile shipped as post9 and post11;
this free poll body is the only part left. Tick costs measured with get_tick_count: assignment,
name lookup, `not`, `return`, `global`, direct calls, `get_time()` and tuple unpacking are free;
`pass`, `if`, each operator, index, `+=` and reads cost 1; loops cost 1 to enter.

Tried, not used (all paired vs post8, no failures unless noted):
- Rules: the goal is 32 x 1024^2 with ~1.7 cells of margin, harvest spreads only from cells whose
  neighbours are all sorted (no torus wrap), so harvesting one action early drops 725 -> 1..676
  cells; uneven/three rounds need more plantings; fertilizer is supply-bound (1 per 1.25 s, the
  5th arrives too late); water is surplus but growth binds < 6 ms; polyculture can't apply to
  cactus. Moving/removing fertilizers: 0 to +0.0035.
- Launch: pre-tilling late chunks from drones with slack (+0.004..+0.029), 541 spawn-tree
  neighbours and 80 mid-flight spawn points (best -0.0025 ± 0.0015, noise on fresh seeds). ~10
  chunks finish within 0.05 s of each other in round A, so speeding one hands the lead to another.
  Shifting w28/w29 launch by 1-2 actions made runs miss the goal (in a common-random-numbers copy
  of the sim): check failures whenever w29's timing moves.
- Interpreter: compute is ~1% of drone time; `--tweak compute=0.01` is only -0.073. lazydb (round-B
  only helpers defined inside a DB() called before round B): -0.0005 ± 0.0010 on top of post9,
  not significant; lazyall -0.0016 ± 0.0005 alone. Lookup tables keyed by measure() cost more defs
  than they save.
- Sorting: re-rolling a cactus value needs plant/swap/plant (a cell keeps its number until grown);
  pk thresholds KA/KB/KP all noise; Monte Carlo of smarter round-B push routing and inline
  compare-swaps trade forward work 1:1 for tail work.
- Round B / end: pre-travelling past the growth margin (+0.018..+0.064), last-round-A drone
  harvesting before its pre-travel list plus reading tl before the inline cas (-0.0009 ± 0.0007 on
  8192, not significant). The round-B end is ~11.5 ms above the rule floor, 7.9 of it the last
  drone's verification moves.
