#!/usr/bin/env python3
"""L1 judge — independent, stdlib-only.

Usage:
    python3 tasks/l1-fib/test.py [solution_dir]

solution_dir defaults to the current directory. The judge imports `fib` from
that directory and asserts the exact values frozen in tasks/l1-fib/PROMPT.md.
Exit 0 = PASS (all checks hold); nonzero = FAIL.
"""

import importlib
import os
import sys

# Contract values pinned in tasks/l1-fib/PROMPT.md.
EXPECTED = {
    0: 0,
    1: 1,
    2: 1,
    3: 2,
    5: 5,
    10: 55,
    20: 6765,
    30: 832040,
}


def main() -> int:
    solution_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")

    # Load `fib` from the solution dir, never a stale cached module.
    sys.path.insert(0, solution_dir)
    sys.modules.pop("fib", None)
    importlib.invalidate_caches()
    try:
        mod = importlib.import_module("fib")
    except Exception as exc:  # import error, syntax error, missing file...
        print(f"FAIL: could not import fib from {solution_dir}: {exc!r}")
        return 1

    if not hasattr(mod, "fib") or not callable(mod.fib):
        print("FAIL: module 'fib' has no callable fib(n)")
        return 1

    failures = []
    for n, want in sorted(EXPECTED.items()):
        try:
            got = mod.fib(n)
        except Exception as exc:
            failures.append(f"fib({n}) raised {exc!r}")
            continue
        if not isinstance(got, int) or isinstance(got, bool):
            failures.append(f"fib({n}) returned {got!r} (not int)")
            continue
        if got != want:
            failures.append(f"fib({n}) = {got!r}, expected {want!r}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1

    print("PASS l1-fib")
    return 0


if __name__ == "__main__":
    sys.exit(main())
