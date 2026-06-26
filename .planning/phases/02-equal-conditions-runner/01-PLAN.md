---
phase: 02-equal-conditions-runner
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - benchmark/run.sh
  - benchmark/.gitignore
autonomous: true

must_haves:
  truths:
    - "Running `benchmark/run.sh <tool> <level>` validates the two arguments and creates exactly one fresh isolated run directory before any tool is invoked."
    - "Missing args, an unknown tool (anything other than codex|openhands), or an unknown level prints a usage message and exits nonzero."
    - "A second run.sh invocation cannot proceed while another holds the run lock (serial guarantee) — single mlx backend is never hit by two runs at once."
    - "If the LiteLLM gateway (:4000) is down, the runner aborts with a friendly message before creating a run dir or invoking a tool."
    - "Each invocation resolves and reads the canonical PROMPT.md for the chosen level so the same text can later be fed verbatim."
  artifacts:
    - path: "benchmark/run.sh"
      provides: "Runner entrypoint: arg parsing/validation, level normalization, isolated run-dir creation, serial lock, gateway preflight; tool invocation left as clearly-marked stubs for Plan 02"
      min_lines: 60
    - path: "benchmark/.gitignore"
      provides: "Ignores .runs/ so per-run work dirs and transcripts are not committed"
      contains: ".runs/"
  key_links:
    - from: "benchmark/run.sh"
      to: "benchmark/tasks/<level>/PROMPT.md"
      via: "path resolution + read into variable"
      pattern: "tasks/.*/PROMPT.md"
    - from: "benchmark/run.sh"
      to: "benchmark/.runs/.lock"
      via: "mkdir-based atomic mutex (macOS has no base flock)"
      pattern: "mkdir.*lock"
    - from: "benchmark/run.sh"
      to: "http://localhost:4000/v1/models"
      via: "curl preflight with Authorization: Bearer dummy"
      pattern: "localhost:4000/v1/models"
---

<objective>
Build the skeleton of the single equal-conditions runner command: `benchmark/run.sh <tool> <level>`.
This plan delivers everything that can be proven WITHOUT spending LLM time — argument
validation, level normalization, fresh isolated work-dir creation, the serial lock that
prevents two runs from hitting the single mlx backend at once, and the gateway preflight.
The actual codex/openhands invocations are left as labeled stub functions for Plan 02.

Purpose: Establishes RUN-01 (one command takes tool+level), RUN-02 (isolated fresh dir),
and the serialization mechanism for RUN-05 — all dry-run testable, no model calls.
Output: `benchmark/run.sh` (runnable, stubbed at the invocation step) and `benchmark/.gitignore`.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md

# Pass criterion + invocation convention this runner must honor
@benchmark/README.md

# Reference invocation patterns to learn from (DO NOT couple/source these)
@examples/codex-tests/common.sh
@examples/codex-tests/run.sh
</context>

<tasks>

<task type="auto">
  <name>Task 1: Scaffold run.sh with arg parsing, level normalization, and isolated run-dir creation</name>
  <files>benchmark/run.sh, benchmark/.gitignore</files>
  <action>
Create `benchmark/run.sh` (executable, `#!/usr/bin/env bash`, `set -euo pipefail`).

Behavior:
- Resolve `HERE="$(cd "$(dirname "$0")" && pwd)"` so paths work from any cwd.
- Usage: `run.sh <tool> <level>`. If `$#` != 2, print usage to stderr and exit 2.
- Validate `<tool>` is exactly `codex` or `openhands`; otherwise usage + exit 2.
- Normalize `<level>`: accept `l1`/`l1-fib`/`1` -> `l1-fib`; `l2`/`l2-wordstat`/`2` -> `l2-wordstat`;
  `l3`/`l3-kvstore`/`3` -> `l3-kvstore`. Resolve to the real dir by globbing
  `$HERE/tasks/<short>-*` so this stays robust if a suffix changes. Unknown level -> usage + exit 2.
- Resolve `PROMPT_FILE="$HERE/tasks/<level-dir>/PROMPT.md"`. If it does not exist, error + exit 1.
  Read it into a variable (PROMPT) so Plan 02 can feed it verbatim — do NOT modify the text.
- Create a fresh isolated run dir:
  `RUN_DIR="$HERE/.runs/<tool>-<level-dir>-$(date -u +%Y%m%d-%H%M%S)"`; `mkdir -p "$RUN_DIR"`.
  Use UTC and ensure uniqueness (if the dir already exists in the same second, append a short
  random suffix) so two quick runs never collide.
- Define two clearly-marked STUB functions `run_codex` and `run_openhands` that, for now, just
  `echo "[stub] would invoke <tool> in $RUN_DIR (wired in Plan 02)"`. Dispatch to the right one
  based on `<tool>`. (Plan 02 replaces the stub bodies.)
