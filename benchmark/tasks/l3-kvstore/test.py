#!/usr/bin/env python3
"""L3 judge — independent, stdlib-only, black-box via subprocess.

Usage:
    python3 tasks/l3-kvstore/test.py [solution_dir]

solution_dir defaults to the current directory. The judge drives
`python3 <solution_dir>/cli.py <cmd> ...` in separate processes against a fresh
temp KVSTORE_PATH and checks the exact CLI/persistence/exit-code contract from
tasks/l3-kvstore/PROMPT.md. Exit 0 = PASS; nonzero = FAIL.
"""

import os
import subprocess
import sys
import tempfile


def main():
    solution_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    cli = os.path.join(solution_dir, "cli.py")
    failures = []

    # (1) Required multi-module files must exist.
    required = ["cli.py", "kvstore/__init__.py", "kvstore/storage.py"]
    for rel in required:
        if not os.path.isfile(os.path.join(solution_dir, rel)):
            failures.append(f"missing required file: {rel}")
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        store_path = os.path.join(tmp, "store.db")
        env = {**os.environ, "KVSTORE_PATH": store_path}

        def run(*args):
            # Each call is a SEPARATE process -> exercises cross-process
            # persistence. cwd is the temp dir; KVSTORE_PATH is absolute.
            return subprocess.run(
                [sys.executable, cli, *args],
                env=env, cwd=tmp, capture_output=True, text=True,
            )

        # (2) set several keys -> exit 0 each.
        pairs = [("banana", "yellow"), ("apple", "red"), ("cherry", "dark")]
        for k, v in pairs:
            p = run("set", k, v)
            if p.returncode != 0:
                failures.append(f"set {k} exit {p.returncode}; stderr={p.stderr!r}")

        # (3) get existing key in a separate process -> exit 0, stdout == value.
        for k, v in pairs:
            p = run("get", k)
            if p.returncode != 0:
                failures.append(f"get {k} exit {p.returncode} (want 0)")
            elif p.stdout != v + "\n":
                failures.append(f"get {k} stdout={p.stdout!r}, expected {v + chr(10)!r}")

        # (4) get missing key -> exit 1, empty stdout.
        p = run("get", "nope")
        if p.returncode != 1:
            failures.append(f"get missing exit {p.returncode} (want 1)")
        if p.stdout != "":
            failures.append(f"get missing stdout not empty: {p.stdout!r}")

        # (5) delete existing -> exit 0, then get -> exit 1.
        p = run("delete", "apple")
        if p.returncode != 0:
            failures.append(f"delete existing exit {p.returncode} (want 0)")
        p = run("get", "apple")
        if p.returncode != 1:
            failures.append(f"get after delete exit {p.returncode} (want 1)")

        # (6) delete missing -> exit 0 (idempotent).
        p = run("delete", "apple")
        if p.returncode != 0:
            failures.append(f"delete missing exit {p.returncode} (want 0)")

        # (7) list -> remaining keys sorted ascending, one per line.
        p = run("list")
        if p.returncode != 0:
            failures.append(f"list exit {p.returncode} (want 0)")
        else:
            got = p.stdout.splitlines()
            expected = sorted([k for k, _ in pairs if k != "apple"])  # banana, cherry
            if got != expected:
                failures.append(f"list got {got}, expected {expected}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1

    print("PASS l3-kvstore")
    return 0


if __name__ == "__main__":
    sys.exit(main())
