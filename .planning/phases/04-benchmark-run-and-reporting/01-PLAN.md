---
phase: 04-benchmark-run-and-reporting
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - benchmark/run-matrix.sh
autonomous: true

must_haves:
  truths:
    - "Running run-matrix.sh executes all 6 (tool x level) cells serially against the single backend"
    - "Each of the 6 runs leaves a run dir containing transcript.log and a meta.json with all four metrics"
    - "The 6 runs' metrics are aggregated into one collected results.json"
    - "Cells run strictly one-at-a-time (single mlx backend never hit concurrently)"
  artifacts:
    - path: "benchmark/run-matrix.sh"
      provides: "Serial matrix driver over codex/openhands x l1/l2/l3 that calls run.sh per cell and aggregates metrics"
      min_lines: 40
    - path: "benchmark/.runs/matrix-<ts>/results.json"
      provides: "Aggregated array of the 6 per-run meta.json records (each with run_dir + transcript + 4 metrics)"
      contains: "6 entries"
  key_links:
    - from: "benchmark/run-matrix.sh"
      to: "benchmark/run.sh"
      via: "sequential bash invocation, one per cell (no '&', no concurrency)"
      pattern: "run\\.sh.*\\$tool.*\\$level"
    - from: "benchmark/run-matrix.sh"
      to: "benchmark/.runs/<tool>-<level>-*/meta.json"
      via: "aggregation into results.json"
      pattern: "results\\.json"
---

<objective>
Build and execute the full benchmark matrix: all 6 cells (codex, openhands) x (l1, l2, l3),
run serially via the existing `benchmark/run.sh`, with every run's transcript + metrics preserved
and all 6 meta.json records aggregated into a single collected results file.