- Print a short start summary: tool, resolved level dir, RUN_DIR, PROMPT_FILE.

Also create `benchmark/.gitignore` containing `.runs/` (mirrors examples/codex-tests/.gitignore)
so per-run dirs and transcripts are never committed.

Keep it a single self-contained script — do NOT source examples/codex-tests/common.sh (decoupling);
you may copy small idioms (gateway curl, run-dir naming) inline.
  </action>
  <verify>
chmod +x benchmark/run.sh
bash benchmark/run.sh            # no args -> prints usage, exit 2
bash benchmark/run.sh foo l1     # bad tool -> usage, exit 2
bash benchmark/run.sh codex l9   # bad level -> usage, exit 2
bash benchmark/run.sh codex l1   # stub: creates ONE fresh dir, prints [stub], exit 0
bash benchmark/run.sh codex 1    # numeric alias resolves to l1-fib
ls -d benchmark/.runs/codex-l1-fib-*   # at least one isolated dir exists
grep -q '.runs/' benchmark/.gitignore
  </verify>
  <done>
run.sh validates tool+level (nonzero+usage on bad input), normalizes level aliases, creates a unique
isolated benchmark/.runs/<tool>-<level>-<utc> dir, reads PROMPT.md verbatim into a variable, dispatches
to stub run_codex/run_openhands, and benchmark/.gitignore ignores .runs/. No LLM is called.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add serial run-lock and LiteLLM gateway preflight</name>
  <files>benchmark/run.sh</files>
  <action>
Extend `benchmark/run.sh` so a run is serialized and only starts when the backend is reachable.
Both checks must happen BEFORE creating the run dir / invoking a tool.

Serial lock (RUN-05) — single mlx backend must never be hit by two runs at once:
- Use a mkdir-based atomic mutex (macOS base has no `flock`): LOCK="$HERE/.runs/.lock".
  `mkdir "$LOCK"` succeeds for exactly one process; on failure, the run is already in progress.
- Default behavior: print "another run holds the lock (single backend, serial only)" and exit 3.
  (Simple + safe. A blocking wait is optional; aborting is the deterministic, testable default.)
- Ensure the lock is always released: `trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT`.
  (Guarantees cleanup even on error/Ctrl-C.)

Gateway preflight (supports RUN-03) — abort early if backend down:
- `curl -sf -m 5 http://localhost:4000/v1/models -H "Authorization: Bearer dummy"` >/dev/null.
  On failure: print a friendly message (gateway :4000 not responding; check the LiteLLM/mlx service)
  and exit 1. Mirror the spirit of examples/codex-tests/common.sh::require_gateway, inline.
- Export `LITELLM_API_KEY="${LITELLM_API_KEY:-dummy}"` once near the top.

Order in main flow: validate args -> acquire lock -> gateway preflight -> create RUN_DIR -> dispatch.
  </action>
  <verify>
# Lock held -> second concurrent invocation aborts (uses stub, no LLM):
( bash benchmark/run.sh codex l1 & FIRST=$!; sleep 0.2; \
  bash benchmark/run.sh codex l1; echo "second exit=$?"; wait $FIRST )
# Expect the second to print the lock message and exit 3.
# Lock auto-released afterwards:
test ! -d benchmark/.runs/.lock && echo "lock released"
# Gateway preflight present and reachable in this env:
grep -q 'localhost:4000/v1/models' benchmark/run.sh
bash benchmark/run.sh codex l1 >/dev/null && echo "gateway ok, stub ran"
  </verify>
  <done>
Two concurrent run.sh invocations cannot both proceed (second exits 3 with a clear message), the lock
is always released via EXIT trap, and a down gateway aborts with a friendly nonzero exit before any run
dir/tool invocation. Verified entirely with stubs — no model time consumed.
  </done>
</task>

</tasks>

<verification>
- `bash benchmark/run.sh` (no args) and bad tool/level all exit nonzero with usage.
- `bash benchmark/run.sh codex l1` (stub) creates exactly one fresh benchmark/.runs/codex-l1-fib-* dir.
- Level aliases (l1 / l1-fib / 1) all resolve to tasks/l1-fib.
- Concurrent invocation: only one proceeds; lock released afterward.
- Gateway-down path returns nonzero before creating a run dir.
- No LLM/model call happens anywhere in this plan (invocation is stubbed).
</verification>

<success_criteria>
RUN-01 (one command, tool+level), RUN-02 (fresh isolated dir per run), and the RUN-05 serialization
mechanism are implemented and dry-run verified. benchmark/run.sh is runnable with stubbed invocation;
benchmark/.gitignore ignores .runs/. Ready for Plan 02 to wire the real tool calls.
</success_criteria>

<output>
After completion, create `.planning/phases/02-equal-conditions-runner/02-01-SUMMARY.md`.
</output>
