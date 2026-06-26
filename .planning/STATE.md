# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-26)

**Core value:** 같은 과제를 두 도구에 동일 조건으로 돌려, 재현·검증 가능한 형태로 능력·시간을 비교 기록한다.
**Current focus:** Planning next milestone (v1.0 shipped)

## Current Position

Phase: — (v1.0 complete; next milestone not yet defined)
Plan: —
Status: Ready for /gsd:new-milestone
Last activity: 2026-06-26 — v1.0 milestone complete (5 phases, 10 plans, 18/18 requirements)

Progress: [██████████] v1.0 100%

## Accumulated Context

### Decisions

Full log in PROJECT.md Key Decisions. v1.0 decisions all marked ✓ Good.

### Pending Todos

None.

### Blockers/Concerns (carried forward)

- Single mlx backend → tools must run serially, never concurrently (enforced by run.sh mkdir-mutex).
- codex exec hangs without `< /dev/null` in background/pipe (handled in run.sh).
- OpenHands: feed prompt via inline `--task`, never `--file` (the `--file` workdir anchor leaks output
  to the canonical task dir — fixed in v1.0). Workspace pinned via OPENHANDS_WORK_DIR.
- steps units differ per tool (codex exec-blocks vs openhands agent-messages) — never compare raw counts.
- Benchmark results vary run-to-run (LLM nondeterminism); RESULTS.md is the durable record (.runs/ gitignored).

## Session Continuity

Last session: 2026-06-26
Stopped at: v1.0 milestone archived (milestones/v1.0-*). ROADMAP.md + REQUIREMENTS.md + phases/ removed
(archived). PROJECT.md evolved (requirements → Validated). Tag milestone-v1.0.
Resume file: None
Next: `/gsd:new-milestone` to define the next milestone.
