---
phase: 02-equal-conditions-runner
plan: 02
type: execute
wave: 2
depends_on: [01]
files_modified:
  - benchmark/run.sh
autonomous: true

must_haves:
  truths:
    - "codex runs non-interactively (`codex exec ... < /dev/null`) inside the run dir and never hangs on stdin."
    - "openhands runs non-interactively (`--headless`) with its workspace pinned to $RUN_DIR BY DEFAULT (via env override), so its solution always lands in the isolated run dir, never a shared/global workspace."
    - "Every run leaves a non-empty transcript.log capturing the raw tool output in its run dir."
    - "Every run writes a meta record (meta.json) naming the model used (qwen-122b family) and the exit code, so the same-model criterion is confirmable after the fact."
    - "The PROMPT.md text is fed to the tool verbatim — identical text across both tools."
  artifacts:
    - path: "benchmark/run.sh"
      provides: "Implemented run_codex and run_openhands (replacing Plan 01 stubs): verbatim prompt feed, transcript capture, model-confirming meta record, final summary"
      min_lines: 100
    - path: "benchmark/.runs/<tool>-<level>-<ts>/transcript.log"
      provides: "Raw tool transcript for Phase 3/4 consumption (created at runtime)"
    - path: "benchmark/.runs/<tool>-<level>-<ts>/meta.json"
      provides: "Run record: tool, level, model, base_url, exit_code, timestamps, prompt path (created at runtime)"
  key_links:
    - from: "benchmark/run.sh"
      to: "codex exec"
      via: "LITELLM_API_KEY=dummy codex exec --skip-git-repo-check --sandbox workspace-write \"$PROMPT\" < /dev/null"
      pattern: "codex exec.*< /dev/null"
    - from: "benchmark/run.sh"
      to: "openhands"
      via: "LITELLM_API_KEY=dummy openhands --headless --override-with-envs (workspace pinned to $RUN_DIR) ... < /dev/null inside run dir"
      pattern: "openhands.*--headless"
    - from: "benchmark/run.sh"
      to: "openhands workspace = $RUN_DIR"
      via: "--override-with-envs with workspace/sandbox vars (e.g. SANDBOX_VOLUMES / WORKSPACE_BASE) set to $RUN_DIR — applied unconditionally"
      pattern: "override-with-envs"
    - from: "benchmark/run.sh"
      to: "transcript.log"
      via: "tee of combined stdout+stderr into the run dir"
      pattern: "tee.*transcript"
    - from: "benchmark/run.sh"
      to: "model config"
      via: "resolve model from ~/.codex/config.toml (codex) and ~/.openhands/agent_settings.json (openhands) into meta.json"
      pattern: "qwen-122b"
---

<objective>
Wire the real, non-interactive, same-model tool invocations into `benchmark/run.sh`, replacing the
Plan 01 stubs. After this plan, `benchmark/run.sh <tool> <level>` actually drives codex or openhands
against qwen-122b (LiteLLM :4000), captures the raw transcript, and records the model used — leaving
a clean isolated work dir + log behind for Phase 3/4.

Purpose: Delivers RUN-03 (both tools -> qwen-122b, model confirmable from the run record),
RUN-04 (codex `< /dev/null`, openhands `--headless` — no hangs/interactive blocks), and completes
RUN-05 (the real invocation runs under the Plan 01 lock).
Output: Implemented run_codex/run_openhands; per-run transcript.log + meta.json.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/STATE.md

# Pass criterion + verbatim-prompt convention
@benchmark/README.md

# Plan 01 output this plan extends (stubs -> real)
@.planning/phases/02-equal-conditions-runner/02-01-SUMMARY.md

# Verified invocation idioms (do not couple)
@examples/codex-tests/levels/03-single-file.sh
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement run_codex (non-interactive, verbatim prompt, transcript capture)</name>
  <files>benchmark/run.sh</files>
  <action>
Replace the `run_codex` stub with a real invocation. The function receives RUN_DIR and PROMPT (the
verbatim PROMPT.md text) from the main flow.

