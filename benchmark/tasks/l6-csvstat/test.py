#!/usr/bin/env python3
"""L6 judge — independent, stdlib-only, black-box via subprocess.

Writes its own CSV to a temp dir, runs `python3 csvstat.py <csv> ...` in the solution
dir, and checks stdout + exit code. Computes expected stats itself; never trusts the
solution. Also checks the multi-module structure and error exits.

Usage:  python3 test.py [solution_dir]   (default: current directory)
Exit 0 = PASS, nonzero = FAIL.
"""
import os
import subprocess
import sys
import tempfile

SOL = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
ENTRY = os.path.join(SOL, "csvstat.py")
PKG = os.path.join(SOL, "csvstat")


def fail(msg):
    print(f"FAIL l6-csvstat: {msg}")
    sys.exit(1)


def fmt(x):
    return str(int(x)) if x == int(x) else str(x)


def main():
    if not os.path.isfile(ENTRY):
        fail("missing csvstat.py at solution root")
    if not (os.path.isdir(PKG) and os.path.isfile(os.path.join(PKG, "__init__.py"))
            and os.path.isfile(os.path.join(PKG, "stats.py"))):
        fail("missing csvstat/ package (need __init__.py and stats.py)")

    tmp = tempfile.mkdtemp()
    csv_path = os.path.join(tmp, "data.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("name,age,score\namy,30,1\nbob,40,2\ncid,50,3\ndan,20,4\n")

    def run(*args):
        p = subprocess.run([sys.executable, "csvstat.py", *args], cwd=SOL,
                           capture_output=True, text=True, timeout=30)
        return p.returncode, p.stdout.strip()

    # --cols (header order)
    rc, out = run(csv_path, "--cols")
    if rc != 0:
        fail(f"--cols exited {rc}")
    if out != "name\nage\nscore":
        fail(f"--cols mismatch:\n{out!r}")

    # --col score : 1,2,3,4 → count4 min1 max4 sum10 mean2.5
    rc, out = run(csv_path, "--col", "score")
    if rc != 0:
        fail(f"--col score exited {rc}")
    want = ("count: 4\nmin: 1\nmax: 4\nsum: 10\nmean: 2.5")
    if out != want:
        fail(f"--col score mismatch:\ngot:\n{out}\nwant:\n{want}")

    # --col age : 30,40,50,20 → sum140 mean35 (integral mean → '35')
    rc, out = run(csv_path, "--col", "age")
    want_age = ("count: 4\nmin: 20\nmax: 50\nsum: 140\nmean: 35")
    if rc != 0 or out != want_age:
        fail(f"--col age mismatch (rc={rc}):\ngot:\n{out}\nwant:\n{want_age}")

    # errors → nonzero
    if run(csv_path, "--col", "name")[0] == 0:      # non-numeric column
        fail("--col on non-numeric column exited 0 (want nonzero)")
    if run(csv_path, "--col", "nope")[0] == 0:      # missing column
        fail("--col on missing column exited 0 (want nonzero)")
    if run(os.path.join(tmp, "nofile.csv"), "--cols")[0] == 0:  # missing file
        fail("missing file exited 0 (want nonzero)")
    if run(csv_path)[0] == 0:                        # missing flag
        fail("missing flag exited 0 (want nonzero)")

    print("PASS l6-csvstat")
    sys.exit(0)


if __name__ == "__main__":
    main()
