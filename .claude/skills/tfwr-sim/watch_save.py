"""Measure what the running game actually produces, by watching save.json.

    python watch_save.py <save folder> [minutes] [item ...]

The game rewrites save.json about every 30 seconds while it runs. This prints the item counts
each time the file changes and, at the end, the per-minute change of each watched item.
It only reads the file. Defaults: 10 minutes, every item that changed.
"""
import json
import os
import sys
import time


def read_shared(path):
    """Read a file without blocking the game from replacing it.

    The game saves with File.Replace, which fails (and drops the whole save, code included) if
    any process has save.json open without delete sharing. Python's open() doesn't grant that on
    Windows, so open the file through CreateFileW with FILE_SHARE_DELETE instead.
    """
    if os.name != "nt":
        with open(path, "rb") as f:
            return f.read()
    import ctypes
    import msvcrt
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                     wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD,
                                     wintypes.HANDLE]
    GENERIC_READ, OPEN_EXISTING = 0x80000000, 3
    SHARE_ALL = 0x1 | 0x2 | 0x4  # FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE
    handle = kernel32.CreateFileW(path, GENERIC_READ, SHARE_ALL, None, OPEN_EXISTING, 0, None)
    if handle == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    with os.fdopen(msvcrt.open_osfhandle(handle, os.O_RDONLY), "rb") as f:
        return f.read()


def read_items(path):
    data = json.loads(read_shared(path).decode("utf-8"))
    return {e["name"]: e["nr"] for e in data["items"]["serializeList"]}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    if not os.path.isfile(os.path.join(sys.argv[1], "save.json")):
        sys.exit(f"no save.json in {sys.argv[1]!r}\n{__doc__}")
    path = os.path.join(sys.argv[1], "save.json")
    minutes = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
    watched = sys.argv[3:]
    first = last_mtime = None
    latest = (0.0, {})
    start = time.time()
    while time.time() - start < minutes * 60:
        try:
            mtime = os.path.getmtime(path)
            if mtime != last_mtime:
                items = read_items(path)
                last_mtime = mtime
                latest = (mtime, items)
                if first is None:
                    first = latest
                shown = watched or sorted(k for k in items if items[k] != first[1].get(k))
                print(time.strftime("%H:%M:%S", time.localtime(mtime)),
                      "  ".join(f"{k}={items.get(k, 0):,.0f}" for k in shown), flush=True)
        except (OSError, ValueError, KeyError):
            pass  # the game is in the middle of replacing the file
        time.sleep(0.5)
    if first is None or latest[0] == first[0]:
        sys.exit("save.json did not change; is the game running with this save?")
    span = (latest[0] - first[0]) / 60
    print(f"\nover {span:.1f} min:")
    for name in watched or sorted(latest[1]):
        delta = latest[1].get(name, 0) - first[1].get(name, 0)
        if delta:
            print(f"  {name:16} {delta:+16,.0f}  ({delta / span:+14,.0f} /min)")


if __name__ == "__main__":
    main()
