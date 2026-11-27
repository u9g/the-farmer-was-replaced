post9 on the post8 entry: 7.057 -> 7.044 s on a full 1023-run attempt (seeds from 1400000).
Paired results, with no failed runs (about 5,600 candidate runs):

| Seeds | Δ mean ± se | Faster on |
|---|---|---|
| 900000-902047 | -7.2 ± 0.5 ms | 582 of 2048 |
| 300000-301023 | -7.7 ± 0.8 ms | 300 of 1024 |
| 1300000-1301023 | -7.7 ± 0.8 ms | 295 of 1024 |
| 1-1000 | -7.2 ± 0.8 ms | 291 of 1000 |

    sh apply.sh post8_entry.py ../../../cactus_lb_entry.py

This rebuilds the shipped entry byte for byte from the post8 one
(`git show bd2dbf0:cactus_lb_entry.py`). Both passes work on round-B forked tails (`own` / `hlp`):

- `fwd.py` (with `K=0`, so the old split table SP is kept): the helper walks only from j to its
  first cell lo, then fixes lo..e FORWARD. It used to walk all the way to e and fix back down to
  lo. The order is safe because fixing one middle cell only moves the cells it shares with the next
  one in the direction that cell's own check allows. So two drones fixing neighbouring cells never
  undo each other's work. Alone: -3.6 ± 0.3 ms.
- `gate.py C=0.09`: a drone spawns a helper only when `get_time() + 0.09 * cells_left > DL`, where
  `DL = max(tl + 0.9676, hb + 2.6)`, the drone's own deadline. No drone slot is free until about
  2.04 s into round B, so owners compete for the few that open. Owners whose fixes would finish
  inside their growth wait anyway were taking slots that late owners needed. This only pays with
  the forward helper: gating the old backward helper gave +0.9 ms. Other values of C: 0.08 gave
  -0.9 ms, 0.06 gave +27 ms.

Found with the head-of-line tools in `.claude/skills/cactus-diag/` (`hol_tail.py`). With the
growth and harvester fixes of 9074341, the helper's walk was the biggest item past the growth
wait on round B's latest drones (189 ms per run over the 3 latest). Now it is 137 ms; what is
left is the walk to the helper's own first cell, about 0.7n cells.

Tried, not used:
- Re-fitted split tables (cost models f = 0.5 to 2.0, owner share -1 or +1): no better. Giving
  the helper one cell more cost +13.3 ms.
- The helper calling `own` so it can fork again (three parts): -4.4 against -4.5 ms. Free
  slots are too rare for a second fork.
- Spawning helpers during round-B planting: no slot is free then.
