import sys
s=open(sys.argv[1]).read()
old="""		for d in P:
			move(d)
		while (get_time() // WDT) - num_items(Items.Water) < NSIG + 1:
			pass
		harvest()
"""
new="""		i = 0
		n = len(P)
		while (get_time() // WDT) - num_items(Items.Water) < NSIG + 1:
			if i < n:
				move(P[i])
				i += 1
		while i < n and get_entity_type() != Entities.Cactus:
			move(P[i])
			i += 1
		harvest()
		while i < n:
			move(P[i])
			i += 1
"""
assert s.count(old)==1
open(sys.argv[2],'w').write(s.replace(old,new))