Purpose: This satisfies REP-01 (all six cells executed, metrics collected) and produces the raw
evidence base (REP-03's preserved transcripts) that Plan 02's report turns into a committed artifact.
This is the real-LLM-time plan — actually running the matrix end to end.
Output: `benchmark/run-matrix.sh` (the driver) plus a fresh `benchmark/.runs/matrix-<ts>/` containing
`results.json` (6 aggregated metric records) and per-cell console logs; each cell's own
`.runs/<tool>-<level>-<stamp>/` holds its transcript.log + fully-scored meta.json.

Precondition: the LiteLLM gateway (:4000) backed by qwen-122b must be up — run.sh preflights it and
aborts a cell if it is down. Bring the backend up before executing Task 2.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md

# The single-cell runner this driver orchestrates (do NOT modify it):
@benchmark/run.sh
# The scorer run.sh auto-invokes (defines the meta.json metric fields the matrix collects):
@benchmark/score.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Write benchmark/run-matrix.sh (serial 6-cell driver + aggregator)</name>
  <files>benchmark/run-matrix.sh</files>
  <action>
Create `benchmark/run-matrix.sh` (chmod +x) that drives the full matrix by calling the EXISTING
`benchmark/run.sh` once per cell, serially, and aggregating the results. Do NOT modify run.sh or score.py.

Structure:
- `#!/usr/bin/env bash` + `set -euo pipefail`. `HERE="$(cd "$(dirname "$0")" && pwd)"`.
- `TOOLS=(codex openhands)` and `LEVELS=(l1 l2 l3)` (these aliases are accepted by run.sh).
- Create a single timestamped matrix dir: `TS="$(date -u +%Y%m%d-%H%M%S)"`,
  `MATRIX_DIR="$HERE/.runs/matrix-$TS"`, `mkdir -p "$MATRIX_DIR"`.
- CRITICAL — do NOT acquire `.runs/.lock` here. run.sh acquires and releases that mkdir-mutex itself
  per cell; if the driver held it, every run.sh call would abort with exit 3. The driver's only job is
  to call run.sh one cell at a time and wait for each to finish before starting the next.
- Loop tool-major over LEVELS (6 iterations total). For each (tool, level):
    - Run the cell capturing its console output but NEVER aborting the whole sweep on a single
      failure: wrap with `set +e`; `bash "$HERE/run.sh" "$tool" "$level" 2>&1 | tee "$MATRIX_DIR/$tool-$level.console.log"`;
      `cell_exit="${PIPESTATUS[0]}"`; `set -e`. (No `&` — strictly serial, one backend at a time.)
    - Resolve the run dir run.sh just created: `RD="$(ls -dt "$HERE"/.runs/$tool-$level-* 2>/dev/null | head -1)"`
      (newest by mtime for that cell). Record one manifest line: `"$tool $level $cell_exit $RD"` appended
      to `"$MATRIX_DIR/manifest.txt"`.
    - Echo a short progress line so a long sweep shows liveness (`[N/6] tool level -> exit, run dir`).
- After all 6 cells, aggregate into `"$MATRIX_DIR/results.json"` with an inline python3 here-doc:
  read each manifest line, and for each cell load `<RD>/meta.json` if present and append it to a JSON
  array; for a cell whose meta.json is missing/unreadable, append a placeholder object
  `{"tool":..., "level":..., "run_dir":..., "cell_exit":..., "error":"meta.json missing"}` so the
  report can flag it. Write the array (indent=2) to results.json. Pass the manifest path + MATRIX_DIR
  into python via argv/env (avoid fragile shell interpolation).
- Final summary to stdout: total cells, how many produced meta.json, and the absolute path of
  `results.json` and `MATRIX_DIR` (Plan 02 reads results.json from here).

Keep it stdlib/bash + python3 only (no new deps), mirroring the existing harness conventions.
  </action>
  <verify>
`bash -n benchmark/run-matrix.sh` exits 0 (syntax valid). `test -x benchmark/run-matrix.sh`.
Confirm by inspection: no `&` backgrounding of run.sh, no `mkdir .runs/.lock` in the driver,
exactly TOOLS x LEVELS = 6 invocations, and an aggregation step writing results.json.
  </verify>
  <done>
benchmark/run-matrix.sh exists, is executable, passes `bash -n`, calls run.sh serially for all 6 cells,
and contains a results.json aggregation step. No edits to run.sh or score.py.
  </done>
</task>

<task type="auto">
  <name>Task 2: Execute the full matrix (real LLM run) and verify artifacts</name>
  <files>benchmark/run-matrix.sh</files>
  <action>
Run the matrix end to end: `bash benchmark/run-matrix.sh`. This is the long, real-LLM-time task —
all 6 cells run serially; L3 (kvstore) cells are slowest, so the whole sweep may take tens of minutes.
Let it complete; do not interrupt or parallelize.

This produces a fresh `benchmark/.runs/matrix-<ts>/` with `results.json`, `manifest.txt`, and six
`*.console.log` files, plus six per-cell run dirs under `benchmark/.runs/` each holding `transcript.log`
and a fully-scored `meta.json`.

Note for verification: do NOT re-run the agents to verify. Verify by inspecting the produced artifacts
only (the metrics are already scored into each meta.json by run.sh's auto-hook).

If the LiteLLM/:4000 backend is down, run.sh will abort the affected cell(s) with a gateway error —
bring the backend up and re-run the matrix (a re-run creates a new clean matrix-<ts> dir).
  </action>
  <verify>
Inspect artifacts (zero new LLM time). Capture the latest matrix dir then assert structure + metrics:

```bash
MX="$(ls -dt benchmark/.runs/matrix-* | head -1)"
echo "matrix: $MX"
python3 - "$MX/results.json" <<'PY'
import json,sys,os
data=json.load(open(sys.argv[1]))
assert len(data)==6, f"expected 6 cells, got {len(data)}"
need={"tool","level","passed","duration_seconds","steps","step_method","files","loc","run_dir","transcript"}
for c in data:
    miss=need-set(c)
    assert not miss, f"{c.get('tool')}/{c.get('level')} missing {miss} (errored cell?)"
    t=os.path.join(c["run_dir"], c["transcript"])
    assert os.path.isfile(t), f"missing transcript {t}"
print("OK: 6 cells, all 4 metrics present, transcripts on disk")
for c in data:
    print(f"  {c['tool']:9} {c['level']:3} passed={c['passed']} {c['duration_seconds']}s steps={c['steps']}({c['step_method']}) {c['files']}f/{c['loc']}loc")
PY
```

All assertions pass; the printout shows 6 rows spanning both tools and all three levels.
  </verify>
  <done>
A matrix-<ts>/results.json with 6 cells exists; every cell carries passed/duration_seconds/steps/
step_method/files/loc and an on-disk transcript.log. (REP-01 satisfied; REP-03 raw evidence preserved.)
  </done>
</task>

</tasks>

<verification>
- `benchmark/run-matrix.sh` passes `bash -n` and is executable.
- Driver calls run.sh serially (no `&`) and never acquires `.runs/.lock` itself.
- Latest `benchmark/.runs/matrix-<ts>/results.json` contains exactly 6 cells (codex/openhands x l1/l2/l3).
- Each cell has all four metrics and a transcript.log present on disk.
</verification>

<success_criteria>
- All 6 matrix cells executed serially via the existing run.sh against qwen-122b (REP-01).
- Metrics for all 6 runs collected into one results.json (REP-01).
- Every run's transcript.log + meta.json preserved on disk (raw evidence for REP-03).
- No concurrency: single backend honored throughout the sweep.
</success_criteria>

<output>
After completion, create `.planning/phases/04-benchmark-run-and-reporting/04-01-SUMMARY.md`.
Record: the matrix dir path used, the 6-cell results (pass/time/steps+step_method/size), any cell that
errored or was retried, and confirm results.json + transcripts are present for Plan 02 to consume.
</output>
