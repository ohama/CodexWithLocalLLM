#!/usr/bin/env python3
"""L2 reference CLI — wordstat.py (stdlib only).

Usage: python3 wordstat.py <textfile>

Reads the UTF-8 file at argv[1] and prints, in this exact order:

    total: <int>
    unique: <int>
    top:
    <word> <count>     # up to 5, count desc then word asc, one space

Exits 0 on success. Tokenization/counting live in the sibling module
`wordcount` (genuine multi-file project).
"""

import sys

import wordcount


def main():
    if len(sys.argv) < 2:
        print("usage: python3 wordstat.py <textfile>", file=sys.stderr)
        return 1

    with open(sys.argv[1], encoding="utf-8") as f:
        text = f.read()

    total, unique, top = wordcount.analyze(text, 5)

    print(f"total: {total}")
    print(f"unique: {unique}")
    print("top:")
    for word, count in top:
        print(f"{word} {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
