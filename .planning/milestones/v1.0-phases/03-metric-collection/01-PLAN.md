---
phase: 03-metric-collection
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - benchmark/score.py
autonomous: true

must_haves:
  truths:
    - "Running score.py on a finished run dir decides pass/fail by RE-RUNNING the level's independent judge against the produced files (tool self-report is ignored)."
    - "The wall-clock duration of the run is computed and recorded in seconds."
    - "passed, judge_exit, and duration_seconds are written back into the run dir's meta.json without losing existing fields."
    - "score.py runs on the two existing sample run dirs with no new agent/LLM run."
  artifacts:
    - path: "benchmark/score.py"
      provides: "Standalone scorer: reads a run dir's meta.json, re-runs the level judge, computes duration, extends meta.json"
      min_lines: 60
      exports: ["main", "score_run"]
  key_links:
    - from: "benchmark/score.py"
      to: "benchmark/tasks/<level>/test.py"
      via: "subprocess python3 test.py <run_dir>, level taken from meta.json['level']"
      pattern: "tasks.*test\\.py"
    - from: "benchmark/score.py"
      to: "<run_dir>/meta.json"
      via: "json.load then json.dump back with new metric fields merged in"
      pattern: "json\\.(load|dump)"
---

<objective>
Create `benchmark/score.py`, a standalone, re-runnable scorer that takes a single
finished run directory and records the two "truth" metrics:

- MET-01: pass/fail decided by RE-RUNNING the task's independent judge
  (`benchmark/tasks/<level>/test.py <run_dir>`) against the files the agent
  actually produced — the tool's own "all tests pass" claim is never trusted.
- MET-02: wall-clock `duration_seconds` derived from the `started_at`/`finished_at`
  timestamps already present in meta.json.