- `cd "$RUN_DIR"` so codex writes its solution INTO the isolated dir (codex exec writes to cwd).
- Invoke exactly (the `< /dev/null` is MANDATORY — without it codex hangs on stdin in non-tty/background):
  `LITELLM_API_KEY=dummy codex exec --skip-git-repo-check --sandbox workspace-write "$PROMPT" < /dev/null`
- Capture combined stdout+stderr to the transcript while still showing progress:
  pipe through `tee "$RUN_DIR/transcript.log"` (use `2>&1` so errors are captured too).
- Capture the tool exit code into a variable (mind `set -o pipefail` + tee — use
  `${PIPESTATUS[0]}` to get codex's real exit code, not tee's). Store it for Task 3's meta record.
- Do NOT fail the whole script on a nonzero tool exit — a failed agent run is still a valid recorded
  run (pass/fail judging is Phase 3). Just record the code and continue to finalize.

The prompt MUST be passed verbatim (same text both tools). Do not append tool-specific instructions.
  </action>
  <verify>
# Structure checks (no LLM):
grep -q 'codex exec' benchmark/run.sh
grep -q '< /dev/null' benchmark/run.sh
grep -q 'skip-git-repo-check' benchmark/run.sh
grep -q 'sandbox workspace-write' benchmark/run.sh
grep -q 'tee .*transcript.log' benchmark/run.sh
bash -n benchmark/run.sh   # syntax OK
# (A real codex run is exercised once in Plan 03's smoke verification, not here.)
  </verify>
  <done>
run_codex cd's into RUN_DIR, invokes `codex exec --skip-git-repo-check --sandbox workspace-write "$PROMPT" < /dev/null`,
tees combined output to transcript.log, and records the real codex exit code (via PIPESTATUS) without
aborting the script on agent failure.
  </done>
</task>

<task type="auto">
  <name>Task 2: Implement run_openhands (headless, verbatim prompt, workspace pinned to RUN_DIR by default)</name>
  <files>benchmark/run.sh</files>
  <action>
Replace the `run_openhands` stub with a real non-interactive invocation.

- `cd "$RUN_DIR"` first (set cwd to the isolated dir).
- Feed the prompt verbatim. Prefer the file form to avoid shell-escaping of multi-line prompts:
  `LITELLM_API_KEY=dummy openhands --file "$PROMPT_FILE" --headless < /dev/null`
  (equivalently `--task "$PROMPT"`; `--file` is safer for multi-line text — both feed identical text).
  Keep `< /dev/null` for the same non-tty safety as codex.
- Non-interactive hardening: openhands may still prompt for action approval. If `--headless` alone
  blocks, add `--always-approve` and/or `--exit-without-confirmation` (both are valid flags per
  `openhands --help`) so the run completes without human input. Document which flags were needed in
  the SUMMARY.
- Workspace isolation (PROACTIVE — pin BY DEFAULT, do not leave conditional): OpenHands' local
  runtime resolves its workspace from a configured workspace_base / sandbox volume, NOT from cwd, so
  without an explicit pin its solution can land in ~/.openhands/workspace and break RUN-02. Therefore
  ALWAYS pin the workspace to $RUN_DIR using the documented env override on every openhands invocation:
  `--override-with-envs` with the appropriate workspace/sandbox vars (e.g. SANDBOX_VOLUMES and/or
  WORKSPACE_BASE) set to "$RUN_DIR". This is the default path, not a fallback — there is no "run first,
  fix if misplaced" branch. (Consult `openhands --help` for the exact env-var names and record the
  resolved set in the SUMMARY.) With this pin in place, Plan 03's human-verify is a CONFIRMATION of
  isolation, not a fix point.
- Capture combined stdout+stderr via `tee "$RUN_DIR/transcript.log"`; record the real exit code with
  `${PIPESTATUS[0]}`. As with codex, do not abort the script on a nonzero agent exit.
  </action>
  <verify>
grep -q 'openhands' benchmark/run.sh
grep -q -- '--headless' benchmark/run.sh
grep -Eq 'openhands --(file|task)' benchmark/run.sh
grep -q -- '--override-with-envs' benchmark/run.sh   # workspace pin applied by default
grep -q '< /dev/null' benchmark/run.sh
grep -q 'tee .*transcript.log' benchmark/run.sh
bash -n benchmark/run.sh   # syntax OK
# (A real openhands run + isolation confirmation happens in Plan 03's human-verify.)
  </verify>
  <done>
