---
phase: 02-equal-conditions-runner
plan: 01
subsystem: infra
tags: [bash, runner, mkdir-mutex, litellm, gateway-preflight, macos]

# Dependency graph
requires:
  - phase: 01-fixed-tasks
    provides: frozen tasks/l{1,2,3}-* PROMPT.md + stdlib-only judges the runner will drive/score
provides:
  - benchmark/run.sh runner skeleton (arg parse/validate, level normalization, isolated run-dir, serial lock, gateway preflight)
  - serial single-backend guarantee via mkdir-based atomic mutex (.runs/.lock)
  - LiteLLM :4000 gateway preflight that aborts before any run dir/tool call
  - labeled run_codex / run_openhands stubs as the wiring point for Plan 02
  - benchmark/.gitignore ignoring .runs/
affects: [02-02 (wire real codex/openhands invocations into the stubs), scoring/transcript capture]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "mkdir-based atomic mutex for serial backend access (macOS has no flock)"
    - "EXIT-trap installed only AFTER lock acquire so losers never delete holder's lock"
    - "level alias -> short key -> glob tasks/<short>-* to survive suffix renames"
    - "read canonical PROMPT.md verbatim into a variable for byte-identical replay"

key-files:
  created:
    - benchmark/run.sh
    - benchmark/.gitignore
  modified: []

key-decisions:
  - "Serial lock default is abort (exit 3), not block-and-wait — deterministic and testable"
  - "Validation (args/level/prompt) runs before lock acquire so bad input never grabs the backend lock"
  - "run.sh stays self-contained — copied idioms from examples/codex-tests/common.sh inline, did not source it (decoupling)"

patterns-established:
  - "mkdir-mutex serialization: acquire then trap, never trap then acquire"
  - "gateway preflight before side effects (run dir / tool call)"

# Metrics
duration: ~6min
completed: 2026-06-26
---

# Phase 2 Plan 01: Equal-Conditions Runner Skeleton Summary

**benchmark/run.sh skeleton: validates tool+level, normalizes level aliases, creates one fresh isolated .runs/ dir, serializes runs via a mkdir-mutex, and preflights the LiteLLM :4000 gateway — all dry-run testable with stubbed tool invocation (no LLM time spent).**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-06-26T02:00:17Z
- **Completed:** 2026-06-26T02:02:00Z
- **Tasks:** 2
- **Files modified:** 2 (both created)

## Accomplishments
- RUN-01: one command `benchmark/run.sh <tool> <level>` takes tool + level, validates both (exit 2 + usage on bad input).
- RUN-02: each run gets a fresh isolated `.runs/<tool>-<level>-<utc>` dir with a same-second collision guard.
- RUN-05 mechanism: mkdir-based atomic mutex `.runs/.lock` serializes the single mlx backend; a losing run exits 3 and leaves the holder's lock intact (EXIT trap installed only post-acquire).
- Gateway preflight (supports RUN-03): curl on `http://localhost:4000/v1/models` aborts (exit 1) with a friendly message before any run dir or tool call.
- Canonical PROMPT.md is read verbatim into a variable so Plan 02 can feed it byte-identically.
- Level aliases (`l1`/`l1-fib`/`1`, etc.) map to a short key then glob `tasks/<short>-*`, robust to suffix renames.

## Task Commits

Each task was committed atomically:

1. **Task 1: Scaffold run.sh — arg parsing, level normalization, isolated run-dir** - `39f88e8` (feat)
2. **Task 2: Add serial run-lock and LiteLLM gateway preflight** - `f70cc2c` (feat)

**Plan metadata:** (docs commit follows this summary)

## Files Created/Modified
- `benchmark/run.sh` - Runner entrypoint: arg validation, level normalization (alias->glob), verbatim PROMPT.md read, mkdir-mutex serial lock, gateway preflight, isolated run-dir creation, stubbed run_codex/run_openhands dispatch.
- `benchmark/.gitignore` - Ignores `.runs/` so per-run work dirs and transcripts are never committed.

## Decisions Made
- Serial lock aborts (exit 3) rather than blocking — deterministic and unit-testable, no timing race.
- Validation precedes lock acquisition so malformed input never seizes the backend lock.
- run.sh kept self-contained: gateway-curl and run-dir-naming idioms copied inline from `examples/codex-tests/common.sh` rather than sourcing it (decoupling, per plan).
- EXIT trap installed strictly after a successful `mkdir "$LOCK"` so a losing invocation cannot delete the holder's lock.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None. The gateway was already up in this environment, so the gateway-reachable verify steps passed directly; the gateway-down path is established by code (curl `-sf` failure -> exit 1 before side effects) but not exercised live (no need to take the service down).

## User Setup Required
None - no external service configuration required for this plan. (Live runs in Plan 02 will require the LiteLLM/mlx gateway on :4000, which the preflight already checks.)

## Next Phase Readiness
- Skeleton is runnable and verified with stubs; the two `run_codex` / `run_openhands` stub bodies are the single, clearly-marked wiring point for Plan 02.
- Plan 02 must handle the known `codex exec` stdin-hang (`< /dev/null`) when replacing the stub.
- Serial guarantee and gateway preflight already enforce the single-backend / backend-up invariants for real invocations.

---
*Phase: 02-equal-conditions-runner*
*Completed: 2026-06-26*
