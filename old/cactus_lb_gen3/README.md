Generator for `cactus_lb_entry.py` (Leaderboards.Cactus): one 725-cell layout (walls 0 mod 3 with 3-wide strips 9, 10, 12, and the 3-cell top-right corner strip left empty since it costs a whole junction) harvested twice.

    RELAX=2 WALLS=0,3,6,9,12,15,18,21,24,27,31,35,38,42,45,48,51,54,57,60,61,62 INL=0 BMODE=2 PRET=1 CCFLAT=1100 ZB=0.5 python b10.py ../../cactus_lb_entry.py

Each drone plants its chunk with no sorting (deterministic forward pass), then walks back over a
deferred tail fixing order while the cactus grow: 2-wide pairs by swap, 3-wide middles by `fm`
(only ever lowers a bottom or raises a top), connector junctions by `cc` (read, plan, execute).
Cells before the tail are fixed inline at plant time. Phase A ends with a water signal per drone,
phase B with the drone count. `cmodel.py` is a tick-level concurrent model of the generated
program (races, growth, harvest pop) used to tune the plan: `python cmodel.py 30`.

`b10.py` extends `b9.py`: `PRET=1` walks each drone toward its phase-B start during its idle time
at the end of phase A, and `BMODE=2` assigns phase-B chunks to drones counting only the travel that
does not fit in that idle time. `INL=1` (off by default) fixes junctions inline once their
neighbourhood is planted. Run the model with `GEN=b10 python cmodel.py 12`.

`RELAX=2` makes the drone that owns a junction the only one that ever fixes an edge touching the
junction's 1-ring (its cells and their neighbours), fixing those cross-chunk edges in its
back-walk. Chunk cuts then only have to stay outside the 1-ring (plus any 3-wide middles next to
it) instead of the whole 2-ring, so a junction can sit at the end of a drone's walk.
