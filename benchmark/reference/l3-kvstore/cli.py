#!/usr/bin/env python3
"""L3 reference CLI — cli.py (stdlib only).

Commands (run as `python3 cli.py <cmd> ...`):
    set <key> <value>   store the pair; exit 0
    get <key>           print value + newline, exit 0; missing -> nothing, exit 1
    delete <key>        remove if present; exit 0 (idempotent)
    list                keys sorted ascending, one per line; exit 0

Persistence file is $KVSTORE_PATH or ./kvstore.db (see kvstore.storage).
"""

import sys

from kvstore import Store

_MISSING = object()


def main(argv):
    if not argv:
        print("usage: python3 cli.py <set|get|delete|list> ...", file=sys.stderr)
        return 2

    cmd, rest = argv[0], argv[1:]
    store = Store()

    if cmd == "set":
        if len(rest) != 2:
            print("usage: cli.py set <key> <value>", file=sys.stderr)
            return 2
        store.set(rest[0], rest[1])
        return 0

    if cmd == "get":
        if len(rest) != 1:
            print("usage: cli.py get <key>", file=sys.stderr)
            return 2
        value = store.get(rest[0], _MISSING)
        if value is _MISSING:
            return 1
        print(value)
        return 0

    if cmd == "delete":
        if len(rest) != 1:
            print("usage: cli.py delete <key>", file=sys.stderr)
            return 2
        store.delete(rest[0])
        return 0

    if cmd == "list":
        for key in store.keys():
            print(key)
        return 0

    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
