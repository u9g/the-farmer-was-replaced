post11 on the post10 entry: the end of round B. Paired results, with no failed runs:

| Seeds | Δ mean ± se | Faster on |
|---|---|---|
| 2200000-2202047 | -1.5 ± 0.2 ms | 1737 of 2048 |
| 2600000-2602047 | -2.0 ± 0.2 ms | 1735 of 2048 |

    python3 bend.py post10_entry.py ../../../cactus_lb_entry.py fqh

This rebuilds the shipped entry byte for byte from post10 (`git show 216e167:cactus_lb_entry.py`).

What the end of round B waits on, from 128 traces: the 62 ms between the last cactus growing and
the harvest is mostly fix work; the last swap ends after the last growth in 86-96 of 128 runs.
Against the later of the two, the harvest starts only 4.8 ms late. About 3.8 ms of that is a fixed
cost in every run: the last fixer's final reads, and the main drone's poll and harvest start. The
`hb + 2.6` floor never set the harvest time in any of the 128 runs.

The three steps (`fqh`):
- f: the main drone runs `wait_until(hm + 2.6)` before `while num_drones() > 1:` rather than
  after it, so the floor wait overlaps the other drones' work. -0.5 ms.
- h: `hlp` and `own` call the final `FS[e]()` after the loop, instead of testing `if j < e` on
  every pass. e only ever shrinks to j+1 or more, so it behaves the same. About -0.3 ms.
- q: w13's round-B deadline is 67 ms earlier (`pkq()`; round A keeps `wA = use_item(Items.Water,
  4)`). Its last `pk_East_North_None_0_0` always pushes the second-to-last cactus North onto
  (7,22). w13 watered that cell with 4 water in round A in all 128 seeds, and wet cells stay wet
  through the harvest. Both watered cacti grow before the third-to-last plant, which is then
  what sets the deadline: P+0.868 instead of P+0.935 (P is w13's final plant), a margin of about
  24 ms. If either water use failed, the old rule applies. About -0.6 ms.

Tried, not used:
- Cutting every watered chunk's wait (the `- 0.0988`) by another 30 or 60 ms: fails seed 9. Only
  w13 had room that could be proven.
- Writing the growth waits inline as `while get_time() < tl + 0.9676: pass`: +11.9 ms. Keep
  `wait_until`, which the simulator skips cheaply.
- The last drone harvesting instead of the main drone: no gain, and two drones ending in the same
  tick could leave nobody to harvest.
- Dropping the `hb + 2.6` floor: it can't be proven safe, and it is worth nothing once f is in.
