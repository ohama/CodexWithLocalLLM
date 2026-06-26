#!/usr/bin/env python3
"""L5 reference — todo manager CLI (subcommands over JSON store)."""
import sys

import store


def main(argv):
    if not argv:
        sys.exit(1)
    cmd = argv[0]
    if cmd == "add":
        if len(argv) < 2:
            sys.exit(1)
        print(f"added {store.add(argv[1])}")
        sys.exit(0)
    if cmd == "list":
        for t in store.items():
            status = "[x]" if t["done"] else "[ ]"
            print(f"{t['id']} {status} {t['text']}")
        sys.exit(0)
    if cmd in ("done", "rm"):
        if len(argv) < 2:
            sys.exit(1)
        try:
            tid = int(argv[1])
        except ValueError:
            sys.exit(1)
        ok = store.set_done(tid) if cmd == "done" else store.remove(tid)
        sys.exit(0 if ok else 1)
    sys.exit(1)  # unknown command


if __name__ == "__main__":
    main(sys.argv[1:])
