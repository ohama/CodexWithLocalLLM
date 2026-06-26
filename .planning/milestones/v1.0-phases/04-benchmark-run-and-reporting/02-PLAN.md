---
phase: 04-benchmark-run-and-reporting
plan: 02
type: execute
wave: 2
depends_on: ["04-01"]
files_modified:
  - benchmark/report.py
  - benchmark/RESULTS.md

must_haves:
  truths:
    - "benchmark/RESULTS.md presents a tool x level matrix table with success and time columns"
    - "Each step count in the report is shown beside its step_method (codex/openhands units differ)"
    - "RESULTS.md references every run's transcript and embeds a short evidence excerpt per run"
    - "RESULTS.md gives a per-level codex-vs-openhands difference summary (time, process, output)"
    - "RESULTS.md is a durable committed artifact, independent of the gitignored .runs dir"
  artifacts:
    - path: "benchmark/report.py"
      provides: "Report generator: reads aggregated results.json, emits RESULTS.md (table + transcript refs + per-level diffs)"
      min_lines: 50
    - path: "benchmark/RESULTS.md"
      provides: "The committed comparison report: 6-cell matrix + per-level codex-vs-openhands summaries"
      contains: "tool x level table with success and time columns"
  key_links:
    - from: "benchmark/report.py"
      to: "benchmark/.runs/matrix-<ts>/results.json"
      via: "json load (argv path or auto-discovered latest matrix)"
      pattern: "results\\.json"
    - from: "benchmark/report.py"
      to: "benchmark/RESULTS.md"
      via: "writes markdown table + summaries"
      pattern: "RESULTS\\.md"
    - from: "benchmark/RESULTS.md"
      to: "benchmark/.runs/<tool>-<level>-*/transcript.log"
      via: "per-run transcript path reference + excerpt"
      pattern: "transcript\\.log"
---

<objective>
Generate the committed comparison report from the collected matrix metrics: a tool x level results
table (success + time + steps[with step_method] + size), transcript references with short evidence
excerpts, and a per-level codex-vs-openhands difference summary.

Purpose: Satisfies REP-02 (results as a tool x level matrix table with success + time) and REP-03's
durable half — because `benchmark/.runs/` is GITIGNORED, the raw run dirs never enter version control,
so the report MUST itself capture the evidence (metrics table + transcript references/excerpts) into a
committed `benchmark/RESULTS.md`. That report is the durable record.
Output: `benchmark/report.py` (re-runnable generator, ~0 LLM time) and the generated `benchmark/RESULTS.md`.

Constraint carried from Phase 3: step counts use DIFFERENT units per tool (codex = 'exec' tool-call
blocks; openhands = 'Number of agent messages'). The report MUST surface step_method beside every step
number and must NOT compare raw step counts as identical units in the per-level summary.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md

# What this plan consumes (produced by Plan 04-01): the aggregated 6-cell metrics.
@.planning/phases/04-benchmark-run-and-reporting/04-01-SUMMARY.md
# The metric field definitions (passed / duration_seconds / steps / step_method / files / loc):
@benchmark/score.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Write benchmark/report.py (results.json -> RESULTS.md generator)</name>
  <files>benchmark/report.py</files>
  <action>
Create `benchmark/report.py` (stdlib-only: json, os, sys, glob). It reads the aggregated metrics from
Plan 04-01 and emits `benchmark/RESULTS.md`. Do NOT re-run any agent or judge — this is pure formatting
over the already-scored results.json.

Input resolution:
- `argv[1]` optional: a results.json path OR a matrix dir (then use `<dir>/results.json`).
- Default: auto-discover the latest matrix — `sorted(glob(benchmark/.runs/matrix-*/results.json))[-1]`.
- If none found, exit nonzero with a clear message ("run benchmark/run-matrix.sh first").

Output `benchmark/RESULTS.md` containing, in order:
1. Title + provenance line: source results.json path, model(s) used (from the meta `model` field per
   tool — note codex vs openhands report slightly different model strings, both qwen-122b family),
   and the matrix timestamp.
2. The tool x level MATRIX TABLE (REP-02). Rows = the 6 cells; columns MUST include at least:
   tool, level, success (pass/fail from `passed`), time (`duration_seconds`), steps shown as
   `N (step_method)`, and size (`files`f / `loc`loc). An errored/placeholder cell renders as `ERROR`/`—`
   rather than crashing.
3. A short "Reading the numbers" note stating that step counts are NOT directly comparable across tools
   (codex 'exec' blocks vs openhands agent messages) — surface step_method, never compare raw counts.
