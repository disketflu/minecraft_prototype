import harfang as hg

def RangeAdjust(val, in_lower, in_upper, out_lower, out_upper):
    return (val-in_lower)/(in_upper-in_lower)*(out_upper-out_lower)+out_lower
    