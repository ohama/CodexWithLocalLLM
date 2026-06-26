---
phase: 02-equal-conditions-runner
verified: 2026-06-26T02:30:00Z
status: passed
score: 5/5 must-haves verified
re_verification:
  previous_status: none
  note: initial verification
---

# Phase 2: Equal-Conditions Runner Verification Report

**Phase Goal:** A single command runs a chosen (tool, level) under identical, isolated conditions against qwen-122b, non-interactively and serially. (No judging / metrics / matrix / repro — those are Phases 3/4/5.)
**Verified:** 2026-06-26T02:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| - | ----- | ------ | -------- |
| 1 | One command `run.sh <tool> <level>` launches a run | ✓ VERIFIED | run.sh §1-2: arg count check (`[ "$#" -eq 2 ]`), tool case (codex/openhands), level alias map (l1/l1-fib/1 …) with usage()/exit 2 on bad input. `bash -n` passes. |
| 2 | Each run uses a fresh isolated work dir, no leftover/cross-tool contamination | ✓ VERIFIED | run.sh §6: `RUN_DIR=.runs/$TOOL-$LEVEL-$STAMP` (UTC stamp + `$RANDOM` collision guard), `mkdir -p`. Two real run dirs are distinct (`codex-l1-fib-20260626-021103`, `openhands-l1-fib-20260626-021227`); each holds only its own fib.py/transcript.log/meta.json. openhands pinned via `OPENHANDS_WORK_DIR=$RUN_DIR`; codex via `cd "$RUN_DIR"` + `--sandbox workspace-write`. |
| 3 | Both tools invoked against qwen-122b (:4000); same model confirmable from log/meta | ✓ VERIFIED | §5 preflight curls `http://localhost:4000/v1/models`; §8 resolve_model reads codex `~/.codex/config.toml` and openhands `~/.openhands/agent_settings.json`, asserts `*qwen-122b*` family. meta.json: codex `qwen-122b-codex`, openhands `openai/qwen-122b`, both `base_url http://localhost:4000/v1`. Transcripts confirm: codex `model: qwen-122b-codex`, openhands `Agent initialized with model: openai/qwen-122b`. |
| 4 | codex runs `< /dev/null`, openhands `--headless`; neither hangs/blocks interactively | ✓ VERIFIED | run_codex: `codex exec --skip-git-repo-check --sandbox workspace-write "$PROMPT" < /dev/null`. run_openhands: `openhands --file ... --headless --always-approve --exit-without-confirmation --override-with-envs < /dev/null`. Both real runs reached completion with exit_code 0 (no hang). codex transcript shows "Reading additional input from stdin..." then proceeds (no block). |
| 5 | Runs are serialized (single backend, no concurrency) | ✓ VERIFIED | §4: mkdir-based atomic mutex `.runs/.lock`; second concurrent invocation exits 3. Cleanup `trap ... EXIT` installed ONLY after acquiring lock (correctly avoids loser deleting holder's lock). Lock dir is absent now (clean release). |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `benchmark/run.sh` | Single-command runner, full pipeline | ✓ VERIFIED | 208 lines, `set -euo pipefail`, executable (`-rwxr-xr-x`), `bash -n` clean. Real run_codex/run_openhands functions (not stubs). |
| `.runs/codex-l1-fib-*/` | fib.py + transcript.log + meta.json, exit 0 | ✓ VERIFIED | fib.py (31 lines, real iterative impl + self-tests), transcript.log (3458 B), meta.json exit_code 0, model qwen-122b-codex. |
| `.runs/openhands-l1-fib-*/` | fib.py + transcript.log + meta.json, exit 0 | ✓ VERIFIED | fib.py (30 lines, real impl), transcript.log (3636 B), meta.json exit_code 0, model openai/qwen-122b. |
| `benchmark/tasks/l1-fib/PROMPT.md` | Canonical prompt fed verbatim | ✓ VERIFIED | Present; referenced by both meta.json `prompt_file` and read verbatim (`PROMPT="$(cat "$PROMPT_FILE")"`). |
| `benchmark/.gitignore` | Excludes `.runs/` | ✓ VERIFIED | Contains `.runs/`. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| run.sh | LiteLLM :4000 | curl preflight `/v1/models` | ✓ WIRED | Aborts before run dir creation if backend down. |
| run.sh | tool config | resolve_model → meta.json | ✓ WIRED | Reads each tool's own config (toml grep / json python3); family-asserts qwen-122b; written to meta.json. |
| run_codex | RUN_DIR | `cd "$RUN_DIR"` + workspace-write | ✓ WIRED | Solution (fib.py) landed in correct isolated dir. |
| run_openhands | RUN_DIR | `OPENHANDS_WORK_DIR=$RUN_DIR` | ✓ WIRED | Solution (fib.py) landed in correct isolated dir (output isolation confirmed). |
| tool stdout/err | transcript.log | `2>&1 | tee` + `${PIPESTATUS[0]}` | ✓ WIRED | Real tool exit captured (not tee's); both transcripts populated, exit 0 recorded. |

### Requirements Coverage

| Requirement | Status | Notes |
| ----------- | ------ | ----- |
| RUN-01 (one command, tool+level) | ✓ SATISFIED | Truth 1. |
| RUN-02 (isolated work dir, no contamination) | ✓ SATISFIED | Truth 2. |
| RUN-03 (same model qwen-122b :4000) | ✓ SATISFIED | Truth 3. |
| RUN-04 (codex `< /dev/null`, openhands `--headless`) | ✓ SATISFIED | Truth 4. |
| RUN-05 (serial, single backend) | ✓ SATISFIED | Truth 5. |

### Scope Check (Phase 2 must NOT include Phases 3/4/5 work)

| Out-of-scope concern | Present? | Evidence |
| -------------------- | -------- | -------- |
| Pass/fail judging | No | No test.py re-run / pytest / pass-fail logic in run.sh. Comments explicitly defer judging to Phase 3. |
| Metric extraction | No | No duration math, LOC/file counts, step counts, or aggregation. Timestamps are record-only provenance (commented as such). |
| Full matrix | No | Single (tool,level) per invocation; no loops over tools/levels. |
| Reproducibility doc | No | None added. |

### Anti-Patterns Found

None blocking. The only `stub` keyword hit is a Plan-01 header comment ("Tool invocation is stubbed in this plan (Plan 01) and wired for real in Plan 02") — stale narrative, since run_codex/run_openhands are now fully wired. Cosmetic only.

### Human Verification Required

None required for goal achievement. (Live runs already executed with exit 0 and correct output isolation; this was the human-verify item from 03-PLAN and is satisfied by the existing artifacts.)

### Notes / Observations

- Model NAMES differ per tool (`qwen-122b-codex` vs `openai/qwen-122b`) but both resolve to the same qwen-122b backend on :4000, satisfying the "same model family / same backend" criterion. The script's `*qwen-122b*` assertion enforces this. Not a gap.
- codex transcript emits a benign warning: "Model metadata for `qwen-122b-codex` not found. Defaulting to fallback metadata." Does not affect the run (exit 0); noted for awareness.

### Gaps Summary

No gaps. All 5 success criteria / RUN-01..RUN-05 verified against actual artifacts. Scope correctly bounded — no Phase 3/4/5 logic leaked in.

---

_Verified: 2026-06-26T02:30:00Z_
_Verifier: Claude (gsd-verifier)_
