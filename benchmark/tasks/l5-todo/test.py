#!/usr/bin/env python3
"""L5 judge — independent, stdlib-only, black-box via subprocess across processes.

Drives `python3 todo.py <cmd> ...` in the solution dir with a hermetic TODO_PATH
(temp file), exercising add/list/done/rm, id stability, persistence, and exit codes.
Never trusts the solution's self-report.

Usage:  python3 test.py [solution_dir]   (default: current directory)
Exit 0 = PASS, nonzero = FAIL.
"""
import os
import subprocess
import sys
import tempfile

SOL = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
ENTRY = os.path.join(SOL, "todo.py")


def fail(msg):
    print(f"FAIL l5-todo: {msg}")
    sys.exit(1)


def main():
    if not os.path.isfile(ENTRY):
        fail("missing todo.py at solution root")
    # require multi-file: at least one more .py besides todo.py
    extra = [f for f in os.listdir(SOL) if f.endswith(".py") and f != "todo.py"]
    if not extra and not any(os.path.isdir(os.path.join(SOL, d)) for d in os.listdir(SOL)):
        fail("expected a multi-file project (todo.py + helper module)")

    tmp = tempfile.mkdtemp()
    env = dict(os.environ, TODO_PATH=os.path.join(tmp, "todos.json"))

    def run(*args):
        p = subprocess.run([sys.executable, "todo.py", *args], cwd=SOL, env=env,
                           capture_output=True, text=True, timeout=30)
        return p.returncode, p.stdout.strip()

    # add two tasks → ids 1, 2 (separate processes; must persist)
    rc, out = run("add", "buy milk")
    if rc != 0 or out != "added 1":
        fail(f"add#1: rc={rc} out={out!r} (want 'added 1')")
    rc, out = run("add", "write report")
    if rc != 0 or out != "added 2":
        fail(f"add#2: rc={rc} out={out!r} (want 'added 2')")

    # mark 1 done
    rc, _ = run("done", "1")
    if rc != 0:
        fail(f"done 1 exited {rc} (want 0)")

    # list shows status + order
    rc, out = run("list")
    if rc != 0:
        fail(f"list exited {rc}")
    if out != "1 [x] buy milk\n2 [ ] write report":
        fail(f"list mismatch:\n{out!r}")

    # remove 1; id 2 must stay (no renumber)
    rc, _ = run("rm", "1")
    if rc != 0:
        fail(f"rm 1 exited {rc}")
    rc, out = run("list")
    if out != "2 [ ] write report":
        fail(f"after rm, list mismatch:\n{out!r}")

    # id stability: next add is 3, not reuse of 1
    rc, out = run("add", "third")
    if out != "added 3":
        fail(f"id not stable: add after rm gave {out!r} (want 'added 3')")

    # nonexistent id → nonzero
    rc, _ = run("done", "99")
    if rc == 0:
        fail("done on missing id exited 0 (want nonzero)")
    rc, _ = run("rm", "99")
    if rc == 0:
        fail("rm on missing id exited 0 (want nonzero)")

    # unknown command / missing arg → nonzero
    if run("bogus")[0] == 0:
        fail("unknown command exited 0 (want nonzero)")
    if run("add")[0] == 0:
        fail("add with no text exited 0 (want nonzero)")

    print("PASS l5-todo")
    sys.exit(0)


if __name__ == "__main__":
    main()
