Post-passes on the post3 entry: 7.178 -> 7.149 s on 2048 fresh seeds (30001-32048), 7.176 -> 7.149 s
on a full 1008-run attempt, 4096 more seeds (40001-44096) at 7.149 s without a failure.

    python apply.py IN.py OUT.py

runs, in this order (each is a text pass over the finished, nested entry):

1. `apply_preplant.py` (-0.014 s alone): ten dead-end cells of 3-wide columns lie on another
   drone's launch flight, after its last spawn and at least 6 actions before their owner gets
   there. The passing drone tills and plants the cell (+2 actions), the owner drops its
   `move; till; plant; move back` (-4). The ten picks are hard-coded, chosen with a two-round
   model fitted to traces: a round-A-only pick set moved the first harvest 0.021 s earlier and the
   score not at all.
2. `apply_sync.py 19` (-0.011 s alone), four steps:
   - `hmove.py 19`: the first-harvest role moves from w3 to w19 (swept all 31; 12/19/23/25 best);
   - `jq.py`: junction work lists keep a read index and per-cell pending flags instead of
     `len(wk)`, `wk.pop(0)` and `k in wk` (same order, same de-duplication);
   - `ptw2.py`: pre-travel `if get_time() < e` checks nested; once past `e` the rest of the moves
     go in as one tuple. `P` becomes a list of tuples, so passes that index it run before this;
   - `lh.py`: the last drone to finish round A harvests itself when the other 31 water signals are
     in and it stands on a cactus; the harvester only harvests if no one did.
3. `wat2.py OUT w3,w27,w15,w20` (-0.002 s alone): `use_item(Items.Water, 4)` on the cell just
   before the chunk's last round-B plant, and the growth wait counted from the plant before, as
   fert.py does. Watering after the last plant failed a run (xcasw moved the cactus 0.019 s after
   the water). Re-pick the chunks (the growth-bound ones setting the second harvest) after any
   regeneration.

Found at the same time, not used:

- Swapping post3's four fertilizers for water (same sites): the same time, it only frees margin.
- Water on every round-B chunk's last plant: +0.017 s (the action delays fix-bound tails).
- Moving the top-level helper defs into the drones, a re-optimised launch tree: <= 0.003 s, noise.
- Generator knobs JF, C_FM, C_CAS, SOFT, TAPERX, JRING, PTM, PTF, NMIN, COLFIX in round A only:
  the shipped values are the optimum or within noise. Planning from measured lateness (CORR): worse.
- Shorter xcasw sleep: 0.0 fails seed 16; anything under 0.033 s is unsafe.
- Rules: nothing gives cactus faster. Every unlock is maxed, growth is exactly 1 s unless watered,
  fertilizer arrives every 1.25 s, no trade, grassland only turns to soil by till.

Bounds measured on the way: all compute free would save 0.089 s; instant growth everywhere in
round B 0.018 s; every drone at its round-B start by the first harvest 0.024 s.

Promising, not built: modelling plant-on-the-way cells in the planner and rebalancing (estimated
0.05-0.09 s in round A); 4-wide bands paired with 2-wide ones (about 1 move per cell instead of
1.33, more fix swaps; maybe -0.03 s); round-A work stealing with a watered cell as the claim flag
(`get_water()` is 1 tick).

Note: the README's merged g5 command no longer reproduces the shipped pre-post3 entry (7.285 s
against 7.202 s), so these passes are applied to the committed entry, not a regenerated one.
