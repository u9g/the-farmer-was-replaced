# Fastest reset: remake the maze instead of reusing it (tried, much slower)

The idea, from watching leaderboard runs: park the drones round the field, make a fresh maze,
and if the treasure is within a couple of steps of a drone let that drone fetch it; otherwise
cut the maze down and make a new one. No maps are needed.

`mz_remake.py` does this for the reset's last maze phase (1M gold, 16x16, 16 drones, Mazes 4).
After each new maze every drone reads the treasure with `measure()`. The drone nearest to it
(Manhattan distance) acts. If the treasure is within `K` cells, the drone searches for it with
a depth-first walk of at most `LIM` steps. Either way it then harvests (the treasure, or the
hedge it ended on), walks home over the cleared field and plants a bush for the next maze.
`EDGE = True` parks the drones on the border instead of in the centres of a 4x4 grid of blocks.

## Results

Runs are `--leaderboard fastest_reset` with the unlocks the reset has at that point, and enough
weird substance and power for the whole phase:

```
--set speed=5 --set plant=1 --set expand=7 --set carrots=5 --set grass=4 --set trees=4
--set watering=6 --set sunflowers=1 --set fertilizer=1 --set mazes=4 --set megafarm=4
--set pumpkins=5 --set polyculture=1 --set cactus=3 --set dinosaurs=5
--give weird_substance=1000000 --give power=100000 --give carrot=100000 --give bone=10000000
```

| version | time to 1M gold | weird substance used |
|---|---|---|
| `run_reset.py` mazes (mapped, 300 uses each) | 90 s (8 seeds: 86-104 s) | 62,720 |
| remake, K 1, LIM 3 | 502 s | 410,496 |
| remake, K 2, LIM 4 | 455 s | 220,032 |
| remake, K 3, LIM 4 | 463 s | 196,352 |
| remake, K 3, LIM 6 | 534 s | 152,832 |
| remake, K 4, LIM 6 | 541 s | 145,920 |
| remake, border parks, K 3, LIM 6 | 506 s | 199,040 |

## Why it loses here

- A new maze costs the same weird substance as one reuse (maze size x 2^(Mazes-1)), and so does a
  maze that is cut down without its treasure being taken. Every miss is a whole treasure's
  worth of weird substance gone.
- Each new maze takes at least three actions in a row: harvest, plant a bush, then use weird
  substance. A reuse is one `use_item` on the treasure, and it gives the same gold. In the runs
  above a make-and-cut cycle took about 0.26 s, against about 0.18 s per treasure for the
  current mapped maze. Even if every treasure were next to a drone, remaking would be slower.
- A reused treasure lands on a uniformly random cell. With 16 drones each parked in the middle
  of 16 mapped cells, the nearest one is a step or two away. A fresh maze puts the treasure on
  a dead end, and no drone knows the walls round it, so most mazes miss (only 15% to 43% of mazes
  paid out here).

The trade could pay off with unlimited weird substance and a slow maze to map (for example a
32x32 maze board). In the reset, the mazes are 16x16, mapping takes about 5 s of the 90, and
weird substance has to be farmed.
