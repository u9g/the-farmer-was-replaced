g4: an alternative generator for `cactus_lb_entry.py` (Leaderboards.Cactus). It produces valid
entries (every run meets the goal) but does not yet beat g3: 8.14 s over 16 runs with g3's layout,
against 7.865 s for the shipped g3 entry.

    TAPERX=4 JMAX=5 WIDTHS=2,2,2,2,2,3,3,3,3,3,3,3,2,2,2,2,2,2,2 AITER=2 BJ=0,10,20 SLK=0,0.1 python g4.py out.py

Uses `lay.py`, `g2.py` (layout and taper), `jlazy.py`, `spawnmm.py` and `build_entry.py` from
`../cactus_lb_g2`. `g4_core.py` holds the layout, op list, Monte Carlo op costs and cut tables;
`g4.py` the planner and code generation; `t4.py` the runtime template.

## Model

- Every fix is a monotone op: a pure-pure CAS, an isolated-middle settle (`fm`) or a junction settle
  (`jf`). A pure-low cell only ever gets smaller, a pure-high one larger, so ops commute: the field
  ends sorted when every op runs once after its cells are planted and no two drones run ops on a
  shared cell at the same moment. There are no `while measure(d) == None` waits on other drones
  except at F|R cuts.
- Chunks are snake segments walked in either direction. At F|F / R|R cuts the drone whose walk ends
  at the cut runs every straddling op at the start of its tail (the other side was planted long
  before). At R|F cuts the later arriver CASes right after its first plant. At F|R cuts the later
  finisher waits for the other's last cell (`xcasw`). In those two the other drone's ops on the
  shared cell are forced inline.
- Round-A tails walk back m cells running deferred ops and stop at u_k. Round B is cyclic: drone k
  plants snake[u_k, u_k+1), the last segment wraps from the snake's end to its start (2 moves on
  the torus). So round B needs no travel, and B balance is set by choosing the A tail depths
  (`plan_B`).

## Findings (per drone, 725 cells, 6075 ticks/s, 200-tick actions)

- Essential work: round A till + plant + move 68 actions (2.24 s), round B plant + move 45 actions
  (1.49 s), plus two 1 s growth waits. Floor before deploy and fixes: 5.73 s.
- Deploy (spawn + travel to chunk starts) is 22 actions in g3 and g4. With chunks that start at band
  ends near the origin it could be ~13-15.
- Fix work is the real limit: in g3's layout ~23 actions per drone per round (fm 144 x 2 actions,
  jf 18 x ~16 actions, CAS ~155 actions). It does not fit in the 1 s tail together with the
  walk-back, so it spills onto the critical path. Reaching 6.5 s needs fix work near 10 actions per
  drone per round, which means junction settles near 5 actions each (the clairvoyant optimum for
  the bottom-edge T junction, searched exhaustively in `jopt2`, is 8.4-11) and few 3-wide middles.
- Water (grow time / (1 + 4 x volume), ~25.6 water/s) only helps once tails have slack. With
  saturated tails, watering the last cells of each chunk makes things worse (tested on g3:
  7.91-8.09 s, and some variants miss the goal).
