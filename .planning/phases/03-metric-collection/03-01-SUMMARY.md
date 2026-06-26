---
phase: 03-metric-collection
plan: 01
subsystem: testing
tags: [python, stdlib, scoring, judge, metrics, subprocess, datetime]

# Dependency graph
requires:
  - phase: 01-fixed-tasks
    provides: independent stdlib judges tasks/<level>/test.py (argv[1]=solution dir, exit 0 = PASS)
  - phase: 02-equal-conditions-runner
    provides: per-run dir contract — meta.json (level/started_at/finished_at/...) + transcript.log + produced files
provides:
  - benchmark/score.py — standalone re-runnable scorer for a single finished run dir
  - MET-01 passed/judge_exit recorded from an independent judge re-run (tool self-report ignored)
  - MET-02 duration_seconds recorded from meta timestamps
  - meta.json extended in place, original fields preserved, idempotent
affects: [03-metric-collection plan 02 (step-count + output-size metrics), reporting/aggregation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Scorer re-runs the level judge as a separate subprocess against produced files; judge exit is the only source of truth for pass/fail"
    - "meta.json extended in place via load -> merge -> dump, preserving all keys, idempotent on re-run"

key-files:
  created:
    - benchmark/score.py
  modified: []

key-decisions:
  - "Correctness decided ONLY by judge process exit; transcript/self-report/meta exit_code never consulted"
  - "meta['level'] is the full tasks/ subdir name (l1-fib/...) -> direct judge path, no mapping table"
  - "Missing judge -> passed=false, judge_exit=null, judge_note (best-effort, never crash)"
  - "Malformed/missing timestamps -> duration_seconds=null (best-effort, never crash)"
  - "duration_seconds is int (timestamps are second-resolution UTC ISO)"

patterns-established:
  - "Idempotent in-place meta.json extension: re-running the scorer yields identical metric values"
  - "Independent verification: pass/fail comes from a fresh judge process, decoupled from the agent run"

# Metrics
duration: ~12min
completed: 2026-06-26
---

# Phase 3 Plan 01: Metric Collection (MET-01 + MET-02) Summary

**benchmark/score.py: a stdlib-only re-runnable scorer that decides pass/fail by re-running the level's independent judge against the agent's produced files and records wall-clock duration, extending meta.json in place.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-06-26T02:31:00Z
- **Completed:** 2026-06-26T02:43:51Z
- **Tasks:** 3
- **Files modified:** 1 (benchmark/score.py created)

## Accomplishments
- MET-01: pass/fail decided by re-running `tasks/<level>/test.py <run_dir>` as a separate process; records `passed` (bool) and `judge_exit` (int). The tool's own "all tests pass" claim is never trusted.
- MET-02: `duration_seconds` computed from `started_at`/`finished_at` meta timestamps.
- meta.json extended in place with all original fields preserved; re-running is idempotent.
- Verified on both existing sample run dirs with zero new LLM time: codex (passed=true, judge_exit=0, 43s) and openhands (passed=true, judge_exit=0, 49s).

## Task Commits

Each task was committed atomically:

1. **Task 1: Scaffold score.py — load meta.json, resolve paths, write-back skeleton** - `13f7a87` (feat)
2. **Task 2: MET-01 — independent pass/fail via judge re-run** - `f859552` (feat)
3. **Task 3: MET-02 — wall-clock duration_seconds** - `fd0e3ee` (feat)

**Plan metadata:** docs(03-01): complete plan (this commit)

## Files Created/Modified
- `benchmark/score.py` - Standalone scorer. `score_run(run_dir)` reads meta.json, re-runs the level judge for MET-01, computes duration for MET-02, merges into meta and writes back idempotently. `main()` takes argv[1] run dir and prints a one-line summary.

## Decisions Made
- Correctness is decided ONLY by the judge process exit code — transcript text, agent self-report, and meta `exit_code` are explicitly ignored (MET-01 independence).
- `meta["level"]` is already the full tasks/ subdir name (e.g. `l1-fib`), so it maps directly to `tasks/<level>/test.py` with no mapping table.
- Best-effort robustness: missing judge yields `passed=false`/`judge_exit=null`/`judge_note`; missing or malformed timestamps yield `duration_seconds=null`. The scorer never crashes on a degraded run dir.
- `duration_seconds` is an int (timestamps are second-resolution).

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None. The L1 judge creates a `__pycache__/` inside the run dir on import (expected and noted in the plan; Plan 02's file counter excludes it).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- score.py is ready for Plan 02 to extend with step-count and output-size metrics (same load -> merge -> dump pattern).
- `benchmark/.runs/` is gitignored, so the sample run dirs' extended meta.json changes are local only; score.py is the committed, re-runnable artifact.
- No blockers.

---
*Phase: 03-metric-collection*
*Completed: 2026-06-26*
