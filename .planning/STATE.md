# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-26)

**Core value:** 같은 과제를 두 도구에 동일 조건으로 돌려, 재현·검증 가능한 형태로 능력·시간을 비교 기록한다.
**Current focus:** Phase 2 — Equal-Conditions Runner

## Current Position

Phase: 2 of 5 (Equal-Conditions Runner)
Plan: 2 of 3 in current phase
Status: In progress
Last activity: 2026-06-26 — Completed 02-02-PLAN.md (wired real codex/openhands invocations: codex exec < /dev/null, openhands --headless with workspace pinned to RUN_DIR; transcript.log + model-confirming meta.json per run)

Progress: [████░░░░░░] 36%

## Performance Metrics

**Velocity:**
- Total plans completed: 4
- Average duration: ~9 min
- Total execution time: 0.6 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 — Fixed Tasks | 2/2 | ~16 min | ~8 min |
| 2 — Equal-Conditions Runner | 2/3 | ~18 min | ~9 min |

**Recent Trend:**
- Last 5 plans: 01-01 (~7 min), 01-02 (~9 min), 02-01 (~6 min), 02-02 (~12 min)
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
- Runner serial lock = mkdir-based atomic mutex (.runs/.lock); macOS base has no flock (02-01)
- Serial lock default = abort with exit 3, not block-and-wait — deterministic/testable (02-01)
- EXIT-trap rmdir installed only AFTER lock acquire so a losing run never deletes the holder's lock (02-01)
- Arg/level/prompt validation runs before lock acquire so bad input never seizes the backend lock (02-01)
- run.sh self-contained: gateway-curl + run-dir idioms copied inline, examples/codex-tests/common.sh NOT sourced (decoupling) (02-01)
- OpenHands workspace pinned via OPENHANDS_WORK_DIR (get_work_dir mechanism in CLI 1.16.0/SDK 1.21.0), NOT SANDBOX_VOLUMES/WORKSPACE_BASE which belong to the older docker app (02-02)
- --override-with-envs repurposed to pin the LLM model (LLM_MODEL) from the runner — it only overrides LLM_* in this version and requires them; strengthens RUN-03 against config drift (02-02)
- Tool exit captured via ${PIPESTATUS[0]} under set +e; nonzero agent exit is a valid recorded run (never abort), meta.json written regardless (02-02)
- meta.json model resolved from each tool's own config (codex config.toml / openhands agent_settings.json) so same-model criterion is offline-confirmable (02-02)

### Pending Todos

[From .planning/todos/pending/ — ideas captured during sessions]

None yet.

### Blockers/Concerns

[Issues that affect future work]

- codex exec hangs without `< /dev/null` in background/pipe — handled in runner (run_codex uses `< /dev/null`) (02-02)
- Single mlx backend → tools must run serially, never concurrently (enforced by mkdir-mutex lock) (Phase 2)
- Plan 03 must verify at runtime that openhands `--always-approve --exit-without-confirmation` don't conflict with `--headless` (could not be exercised without model time); `--headless` alone already auto-approves if they need trimming (02-02)
- Plan 03 human-verify should CONFIRM openhands solution lands in $RUN_DIR (OPENHANDS_WORK_DIR pin), not fix it (02-02)

## Session Continuity

Last session: 2026-06-26
Stopped at: Completed 02-02-PLAN.md — wired real codex/openhands invocations into run.sh (codex exec < /dev/null; openhands --headless, workspace pinned to RUN_DIR via OPENHANDS_WORK_DIR, model pinned via --override-with-envs); per-run transcript.log + model-confirming meta.json. Structurally verified (no model time).
Resume file: None
Next: Phase 2 Plan 03 — single real smoke run + OpenHands isolation human-verify; confirm transcript.log/meta.json populate and the solution lands in $RUN_DIR
