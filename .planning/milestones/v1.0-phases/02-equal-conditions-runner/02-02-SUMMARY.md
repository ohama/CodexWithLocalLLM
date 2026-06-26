---
phase: 02-equal-conditions-runner
plan: 02
subsystem: infra
tags: [bash, runner, codex-exec, openhands-headless, litellm, qwen-122b, transcript, meta-json]

# Dependency graph
requires:
  - phase: 02-equal-conditions-runner
    provides: run.sh skeleton (arg/level validation, isolated run-dir, mkdir-mutex serial lock, gateway preflight, labeled run_codex/run_openhands stubs)
  - phase: 01-fixed-tasks
    provides: frozen tasks/l{1,2,3}-* PROMPT.md fed verbatim to both tools
provides:
  - real non-interactive codex invocation (codex exec ... < /dev/null) writing into the isolated run dir
  - real non-interactive openhands invocation (--headless, workspace pinned to RUN_DIR via OPENHANDS_WORK_DIR, model pinned via --override-with-envs)
  - per-run transcript.log (tee of combined stdout+stderr) for Phase 3/4 consumption
  - per-run meta.json naming the qwen-122b model, base_url, exit_code, and record-only timestamps (same-model criterion confirmable offline)
affects: [02-03 (real smoke run + openhands isolation human-verify), Phase 3 (metric measurement reads meta.json + transcript.log), Phase 4 (scoring)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "set +e around the tool pipeline, read ${PIPESTATUS[0]} for the real agent exit (tee masks it under pipefail)"
    - "nonzero agent exit is a valid recorded run — never abort the script; record the code and finalize"
    - "model resolved from each tool's own config (grep/sed toml, python3 json) as the single source of truth"
    - "OpenHands workspace pinned via OPENHANDS_WORK_DIR (get_work_dir() mechanism), LLM pinned via --override-with-envs + LLM_* env"

key-files:
  created: []
  modified:
    - benchmark/run.sh

key-decisions:
  - "Workspace pin uses OPENHANDS_WORK_DIR, not SANDBOX_VOLUMES/WORKSPACE_BASE — the installed OpenHands (CLI 1.16.0 / SDK 1.21.0) resolves its workspace via get_work_dir()=os.environ.get('OPENHANDS_WORK_DIR', os.getcwd())"
  - "--override-with-envs repurposed to pin the LLM model from the runner (it only overrides LLM_API_KEY/LLM_BASE_URL/LLM_MODEL in this version, and requires them when enabled) — strengthens RUN-03 same-model guarantee against config drift"
  - "meta.json exit_code is numeric (not string); meta written even on nonzero agent exit"
  - "Model resolved from each tool's own config (codex config.toml / openhands agent_settings.json) so meta.json is authoritative without rerunning"

patterns-established:
  - "tool pipeline pattern: set +e; <tool> ... < /dev/null 2>&1 | tee transcript.log; EXIT=${PIPESTATUS[0]}; set -e"
  - "same-model assertion: warn (don't abort) if resolved model is not in the qwen-122b family"

# Metrics
duration: ~12min
completed: 2026-06-26
---

# Phase 2 Plan 02: Wire Real Same-Model Tool Invocations Summary

**benchmark/run.sh now drives codex (`codex exec ... < /dev/null`) and openhands (`--headless`, workspace pinned to the isolated run dir, LLM pinned to qwen-122b) non-interactively against LiteLLM :4000, feeds the frozen PROMPT.md verbatim to both, and leaves a transcript.log + a model-confirming meta.json behind — all structurally verified with ~zero model time (the single real smoke is Plan 03).**

## Performance

- **Duration:** ~12 min
- **Tasks:** 3 (+1 formatting fix)
- **Files modified:** 1 (benchmark/run.sh)

## Accomplishments

- RUN-04 (codex): `run_codex` cd's into the isolated RUN_DIR and runs `LITELLM_API_KEY=dummy codex exec --skip-git-repo-check --sandbox workspace-write "$PROMPT" < /dev/null`, capturing the real exit via `${PIPESTATUS[0]}`. The mandatory `< /dev/null` prevents the known stdin hang.
- RUN-04 (openhands): `run_openhands` runs `openhands --file "$PROMPT_FILE" --headless --always-approve --exit-without-confirmation --override-with-envs < /dev/null`, non-interactive with no human confirmation block.
- RUN-02 (isolation, by default): OpenHands workspace pinned to `$RUN_DIR` via `OPENHANDS_WORK_DIR` on every run (the actual mechanism in the installed version), so the solution always lands in the isolated dir.
- RUN-03 (same model, confirmable): model resolved from each tool's own config (codex `qwen-122b-codex`, openhands `openai/qwen-122b`), recorded in `meta.json`, and — for openhands — enforced from the runner via `--override-with-envs` + `LLM_MODEL`. A same-model assertion warns if the resolved model leaves the qwen-122b family.
- Verbatim prompt: both tools receive the identical PROMPT.md text (codex via `"$PROMPT"`, openhands via `--file "$PROMPT_FILE"`), no tool-specific additions.
- Every run leaves `transcript.log` (tee of combined stdout+stderr) and `meta.json` (tool, level, model, base_url, prompt_file, run_dir, started_at/finished_at, numeric exit_code, transcript) in its run dir. meta.json is written even on a nonzero agent exit.
- RUN-05 (real-invocation half): the live invocation runs under the Plan 01 mkdir-mutex serial lock.

## Task Commits

Each task was committed atomically (only benchmark/run.sh staged):

1. **Task 1: Implement run_codex** — `795fc7e` (feat)
2. **Task 2: Implement run_openhands (headless, workspace pinned)** — `31b91c7` (feat)
3. **Task 3: Model-confirming meta.json + final summary** — `3fa1690` (feat)
4. **Formatting: codex exec + `< /dev/null` on one line (key-link match)** — `39bc8f0` (style)

**Plan metadata:** docs commit follows this summary.

## Files Created/Modified

- `benchmark/run.sh` — Replaced the Plan 01 stubs: real codex/openhands invocations, transcript capture, model resolution + same-model assertion, record-only timestamps, meta.json, final summary. Sections renumbered (added §8 model resolution, §10 meta.json, §11 final summary).

## Decisions Made

- **Workspace pin mechanism corrected to OPENHANDS_WORK_DIR.** The plan assumed `--override-with-envs` would carry `SANDBOX_VOLUMES`/`WORKSPACE_BASE` to pin the workspace. Source inspection of the installed OpenHands (`openhands_cli` 1.16.0, SDK 1.21.0) shows the workspace is resolved by `get_work_dir() = os.environ.get("OPENHANDS_WORK_DIR", os.getcwd())`, and `--override-with-envs` overrides only the LLM (`LLM_API_KEY`/`LLM_BASE_URL`/`LLM_MODEL`). So the workspace is pinned via `OPENHANDS_WORK_DIR="$RUN_DIR"` (+ `cd`), and `--override-with-envs` is repurposed to pin the LLM model — which actually strengthens the same-model guarantee.
- **`--override-with-envs` requires LLM env vars** when enabled, so the runner exports `LLM_API_KEY=dummy`, `LLM_BASE_URL=http://localhost:4000/v1`, `LLM_MODEL=$MODEL` before invoking.
- **Non-interactive hardening flags:** `--headless` already auto-approves actions; `--always-approve` and `--exit-without-confirmation` (both valid per `openhands --help`) are added as belt-and-suspenders so the run can never block for confirmation.
- **meta.json model is resolved from config, not the transcript** — authoritative and offline-confirmable.

## Deviations from Plan

### Rule 3 (blocking mechanism mismatch) — OpenHands workspace pin

- **Found during:** Task 2 (inspecting `openhands --help` and the installed source before wiring).
- **Issue:** The plan's prescribed workspace-pin mechanism (`--override-with-envs` with `SANDBOX_VOLUMES`/`WORKSPACE_BASE`) does not exist in the installed OpenHands version; those vars belong to the older docker app. Using only that approach would have left the workspace at the default and risked RUN-02.
- **Fix:** Pinned the workspace via the version-correct `OPENHANDS_WORK_DIR="$RUN_DIR"` (confirmed from `openhands_cli/locations.py:get_work_dir`), and repurposed `--override-with-envs` to pin the LLM model (`LLM_MODEL`) from the runner. All plan truths and key_links still hold (`--headless`, `openhands --file`, `--override-with-envs`, `< /dev/null`, `tee ... transcript.log`).
- **Files modified:** benchmark/run.sh
- **Commit:** 31b91c7

### Minor — single-line codex invocation

- Kept `codex exec ... < /dev/null` on one physical line so the `codex exec.*< /dev/null` key-link pattern matches (commit 39bc8f0). No behavior change.

## Authentication Gates

None — `LITELLM_API_KEY=dummy` and the local gateway require no interactive login. (Live token use is exercised in Plan 03's smoke run.)

## Issues Encountered

- The installed OpenHands diverged from the plan's assumed flag/env model (see Deviations). Resolved by reading the package source (`openhands_cli/locations.py`, `entrypoint.py`, `stores/agent_store.py`, `argparsers/util.py`) rather than guessing.

## Verification Evidence (structural, ~0 model time)

- `bash -n benchmark/run.sh` passes.
- Present in run.sh: `codex exec.*< /dev/null`, `--sandbox workspace-write`, `--skip-git-repo-check`, `openhands.*--headless`, `--override-with-envs`, `tee.*transcript.log`, `meta.json`, `qwen-122b`.
- Config sources readable: codex resolves to `qwen-122b-codex`, openhands resolves to `openai/qwen-122b` (both qwen-122b family).
- meta.json heredoc produces valid JSON with a numeric `exit_code` (validated via python3 json.load).

## User Setup Required

None for wiring. Plan 03's real smoke run requires the LiteLLM/mlx gateway on :4000 (already checked by the preflight) and the human-verify of OpenHands isolation.

## Next Phase Readiness

- run_codex / run_openhands are fully wired; the only remaining proof is a single real smoke run (Plan 03), where the OPENHANDS_WORK_DIR pin should be CONFIRMED (the solution lands in `$RUN_DIR`), not fixed.
- Plan 03 should sanity-check that `--always-approve --exit-without-confirmation` don't conflict at runtime (could not be exercised here without model time); `--headless` alone already auto-approves if those need trimming.
- transcript.log + meta.json schema is stable for Phase 3 metric measurement.

---
*Phase: 02-equal-conditions-runner*
*Completed: 2026-06-26*
