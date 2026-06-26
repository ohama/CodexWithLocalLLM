---
phase: 02-equal-conditions-runner
plan: 03
subsystem: infra
tags: [bash, runner, codex-exec, openhands-headless, litellm, qwen-122b, smoke-test, isolation]

# Dependency graph
requires:
  - phase: 02-equal-conditions-runner
    provides: run.sh wired with real codex/openhands invocations (transcript.log + model-confirming meta.json, workspace pinned via OPENHANDS_WORK_DIR)
  - phase: 01-fixed-tasks
    provides: frozen tasks/l1-fib PROMPT.md fed verbatim to both tools
provides:
  - live-confirmed equal-conditions runner — RUN-01..RUN-05 verified on the real qwen-122b backend
  - two reference run dirs under benchmark/.runs/ (one per tool) with solution + transcript.log + meta.json, ready as Phase 3 inputs
  - confirmation that OpenHands' OPENHANDS_WORK_DIR pin lands the solution INSIDE the isolated run dir (no leakage to repo root or ~/.openhands/workspace)
affects: [Phase 3 (metric measurement reads meta.json + transcript.log), Phase 4 (scoring)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "one real L1 smoke per tool, run serially under the mkdir-mutex lock, is the live proof of RUN-01..05"
    - "isolation confirmed by absence of solution files in repo root and ~/.openhands/workspace, presence in $RUN_DIR"

key-files:
  created:
    - benchmark/.runs/codex-l1-fib-20260626-021103/ (fib.py + transcript.log + meta.json; runtime artifact, gitignored)
    - benchmark/.runs/openhands-l1-fib-20260626-021227/ (fib.py + transcript.log + meta.json; runtime artifact, gitignored)
  modified: []

key-decisions:
  - "Live confirmation only — no judging/metrics in Phase 2 (deferred to Phase 3); the smoke run proves the runner mechanics, not task correctness (though both happened to PASS the hidden judge)"
  - "Empty plan-01 stub run dirs removed (only dirs with no meta.json/transcript.log); the two real run dirs left in place as Phase 3 reference inputs"

patterns-established:
  - "Pattern: equal-conditions live smoke = run both tools serially at L1, then assert each left an isolated dir with non-empty transcript.log + qwen-122b meta.json + a solution file"

# Metrics
duration: ~8min
completed: 2026-06-26
---

# Phase 2 Plan 03: Live Smoke and Verify Summary

**Both tools driven through benchmark/run.sh at L1 on the real qwen-122b backend, serially under the lock — each left an isolated run dir with a non-empty transcript.log, a meta.json naming its qwen-122b model @ :4000, and a fib.py solution inside the dir; no file leaked to the repo root or ~/.openhands/workspace, confirming RUN-01..RUN-05 live and closing Phase 2.**

## Performance

- **Duration:** ~8 min
- **Tasks:** 2 (1 auto + 1 human-verify checkpoint, approved)
- **Files modified:** 0 (live runs only; benchmark/run.sh unchanged from Plan 02)

## Accomplishments

- **RUN-01 (one command per tool/level):** `bash benchmark/run.sh codex l1` and `bash benchmark/run.sh openhands l1` each completed end-to-end from a single command, non-interactively.
- **RUN-02 (isolation):** Each run wrote its `fib.py` solution INSIDE its own run dir. The OpenHands `OPENHANDS_WORK_DIR` pin (from Plan 02) lands the solution in `$RUN_DIR` by default — confirmed, not fixed. No `fib.py` leaked to the repo root or `~/.openhands/workspace`. The two run dirs are separate with no cross-contamination.
- **RUN-03 (same model, confirmable offline):** Both `meta.json` files name a qwen-122b-family model — codex `qwen-122b-codex`, openhands `openai/qwen-122b` — with `base_url` `http://localhost:4000/v1` (LiteLLM :4000).
- **RUN-04 (non-interactive):** Neither run hung on stdin nor blocked on an interactive prompt; both returned on their own (codex `< /dev/null`, openhands `--headless`). Both recorded `exit_code: 0`.
- **RUN-05 (serial on single backend):** Runs were serial under the mkdir-mutex lock — codex finished at `2026-06-26T02:11:46Z` before openhands started at `2026-06-26T02:12:27Z`.

## Live Evidence

**codex run** — `benchmark/.runs/codex-l1-fib-20260626-021103/`
- `transcript.log` (3458 bytes, non-empty)
- `meta.json`: model `qwen-122b-codex`, base_url `http://localhost:4000/v1`, exit_code `0`, started `02:11:03Z` / finished `02:11:46Z`
- `fib.py` (655 bytes) present in the run dir

**openhands run** — `benchmark/.runs/openhands-l1-fib-20260626-021227/`
- `transcript.log` (3636 bytes, non-empty)
- `meta.json`: model `openai/qwen-122b`, base_url `http://localhost:4000/v1`, exit_code `0`, started `02:12:27Z` / finished `02:13:16Z`
- `fib.py` (655 bytes) present in the run dir (isolation confirmed)

Independently re-verified by the orchestrator: the hidden L1 judge returns PASS for both solutions; no `fib.py` in the repo root or `~/.openhands/workspace`; serial ordering holds; both models are qwen-122b family. (Judging is recorded as evidence only — formal metrics are Phase 3.)

## RUN-01..RUN-05 Status

| Req | Description | Status |
|-----|-------------|--------|
| RUN-01 | One command per (tool, level) | Confirmed live (both tools) |
| RUN-02 | Isolated run dirs, no cross-contamination / leakage | Confirmed live (human-verified for openhands) |
| RUN-03 | Both tools on qwen-122b, confirmable from meta.json | Confirmed live (both meta.json) |
| RUN-04 | Non-interactive (no hang / no interactive block) | Confirmed live (both exit 0, returned on own) |
| RUN-05 | Serial execution on the single backend | Confirmed live (timestamps non-overlapping) |

## Task Commits

No source code commits — this plan spends model time and produces runtime artifacts (gitignored), not code changes.

1. **Task 1: Real codex L1 smoke run + structural assertions** — no commit (live run; artifacts under `benchmark/.runs/`, gitignored)
2. **Task 2: Human-verify openhands isolation** — checkpoint APPROVED (live run; artifacts gitignored)

**Plan metadata:** `docs(02-03)` commit follows this summary (only `.planning/` files staged).

## Files Created/Modified

- No tracked files modified. Two runtime run dirs created under `benchmark/.runs/` (gitignored).
- Cleanup: removed four empty plan-01 stub dirs (`codex-l1-fib-20260626-020043`, `-020043-21357`, `-020125`, `-020126`) — each contained no `meta.json`/`transcript.log`. The two real run dirs were left in place as Phase 3 reference inputs.

## Decisions Made

- **No judging/metrics in this plan.** Phase 2 only proves the runner leaves clean isolated dirs + raw logs; correctness scoring is Phase 3. (The judges happened to PASS, recorded as confidence-building evidence.)
- **Kept the two real run dirs, removed empty stubs.** Only dirs with no artifacts were removed, so nothing of value was lost; the real codex/openhands dirs remain as ready-made Phase 3 inputs.

## Deviations from Plan

None - plan executed exactly as written. The OpenHands isolation was a confirmation point (per Plan 02's `OPENHANDS_WORK_DIR` pin) and required no fix — the solution landed in `$RUN_DIR` by default.

## Authentication Gates

None — the local LiteLLM gateway at :4000 uses `LITELLM_API_KEY=dummy`; no interactive login was required during either live run.

## Issues Encountered

None. Both tools ran clean on the first live attempt; no hang, no interactive block, no leakage.

## User Setup Required

None - the LiteLLM/mlx qwen-122b backend on :4000 was already up (checked by the runner preflight).

## Next Phase Readiness

- **Phase 2 is complete.** The equal-conditions runner is live-proven: `benchmark/run.sh <tool> <level>` produces an isolated dir per run with `transcript.log` + `meta.json` (qwen-122b @ :4000) and the agent's solution inside it, serially on the single backend.
- The two L1 run dirs are stable reference inputs for Phase 3 (metric measurement reads `meta.json` + `transcript.log`).
- `meta.json` schema (tool, level, model, base_url, prompt_file, run_dir, started_at, finished_at, exit_code, transcript) is confirmed stable across both tools.
- No blockers carried into Phase 3.

---
*Phase: 02-equal-conditions-runner*
*Completed: 2026-06-26*
