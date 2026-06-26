#!/usr/bin/env python3
"""L6 reference — CSV column statistics CLI."""
import csv
import os
import sys

from csvstat.stats import column_stats, fmt


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        raise ValueError("empty file")
    return rows[0], rows[1:]


def main(argv):
    if len(argv) < 2:
        sys.exit(1)
    path = argv[0]
    if not os.path.isfile(path):
        sys.exit(1)
    try:
        header, data = read_csv(path)
    except (OSError, ValueError):
        sys.exit(1)

    if argv[1] == "--cols":
        for c in header:
            print(c)
        sys.exit(0)

    if argv[1] == "--col":
        if len(argv) < 3:
            sys.exit(1)
        name = argv[2]
        if name not in header:
            sys.exit(1)
        idx = header.index(name)
        try:
            values = [row[idx] for row in data]
            s = column_stats(values)
        except (ValueError, IndexError):
            sys.exit(1)
        print(f"count: {s['count']}")
        print(f"min: {fmt(s['min'])}")
        print(f"max: {fmt(s['max'])}")
        print(f"sum: {fmt(s['sum'])}")
        print(f"mean: {fmt(s['mean'])}")
        sys.exit(0)

    sys.exit(1)  # unknown flag


if __name__ == "__main__":
    main(sys.argv[1:])
