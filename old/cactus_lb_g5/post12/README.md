# post12: fewer top-level defs before the first spawn

    python3 rw.py IN.py OUT.py wait,inl,pk     (IN = the post11 entry, git show c248ffa:cactus_lb_entry.py)

Every top-level `def` the main drone runs before its first `spawn_drone` costs 1 tick, and the
whole run starts that much later. Passing an argument and looking up `Entities.Cactus` or a
direction cost 0 ticks, so merging functions that differ by one direction is free at run time.

- `wait`: `wait_until(X)` becomes `wuT = X` / `while get_time() < wuT: pass`, and its def is dropped.
- `inl`: the bodies of `fS_NE` and `fSW_E` are copied into their callers.
- `pk`: three pairs of `pk_*` routines that differ by one direction become `pkA(x, y)`, `pkB(x)`, `pkC(x)`.

-1.0 ms on seeds 1..2048 and -1.1 ms on 70001..72048, no failures. It shifts the start, so every seed gains about the same.

The other passes in rw.py (`xcas`, `tfs`, `tfsl`, `nitems`, `hlp`, `own`, `end`) were within noise
on the pre-post9 entry and are not applied. `end` and `hlp` target code that post9 and post11 have since replaced.