Purpose: Turns the record-only meta.json (written by Phase 2's run.sh) into a
record that carries independently-verified correctness and timing. This is the
foundation Plan 02 extends with step-count and output-size metrics.

Output: `benchmark/score.py` plus, when run, a meta.json extended in place with
`passed`, `judge_exit`, and `duration_seconds`.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md

# The contract score.py reads/extends (Phase 2 output):
@benchmark/run.sh
# meta.json produced per run (fields: tool, level, model, base_url, prompt_file,
# run_dir, started_at, finished_at, exit_code, transcript). `level` is the FULL
# dir name, e.g. "l1-fib", which maps directly to tasks/<level>/test.py:
@benchmark/.runs/codex-l1-fib-20260626-021103/meta.json
@benchmark/.runs/openhands-l1-fib-20260626-021227/meta.json

# The judges score.py re-runs (argv[1] = solution dir, exit 0 = PASS):
@benchmark/tasks/l1-fib/test.py
@benchmark/tasks/l3-kvstore/test.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Scaffold score.py — load meta.json, resolve paths, write-back skeleton</name>
  <files>benchmark/score.py</files>
  <action>
    Create `benchmark/score.py` (stdlib only — json, os, sys, subprocess, datetime;
    no external deps, matching the project's stdlib-only constraint).

    Structure:
    - `HERE = os.path.dirname(os.path.abspath(__file__))` so the scorer locates
      `tasks/<level>/test.py` relative to itself, independent of cwd.
    - `def score_run(run_dir) -> dict:` — the core entry. It:
        1. Reads `<run_dir>/meta.json` (json.load). Abort with a clear error if missing.
        2. Computes the metric fields (Task 2 + Task 3 fill these in).
        3. Merges the new fields into the loaded meta dict (preserve ALL existing
           keys — tool, level, model, base_url, prompt_file, run_dir, started_at,
           finished_at, exit_code, transcript).
        4. Writes the merged dict back to `<run_dir>/meta.json` (json.dump,
           indent=2). Re-running must be idempotent (same inputs -> same output).
        5. Returns the merged dict.
    - `def main(): run_dir = sys.argv[1]; m = score_run(run_dir); print a one-line
      human summary (level, passed, duration_seconds); return 0`.
    - `if __name__ == "__main__": sys.exit(main())`.

    For THIS task, leave the metric computation as obvious placeholders to be
    filled by Tasks 2 and 3 (do not invent values). Keep it small and readable.
  </action>
  <verify>
    python3 -c "import ast; ast.parse(open('benchmark/score.py').read())"  # parses
    python3 benchmark/score.py benchmark/.runs/codex-l1-fib-20260626-021103  # runs, no traceback, meta.json still has original keys
  </verify>
  <done>score.py parses, loads a sample meta.json, and writes it back with all original keys intact.</done>
</task>

<task type="auto">
  <name>Task 2: MET-01 — independent pass/fail via judge re-run</name>
  <files>benchmark/score.py</files>
  <action>
    Implement independent correctness judging inside `score_run`:

    - Map level -> judge: `judge = os.path.join(HERE, "tasks", meta["level"], "test.py")`.
      `meta["level"]` is the full dir name (e.g. "l1-fib", "l2-wordstat",
      "l3-kvstore"), which already matches the tasks/ subdir exactly — no extra
      mapping table needed. If the judge file does not exist, record
      passed=false, judge_exit=null, and a note; do NOT crash.
    - Run the judge as a SEPARATE process against the produced files:
        `subprocess.run([sys.executable, judge, run_dir], capture_output=True, text=True)`.
      Use an absolute run_dir.
    - Record: `passed = (proc.returncode == 0)` (BOOL), `judge_exit = proc.returncode` (INT).
      This is the only source of truth for success — never parse the transcript or
      meta's exit_code for correctness. The agent's own "all tests pass" message is
      explicitly ignored.
    - Merge `passed` and `judge_exit` into the meta dict.

    Note for implementer: the L1 judge imports `fib` and will create a
    `__pycache__/` dir inside the run dir — that is expected and harmless here
    (Plan 02's file counter explicitly excludes __pycache__).
  </action>
  <verify>
    python3 benchmark/score.py benchmark/.runs/codex-l1-fib-20260626-021103 && python3 -c "import json;m=json.load(open('benchmark/.runs/codex-l1-fib-20260626-021103/meta.json'));assert m['passed'] is True and m['judge_exit']==0, m;print('codex MET-01 ok')"
    python3 benchmark/score.py benchmark/.runs/openhands-l1-fib-20260626-021227 && python3 -c "import json;m=json.load(open('benchmark/.runs/openhands-l1-fib-20260626-021227/meta.json'));assert m['passed'] is True and m['judge_exit']==0, m;print('openhands MET-01 ok')"
  </verify>
  <done>Both sample run dirs get passed=true, judge_exit=0 derived from an actual judge re-run against their fib.py (not from the transcript).</done>
</task>

<task type="auto">
  <name>Task 3: MET-02 — wall-clock duration_seconds</name>
  <files>benchmark/score.py</files>
  <action>
    Implement duration computation inside `score_run`:

    - Parse `meta["started_at"]` and `meta["finished_at"]`. Both are UTC ISO of the
      form `2026-06-26T02:11:03Z`. Use
      `datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")` (stdlib) for each.
    - `duration_seconds = int((finished - started).total_seconds())` (or float —
      pick one and be consistent; int seconds is fine since timestamps are
      second-resolution).
    - If either timestamp is missing/malformed, record `duration_seconds = null`
      and continue (best-effort; never crash).
    - Merge `duration_seconds` into the meta dict.
  </action>
  <verify>
    python3 benchmark/score.py benchmark/.runs/codex-l1-fib-20260626-021103 && python3 -c "import json;m=json.load(open('benchmark/.runs/codex-l1-fib-20260626-021103/meta.json'));assert m['duration_seconds']==43,m;print('codex dur',m['duration_seconds'])"
    python3 benchmark/score.py benchmark/.runs/openhands-l1-fib-20260626-021227 && python3 -c "import json;m=json.load(open('benchmark/.runs/openhands-l1-fib-20260626-021227/meta.json'));assert m['duration_seconds']==49,m;print('openhands dur',m['duration_seconds'])"
  </verify>
  <done>codex sample records duration_seconds=43 (02:11:03->02:11:46), openhands records 49 (02:12:27->02:13:16), computed from meta timestamps.</done>
</task>

</tasks>

<verification>
Runnable entirely on the EXISTING sample run dirs — no new agent/LLM run:

1. `python3 -c "import ast; ast.parse(open('benchmark/score.py').read())"` — score.py is valid Python.
2. `python3 benchmark/score.py benchmark/.runs/codex-l1-fib-20260626-021103` — exits 0, prints a summary line.
3. `python3 benchmark/score.py benchmark/.runs/openhands-l1-fib-20260626-021227` — exits 0, prints a summary line.
4. For BOTH run dirs, meta.json now contains: passed (true), judge_exit (0),
   duration_seconds (43 / 49), AND still contains every original field
   (tool, level, model, base_url, prompt_file, run_dir, started_at, finished_at,
   exit_code, transcript).
5. Idempotency: run score.py twice on the same dir -> identical metric values.
6. MET-01 independence proof: passed comes from the judge process exit, not from
   the transcript's "all tests pass" text.
</verification>

<success_criteria>
- benchmark/score.py exists, stdlib-only, runs against any run dir given as argv[1].
- MET-01: passed + judge_exit recorded from an independent `tasks/<level>/test.py <run_dir>` re-run.
- MET-02: duration_seconds recorded from meta timestamps.
- meta.json extended in place, original fields preserved, idempotent on re-run.
- Verified on both existing sample dirs with zero new LLM time.
</success_criteria>

<output>
After completion, create `.planning/phases/03-metric-collection/03-01-SUMMARY.md`.
</output>
