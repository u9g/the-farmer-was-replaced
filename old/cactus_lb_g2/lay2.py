from lay import *
def viol(c,R,vals):
    for d,n in nb(c,R):
        if n in vals:
            v,w=vals[c],vals[n]
            if (d in UPD and v>w) or (d not in UPD and v<w): return d,n
    return None
def settle2(dr,c,R,vals):
    # drone at c. fix violations at c; cascade only where a violation really exists.
    while True:
        x=viol(c,R,vals)
        if x is None: return
        d,n=x
        vals[c],vals[n]=vals[n],vals[c]; dr.swaps+=1
        if viol(n,R,vals) is not None:
            back=dr.pos; dr.go(n); settle2(dr,n,R,vals); dr.go(back)