4. TRANSCRIPT REFERENCES + EVIDENCE EXCERPTS (REP-03 durability): for each run, print the absolute
   `run_dir/transcript.log` path and a fenced short excerpt (e.g. first ~20 lines, or first+last lines)
   read from that transcript if present (best-effort; if missing, note "transcript unavailable"). This
   bakes evidence into the committed report since .runs is gitignored.
5. PER-LEVEL DIFFERENCE SUMMARY (REP-03): for each level l1/l2/l3, a short paragraph comparing codex vs
   openhands on (a) time = duration_seconds delta, (b) process = steps with each tool's step_method
   spelled out (explicitly noting units differ), and (c) output = files/loc delta and pass/fail.

Best-effort throughout: missing fields render as `—`; report.py never crashes on a partial cell.
Make it re-runnable/idempotent (same results.json -> same RESULTS.md).
  </action>
  <verify>
`python3 -m py_compile benchmark/report.py` exits 0. Inspect: input auto-discovers latest
results.json (with argv override), and the writer emits a markdown table plus per-level sections and
transcript references including step_method.
  </verify>
  <done>
benchmark/report.py exists, compiles, reads results.json (argv or latest matrix), and is structured to
emit the matrix table + transcript refs/excerpts + per-level diff summary with step_method surfaced.
  </done>
</task>

<task type="auto">
  <name>Task 2: Generate benchmark/RESULTS.md and verify it captures all required evidence</name>
  <files>benchmark/RESULTS.md</files>
  <action>
Run `python3 benchmark/report.py` to generate `benchmark/RESULTS.md` from the latest matrix results.json
(produced by Plan 04-01). This is ~0 LLM time — pure formatting over collected metrics.

Confirm the generated RESULTS.md is the durable, committable record: it lives at benchmark/RESULTS.md
(outside the gitignored .runs/), contains the full 6-cell table, the step_method caveat, transcript
references with excerpts, and the per-level codex-vs-openhands summaries.

This file is the Phase 4 deliverable artifact and should be tracked in version control (it is the only
durable copy of the matrix evidence, since benchmark/.runs/ is gitignored).
  </action>
  <verify>
Generate then assert content (no re-run of agents):

```bash
python3 benchmark/report.py
python3 - <<'PY'
import re
md=open("benchmark/RESULTS.md").read()
assert "| codex" in md or "codex" in md, "codex rows missing"
assert "openhands" in md, "openhands rows missing"
for lvl in ("l1","l2","l3"):
    assert lvl in md, f"level {lvl} missing"
assert "step_method" in md or "agent messages" in md or "exec" in md, "step_method/units not surfaced"
assert "transcript.log" in md, "transcript references missing"
# success + time columns present
assert re.search(r"success|pass", md, re.I), "success column missing"
assert re.search(r"time|duration|second", md, re.I), "time column missing"
print("OK: matrix table, both tools, 3 levels, step_method, transcript refs, success+time present")
PY
```

All assertions pass; RESULTS.md exists at benchmark/RESULTS.md.
  </verify>
  <done>
benchmark/RESULTS.md exists with: the 6-cell tool x level table (success + time + steps[step_method] +
size), transcript references/excerpts for every run, and a per-level codex-vs-openhands difference
summary. (REP-02 + REP-03 satisfied; durable committed evidence.)
  </done>
</task>

</tasks>

<verification>
- `python3 -m py_compile benchmark/report.py` passes.
- `python3 benchmark/report.py` regenerates benchmark/RESULTS.md from the latest results.json.
- RESULTS.md contains: 6-cell matrix table with success + time columns, step_method beside step counts,
  transcript.log references with excerpts, and per-level l1/l2/l3 codex-vs-openhands summaries.
- RESULTS.md lives outside .runs/ (durable / committable).
</verification>

<success_criteria>
- Results presented as a tool x level matrix table including success and time columns (REP-02).
- Raw transcripts referenced from the report, with evidence excerpts embedded so the committed report is
  self-contained despite .runs being gitignored (REP-03).
- Per-level codex-vs-openhands difference summary covers time, process, and output (REP-03).
- step_method surfaced beside every step count; raw step counts never compared as identical units.
</success_criteria>

<output>
After completion, create `.planning/phases/04-benchmark-run-and-reporting/04-02-SUMMARY.md`.
Record: the results.json source used, a copy of the final matrix table, the key per-level findings, and
confirm RESULTS.md is in place as the durable Phase 4 deliverable.
</output>
