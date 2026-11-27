Interpreter-tick rewrites on the post4 entry: 7.151 -> 7.136 s on 2048 fresh seeds (80000-82047),
7.147 -> 7.134 s on seeds 60000-61023, no failures.

    sh apply.sh IN.py OUT.py

- `rewrite_fix.py --peel`: the fix routines (`fSW_NE` and friends) loop on one chained compare,
  `while not a <= v >= b:`, and the `s` variants test for `None` only on the first pass (a planted
  neighbour never reads `None` again).
- `rewrite_inline.py --peel`: the same form for the 148 inline junction fix loops. Each block is
  regenerated from its parse and must match the original text before it is replaced.
- `sed`: `while wk:`, `if h:` for `if h != None:` on spawn handles, `if not a != None != b:`.

Tick rules found on the way (simulator interpreter, 1 op = 1/6075 s): `if`, each arithmetic or
comparison step, `and`/`or`, `pass`, `+=`, an index, a tuple literal, a `def`, a call through a
variable and every sensor read cost 1; a list literal costs one per element, a dict 1 + one per
entry, `in` over a list one per element compared; name lookups, constants, `=`, `not`,
`return`/`break`/`continue`, `get_time()` and direct calls are free. A chained compare stops at
the first false step, so it beats `x and y`. All compute free would save about 0.08 s.

Not used: `rewrite_unroll.py` (every `hlp`/`own` call unrolled into straight-line code, -0.003 s)
takes the entry over the leaderboard limit of 100,000 syntax nodes
(`error_leaderboard_code_too_large`). Reusing the swapped-in value instead of measuring again
failed seed 640 (a race with a neighbour drone).