run_openhands cd's into RUN_DIR, invokes openhands headless with the verbatim prompt and `< /dev/null`,
unconditionally pins the workspace to $RUN_DIR via `--override-with-envs` (so the solution always lands
in the isolated run dir), tees output to transcript.log, and records the real exit code.
  </done>
</task>

<task type="auto">
  <name>Task 3: Write model-confirming meta record + final run summary</name>
  <files>benchmark/run.sh</files>
  <action>
After the tool invocation returns, write `$RUN_DIR/meta.json` so the run is self-describing and the
same-model criterion (RUN-03 success criterion 3) is confirmable without rerunning anything.

Resolve the model per tool from config (single source of truth):
- codex -> read `model = "..."` from `~/.codex/config.toml` (currently `qwen-122b-codex`, which maps
  to the same qwen-122b backend via LiteLLM).
- openhands -> read `.llm.model` from `~/.openhands/agent_settings.json` (currently `openai/qwen-122b`).
Use stdlib-friendly extraction (grep/sed for the toml line; `python3 -c` json read for the json) — no
new deps. If the tool transcript also echoes a model string, that's a bonus, but meta.json is the
authoritative record.

meta.json fields (one JSON object):
  tool, level, model, base_url ("http://localhost:4000/v1"), prompt_file, run_dir,
  started_at, finished_at (UTC ISO), exit_code (the real tool exit code from Task 1/2),
  transcript ("transcript.log").

NOTE (scope): started_at/finished_at are RECORD-ONLY timestamps for provenance. Do NOT compute,
aggregate, or judge wall-clock metrics here — metric measurement/aggregation is Phase 3.

Then print a final summary to stdout: RUN_DIR, transcript path, resolved model, exit_code.

Edge: meta.json must be written even when the agent exited nonzero (recording a failed run is valid).
  </action>
  <verify>
grep -q 'meta.json' benchmark/run.sh
grep -q 'qwen-122b' benchmark/run.sh   # model resolution present
grep -q 'base_url' benchmark/run.sh
bash -n benchmark/run.sh
# Confirm config sources are readable in this env:
test -f ~/.codex/config.toml && grep -q 'qwen-122b' ~/.codex/config.toml && echo "codex model source ok"
python3 -c "import json;print(json.load(open('${HOME}/.openhands/agent_settings.json'))['llm']['model'])"
  </verify>
  <done>
Every run writes meta.json naming the qwen-122b model (resolved from the tool's own config), base_url,
exit_code, and record-only timestamps; the runner prints a final summary. The same-model criterion is
confirmable from the run record alone. No new dependencies introduced (stdlib + grep/sed).
  </done>
</task>

</tasks>

<verification>
- bash -n benchmark/run.sh passes (syntax) after all three tasks.
- run.sh contains: `codex exec ... < /dev/null`, `--sandbox workspace-write`, `--skip-git-repo-check`,
  `openhands ... --headless`, `--override-with-envs` (workspace pinned to $RUN_DIR), `tee ... transcript.log`,
  `meta.json`, model resolution to qwen-122b.
- Config sources (~/.codex/config.toml, ~/.openhands/agent_settings.json) are readable and contain the
  qwen-122b model strings.
- No real LLM run is required to verify this plan (the single real smoke is Plan 03). This keeps model
  time near zero while proving the wiring is correct.
</verification>

<success_criteria>
RUN-03 (both tools -> qwen-122b, model confirmable from meta.json), RUN-04 (codex `< /dev/null`,
openhands `--headless`, no interactive block), and the real-invocation half of RUN-05 are implemented.
openhands' workspace is pinned to the isolated run dir by default. Each run leaves an isolated dir with
transcript.log + meta.json. Structurally verified with ~0 model time.
</success_criteria>

<output>
After completion, create `.planning/phases/02-equal-conditions-runner/02-02-SUMMARY.md`.
</output>
