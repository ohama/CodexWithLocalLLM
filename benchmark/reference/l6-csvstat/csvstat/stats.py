#!/usr/bin/env python3
"""L6 reference — numeric column statistics."""


def fmt(x):
    return str(int(x)) if x == int(x) else str(x)


def _num(s):
    """Parse a CSV cell as a number; raise ValueError if not numeric."""
    v = float(s)
    return int(v) if v == int(v) and "." not in s and "e" not in s.lower() else v


def column_stats(values):
    """values: list of raw strings for one column. Returns dict of stats.

    Raises ValueError if any value isn't numeric or the column is empty.
    """
    if not values:
        raise ValueError("empty column")
    nums = [_num(v) for v in values]
    total = sum(nums)
    return {
        "count": len(nums),
        "min": min(nums),
        "max": max(nums),
        "sum": total,
        "mean": total / len(nums),
    }
