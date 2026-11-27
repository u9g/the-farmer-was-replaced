# Writes work/int_<cand>.py: run_reset.py with a candidate's run_farm(need) used for run_plan's
# one-drone hay/wood/carrot rounds on 3x3..6x6 fields (names that clash with run_reset get a prefix)
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
def names(s):
    return set(re.findall(r'^def (\w+)', s, re.M)) | set(re.findall(r'^([A-Za-z_]\w*)\s*=', s, re.M))
for cand in sys.argv[1:]:
    base = open(REPO + '/run_reset.py').read()
    c = open(cand).read()
    for n in sorted(names(c) - {'run_farm'}, key=len, reverse=True):
        c = re.sub(r'\b%s\b' % n, 'cf_' + n, c)
    c = re.sub(r'\brun_farm\b', 'cand_farm', c)
    old = "\t\t\tif item == Items.Hay or item == Items.Wood or item == Items.Carrot:\n\t\t\t\tpower_check()\n\t\t\t\tmixed_round(set_need(plan, i))\n"
    assert old in base
    new = ("\t\t\tif item == Items.Hay or item == Items.Wood or item == Items.Carrot:\n"
           "\t\t\t\tif max_drones() == 1 and get_world_size() >= 3 and get_world_size() <= 6:\n"
           "\t\t\t\t\tcand_farm(set_need(plan, i)[0])\n"
           "\t\t\t\telse:\n"
           "\t\t\t\t\tpower_check()\n"
           "\t\t\t\t\tmixed_round(set_need(plan, i))\n")
    base = base.replace(old, new)
    tail = base.index('# (skipped when the script is restarted')
    out = base[:tail] + '\n# ---- farm design from old/farm_search/' + os.path.basename(cand) + ' ----\n' + c + '\n\n' + base[tail:]
    os.makedirs(HERE + '/work', exist_ok=True)
    open(HERE + '/work/int_' + os.path.basename(cand), 'w').write(out)
    print('wrote work/int_' + os.path.basename(cand))
