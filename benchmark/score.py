#!/usr/bin/env python3
"""Standalone scorer for a single finished benchmark run directory.

Usage:
    python3 benchmark/score.py <run_dir>

Reads <run_dir>/meta.json (written by Phase 2's run.sh), records the two
"truth" metrics, and writes the extended meta.json back in place:

  MET-01  passed / judge_exit  — pass/fail decided by RE-RUNNING the level's
          independent judge (tasks/<level>/test.py) against the files the agent
          actually produced. The tool's own "all tests pass" claim is ignored.
  MET-02  duration_seconds     — wall-clock seconds from started_at/finished_at.

stdlib-only (json, os, sys, subprocess, datetime); re-running is idempotent.
"""

import json
import os
import subprocess
import sys

# Locate tasks/<level>/test.py relative to this file, independent of cwd.
HERE = os.path.dirname(os.path.abspath(__file__))


def score_run(run_dir):
    """Score one finished run dir; extend its meta.json in place; return meta."""
    run_dir = os.path.abspath(run_dir)
    meta_path = os.path.join(run_dir, "meta.json")
    if not os.path.isfile(meta_path):
        raise SystemExit(f"score.py: no meta.json in {run_dir}")

    with open(meta_path) as fh:
        meta = json.load(fh)

    # --- MET-01: independent pass/fail by RE-RUNNING the level's judge ---
    # meta["level"] is the full tasks/ subdir name (e.g. "l1-fib"), so it maps
    # directly to the judge with no extra mapping table. Correctness is decided
    # ONLY by the judge process exit — the transcript / agent self-report and
    # meta["exit_code"] are never consulted here.
    judge = os.path.join(HERE, "tasks", str(meta.get("level")), "test.py")
    if not os.path.isfile(judge):
        meta["passed"] = False
        meta["judge_exit"] = None
        meta["judge_note"] = f"judge not found: {judge}"
    else:
        proc = subprocess.run(
            [sys.executable, judge, run_dir],
            capture_output=True,
            text=True,
        )
        meta["passed"] = (proc.returncode == 0)
        meta["judge_exit"] = proc.returncode
        meta.pop("judge_note", None)

    # --- MET-02: wall-clock duration_seconds (filled in by Task 3) ---

    with open(meta_path, "w") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")

    return meta


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 benchmark/score.py <run_dir>")
    run_dir = sys.argv[1]
    m = score_run(run_dir)
    print(
        f"{m.get('level')}  passed={m.get('passed')}  "
        f"duration_seconds={m.get('duration_seconds')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
