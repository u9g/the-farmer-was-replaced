# The Farmer Was Replaced simulator

[`tfwr_sim.rs`](.claude/skills/tfwr-sim/tfwr_sim.rs) is a headless, one-file Rust port of
[The Farmer Was Replaced](https://store.steampowered.com/app/2060160/The_Farmer_Was_Replaced/)'s
engine. It runs a farming script offline and tells you how many items per minute it makes. A run
takes from a few milliseconds to a few seconds, and several runs go in parallel, one per CPU core.

The port follows the game's own code function by function: the tokenizer, parser and interpreter,
tick costs, drone scheduling, timers, the farm grid, plants (grass, bush, tree, carrot, pumpkin,
sunflower, cactus), mazes, the dinosaur hat, water, fertilizer, power, polyculture, unlocks and the
random number generator. It is deterministic: the same script and seed always give the same result.

## Running it

It needs nightly Rust and no crates. Run it from your save folder,
`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced\Saves\<save name>\`,
because it reads your unlock levels and inventory from the `save.json` there:

```
cargo +nightly -Zscript path/to/tfwr_sim.rs cactus.py --seed 1 --seeds 32 --quiet
```

The first run builds it in about 25 seconds (it is built fully optimised, as one unit), and later runs use cargo's cache. Every run simulates
one game minute. A script too slow to harvest three times in that minute keeps going until it
has, up to ten minutes.

Give several scripts to compare them on the same seeds. `--brief` prints one line per script, best
first:

```
cargo +nightly -Zscript path/to/tfwr_sim.rs cactus.py cactus_new.py --seed 1 --seeds 32 --brief
```

```
     3,835,006 cactus/min     7.85s cycle       502,894 per harvest (min      273,800)  cactus_mesh.py
     3,122,538 cactus/min    10.07s cycle       524,288 per harvest (min      524,288)  cactus_sort_only.py
```

| Option | Meaning |
|---|---|
| `--seeds N` | run N seeds and report the mean, min and max rate (default 1) |
| `--seed N` | first seed; fix it so two commands see the same random numbers |
| `--jobs N` | runs at once (default: one per CPU core) |
| `--item NAME` | item to report (guessed from the file name otherwise) |
| `--save PATH` | save file to read unlocks and inventory from (default: `save.json` beside the script) |
| `--set unlock=level` | override an upgrade, e.g. `--set cactus=5` |
| `--give item=n` | override an inventory count, e.g. `--give pumpkin=1e9` |
| `--size N`, `--drones N` | override the field size and drone limit |
| `--fps N` | simulate the game at a given frame rate |
| `--quiet` | hide the script's `print` / `quick_print` output |
| `--brief` | one line per script, sorted by rate |
| `--leaderboard NAME` | run it as a leaderboard attempt, as below |
| `--profile` | report where the time goes, by drone, unlock, function and line |
| `--whatif` | leaderboard runs: what a 20% improvement in each of ticks, compute, growth and each item would save |
| `--tweak name=factor` | change a rule for a what-if: `speed`, `compute`, `grow`, `cost.<item>`, `yield.<item>` |
| `script.py@NAME=value` | run the script with the top-level `NAME = ...` replaced (several: `@A=1@B=2`; a multi-line list too), no file written |
| `--sweep NAME=v1,v2,...` | add one `@NAME=v` variant per value after each script, paired against the first (repeat to scan several names) |
| `--crn` | common random numbers: each plant's random draws come from a stream of its own cell, so versions of a script see the same luck and paired differences are less noisy (not the game's draws) |

### Leaderboard runs

Give the script that calls `leaderboard_run(...)`, or the entry script with `--leaderboard NAME`,
and the simulator runs it the way the game does: the board's fixed unlocks and items, each run
lasting until the script ends, repeated until the runs cover two hours of game time, scored by their
mean time. `--seeds N` does exactly N runs instead.

```
cargo +nightly -Zscript path/to/tfwr_sim.rs run_cactus_lb.py --quiet
```

```
Leaderboards.cactus with cactus_lb_entry.py
  score 0:57.796 (57.796s) = mean of 125 runs (2:00:24.514 simulated); min 53.123s, max 67.370s; goal met 0.034s before the end on average
```

The game scored the same script 57.7 s. Mining DLC boards are not supported.

### Where the time goes

`--profile` splits a run's time into actions by kind, interpreter work, polling and `wait_for`, for
the main drone (whose time is the run's) and for all drones against the drone limit. It lists each
unlock with how long it took, the cost item that held it up and how long it sat affordable before
the script bought it, then the functions and source lines that took the most time. `--whatif`
reruns the same seeds with one thing 20% better each time (every tick, interpreter work, plant
growth, each item's share of unlock costs) and ranks what each would save:

```
cargo +nightly -Zscript path/to/tfwr_sim.rs run_reset_lb.py --seed 1 --seeds 8 --profile --whatif
```

## Reading the output

- **steady state** is the rate from the first full-size harvest to the last. It leaves out one-time
  setup such as tilling, so it is the number to optimise.
- **mean over N seeds** pools every seed's harvests. A script whose cycle time varies needs many
  seeds; one with a fixed cycle reads the same on every seed.
- **in-game inventory tooltip would read** is the game's own items/min figure, computed the same way
  the game computes it.
- Negative item lines are inputs being used up, per minute.
- `warning xN` lines are the game's warnings (failed plant, failed swap) with a count, and `ERROR:`
  is a runtime error with its file and line.

Idle drones are cheap to simulate when they wait in one of these two forms, which the simulator
skips through with the same result as running every pass:

```python
while get_time() < deadline:
	pass

while num_items(Items.Power) > 0:
	pass
```

Any other spin is interpreted tick by tick, which costs about 2.5 s per simulated minute of 32
busy drones.

## Accuracy

Checked against the running game for cactus: the same 524,288 cactus per harvest at cactus level
4. Over 20.5 minutes the game made 39 harvests (31.5 s per cycle, 997k cactus/min), and the
simulator gave 31.8 s and 990k/min. Other crops have not been checked against the game yet.

[`watch_save.py`](.claude/skills/tfwr-sim/watch_save.py) measures the real per-minute rate from
the save file while the game runs:

```
python path/to/watch_save.py <save folder> 10 cactus pumpkin
```

The game rewrites `save.json` every 30 seconds, and the save fails if anything holds the file
open at that moment. `watch_save.py` and the simulator open it with delete sharing so they never
get in the way. Don't read it any other way while the game is running.

## Limits

- The mining DLC (`dig`, `push`, `place`, `hover`, bamboo, rice, mushrooms and so on),
  and `simulate()` are not ported. A script that calls one stops with an error naming it.
  Leaderboard runs work from the command line (above), not by calling `leaderboard_run()` inside a
  run.
- Every run starts on a freshly generated, dry field, not your current farm.
- The game seeds its randomness from the clock, so no seed reproduces a particular game run.
- `import` only finds `.py` files in the script's folder.

[`SKILL.md`](.claude/skills/tfwr-sim/SKILL.md) has more detail, including the tick cost of every
operation and notes for changing the simulator. It also makes the simulator a
[Claude Code](https://claude.com/claude-code) skill when this folder is opened in Claude Code.
