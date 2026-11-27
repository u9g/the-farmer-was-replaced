# Nest each drone's function inside its spawner, defined just before the spawn_drone call, so the
# main drone defines only its own children before its first spawn (a def is 1 tick).
import re, sys


def nest(text):
    src = text.split("\n")
    i0 = next(i for i, l in enumerate(src) if re.match(r"def w\d+\(\):", l))
    head = src[:i0]
    funcs = {}
    cur = None
    tail = []
    for l in src[i0:]:
        m = re.match(r"def (w\d+)\(\):", l)
        if m:
            cur = m.group(1)
            funcs[cur] = []
            continue
        if l.startswith("\t") or l == "":
            if cur:
                funcs[cur].append(l)
        else:
            tail.append(l)
            cur = None

    def emit(name, ind):
        out = [ind + "def %s():" % name]
        for l in funcs[name]:
            m = re.match(r"\tspawn_drone\((w\d+)\)$", l)
            if m:
                out += emit(m.group(1), ind + "\t")
            if l == "":
                continue
            out.append(ind + l)
        return out

    return "\n".join(head + emit("w0", "") + [""] + tail) + "\n"


if __name__ == "__main__":
    open(sys.argv[2], "w", newline="\n").write(nest(open(sys.argv[1]).read()))
