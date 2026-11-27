post10 on the post9 entry: one call in w0's round-B tail. Paired results, with no failed runs:

| Seeds | Δ mean ± se | Faster on |
|---|---|---|
| 900000-902047 | -1.5 ± 0.3 ms | 186 of 2048 |
| 1500000-1502047 | -1.3 ± 0.2 ms | 184 of 2048 |
| 300000-301023 | -0.9 ± 0.4 ms | 87 of 1024 |
| 1-512 | -0.9 ± 0.3 ms | 36 of 512 |

    python3 xcasq.py post9_entry.py ../../../cactus_lb_entry.py

This rebuilds the shipped entry byte for byte from post9 (`git show 190da7b:cactus_lb_entry.py`).

w0 is the main drone, latest in round B in about 9 of 128 runs. Its `xcasw(North, 1)` pairs with
a cell w2 plants about 54 ms after w0's last plant. It spun on the empty cell for 61 ms per run,
then always waited a further 50 ms. `xcasq` returns straight after the spin when the pair is
already in order. That is safe because w2's own later West fix can only raise its cell.

Found while bounding round B's fix work on the latest drones with the head-of-line tools. All of
that work together is worth at most 27 ms if made free; the latest drone's work cut to the
runner-up's is worth 18 ms.

Tried, not used:
- Swapping straight after the spin, with no wait: fails seed 9. w2 must make its own West fix
  first, or w0's larger value is pushed on into (3,6) and nothing re-checks it.
- A 40 ms wait instead of 50: -1.7 ± 0.3 ms, within noise of this and with less safety margin.
- The same early return in the shared `xcasw`, which also covers round A's w29: +0.3 ± 1.0 ms.
- A cheaper race-safe middle settle in the forked tables (`fmSW_NE`, reading each cell once and
  re-reading its own cell after each swap): +1.2 ± 0.4 ms. The read-once version that failed
  runs tracked its own cell's value in a variable instead of re-reading it.
