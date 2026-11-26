---
name: tfwr-sim
description: Run and benchmark The Farmer Was Replaced scripts offline with a headless port of the game. Use when asked how fast a farming script is (items per minute), to compare or optimise script versions for a crop, to explain where a script spends its ticks, or to check a script against the running game.
---

# The Farmer Was Replaced simulator

`tfwr_sim.rs`, next to this file, is a one-file Rust port of the game's own code (decompiled
`Core.dll` / `Utils.dll`): tokenizer, parser, interpreter, tick costs, drone scheduling, timers,
plants, mazes, the dinosaur hat, unlocks and the random number generator. A run takes from a few
milliseconds to a few seconds, and runs go in parallel, one per CPU core.

It needs nightly Rust and no crates. The game's scripts live in the save folder,
`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced\Saves\<save name>\`.

## Running a script

Run from the save folder, giving the path to `tfwr_sim.rs` in this skill's folder:

```
cargo +nightly -Zscript <skill folder>/tfwr_sim.rs cactus.py --seed 1 --seeds 32 --quiet
```

Every run simulates one game minute. There is no duration option: a script too slow to harvest
the reported item three times in that minute keeps running until it has, up to ten minutes.

Every run is also capped at 10 seconds of real time (`WALL_LIMIT_SECONDS` in `tfwr_sim.rs`). A run
that goes over stops with the error "something in this run is taking too long, make an
optimization that keeps this run under 10s for whatever code you are running and push it". When
you see it, make the script cheaper to simulate (write busy waits as `while get_time() < x: pass`,
stop drones from spinning on sensors, cut runaway loops) rather than raising the limit, then commit
and push the fix. Runs share the CPU, so many agents running the simulator at once each with every
core (`--jobs` default) can push an ordinary run past 10 s: split the cores with `--jobs`.

Give several scripts to compare them. Every script gets the same seeds, all the runs go in
parallel, and a line per script is printed at the end:

```
cargo +nightly -Zscript <skill folder>/tfwr_sim.rs cactus.py cactus_new.py --seed 1 --seeds 32 --quiet
```

Never loop over scripts or seeds in the shell: one command with all of them is faster.

Add `--brief` to get one line per script, best first, instead of the per-run reports:

```
     3,835,006 cactus/min     7.85s cycle       502,894 per harvest (min      273,800)  cactus_mesh.py
     3,122,538 cactus/min    10.07s cycle       524,288 per harvest (min      524,288)  cactus_sort_only.py  [ERROR in 1 of 32 runs: ...]
