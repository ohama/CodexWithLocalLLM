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
  MET-03  steps / step_method  — TOOL-AWARE step/tool-call count from the
          transcript. The two tools' transcripts differ, so the extractor
          branches on meta["tool"] and records the heuristic it used in
          step_method (units differ per tool — keep both, never just the number).
  MET-04  files / loc          — output size: number of files the agent produced
          in the run dir and total lines of code, excluding harness artifacts
          (transcript.log, meta.json) and __pycache__/.pyc.

stdlib-only (json, os, re, sys, subprocess, datetime); re-running is idempotent.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime

# Locate tasks/<level>/test.py relative to this file, independent of cwd.
HERE = os.path.dirname(os.path.abspath(__file__))

# ANSI CSI color/SGR escape sequences, stripped before parsing openhands output.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
# openhands prints a run summary line like "Number of agent messages: 4".
_OH_MSGS_RE = re.compile(r"Number of agent messages:\s*(\d+)")

# Harness artifacts that exist in every run dir but were NOT produced by the
# agent — excluded from the output-size count.
_HARNESS_FILES = {"transcript.log", "meta.json"}


def extract_steps(run_dir, meta):
    """MET-03: tool-aware step/tool-call count from the transcript.

    Returns (steps:int, step_method:str). Units differ per tool — codex counts
    `exec` command blocks, openhands reads its "Number of agent messages: N"
    summary — so step_method documents which heuristic produced the number.
    Best-effort: a missing transcript or absent marker yields steps=0 with a
    self-describing step_method, never a crash.
    """
    tool = meta.get("tool")
    transcript = os.path.join(run_dir, meta.get("transcript") or "transcript.log")
    if not os.path.isfile(transcript):
        return 0, "transcript-missing"

    with open(transcript, encoding="utf-8", errors="ignore") as fh:
        text = fh.read()

    if tool == "codex":
        # Each command execution is a line that is exactly `exec`, followed by
        # the command and a ` succeeded in `/` failed in ` line. Count tool
        # calls as the number of standalone `exec` markers.
        steps = sum(1 for line in text.splitlines() if line.strip() == "exec")
        return steps, "codex:count of 'exec' blocks"

    if tool == "openhands":
        # stdout is ANSI-colored — strip SGR codes first, then read the summary.
        clean = _ANSI_RE.sub("", text)
        m = _OH_MSGS_RE.search(clean)
        if m:
            return int(m.group(1)), "openhands:Number of agent messages"
        return 0, "openhands:summary-not-found"

    if tool in ("qclaude", "qclaude35", "qcf"):
        # Claude Code is run with `--output-format stream-json --verbose`, so the
        # transcript is JSONL of events. Count tool_use blocks in assistant turns
        # — the analog of codex's `exec` count (one per tool invocation).
        steps = 0
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                continue  # non-JSON noise (warnings) — skip
            if obj.get("type") != "assistant":
                continue
            content = obj.get("message", {}).get("content", [])
            if isinstance(content, list):
                steps += sum(1 for b in content
                             if isinstance(b, dict) and b.get("type") == "tool_use")
        return steps, "qclaude:count of tool_use events"

    return 0, f"unknown-tool:{tool}"


def measure_output(run_dir):
    """MET-04: output size — count of agent-produced files and total LOC.

    Walks run_dir (so multi-file L2/L3 solutions in subdirs like kvstore/ are
    counted) and excludes the harness artifacts and caches:
      - exact names: transcript.log, meta.json
      - anything under a __pycache__/ directory
      - .pyc files
    Returns (files:int, loc:int). LOC sums line counts of each produced file read
    as text; unreadable/binary files contribute 0 lines (best-effort).
    """
    files = 0
    loc = 0
    for root, dirs, names in os.walk(run_dir):
        # Prune cache dirs so nothing beneath them is ever counted.
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in names:
            if name in _HARNESS_FILES or name.endswith(".pyc"):
                continue
            files += 1
            path = os.path.join(root, name)
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    loc += len(fh.read().splitlines())
            except OSError:
                pass  # unreadable -> counted as a file, 0 lines
    return files, loc


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

    # --- MET-02: wall-clock duration_seconds from meta timestamps ---
    # Timestamps are second-resolution UTC ISO, e.g. "2026-06-26T02:11:03Z".
    # Best-effort: a missing/malformed timestamp yields null, never a crash.
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    try:
        started = datetime.strptime(meta["started_at"], fmt)
        finished = datetime.strptime(meta["finished_at"], fmt)
        meta["duration_seconds"] = int((finished - started).total_seconds())
    except (KeyError, TypeError, ValueError):
        meta["duration_seconds"] = None

    # --- MET-03: tool-aware step/tool-call count from the transcript ---
    meta["steps"], meta["step_method"] = extract_steps(run_dir, meta)

    # --- MET-04: output size — agent-produced files + total LOC ---
    meta["files"], meta["loc"] = measure_output(run_dir)

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
        f"duration_seconds={m.get('duration_seconds')}  "
        f"steps={m.get('steps')} ({m.get('step_method')})  "
        f"files={m.get('files')}  loc={m.get('loc')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
