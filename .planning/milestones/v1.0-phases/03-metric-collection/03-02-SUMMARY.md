---
phase: 03-metric-collection
plan: 02
subsystem: testing
tags: [python, stdlib, scoring, metrics, transcript-parsing, ansi, regex, bash, os-walk]

# Dependency graph
requires:
  - phase: 03-metric-collection
    provides: benchmark/score.py (MET-01 passed/judge_exit + MET-02 duration_seconds; idempotent in-place meta.json extension)
  - phase: 02-equal-conditions-runner
    provides: per-run dir contract — meta.json (tool/level/transcript/...) + transcript.log + agent-produced files; run.sh sections 1-11
provides:
  - MET-03 steps + step_method — tool-aware step/tool-call count parsed from transcript.log
  - MET-04 files + loc — output-size count of agent-produced files, harness/cache excluded
  - run.sh auto-invokes score.py after meta.json write (best-effort, never aborts the run)
  - all four metrics (passed, duration_seconds, steps, files+loc) land in ONE meta.json per run
affects: [04-reporting (must surface step_method, not just raw steps — units differ per tool), aggregation/matrix runs]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Tool-aware transcript parsing: extractor branches on meta['tool'] and records the heuristic in step_method (codex exec-blocks vs openhands agent-messages)"
    - "ANSI SGR strip (re.sub r'\\x1b\\[[0-9;]*m') before parsing openhands' colored summary"
    - "os.walk with in-place dirs[] prune of __pycache__ so cache files are never counted; exclude transcript.log/meta.json/.pyc"
    - "Best-effort scorer hook in set -euo pipefail bash: set +e / capture exit / set -e so a scorer hiccup never fails or masks the run"

key-files:
  created: []
  modified:
    - benchmark/score.py
    - benchmark/run.sh

key-decisions:
  - "steps units differ per tool, so step_method is ALWAYS recorded alongside the number — never just the raw count"
  - "codex steps = count of standalone 'exec' marker lines (line.strip()=='exec'); openhands steps = 'Number of agent messages: N' after ANSI strip"
  - "Missing transcript -> steps=0/step_method='transcript-missing'; openhands marker absent -> steps=0/'openhands:summary-not-found' (best-effort, never crash)"
  - "Output-size exclusions: transcript.log, meta.json, __pycache__/, .pyc; os.walk recurses so multi-file L2/L3 solutions in subdirs are counted"
  - "loc = newline count via splitlines, utf-8 errors=ignore; unreadable file counts as 1 file / 0 lines"
  - "run.sh scorer hook is purely additive (section 10b) — Phase 2 arg/lock/isolation/tool/meta fields unchanged"

patterns-established:
  - "Tool-aware metric extraction with self-documenting method string (heuristic visible, not hidden)"
  - "Best-effort enrichment hook: scorer failure is isolated and warned, the run record always survives"

# Metrics
duration: ~8min
completed: 2026-06-26
---

# Phase 3 Plan 02: Metric Collection (MET-03 + MET-04 + scorer hook) Summary

**score.py now extracts a tool-aware step count (codex 'exec' blocks vs openhands 'Number of agent messages', each tagged with step_method) and output size (agent-produced files + LOC, excluding transcript.log/meta.json/__pycache__), and run.sh auto-invokes the scorer after writing meta.json (best-effort) so a single run yields all four metrics in one record.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-06-26T02:45:52Z
- **Completed:** 2026-06-26T02:53:00Z
- **Tasks:** 3
- **Files modified:** 2 (benchmark/score.py, benchmark/run.sh)

## Accomplishments
- MET-03: `extract_steps()` branches on `meta["tool"]` — codex counts standalone `exec` blocks (sample -> 2), openhands parses `Number of agent messages: N` after stripping ANSI SGR codes (sample -> 4). Records `steps` (int) + `step_method` (str) so the heuristic and its per-tool units are documented, never hidden.
- MET-04: `measure_output()` walks the run dir, counts agent-produced files and sums LOC, excluding `transcript.log`, `meta.json`, `__pycache__/`, and `.pyc`. L1 samples -> files=1 (fib.py), loc=31 despite each dir also holding a transcript, meta.json, and a `__pycache__/`.
- run.sh section 10b invokes `python3 score.py "$RUN_DIR"` after the meta.json heredoc, guarded with `set +e`/capture/`set -e`; a scorer failure prints a warning but never aborts or masks the run. Section 11 echoes all four metrics back from meta.json.
- All four metrics now land in ONE meta.json record per run; verified idempotent on both existing sample dirs with zero new LLM time.

## Task Commits

Each task was committed atomically:

1. **Task 1: MET-03 — tool-aware step/tool-call extraction** - `9ff1dfa` (feat)
2. **Task 2: MET-04 — output size (file count + LOC)** - `7d00377` (feat)
3. **Task 3: auto-invoke scorer in run.sh after meta.json write** - `b42facd` (feat)

**Plan metadata:** docs(03-02): complete plan (this commit)

## Files Created/Modified
- `benchmark/score.py` - Added `extract_steps(run_dir, meta)` (MET-03, tool-aware) and `measure_output(run_dir)` (MET-04, file/LOC count with harness+cache exclusions); both wired into `score_run` and surfaced in the `main()` one-line summary. New `re` import, `_ANSI_RE`/`_OH_MSGS_RE`/`_HARNESS_FILES` module constants.
- `benchmark/run.sh` - New section 10b auto-scores the run dir after meta.json is written (best-effort, failure-isolated); section 11 prints passed/duration/steps/files+loc read back from meta.json. Phase 2 behavior unchanged.

## Decisions Made
- `step_method` is always recorded alongside `steps` because units differ per tool (codex tool-call invocations vs openhands agent messages) — Phase 4 reporting must surface it, not just the raw number.
- codex step count = standalone `exec` marker lines (`line.strip() == "exec"`); openhands = `Number of agent messages: N` after ANSI strip. Heuristic kept deliberately simple and approximate per phase guidance — no universal parser.
- Output-size exclusions are exact names (`transcript.log`, `meta.json`), `__pycache__/` (pruned during `os.walk`), and `.pyc`. `os.walk` recurses so future multi-file L2/L3 solutions in subdirs are counted.
- LOC counts newlines via `splitlines()` reading utf-8 with `errors="ignore"`; unreadable/binary files count as 1 file / 0 lines (best-effort).
- Scorer hook in run.sh is purely additive and failure-isolated under `set -euo pipefail` — the run record already exists, scoring only enriches it.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None. The `__pycache__/` left in each run dir by the L1 judge (from Plan 01) is correctly excluded by the MET-04 walk, so files=1 holds.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 3 is complete: every run now carries pass/fail, duration, steps (+method), and size in one structured meta.json, produced automatically by run.sh.
- **Carry-forward for Phase 4:** `steps` units differ per tool — the report must surface `step_method`, not just the raw number, to avoid comparing codex tool-calls against openhands agent-messages as if identical.
- `benchmark/.runs/` is gitignored, so the sample dirs' extended meta.json are local only; score.py + run.sh are the committed, re-runnable artifacts.
- No blockers.

---
*Phase: 03-metric-collection*
*Completed: 2026-06-26*