```

The first run after the file changes takes about 25 s to build (one fully optimised unit); later runs use cargo's cache.

| Option | Meaning |
|---|---|
| `--seeds N` | run N seeds and print mean, min and max of the steady-state rate (default 1) |
| `--seed N` | first seed; fix it so two commands see the same random numbers |
| `--jobs N` | runs to do at once (default: one per CPU core); with more than one the simulator raises itself to above-normal priority so a running game does not take its cores |
| `--item NAME` | item to report (guessed from the start of the file name: `cactus_v2.py` reports cactus, `maze1.py` gold, `dinosaurs.py` bone, `wheat.py` hay, `tree2drones.py` wood; a script whose name says nothing reports the first script's item) |
| `--save PATH` | save file for unlock levels and inventory (default: `save.json` beside the script) |
| `--set unlock=level` | override an upgrade, e.g. `--set cactus=5` |
| `--give item=n` | override an inventory count, e.g. `--give pumpkin=1e9` |
| `--size N`, `--drones N` | override the board size and drone limit from the save |
| `--quiet` | hide `print` / `quick_print` output (shown under each run's report when there are several runs) |
| `--brief` | one line per script, sorted by rate: rate, cycle time, mean and smallest harvest, warnings and errors. Implies `--quiet` |
| `--leaderboard NAME` | run as a leaderboard attempt (see below) |

World size and drone limit come from the save's `expand` and `megafarm` levels unless overridden.

## Leaderboard runs

`--leaderboard NAME` runs a script the way `leaderboard_run()` does in the game, so a time can be
checked before spending two in-game hours on it. Giving the launcher script (one that calls
`leaderboard_run(Leaderboards.X, "file", speedup)`) does the same without the option:

```
cargo +nightly -Zscript <skill folder>/tfwr_sim.rs run_cactus_lb.py --seed 1 --quiet
cargo +nightly -Zscript <skill folder>/tfwr_sim.rs cactus_lb_entry.py --leaderboard cactus --seeds 4 --quiet
```

It follows the game's code (`BuiltinFunctions.LeaderboardRun`, `MainSim.StartLeaderboard` and
`MainSim.LeaderboardExecutionFinished` in Core.dll, and the `LeaderboardSO` assets):

- save.json is ignored. Every board but the resets starts with every unlock at its top level (a
  32x32 farm and 32 drones); `_single` boards get no megafarm and expand only to level 5 (one drone,
  8x8). Fastest reset starts from the basic reset unlocks. The items are the board's own: cactus
  gets 1e9 pumpkins and 1e9 power, maze 1e9 weird substance and power, and so on (`LEADERBOARDS` in
  `tfwr_sim.rs`). `--set` / `--give` still apply on top, for experiments.
- A run lasts until the script ends, meaning every drone has returned, not until the goal is met.
  The time is the game time at that moment. The goal is checked only then.
- Runs repeat with new seeds until they add up to two hours of game time, and the score is their
  mean, the number the game uploads. `--seeds N` does exactly N runs instead, for a quick check.
  Any run that ends short of the goal, errors, or has not ended after two game hours fails the
  whole attempt, as in the game.
- The code size limit is checked: at most 100,000 syntax nodes over the file and everything it
  imports (`error_leaderboard_code_too_large`).
- A leaderboard run may take up to 120 s of real time, not 10.
- Runs go to all cores and stop as soon as the finished runs cover two hours. Until the first one
  is back only four start (a reset needs two to four of its long runs, and runs that would be
  dropped only take cores from the ones needed), and a run stops as soon as the game time the runs
  before it have reached already covers two hours. A cactus attempt of about 470 runs (15.4 s
  each) takes about 5 s on 16 threads, about 0.075 s of CPU per run; a whole fastest-reset attempt
  (three runs of about 42 minutes) takes about half a second.

The report shows the first run in full, then the score, the number of runs, their spread and how
long the script ran on after the goal was met:

```
Leaderboards.cactus with cactus_lb_entry.py
  score 0:57.796 (57.796s) = mean of 125 runs (2:00:24.514 simulated); min 53.123s, max 67.370s; goal met 0.034s before the end on average
