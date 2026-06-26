#!/usr/bin/env python3
"""L2 judge — independent, stdlib-only, black-box via subprocess.

Usage:
    python3 tasks/l2-wordstat/test.py [solution_dir]

solution_dir defaults to the current directory. The judge runs
`python3 <solution_dir>/wordstat.py <inputfile>` on crafted inputs and checks
the EXACT stdout contract from tasks/l2-wordstat/PROMPT.md
(total / unique / top with count-desc then word-asc ordering).
Exit 0 = PASS; nonzero = FAIL.
"""

import os
import subprocess
import sys
import tempfile


def run_wordstat(solution_dir, input_path):
    """Run the solution's wordstat.py on input_path; return CompletedProcess."""
    entry = os.path.join(solution_dir, "wordstat.py")
    return subprocess.run(
        [sys.executable, entry, input_path],
        capture_output=True,
        text=True,
    )


def parse_output(stdout):
    """Parse the contract stdout into (total, unique, [(word, count), ...]).

    Raises ValueError on any structural deviation from the contract.
    """
    lines = stdout.splitlines()
    if len(lines) < 3:
        raise ValueError(f"too few lines: {lines!r}")
    if not lines[0].startswith("total: "):
        raise ValueError(f"line 1 not 'total: <int>': {lines[0]!r}")
    if not lines[1].startswith("unique: "):
        raise ValueError(f"line 2 not 'unique: <int>': {lines[1]!r}")
    if lines[2] != "top:":
        raise ValueError(f"line 3 not 'top:': {lines[2]!r}")

    total = int(lines[0][len("total: "):])
    unique = int(lines[1][len("unique: "):])

    top = []
    for ln in lines[3:]:
        if ln == "":
            continue
        parts = ln.split(" ")
        if len(parts) != 2:
            raise ValueError(f"top line not '<word> <count>': {ln!r}")
        top.append((parts[0], int(parts[1])))
    return total, unique, top


def check_case(solution_dir, tmpdir, name, content, exp_total, exp_unique, exp_top):
    """Run one fixture; return list of failure strings (empty == pass)."""
    input_path = os.path.join(tmpdir, f"{name}.txt")
    with open(input_path, "w", encoding="utf-8") as f:
        f.write(content)

    proc = run_wordstat(solution_dir, input_path)
    fails = []
    if proc.returncode != 0:
        fails.append(
            f"[{name}] exit {proc.returncode} (want 0); stderr={proc.stderr!r}"
        )
        return fails

    try:
        total, unique, top = parse_output(proc.stdout)
    except ValueError as exc:
        fails.append(f"[{name}] bad stdout ({exc}); raw={proc.stdout!r}")
        return fails

    if total != exp_total:
        fails.append(f"[{name}] total={total}, expected {exp_total}")
    if unique != exp_unique:
        fails.append(f"[{name}] unique={unique}, expected {exp_unique}")
    if top != exp_top:
        fails.append(f"[{name}] top={top}, expected {exp_top}")
    return fails


def main():
    solution_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")

    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        # Case 1: tie-free top-5. Counts are strictly distinct down to the 5th
        # slot (egg=2), and the only count-1 words (fig, grape) sit BELOW it,
        # so the 5th slot is unambiguous (no count-1 tie boundary).
        words = (
            ["apple"] * 6
            + ["banana"] * 5
            + ["cherry"] * 4
            + ["date"] * 3
            + ["egg"] * 2
            + ["fig"]
            + ["grape"]
        )
        content1 = " ".join(words) + "\n"
        failures += check_case(
            solution_dir, tmp, "main", content1,
            exp_total=22, exp_unique=7,
            exp_top=[("apple", 6), ("banana", 5), ("cherry", 4),
                     ("date", 3), ("egg", 2)],
        )

        # Case 2: tie-break — alpha and delta both count 2 -> alphabetical.
        content2 = "delta delta alpha alpha charlie\n"
        failures += check_case(
            solution_dir, tmp, "tie", content2,
            exp_total=5, exp_unique=3,
            exp_top=[("alpha", 2), ("delta", 2), ("charlie", 1)],
        )

        # Case 3: tokenization — lowercasing + punctuation as separators.
        # "The cat's" -> the, cat, s. All count 1 -> word ascending.
        content3 = "The cat's\n"
        failures += check_case(
            solution_dir, tmp, "tok", content3,
            exp_total=3, exp_unique=3,
            exp_top=[("cat", 1), ("s", 1), ("the", 1)],
        )

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1

    print("PASS l2-wordstat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
