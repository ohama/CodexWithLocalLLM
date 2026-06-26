# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-26)

**Core value:** 같은 과제를 두 도구에 동일 조건으로 돌려, 재현·검증 가능한 형태로 능력·시간을 비교 기록한다.
**Current focus:** Phase 4 — Benchmark Run & Reporting

## Current Position

Phase: 4 of 5 (Benchmark Run & Reporting)
Plan: 2 of 2 in current phase
Status: Phase complete
Last activity: 2026-06-26 — Completed 04-02-PLAN.md (benchmark/report.py: stdlib-only results.json→RESULTS.md generator, idempotent, zero LLM time; benchmark/RESULTS.md: durable self-contained report — 6-cell tool×level table [success+time+steps(step_method)+size], baked-in ANSI-stripped transcript excerpts, per-level codex-vs-openhands diffs, scoring honesty note [openhands L2/L3 re-run after --file isolation-leak fix; codex L3 genuine truncation FAIL]; step_method surfaced, raw step counts flagged non-comparable)

Progress: [█████████░] 90%

## Performance Metrics

**Velocity:**
- Total plans completed: 7
- Average duration: ~9 min
- Total execution time: 1.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 — Fixed Tasks | 2/2 | ~16 min | ~8 min |
| 2 — Equal-Conditions Runner | 3/3 | ~26 min | ~9 min |
| 3 — Metric Collection | 2/2 | ~20 min | ~10 min |
| 4 — Benchmark Run & Reporting | 2/2 | (01 LLM-time matrix run + 04-02 ~6 min formatting) | — |

**Recent Trend:**
- Last 5 plans: 02-03 (~8 min), 03-01 (~12 min), 03-02 (~8 min), 04-01 (matrix run), 04-02 (~6 min)
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
- MET-03 step count is TOOL-AWARE and always paired with step_method: codex = standalone 'exec' marker lines, openhands = 'Number of agent messages: N' after ANSI strip (units differ per tool — never compare raw counts) (03-02)
- MET-04 output size excludes transcript.log, meta.json, __pycache__/, and .pyc; os.walk recurses so multi-file L2/L3 solutions in subdirs are counted; loc = splitlines on utf-8 errors=ignore (03-02)
- score.py step/size extraction is best-effort: missing transcript→steps=0/transcript-missing, missing openhands marker→0/summary-not-found, unreadable file→1 file/0 loc; never crashes (03-02)
- run.sh auto-invokes score.py after meta.json write (section 10b) guarded by set +e/capture/set -e — scorer failure warns but never aborts/masks the run; purely additive to Phase 2 (03-02)
- benchmark/RESULTS.md is the durable record: transcript excerpts (ANSI-stripped head+tail) baked into the committed report because .runs/ is gitignored — report must be self-contained (04-02)
- report.py is pure formatting over results.json (no agents/judges re-run, zero LLM time), idempotent: same results.json → byte-identical RESULTS.md (04-02)
- Scoring honesty disclosed in-report, not hidden: openhands L2/L3 mis-scored FAIL by a --file isolation leak (workdir anchored to canonical task dir), re-run with inline --task → PASS; codex L3 is a GENUINE truncation FAIL (only ran `mkdir kvstore`, 0f/0loc) (04-02)
- step_method surfaced in table cell + reading note + per-level process line; codex exec-blocks vs openhands agent-messages flagged non-comparable units throughout (04-02)

### Pending Todos

[From .planning/todos/pending/ — ideas captured during sessions]

None yet.

### Blockers/Concerns

[Issues that affect future work]

- Phase 4 report MUST surface step_method, not just the raw steps number — codex tool-calls and openhands agent-messages are different units and cannot be compared directly (03-02)
- codex exec hangs without `< /dev/null` in background/pipe — handled in runner (run_codex uses `< /dev/null`) (02-02)
- Single mlx backend → tools must run serially, never concurrently (enforced by mkdir-mutex lock) (Phase 2)
- RESOLVED (02-03): openhands `--headless --always-approve --exit-without-confirmation` ran clean at runtime, no conflict, exit 0, no interactive block.
- RESOLVED (02-03): openhands solution confirmed landing in $RUN_DIR via OPENHANDS_WORK_DIR pin (live human-verify approved).

## Session Continuity

Last session: 2026-06-26
Stopped at: Completed 04-02-PLAN.md — created benchmark/report.py (stdlib-only results.json→RESULTS.md generator, auto-discovers latest matrix or argv path, idempotent, zero LLM time) and generated benchmark/RESULTS.md (durable committed report: 6-cell tool×level table with success+time+steps[step_method]+size, ANSI-stripped transcript excerpts baked in since .runs/ is gitignored, per-level codex-vs-openhands diffs, scoring honesty note). Verified: py_compile, all content assertions pass, byte-identical on re-run, RESULTS.md not gitignored. Phase 4 complete.
Resume file: None
Next: Phase 5 (final / project wrap-up). Carry-forward: RESULTS.md is the durable deliverable; re-run `python3 benchmark/report.py` after any future matrix.