```

The game scored the same `cactus_lb_entry.py` 57.7 s. Mining DLC boards (bamboo, rice, ores,
dynamite, mushrooms, pyramids, treasure map, the underground reset) are refused, since the DLC is
not ported.

## Reading the output

- **steady state** is the per-minute rate from the first full-size harvest to the last, where
  full-size means at least half the run's biggest harvest. Optimise this; it leaves out one-time
  setup such as tilling. Smaller harvests in between (a stray cactus cut on its own) still count
  toward the amount, but never start or end the window, and the line says how many there were.
- **mean ... over N seeds** pools every seed's harvests. One minute holds only a few harvests, so
  a script with random cycle times needs many seeds: the old cactus script (32 s cycle) reads
  within about 1% at 32 seeds and 2% at 8. A script with a fixed cycle reads the same on every seed.
- **between harvests** is the cycle time with its min and max.
- **in-game inventory tooltip would read** is the game's own "highest" items/min figure, computed by
  the same code as the game, for comparing with what the player sees.
- Negative item lines are inputs being used up. A one-minute run will not show a script running
  dry later: compare the per-minute use with what the save holds.
- Three kinds of wait cost the simulator almost nothing, because it skips the idle passes with the
  same result as running them: `while get_time() < x: pass` (x a plain variable),
  `while num_items(Items.X) > y: pass` (any one comparison, y a number or plain variable), which
  skips passes until another drone's next action or the next power tick, and any `while` loop
  inside a function whose passes only read the farm (`can_harvest`, `get_entity_type`,
  `get_ground_type`, `measure`, `can_move`, `get_pos_x/y`, `get_world_size`, `get_water`) and work
  on the function's own variables, such as `while not can_harvest(): pass` or a `while True:` that
  polls `measure()` until the treasure is in its territory. Once two passes in a row start with the
  same variables and read the same, the drone skips passes until another drone changes something
  one of its reads would see. A pass that does anything else (`get_time`, `num_items`, `random`,
  printing, changing a list or dict, setting a global, calling a function of the script's own, a
  `for` loop) is interpreted tick by tick, about 2.5 s per simulated minute of 32 spinning drones.
  Write waits in the skippable forms.
- A script that never harvests runs the full ten minutes. Draining a big power stock (say
  `--give power=1e7`) by spinning drones takes game hours, so the run then reports 0 items:
  check that the script really farms under the `--give` you used.
- `warning xN` lines are the game's warnings (failed plant, failed swap) with a count.
- `ERROR:` is the script's runtime error with file and line; the run stops there.

## Searching many variants fast

A simulator run takes well under a second. An agent's step of thinking takes most of a minute. So
a search is fast when each step tests many variants, and slow when it tests one.

1. Put every number you might tune (slot lengths, phase counts, deadlines, block sizes) in
   constants at the top of the script, and write a few lines of Python that stamp out one file per
   combination into a scratch folder (not the save folder: the game deletes unknown `.py` files).
2. Run all of them in one command with `--brief`. Fifty variants at 8 seeds is one command and a
   few seconds; read the top of the sorted list.
3. Screen with `--seeds 4` or `8`, then confirm the best few with `--seeds 32`. A script with a
   fixed cycle reads the same on every seed, so its cycle time needs one seed; seeds only matter
   for how often it harvests short or errors.
4. Fix the conditions in the command, not from memory of an earlier run: `--set cactus=4
   --give power=0 --give pumpkin=1e12` and so on. The save changes while the game runs (an upgrade
   bought mid-search doubles every number), so a baseline measured an hour ago is not comparable.
   Always put the baseline script in the same command as the variants.
5. When several agents search at once, give each one idea, this skill, the baseline script and a
   stopping rule (first number within ten minutes, report after about fifteen steps). Each copies
   `tfwr_sim.rs` to its own folder and builds with its own `CARGO_TARGET_DIR`, because a running
   simulator locks the shared binary against rebuilds.
6. For ideas about schedules rather than code (how many sort rounds, which formation), a twenty
   line Python model of the grid screens thousands of options before any script is written. Check
   the winner in the simulator; the model has no tick costs.

## Optimising a script

1. Copy the script to a new file in the save folder and run both in one command with `--seed 1 --seeds 32`.
2. Change one thing at a time. Keep a change only if the mean moves by more than the min-max spread.
3. To see where time goes, add `quick_print(get_time(), get_tick_count())` at phase boundaries and
   run without `--quiet`.
4. Confirm the winner in the real game (see below) before reporting it as fact.

Costs, from the game's code:

- Actions (`move`, `plant`, `harvest`, `till`, `swap`, `spawn_drone`, `use_item`) cost 200 ticks.
  Sensors (`measure`, `can_harvest`, `get_entity_type`, `num_items`) and failed actions cost 1.
- Each arithmetic or comparison operator, `if`, index and `pass` costs 1. `while` and `for` cost 1
  to start and nothing per iteration. Plain assignment, name lookup, `return` and unary `-`/`not`
  are free. A direct function call is free; a call through a variable or parameter costs 1.
- Speed is 400 ticks/s times 1.5 per speed level (level 5 = 3,037.5 ticks/s, about 66 ms per
  action). Actions dominate: cut actions first, ticks second.
- A spawned drone starts 200 ticks after the call with a deep copy of the spawner's globals.
  `wait_for` costs 1 tick and resumes when the other drone ends.
- Plants grow on timers in game seconds, independent of drone speed. Cactus grows in exactly 1 s.

## Checking against the running game

The game rewrites `save.json` about every 30 seconds while running. `watch_save.py` (next to this
file) reads it and reports the real per-minute change:

```
python <skill folder>/watch_save.py <save folder> 10 cactus pumpkin
```

Never read `save.json` any other way while the game is running: no `open('save.json')` or
`json.load(open(...))` one-liners, no `cat`/`Get-Content` loops. The game saves with
`File.Replace`, which fails if anything holds the file open without delete sharing. When that
happens the whole save fails, code included, and the game shows "Failed to write to the save
files". Python's `open()` and most shell tools hold it that way. `watch_save.py` opens it with
`FILE_SHARE_DELETE`, and so does the simulator (Rust's default), so both are safe.

Run the script in the game, watch for at least 10 minutes, and compare with the simulator at the
same upgrade levels. Only cactus has been compared so far: same 524,288 per harvest at cactus
level 4, and over 20.5 minutes the game made 39 harvests (31.5 s per cycle, 997k cactus/min)
against 31.8 s and 990k/min simulated. Treat every other crop's numbers as unverified until
checked this way.

## Limits

- Not ported: the mining DLC (`dig`, `push`, `place`, `hover`, prospecting, bamboo, rice,
  dynamite, mushrooms) and `simulate()`. A script that calls one stops with an error naming it.
  `leaderboard_run()` is not run from inside a script either; give the launcher script or
  `--leaderboard` instead (see Leaderboard runs).
- The "you have not unlocked this keyword" checks are skipped; plant and hat unlock checks are kept.
- Every run starts on a freshly generated, dry field, not the player's current farm.
- The real game seeds its randomness from the clock, so no seed reproduces a particular game run.
- `import` only finds `.py` files in the script's folder.
- Sunflowers, power and the dinosaur hat are ported but no script has exercised them yet.
- The game deletes `.py` files it does not know from the save folder when it saves. Keep helper
  files in sub-folders, and create new game scripts from inside the game.

## Changing the simulator

Function and field names follow the decompiled C# so the two can be read side by side. Each
drone's program runs as plain recursion on a stack of its own (a Windows fiber; elsewhere a thread
that takes turns with the scheduler, slower but the same results). `yp()` stands for every point
where the game's iterators yield: it counts the resume and hands back to the scheduler only when
`PerformExecutionStep` would stop (past the target op count, a side effect, or 1000 resumes), so op
counts and stopping points match the game exactly. Keep it that way when changing a node: an
extra or missing `yp()` changes timing. Some things are not in the game: `skip_busy_waits` (the
shortcut for `while get_time() < x: pass`, `while num_items(i) > y: pass` and steady loop passes,
see `Op::PassMark`: every read, op count and time stays exact, but the ops a skipped wait spends
are booked for power earlier than the game would, so the power left at the end can differ by a
fraction of a unit), shortcuts no script can see (`spawn_reach` copies only the variables a spawned
drone's code can name, `release_spawn_scopes` frees an ended drone's copies, tuples of plain values
are shared rather than copied) and the reporting in `main`. After touching the interpreter or `execute`, build the old and new versions
into separate target directories and `cmp` their full output for the same scripts and seeds,
including a script that uses power and one with `--fps 20`: the simulator is deterministic, so any
difference is a change in behaviour. If the
simulator and the game disagree, decompile `Core.dll` and `Utils.dll` from
`<Steam>\steamapps\common\The Farmer Was Replaced\TheFarmerWasReplaced_Data\Managed` (for example
with `ilspycmd`) and compare the function in question, rather than adjusting numbers to fit.
Entity and unlock tables near the top of the file were decoded from the game's assets and need
re-extracting after a game update.
