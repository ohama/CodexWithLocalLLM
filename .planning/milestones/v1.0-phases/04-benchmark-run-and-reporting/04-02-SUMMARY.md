---
phase: 04-benchmark-run-and-reporting
plan: 02
subsystem: testing
tags: [reporting, benchmark, markdown, results, codex, openhands, qwen-122b]

# Dependency graph
requires:
  - phase: 04-benchmark-run-and-reporting (plan 01)
    provides: aggregated 6-cell metrics (results.json with passed/duration_seconds/steps/step_method/files/loc per cell)
  - phase: 03-metric-collection
    provides: score.py metric definitions (MET-01..04) and tool-aware step_method semantics
provides:
  - benchmark/report.py — re-runnable, idempotent results.json → RESULTS.md generator (stdlib-only)
  - benchmark/RESULTS.md — durable committed comparison report (matrix table + transcript excerpts + per-level diffs + honesty note)
affects: [final-reporting, project-wrap-up, any-future-matrix-reruns]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Report generator is pure formatting over results.json (zero LLM time, no agents/judges re-run)"
    - "Durable self-contained report: transcript excerpts baked into committed markdown because .runs/ is gitignored"
    - "step_method surfaced beside every step count; raw step counts never compared as identical units"

key-files:
  created:
    - benchmark/report.py
    - benchmark/RESULTS.md
  modified: []

key-decisions:
  - "RESULTS.md is self-contained: ANSI-stripped head+tail transcript excerpts baked in since .runs/ is gitignored (transcripts never committed)"
  - "step_method printed in the table cell, the reading note, AND each per-level process line — units (codex exec-blocks vs openhands agent-messages) explicitly flagged non-comparable"
  - "Scoring honesty note baked into report.py as static narrative: openhands L2/L3 re-run after --file isolation-leak fix; codex L3 reported as a genuine truncation FAIL"
  - "report.py is best-effort: missing fields render as em-dash, missing transcript notes 'unavailable', never crashes on a partial cell"

patterns-established:
  - "Auto-discover latest matrix via sorted(glob(matrix-*/results.json))[-1] with argv override (file or dir)"
  - "Idempotent generator: same results.json → byte-identical RESULTS.md"

# Metrics
duration: ~6min
completed: 2026-06-26
---

# Phase 4 Plan 2: Comparison Report Generation Summary

**benchmark/report.py renders the aggregated 6-cell matrix into a durable, self-contained benchmark/RESULTS.md — tool×level table (success+time+steps[step_method]+size), baked-in transcript excerpts, per-level codex-vs-openhands diffs, and an explicit scoring-honesty note.**

## Performance

- **Duration:** ~6 min (pure formatting; zero new LLM time)
- **Completed:** 2026-06-26
- **Tasks:** 2
- **Files modified:** 2 (both created)

## Accomplishments
- `benchmark/report.py`: stdlib-only generator that reads results.json (argv path/dir or latest matrix) and emits RESULTS.md; idempotent and re-runnable with no agent/judge re-execution.
- `benchmark/RESULTS.md`: the durable Phase 4 deliverable — 6-cell matrix, per-level difference summaries, transcript references with ANSI-stripped excerpts, and the scoring honesty note.
- step_method surfaced in three places (table cell, reading-the-numbers note, per-level process line) with an explicit "units differ — not directly comparable" caveat (REP-02 carry-forward from Phase 3 honored).
- codex L3 genuine failure (truncated after `mkdir kvstore`, 0f/0loc) preserved as a real FAIL with corroborating transcript excerpt; openhands L2/L3 isolation-leak re-run disclosed, not hidden.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write benchmark/report.py** - `4a090ae` (feat)
2. **Task 2: Generate benchmark/RESULTS.md** - `f6670f4` (feat)

**Plan metadata:** see docs(04-02) commit below.

## Files Created/Modified
- `benchmark/report.py` - results.json → RESULTS.md generator (input resolution, matrix table, reading/honesty notes, per-level diffs, transcript excerpts)
- `benchmark/RESULTS.md` - committed comparison report (durable evidence; survives gitignored .runs/)

## Final matrix table (as rendered in RESULTS.md)

| Tool | Level | Success | Time | Steps (step_method) | Size (files / loc) |
|------|-------|---------|------|---------------------|--------------------|
| codex | l1-fib | PASS | 26s | 2 (codex:count of 'exec' blocks) | 1f / 31loc |
| openhands | l1-fib | PASS | 49s | 4 (openhands:Number of agent messages) | 1f / 31loc |
| codex | l2-wordstat | PASS | 98s | 10 (codex:count of 'exec' blocks) | 4f / 148loc |
| openhands | l2-wordstat | PASS | 145s | 16 (openhands:Number of agent messages) | 4f / 222loc |
| codex | l3-kvstore | FAIL | 14s | 2 (codex:count of 'exec' blocks) | 0f / 0loc |
| openhands | l3-kvstore | PASS | 147s | 15 (openhands:Number of agent messages) | 9f / 362loc |

## Key per-level findings
- **l1-fib:** both PASS, identical output (1f/31loc). codex faster (26s vs 49s).
- **l2-wordstat:** both PASS. codex faster (98s vs 145s) and leaner (148 vs 222 loc) for the same 4 files.
- **l3-kvstore:** split verdict — codex FAIL (genuine truncation, empty package) vs openhands PASS (9f/362loc, 147s). The headline divergence of the matrix.
- Process counts deliberately not compared as equal units (codex exec-blocks vs openhands agent-messages).

## Decisions Made
- Self-contained report with baked-in excerpts (rationale: .runs/ is gitignored, so the committed report must itself carry the evidence).
- Honesty note authored as static narrative in report.py so every regeneration reproduces the disclosure verbatim.
- Best-effort rendering (em-dash for missing fields, "transcript unavailable" note) so the generator never crashes on a partial/errored cell.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
- Plan's @-referenced `04-01-SUMMARY.md` is not present in the phase dir, but the orchestrator supplied results.json directly and report.py consumes results.json (not the summary), so this did not block execution.
- openhands transcripts contain ANSI escape codes; report.py strips them so excerpts render cleanly in markdown.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- REP-02 (matrix table with success+time) and REP-03 (transcript refs/excerpts + per-level diffs, durable) satisfied.
- RESULTS.md is committed and self-contained; safe even though .runs/ remains gitignored.
- Re-run `python3 benchmark/report.py` after any future matrix to regenerate the report deterministically.

---
*Phase: 04-benchmark-run-and-reporting*
*Completed: 2026-06-26*
