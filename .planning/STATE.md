# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-26)

**Core value:** 같은 과제를 두 도구에 동일 조건으로 돌려, 재현·검증 가능한 형태로 능력·시간을 비교 기록한다.
**Current focus:** Phase 1 — Fixed Tasks

## Current Position

Phase: 1 of 5 (Fixed Tasks)
Plan: 1 of 2 in current phase
Status: In progress
Last activity: 2026-06-26 — Completed 01-01-PLAN.md (froze L1/L2/L3 prompts + pass-criterion README)

Progress: [█░░░░░░░░░] 10%

## Performance Metrics

**Velocity:**
- Total plans completed: 1
- Average duration: ~7 min
- Total execution time: 0.1 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 — Fixed Tasks | 1/2 | ~7 min | ~7 min |

**Recent Trend:**
- Last 5 plans: 01-01 (~7 min)
- Trend: -

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

### Pending Todos

[From .planning/todos/pending/ — ideas captured during sessions]

None yet.

### Blockers/Concerns

[Issues that affect future work]

- codex exec hangs without `< /dev/null` in background/pipe — must be handled in runner (Phase 2)
- Single mlx backend → tools must run serially, never concurrently (Phase 2)

## Session Continuity

Last session: 2026-06-26
Stopped at: Completed 01-01-PLAN.md — benchmark/README.md + 3 frozen PROMPT.md (L1/L2/L3)
Resume file: None
Next: 01-02-PLAN.md — stdlib-only independent judge per level + reference solutions
