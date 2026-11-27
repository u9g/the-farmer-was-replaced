post13 on the post12 entry: 7.037 s on a full 1024-run attempt. Paired results, no failed runs:

| Seeds | Δ mean ± se | Faster on |
|---|---|---|
| 11000000-11008191 | -3.3 ± 0.3 ms | 3168 of 8192 |
| 10000000-10008191 (on post11) | -2.9 ± 0.3 ms | 3115 of 8192 |
| 8000000-8004095 (on post10) | -2.7 ± 0.5 ms | 1589 of 4096 |
| 9000000-9004095 (on post10) | -3.5 ± 0.5 ms | 1669 of 4096 |

    sh apply.sh post12_entry.py ../../../cactus_lb_entry.py   (post12 = git show d0f4a4c:cactus_lb_entry.py)

- `dynwat.py X=6.0` (-1.2 ± 0.3 ms alone on post10): every round-B last plant that is not watered or
  fertilised yet (13 sites on the post12 entry: its merged pk* calls hide 6 of post10's 19) gets `if get_time() > 6.0: use_item(Items.Water, 4)` (before planting where the
  plant before is two actions back, after it where it follows a swap), and the growth wait counts
  from the plant before. Water is plentiful in round B; only late drones pay the action. A threshold
  on `hb` does not work (hb is 0 for every drone that reaches its start after the first harvest).
- `drop10.py` (-1.6 ± 0.4 ms alone): w31's fertilizer (never useful, post8) is dropped, and the freed
  cactus margin (11,600) pays for dropping round-B leaf (10,0): w0 skips its swap and plant there,
  and its junction cell (9,0) loses its East edge. 725 + 724 cells with at most 3 weird cacti still
  clear the goal by 4,448, deterministically.

Found by five agents each chasing wild ideas in one corner of the run, run in parallel with the
post9-post12 session (whose forward helper was the same idea as this search's `fwdhlp.py`, so only
these two passes are new). Dead ends, with bounds from what-if copies of the simulator:

- rules: no loophole. A harvest 20 ms early already loses connectivity in the worst runs (median
  725, worst 281 cells); 50 ms early the median group is ~410. The field sits ready ~1 action
  before the harvest, and no signal under 200 ticks exists for a watcher drone. Unused items
  (polyculture, weird substance) do nothing for cactus; dinosaur-hat moves cost 400 ticks.
- growth: instant growth would save only 0.025 s (0.016 A, 0.017 B); the tails fill the waits.
  Watering more round-A last cells +0.002 to +0.018. No soil is free during round A's wait, so
  round B cannot be planted early.
- launch: the spawn tree is ~0.009 s above its floor for these chunk starts. Free flight for every
  drone would be worth ~0.19 s, single chunks ~0.01. An annealed launch tree +0.0045 ± 0.0064 (128
  seeds). Imports re-run module top level in every drone; compute is never free.
- plan: 725 + 724 is the smallest split that meets the goal; uneven splits explode round-A fixing,
  3 harvests floor at ~8.0 s, one 1024 harvest needs >= 7150 swaps, delete-instead-of-fix ~8.0 s.
- tails: replanting never rerolls (a cell keeps its number until its cactus grows); walls are
  grass; speculative early harvests always miss the goal (margin < one cell); all compute free
  would be worth only ~0.065 s.
