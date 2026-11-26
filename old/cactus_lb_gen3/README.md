Generator for `cactus_lb_entry.py` (Leaderboards.Cactus): one 729-cell layout (walls 0 mod 3 with 3-wide strips 9, 10, 12) harvested twice.

    WSPEC=0:9,10,12 CCFLAT=1100 ZB=0.5 python b9.py ../../cactus_lb_entry.py

Each drone plants its chunk with no sorting (deterministic forward pass), then walks back over a
deferred tail fixing order while the cactus grow: 2-wide pairs by swap, 3-wide middles by `fm`
(only ever lowers a bottom or raises a top), connector junctions by `cc` (read, plan, execute).
Cells before the tail are fixed inline at plant time. Phase A ends with a water signal per drone,
phase B with the drone count. `cmodel.py` is a tick-level concurrent model of the generated
program (races, growth, harvest pop) used to tune the plan: `python cmodel.py 30`.
