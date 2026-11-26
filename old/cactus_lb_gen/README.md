Generator for `cactus_lb_entry.py` (Leaderboards.Cactus).

    mkdir v
    python calib3.py lay1.json v/out.py 5

`lay1.json` is the layout (extra gate tiles and the dropped corner tiles). `calib3.py` cuts the
serpentine into 32 chunks, writes a debug build of `template3.py`, runs it in the simulator to
measure every tile's time, re-cuts, and repeats; the last cut is written without debug prints.
`costs.json` holds the per-tile times measured for the current entry.
