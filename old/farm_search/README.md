# One-drone farm designs found by agents (benchmark win, does not transfer yet)

An experiment in inventing farms automatically: agents write a farm (`run_farm(need)`), a scorer
runs it in the simulator, the agents iterate. One round, three agents with different starting
angles (layout, route and timing, economy), ~45 minutes each.

`eval_farm.py` runs a candidate from a fresh field and empty stock in five states from the early
fastest reset (3x3 to 6x6, one drone) and scores the game seconds to meet a fixed need.
`make_baseline.py` writes `cands/baseline.py` (run_reset's own `mixed_round`). `integrate.py`
puts a candidate into a copy of run_reset.py (every name it defines prefixed) for run_plan's
one-drone hay/wood/carrot rounds on 3x3..6x6.

## Benchmark (16 seeds)

| | A 3x3 | B 4x4 | C 4x4 trees | D 6x6 carrots | E 6x6 mixed | total |
|---|---|---|---|---|---|---|
| baseline (run_reset) | 91.9 | 88.8 | 65.8 | 101.5 | 108.2 | 456.1 |
| layout_18 | 72.9 | 59.6 | 59.8 | 61.8 | 58.8 | 312.8 |
| sched_30 | 73.0 | 56.2 | 58.8 | 59.7 | 60.8 | 308.3 |
| econ_34 | 69.7 | 56.8 | 57.2 | 57.8 | 56.4 | 298.0 |

The three agents found the same main ideas on their own:
- a one-off sunflower burst early: ~10 sunflowers, cut the highest-petal one for 8 power (double
  speed), then turn the cells back into crops. Power arriving at ~20-30 s instead of ~45 s is
  most of D and E's gain
- layouts that keep each crop among other crop types (checkerboards, 2-wide diagonal bands on
  6x6, 4 carrot / 4 bush / 1 grass on 3x3), so the random companion bonus lands more often
  (about x1.9 average yield)
- cells that change crop instead of standing idle (a carrot cell with no seed money grows a bush,
  wood cells go back to grass once wood is covered), and planting by what is still short counting
  what is already growing
- waiting at a nearly ripe plant on small fields, trees on one checkerboard colour with grass
  that is never cut on 4x4 (shorter laps)

## In the real run (int_*, to Megafarm 1, 8 seeds)

econ_34: +270 s against run_plan; sched_30 and layout_18 never finish (they loop forever on a
field or stock they did not expect). econ_34 wins the stretches that look like its benchmark
states and loses the rest:

| stretch | run_plan | econ_34 |
|---|---|---|
| Speed 3 (wood + carrot, 3x3) | 82 s | 70 s |
| Expand 3 | 34 s | 27 s |
| Trees 1 (wood + carrot, 4x4) | 58 s | 37 s |
| Carrots 3 (wood, 4x4 trees) | 72 s | 53 s |
| Grass 2 (300 hay, 4x4) | 16.5 s | 90 s |
| Watering 1, Trees 2, Watering 2, Fertilizer 1, Trees 3 | 2-15 s each | 44-53 s each |
| Sunflowers, Speed 4 | 8.5 s, 48 s | 56 s, 78 s |

The benchmark was too narrow: five fixed states and needs, a fresh field and empty stock, and one
call per state. The run calls the farm ~20 times with every kind of need, on a field and stock
the last round left, and run_plan also plans for the next unlocks (its `look` need). The
candidates restart their layout and sunflower opening on every call, and their per-state layouts
(chosen by field size and need) do not cover hay-heavy or small needs.

## Next round

Score candidates on the run itself: fork the real run at each one-drone stretch
(`tfwr-sim --fork-at`), call the candidate the way run_plan does (current and lookahead needs,
state kept between calls), and score the time to the purchase, summed over all stretches to
Megafarm 1. That benchmark cannot be overfitted without the run getting faster.
