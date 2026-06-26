---
phase: 02-equal-conditions-runner
plan: 03
type: execute
wave: 3
depends_on: [02]
files_modified: []
autonomous: false

must_haves:
  truths:
    - "A real `benchmark/run.sh codex l1` run completes non-interactively and leaves an isolated dir containing the agent's solution, a non-empty transcript.log, and a meta.json naming qwen-122b."
    - "A real `benchmark/run.sh openhands l1` run completes headless and — because Plan 02 pins the workspace to $RUN_DIR by default — leaves its solution INSIDE the run dir (isolation confirmed), with transcript.log + meta.json."
    - "Neither run hangs on stdin nor blocks on an interactive prompt."
    - "The single backend is hit by only one run at a time (runs done serially under the lock)."
  artifacts: []
  key_links:
    - from: "benchmark/run.sh"
      to: "benchmark/.runs/codex-l1-fib-*/"
      via: "real codex L1 smoke run producing solution + transcript + meta"
      pattern: "transcript.log"
    - from: "benchmark/run.sh"
      to: "benchmark/.runs/openhands-l1-fib-*/"
      via: "real openhands L1 smoke run producing solution + transcript + meta"
      pattern: "transcript.log"
---

<objective>
Prove the runner works end-to-end with the smallest real task (L1 fib) for BOTH tools, run serially.
This is the single place in Phase 2 that spends real model time, deliberately kept minimal (L1 only)
and gated for human confirmation — a final eyeball that both tools left clean isolated dirs (openhands'
workspace is already pinned to the run dir by Plan 02, so this is a confirmation, not a fix point).

Purpose: Live confirmation of RUN-01..RUN-05 on the real backend (one isolated run per tool, same
model qwen-122b, non-interactive, serial). No judging/metrics here (that's Phase 3) — we only confirm
each run leaves a clean isolated dir + raw log behind.
Output: Two real run dirs under benchmark/.runs/ + human sign-off.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@benchmark/README.md
@.planning/phases/02-equal-conditions-runner/02-02-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Real codex L1 smoke run + structural assertions</name>
  <files>benchmark/run.sh</files>
  <action>
Run the smallest real task to confirm the codex path end-to-end. First confirm the backend is up
(run.sh's own preflight will do this; if it aborts, surface the message and stop — backend must be
started before this plan).

Execute exactly:
  bash benchmark/run.sh codex l1

Then assert on the newest benchmark/.runs/codex-l1-fib-* dir:
- transcript.log exists and is non-empty.
- meta.json exists, parses as JSON, and its `model` contains `qwen-122b` and `base_url` is the
  LiteLLM :4000 endpoint.
- At least one solution file was written into the run dir (e.g. fib.py) — confirms isolation (codex
  wrote into the run dir, not the repo root).
- The command returned and did not hang (it completed on its own — the `< /dev/null` did its job).

Keep this to a SINGLE L1 codex run (smallest task) to bound model time. Do not run l2/l3 here.
  </action>
  <verify>
D=$(ls -dt benchmark/.runs/codex-l1-fib-* | head -1); echo "$D"
test -s "$D/transcript.log" && echo "transcript non-empty"
python3 -c "import json,sys;m=json.load(open('$D/meta.json'));assert 'qwen-122b' in m['model'];assert '4000' in m['base_url'];print('meta ok',m['model'],m['exit_code'])"
ls "$D" | grep -v -E 'transcript.log|meta.json' | head   # solution file(s) present in isolated dir
  </verify>
  <done>
One real codex L1 run completed non-interactively, leaving an isolated dir with a non-empty transcript,
a meta.json confirming qwen-122b @ :4000, and the agent's solution file(s) inside that dir.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
The equal-conditions runner `benchmark/run.sh <tool> <level>`: isolated run dirs, serial lock,
gateway preflight, non-interactive codex (`< /dev/null`) and openhands (`--headless`, workspace pinned
to the run dir via `--override-with-envs`) invocations, raw transcript capture, and a model-confirming
meta.json. The codex L1 path was just auto-verified. This checkpoint CONFIRMS that openhands' default
workspace pin actually lands the solution INSIDE the run dir.
  </what-built>
  <how-to-verify>
1. Ensure the LiteLLM/mlx backend is up (qwen-122b). The runner preflight will tell you if not.
2. Make sure no other run is active (single backend, serial). Then run:
     bash benchmark/run.sh openhands l1
3. Wait for it to finish on its own (it must NOT hang or ask for interactive input).
4. Find the newest dir:  ls -dt benchmark/.runs/openhands-l1-fib-* | head -1
5. Confirm inside that dir:
     - transcript.log is present and non-empty
     - meta.json shows model containing "qwen-122b" and base_url with :4000
     - the agent's solution file(s) (e.g. fib.py) are INSIDE this run dir (NOT in the repo root,
       NOT in ~/.openhands/workspace). This is the isolation confirmation (RUN-02) — the Plan 02
       workspace pin should make this the default outcome.
6. Sanity: the two run dirs (codex + openhands) are separate and neither leaked into the other.
If, despite the default pin, openhands wrote files somewhere other than the run dir, report where so
the `--override-with-envs` vars in Plan 02's run_openhands can be corrected.
  </how-to-verify>
  <resume-signal>
Type "approved" if both tools left isolated dirs with transcript + meta (qwen-122b) and openhands'
solution is inside its run dir. Otherwise describe what landed where so run_openhands can be adjusted.
  </resume-signal>
</task>

</tasks>

<verification>
- benchmark/.runs/codex-l1-fib-*/ contains transcript.log (non-empty) + meta.json (qwen-122b, :4000) + solution file(s).
- benchmark/.runs/openhands-l1-fib-*/ contains the same, with the solution inside the run dir (human-confirmed).
- Both runs completed non-interactively; runs were performed serially (single backend).
- Only L1 was used — total model time bounded to two small runs.
</verification>

<success_criteria>
All five RUN requirements confirmed live: one command per (tool, level) (RUN-01), isolated dirs with
no cross-contamination (RUN-02), both tools on qwen-122b confirmable from meta.json (RUN-03),
codex `< /dev/null` + openhands `--headless` with no hang/interactive block (RUN-04), and serial
execution on the single backend (RUN-05). Phase 2 leaves clean run dirs + raw logs for Phase 3/4.
</success_criteria>

<output>
After completion, create `.planning/phases/02-equal-conditions-runner/02-03-SUMMARY.md`.
</output>
