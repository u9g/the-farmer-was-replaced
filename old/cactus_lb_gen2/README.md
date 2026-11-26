Generator for `cactus_lb_entry.py` (Leaderboards.Cactus), two harvests with different layouts:
pass A on 2-wide diagonal strips (703 cells), pass B on strips with five 3-wide ones (746 cells).

    CIT=4 KD=10 python build_entry.py ../../cactus_lb_entry.py 5

`lay.py` builds layouts and serpentine orders, `lay2.py` the settle model used for per-cell costs,
`build_entry.py` partitions into 32 chunks (spawn plan, pre-till routes, harvester) and fills
`template.py`.
