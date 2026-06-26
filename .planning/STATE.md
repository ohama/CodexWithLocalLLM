# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-26)

**Core value:** 같은 과제를 두 도구에 동일 조건으로 돌려, 재현·검증 가능한 형태로 능력·시간을 비교 기록한다.
**Current focus:** Phase 1 — Fixed Tasks

## Current Position

Phase: 1 of 5 (Fixed Tasks)
Plan: 2 of 2 in current phase
Status: Phase complete
Last activity: 2026-06-26 — Completed 01-02-PLAN.md (3 stdlib-only judges + references, validated both ways)

Progress: [██░░░░░░░░] 20%

## Performance Metrics

**Velocity:**
- Total plans completed: 2
- Average duration: ~8 min
- Total execution time: 0.3 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 — Fixed Tasks | 2/2 | ~16 min | ~8 min |

**Recent Trend:**
- Last 5 plans: 01-01 (~7 min), 01-02 (~9 min)
- Trend: steady

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- codex+openhands only (hermes excluded) — scope focus
- Single model qwen-122b for both tools — isolate tool differences
- Reuse validated L1/L2/L3 tasks (fib / wordstat / KV) — fast start
- Serial measurement — single mlx backend contention avoidance
- Prompts never reference the hidden judge/test.py — trust decided by independent test only (01-01)
- L3 persistence keyed on env KVSTORE_PATH (default ./kvstore.db) for hermetic runs (01-01)
- Per-command exit codes pinned (get-miss=1, delete idempotent=0) so a black-box judge can key on them (01-01)
- Judges read solution_dir from argv[1] (default cwd) so Phase 2 runner points them at any tool output unchanged (01-02)
- L1 judge uses in-process importlib import; L2/L3 use subprocess black-box (only entry-file names are fixed) (01-02)
- stdlib-only verified via portable import-line scan, not Perl negative-lookahead grep (macOS ERE lacks lookahead) (01-02)

### Pending Todos

[From .planning/todos/pending/ — ideas captured during sessions]

None yet.

### Blockers/Concerns

[Issues that affect future work]

- codex exec hangs without `< /dev/null` in background/pipe — must be handled in runner (Phase 2)
- Single mlx backend → tools must run serially, never concurrently (Phase 2)

## Session Continuity

Last session: 2026-06-26
Stopped at: Completed 01-02-PLAN.md — 3 stdlib-only judges (tasks/l{1,2,3}-*/test.py) + validated references; Phase 1 complete
Resume file: None
Next: Phase 2 — runner that drives Codex CLI + OpenHands on the frozen prompts and scores output with these judges
