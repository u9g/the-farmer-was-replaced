# The Farmer Was Replaced

Farming scripts for [The Farmer Was Replaced](https://store.steampowered.com/app/2060160/The_Farmer_Was_Replaced/),
plus an offline simulator for measuring how fast they farm.

This folder is a game save folder: the game loads every `.py` file here as a script window.

## Scripts

All of them use multiple drones.

| Script | Farms | How |
|---|---|---|
| [`cactus.py`](cactus.py) | Cactus | Mesh sort: each drone walks a 2×4 block and swaps the most out-of-order neighbour pair, then one harvest at a fixed deadline pops the whole sorted field. Grows sunflowers for power when that pays off. |
| [`pumpkins.py`](pumpkins.py) | Pumpkins | One giant pumpkin over the whole field. Each drone replants dead tiles in its own block and cuts the pumpkin the moment it spans the field. Water and fertilizer go only on the last tiles still growing. |
| [`dinosaurs.py`](dinosaurs.py) | Bones | Plays the dinosaur hat as snake over the whole field, filling as much of it as it can before taking the hat off. |
| [`maze.py`](maze.py) | Gold | Maps the maze once, then reuses it up to 300 times, with drones waiting at home cells across the maze. |
| [`maze1.py`](maze1.py) | Gold | Single-drone maze solver: explores, heading toward the treasure first. |
| [`carrots.py`](carrots.py) | Carrots | Carrots on a checkerboard, with each one's requested companion plant on the other colour. |
| [`weird.py`](weird.py) | Weird Substance | Trees and bushes, fertilized so they come up infected. |
| [`wheat.py`](wheat.py) | Hay | Grass regrown on grassland, one column per drone. |
| `*2drones.py` | various | Small two-drone versions for early in the game. |

[`old/`](old) holds earlier cactus and pumpkin versions kept for comparison. Among them is
[`cactus_line_sort_power.py`](old/cactus_line_sort_power.py), which sorts with clock-synchronised
odd-even transposition sorts on rows, then columns.

## The simulator

[`.claude/skills/tfwr-sim/tfwr_sim.rs`](.claude/skills/tfwr-sim/tfwr_sim.rs) is a headless,
one-file Rust port of the game's engine: the interpreter, tick costs, drone scheduling, timers,
plants, mazes, the dinosaur hat, power and the random number generator. It runs a script for a
simulated game minute in well under a second, and reports items per minute and cycle times. Give
it several scripts to compare them on the same seeds.

It needs nightly Rust and no crates. Run it from a save folder, which has the `save.json` it reads
unlock levels and inventory from (that file isn't in this repo):

```
cargo +nightly -Zscript .claude/skills/tfwr-sim/tfwr_sim.rs cactus.py old/cactus_mesh.py --seed 1 --seeds 32 --brief
```

Override the save's conditions with `--set cactus=4`, `--give power=0`, `--size 16` or
`--drones 32`. [`SKILL.md`](.claude/skills/tfwr-sim/SKILL.md) documents every option, how to read
the output, tick costs, and how to check results against the running game with
[`watch_save.py`](.claude/skills/tfwr-sim/watch_save.py).

## Claude Code

The `.claude/skills` folder holds two [Claude Code](https://claude.com/claude-code) skills:
`tfwr-sim`, for benchmarking scripts with the simulator, and `commit-and-push`, which commits and
pushes every change made in this folder.

## Notes

- The game rewrites `save.json` every 30 seconds. Anything that holds that file open at the
  wrong moment makes the whole save fail, code included, so editors and git leave it alone (see
  [`.vscode/settings.json`](.vscode/settings.json)).
- The game deletes `.py` files it doesn't recognise from the save folder. Create new scripts from
  inside the game, and keep experiments somewhere else.
