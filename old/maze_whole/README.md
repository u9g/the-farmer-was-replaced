# Maze leaderboard on the whole board (one 32x32 maze, 32 drones)

`maze_whole.py`: 301 treasures of one 32x32 maze is exactly the goal. Each drone starts on an 8x4
grid of cells, maps only its maze-distance Voronoi region (DFS that does not enter a cell an
already-found start cell is closer to), parks at the region's median and serves its treasures.
Fallbacks: a treasure nobody took for 1 s is fetched by whoever mapped it (shortest route first),
and one nobody mapped is searched for by the drone whose start cell is nearest in a straight line.

Full attempt in the sim: **116.9 s** (62 runs, 95-155 s) against **106.0 s** for
`maze_lb_entry.py` (16 separate 8x8 mazes); the 8x8 split is faster on 51 of 62 paired seeds.

Why it should win and why it does not yet:
- Serving is better than the 8x8 split: the owner is almost always waiting at its median, so a
  treasure costs its route (mean 7.2 moves) plus one use_item, ~0.31 s; no maze runs out, so
  there is no regeneration and no uneven finish (the 8x8 split loses ~4 s to both).
- Mapping is slow and uneven: regions vary in size (up to ~76 cells), and the slowest drone takes
  15-27 s. Treasures landing in a region still being mapped wait; the first take is at ~10 s.
- Disagreement: drones never share maps. Orphan cells (claimed by nobody) still appear in some
  seeds, clustered around one drone's region; each costs 1 s+ before a fallback fetches it, and
  long fetches pull drones away from their own regions. Suspected cause, not confirmed: every
  treasure move opens ~2 walls on a 32x32 maze, and drones still mapping then see a different
  maze. A static-maze Python model of the same exploration gave no orphans.
- Geometric ownership (fixed 8x4 blocks) instead of maze-distance regions is far worse: routes
  inside a block average ~50 moves in a 32x32 DFS maze.

Bug fixed on the way: claim() must let every found home's wave spread, not only its own (half
the treasures were double-claimed before).
