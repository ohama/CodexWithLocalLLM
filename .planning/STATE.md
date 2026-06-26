# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-26)

**Core value:** 같은 과제를 두 도구에 동일 조건으로 돌려, 재현·검증 가능한 형태로 능력·시간을 비교 기록한다.
**Current focus:** Phase 3 — Metric Collection

## Current Position

Phase: 3 of 5 (Metric Collection)
Plan: 1 of (TBD) in current phase
Status: In progress
Last activity: 2026-06-26 — Completed 03-01-PLAN.md (benchmark/score.py: MET-01 independent pass/fail via judge re-run + MET-02 duration_seconds, extends meta.json in place idempotently; verified on both sample run dirs — codex pass/0/43s, openhands pass/0/49s; zero new LLM time)

Progress: [██████░░░░] 55%

## Performance Metrics

**Velocity:**
- Total plans completed: 6
- Average duration: ~9 min
- Total execution time: 0.9 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 — Fixed Tasks | 2/2 | ~16 min | ~8 min |
| 2 — Equal-Conditions Runner | 3/3 | ~26 min | ~9 min |
| 3 — Metric Collection | 1/? | ~12 min | ~12 min |

**Recent Trend:**
- Last 5 plans: 02-01 (~6 min), 02-02 (~12 min), 02-03 (~8 min), 03-01 (~12 min)
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
- OpenHands workspace pinned via OPENHANDS_WORK_DIR (not --override-with-envs, which only pins the LLM) — live-confirmed in 02-03: openhands fib.py lands inside $RUN_DIR, no leakage to repo root or ~/.openhands/workspace (02-03)
- Runner leaves transcript.log + meta.json per run dir as the stable Phase 3 contract; Phase 2 does no judging/metrics — correctness scoring is deferred to Phase 3 (02-03)
- RUN-01..05 confirmed LIVE on real qwen-122b backend: one command/tool, isolated dirs, both qwen-122b @ :4000, non-interactive (exit 0), serial under lock (02-03)
- MET-01 correctness decided ONLY by judge process exit; transcript/self-report/meta exit_code never consulted (03-01)
- meta['level'] is the full tasks/ subdir name → direct judge path tasks/<level>/test.py, no mapping table (03-01)
- score.py is best-effort: missing judge → passed=false/judge_exit=null/judge_note; bad timestamps → duration_seconds=null; never crashes (03-01)
- meta.json extended in place via load→merge→dump, idempotent (same inputs → identical metric values) (03-01)

### Pending Todos

[From .planning/todos/pending/ — ideas captured during sessions]

None yet.

### Blockers/Concerns

[Issues that affect future work]

- codex exec hangs without `< /dev/null` in background/pipe — handled in runner (run_codex uses `< /dev/null`) (02-02)
- Single mlx backend → tools must run serially, never concurrently (enforced by mkdir-mutex lock) (Phase 2)
- RESOLVED (02-03): openhands `--headless --always-approve --exit-without-confirmation` ran clean at runtime, no conflict, exit 0, no interactive block.
- RESOLVED (02-03): openhands solution confirmed landing in $RUN_DIR via OPENHANDS_WORK_DIR pin (live human-verify approved).

## Session Continuity

Last session: 2026-06-26
Stopped at: Completed 03-01-PLAN.md — created benchmark/score.py (stdlib-only). MET-01: pass/fail by re-running tasks/<level>/test.py as a separate process against produced files (passed/judge_exit; self-report ignored). MET-02: duration_seconds from meta timestamps. meta.json extended in place, original keys preserved, idempotent. Verified on both sample run dirs with zero new LLM time: codex pass/0/43s, openhands pass/0/49s.
Resume file: None
Next: Phase 3 Plan 02 — extend score.py with step-count and output-size metrics (same load→merge→dump pattern; exclude __pycache__ from file counting).
