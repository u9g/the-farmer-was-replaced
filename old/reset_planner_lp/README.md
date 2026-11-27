# Fastest reset: plan the whole run with a solver (tried, slower than run_plan)

The idea: stop inventing farms one at a time and solve the run as one system. Measure what each
of `run_reset.py`'s rounds makes per second in each state (field size, drones, levels, speed),
then let a linear program decide what to farm in every stretch between purchases, with stock
carried between them. A search over unlock orders sits on top, and an executor makes the script
follow the solver's schedule so the simulator can check it.

It works as a measuring tool, but no plan it found ran faster than `run_plan`. A linear model of
rates leaves out what decides real round times here: starting a round (clearing and replanting
the field, spawning and collecting drones) and how a round behaves with the stock it really has.

## Files

| file | what it does |
|---|---|
| `bound.py` | lower bound for each hay/wood/carrot stretch (an LP over grass, bush, tree, carrot, with action and regrowth limits), read from a `--profile` unlock table |
| `make_probe.py` | writes `work/probe/run_probe.py`: `run_reset.py` with its run replaced by a timed `farm(PITEM, ...)` (or `power_round()`) that prints the net change of every item |
| `measure.py`, `measure_hwc.py`, `measure_pw.py` | run the probe in many states (`--set`, `--give`) and write `data/rates.json` (pumpkin, weird substance, gold), `data/hwc.json` (hay, wood, carrot rounds), `data/pw.json` (power rounds) |
| `plan_lp.py` | the LP for the run up to Megafarm 2 for a given unlock order (measured rounds as variables, 7 items, stock carried over), simulated annealing over orders that respect prerequisites, and the schedule it implies (`work/sched_<seed>.pkl`) |
| `make_exec.py` | writes `work/exec/run_best.py` and `run_cur.py`: `run_reset.py` that follows a schedule (one combined hay/wood/carrot round, power, then pumpkin, weird, gold rounds per stretch, then the buy), then carries on with `run_plan` |
| `loop.py` | closed loop: solve, execute in the simulator, correct the rates of the rounds each stretch used by executed / predicted time, repeat |

Run from this folder: `python3 make_probe.py work/probe`, `python3 measure.py data/rates.json`
(and the other two), then `python3 plan_lp.py data/profile_seeds1-8.txt 1 3000` or
`python3 loop.py 6 1200`. `data/profile_seeds1-8.txt` is `run_reset_lb.py --seed 1 --seeds 8
--profile --whatif`. The probe and executor are generated from the current `run_reset.py`.

## Results (run_reset.py at 08f4c88, ~25:12)

**How much slack the farming has.** `bound.py` (optimistic: free water, one move per harvest,
the companion bonus at 1.8x before Polyculture and 10x after) against the measured run:

| phase | hay/wood/carrot actual | bound |
|---|---|---|
| 1 drone, to Megafarm 1 | 579 s | 437 s |
| 2 drones, before Polyculture | 85 s | 50 s |
| 2 drones, Polyculture, to Megafarm 2 | 77 s | 22 s |
| Megafarm 2 on | 36 s | 11 s |

About 257 s of slack in hay/wood/carrot and about 110-140 s in the pumpkin stretches. That is
about the 372 s between ~25:12 and 19:00, so 19:00 with this unlock list would need farming at
the ceiling everywhere.

**Measured rounds.** With measured rates the LP predicts the current order to Megafarm 2 at
962 s (1012 s with power charged) against 924 s measured, without any fitting. Things the
probes showed:
- pumpkin and gold rounds on 6x6 and 8x8 are no faster with 2 drones than with 1; 4 drones
  halve the time
- one 6x6 pumpkin harvest with 1 drone takes ~14 s (about 106 moves and 45 plantings, ~11 s
  at the least, since a dead pumpkin is only found by visiting it after it ripens)
- the cost of early pumpkins is mostly their carrot seeds (about 1 carrot per 5 pumpkins)
- `power_round()` makes about 8 power/s net for about 1 carrot per 7 power

**Searched orders.** Every search moved Polyculture (with Pumpkins 1-2) before Megafarm 1. In
the simulator, through `run_plan` (8 seeds, whole runs):

| change | time |
|---|---|
| Pumpkins 1 + Polyculture 1 after Expand 4 | +189 s |
| same after Speed 4 / Trees 3 | +115 s / +130 s |
| Pumpkins 1-2 + Polyculture 1 after Trees 3 / Speed 4 | +93 s / +83 s |
| searched orders, analytic rates | +420 to +818 s |
| searched orders, measured rates | +141 to +284 s |

Polyculture early does make hay/wood/carrot 2-3x faster afterwards (Speed 4's stretch 47.6 s ->
16.5 s), but 3,000 pumpkins on 6x6 with one drone took 4:29 in the run.

**Executing the solver's schedule** (to Megafarm 2, 8 seeds; `run_plan` takes 15:24):

| schedule | executed |
|---|---|
| the LP's schedule for the current order, one round per item | +378 s |
| the same, hay/wood/carrot combined into one round per stretch | +293 s |
| closed loop, 6 iterations (searched plan / current-order plan) | 19:56-23:02 / 20:15-25:43 |

Short stretches ran 2-3x longer than predicted (a round costs ~6-12 s to start), and the loop's
corrections did not converge. `run_plan` is fast because each of its mixed rounds serves several
needs and it rarely switches, which is also why reorders that add switches lose.

## Other one-change tries (whole runs or forks at Expand 7, paired seeds)

| change | time |
|---|---|
| Fertilizer -> Mazes 1 -> Megafarm 1 after Sunflowers / Expand 4 / Speed 4 | +116 / +90 / +32 s |
| Expand 8 after Expand 7 / after Dinosaurs 5 (snake on the generic `HALVES` path) | +231 / +277 s |
| Polyculture 2 anywhere after Dinosaurs 1 | +46 to +53 s (each snake round costs ~50 s to set up) |
| Speed 4 after Trees 1 ... Sunflowers; Speed 5 after Speed 4 / Fertilizer / Mazes 1 | +25 to +259 s; +23 to +37 s |

Also: `--tweak speed=1.2` (or 1.25) never ends; it hangs in `opening()` (line 6114), so the
tick what-if cannot be measured. Halving compute saves 56 s, halving growth times 77 s, and
unlimited power 35 s.

## What a working version would need

Model rounds the way the script farms: one mixed round per stretch whose crop mix is the
decision, with a fixed start-up cost for each round (a mixed-integer program), and rates measured
with the stock a round really has rather than with plenty of everything.
