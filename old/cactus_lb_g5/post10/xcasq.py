"""xcasq.py IN OUT: w0's round-B cross pair returns at once when it needs no swap.

w0's `xcasw(North, 1)` (round B, the cross pair with w2's cell to its North) spins until w2 has
planted that cell, then always waited a further 50 ms before re-reading and swapping. When the
pair is already in order after the spin, the wait is pointless: w2's own later West fix can only
raise its cell, which keeps the pair in order. `xcasq` returns then; otherwise it waits as before
(the wait is needed: w2 must make its own fix first, swapping straight away failed seed 9).
"""
import sys
src = open(sys.argv[1]).read()
XCASQ = '''def xcasq(d, up):
	w = measure(d)
	while w == None:
		w = measure(d)
	if up:
		if measure() <= w:
			return
	elif measure() >= w:
		return
	t = get_time() + 0.05
	while get_time() < t:
		pass
	w = measure(d)
	if up:
		if measure() > w:
			swap(d)
	elif measure() < w:
		swap(d)


'''
anchor = 'def xcas(d, up):'
assert src.count(anchor) == 1
src = src.replace(anchor, XCASQ + anchor)
# the one call: w0's round-B tail, the only `xcasw(North, 1)` at one tab of indent
call = '\n\txcasw(North, 1)\n'
assert src.count(call) == 1, src.count(call)
src = src.replace(call, '\n\txcasq(North, 1)\n')
open(sys.argv[2], 'w').write(src)
